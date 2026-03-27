from __future__ import annotations

from typing import Iterable

from ...domain.ports.hot_posts import HotPostsRankingPort


class RedisHotPostsRankingAdapter(HotPostsRankingPort):
    def __init__(self, *, redis_client, key: str):
        self.redis = redis_client
        self.key = key
        self.meta_rebuilt_at_key = f"{key}:rebuilt_at"

    def get_rebuilt_at(self) -> int | None:
        raw = self.redis.get(self.meta_rebuilt_at_key)
        if raw is None:
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    def set_rebuilt_at(self, *, epoch_seconds: int) -> None:
        self.redis.set(self.meta_rebuilt_at_key, int(epoch_seconds))

    def get_top_ids(self, *, offset: int, limit: int) -> list[int]:
        if limit <= 0:
            return []
        start = max(0, offset)
        end = start + limit - 1
        raw: Iterable[str] = self.redis.zrevrange(self.key, start, end) or []
        ids: list[int] = []
        for item in raw:
            try:
                ids.append(int(item))
            except (TypeError, ValueError):
                continue
        return ids

    def count(self) -> int:
        return int(self.redis.zcard(self.key) or 0)

    def get_score(self, *, post_id: int) -> float | None:
        raw = self.redis.zscore(self.key, str(post_id))
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    def upsert_scores(self, *, pairs: list[tuple[int, float]]) -> None:
        if not pairs:
            return
        mapping = {str(post_id): float(score) for post_id, score in pairs}
        # redis-py 调用形式：zadd(name, mapping)
        self.redis.zadd(self.key, mapping)

    def incr_score(self, *, post_id: int, delta: float) -> float:
        return float(self.redis.zincrby(self.key, float(delta), str(post_id)) or 0.0)

    def remove(self, *, post_id: int) -> None:
        self.redis.zrem(self.key, str(post_id))

    def remove_many(self, *, post_ids: list[int]) -> None:
        if not post_ids:
            return
        members = [str(pid) for pid in post_ids]
        self.redis.zrem(self.key, *members)

    def trim(self, *, max_size: int) -> None:
        if max_size <= 0:
            # 约定：max_size<=0 时清空榜单
            self.redis.delete(self.key)
            return
        total = self.count()
        if total <= max_size:
            return
        # 只保留前若干条（最高分）：删除低分尾部。
        # ZREMRANGEBYRANK 的排名按分数从低到高（最低分排名=0），
        # 所以删除区间：0 .. (total-max_size-1)。
        remove_end = total - max_size - 1
        if remove_end >= 0:
            self.redis.zremrangebyrank(self.key, 0, remove_end)
