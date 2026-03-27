from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..application.dto import PageResult
from ..domain.common.exceptions import DomainError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.hot_posts import HotPostsRankingPort
from ..infrastructure.capabilities import capability_enabled, get_capability
from ..utils.time_util import DateUtils


@dataclass(frozen=True)
class HotPostsConfig:
    key: str
    min_likes: int
    min_comments: int
    max_size: int
    window_days: int | None
    comment_weight: float
    decay_alpha: float
    candidate_limit: int


class HotPostsService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        assembler: ResponseAssemblerPort,
        ranking: HotPostsRankingPort,
        config: HotPostsConfig,
    ):
        self.uow = uow
        self.assembler = assembler
        self.ranking = ranking
        self.config = config

    def list_hot_posts(self, *, page: int, per_page: int, viewer=None) -> PageResult:
        self._ensure_redis_available()

        page = max(1, int(page))
        per_page = max(1, int(per_page))
        offset = (page - 1) * per_page

        ids = self.ranking.get_top_ids(offset=offset, limit=per_page)
        total = self.ranking.count()
        if not ids:
            return PageResult(data=[], total=total)

        posts = self.uow.posts.list_posts_by_ids(ids, viewer=viewer)
        extra_data_map = self.uow.posts.build_post_extra_data_map(
            posts, viewer_id=(viewer.id if viewer else None)
        )
        mapped = self.assembler.batch_map_posts(
            posts, extra_data_map=extra_data_map, is_list=True
        )
        return PageResult(data=mapped, total=total)

    def rebuild_hot_rank(self, *, now: datetime | None = None) -> int:
        self._ensure_redis_available()

        now = now or DateUtils.now_time()
        rebuild_epoch = int(now.timestamp())
        self.ranking.set_rebuilt_at(epoch_seconds=rebuild_epoch)
        since = self._window_since(now)
        candidates = self.uow.posts.list_hot_candidates(
            since=since,
            min_likes=self.config.min_likes,
            min_comments=self.config.min_comments,
            limit=self.config.candidate_limit,
            comment_weight=self.config.comment_weight,
        )
        scored: list[tuple[int, float]] = []
        for post_id, timestamp, like_count, comment_count in candidates:
            score = self._score(
                now=now,
                timestamp=timestamp,
                like_count=like_count,
                comment_count=comment_count,
            )
            score += self._stable_tiebreak(timestamp)
            if score <= 0:
                continue
            scored.append((post_id, score))

        if not scored:
            self.ranking.trim(max_size=0)
            return 0

        scored.sort(key=lambda item: item[1], reverse=True)
        top = scored[: self.config.max_size]
        # 全量重建：先清空旧榜，避免残留旧分数导致脏数据。
        self.ranking.trim(max_size=0)
        self.ranking.upsert_scores(pairs=top)
        return len(top)

    def increment_post_engagement(
        self,
        *,
        post_id: int,
        delta_likes: int = 0,
        delta_comments: int = 0,
        now: datetime | None = None,
    ) -> None:
        self._ensure_redis_available()

        now = now or DateUtils.now_time()
        rebuild_epoch = self._ensure_rebuild_epoch(now=now)

        existing = self.ranking.get_score(post_id=post_id)
        if existing is None:
            # 尚未入榜：先从数据库校验是否满足门槛，然后用“最近一次重建时刻”作为基准写入初始分数。
            engagement = self.uow.posts.get_post_engagement(post_id)
            if not engagement:
                return
            timestamp, deleted, like_count, comment_count = engagement
            if deleted:
                return
            if not self._passes_window(timestamp=timestamp, now=now):
                return
            if (
                like_count < self.config.min_likes
                or comment_count < self.config.min_comments
            ):
                return

            score = self._score_at_epoch(
                rebuild_epoch=rebuild_epoch,
                timestamp=timestamp,
                like_count=like_count,
                comment_count=comment_count,
            )
            score += self._stable_tiebreak(timestamp)
            self.ranking.upsert_scores(pairs=[(post_id, score)])
            self.ranking.trim(max_size=self.config.max_size)
            return

        delta_engagement = float(delta_likes) + float(delta_comments) * float(
            self.config.comment_weight
        )
        if delta_engagement <= 0:
            return

        timestamp = self.uow.posts.get_post_timestamp(post_id)
        if not timestamp:
            return
        if not self._passes_window(timestamp=timestamp, now=now):
            return

        denom = self._age_seconds_at_epoch(
            rebuild_epoch=rebuild_epoch, timestamp=timestamp
        )
        delta_score = delta_engagement / math.pow(denom, float(self.config.decay_alpha))
        self.ranking.incr_score(post_id=post_id, delta=delta_score)
        self.ranking.trim(max_size=self.config.max_size)

    def remove_post(self, *, post_id: int) -> None:
        self._ensure_redis_available()
        self.ranking.remove(post_id=post_id)

    def remove_posts(self, *, post_ids: list[int]) -> None:
        self._ensure_redis_available()
        self.ranking.remove_many(post_ids=post_ids)

    def _ensure_redis_available(self) -> None:
        if capability_enabled("redis", default=True):
            return
        reason = (get_capability("redis") or {}).get("reason", "redis unavailable")
        raise DomainError(message=f"热门榜暂不可用: {reason}", code=503)

    def _window_since(self, now: datetime) -> datetime | None:
        if not self.config.window_days or self.config.window_days <= 0:
            return None
        return now - timedelta(days=self.config.window_days)

    def _passes_window(self, *, timestamp: datetime, now: datetime) -> bool:
        since = self._window_since(now)
        if since is None:
            return True
        return timestamp >= since

    def _score(
        self,
        *,
        now: datetime,
        timestamp: datetime,
        like_count: int,
        comment_count: int,
    ) -> float:
        engagement = float(like_count) + float(comment_count) * float(
            self.config.comment_weight
        )
        if engagement <= 0:
            return 0.0

        age_seconds = max(1.0, (now - timestamp).total_seconds())
        return engagement / math.pow(age_seconds, float(self.config.decay_alpha))

    def _ensure_rebuild_epoch(self, *, now: datetime) -> int:
        existing = self.ranking.get_rebuilt_at()
        if existing:
            return int(existing)
        epoch = int(now.timestamp())
        self.ranking.set_rebuilt_at(epoch_seconds=epoch)
        return epoch

    @staticmethod
    def _age_seconds_at_epoch(*, rebuild_epoch: int, timestamp: datetime) -> float:
        try:
            ts = int(timestamp.timestamp())
        except (OSError, ValueError):
            ts = int(DateUtils.now_time().timestamp())
        return float(max(1, rebuild_epoch - ts))

    def _score_at_epoch(
        self,
        *,
        rebuild_epoch: int,
        timestamp: datetime,
        like_count: int,
        comment_count: int,
    ) -> float:
        engagement = float(like_count) + float(comment_count) * float(
            self.config.comment_weight
        )
        if engagement <= 0:
            return 0.0
        denom = self._age_seconds_at_epoch(
            rebuild_epoch=rebuild_epoch, timestamp=timestamp
        )
        return engagement / math.pow(denom, float(self.config.decay_alpha))

    @staticmethod
    def _stable_tiebreak(timestamp: datetime) -> float:
        # 同分时保证排序稳定：加入一个极小的时间微权重，避免列表抖动。
        # 注意该微权重要足够小，不影响正常的热度排序。
        try:
            return float(timestamp.timestamp()) / 1e15
        except (OSError, ValueError):
            return 0.0
