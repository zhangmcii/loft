from __future__ import annotations

from typing import Protocol


class HotPostsRankingPort(Protocol):
    def get_rebuilt_at(self) -> int | None:
        ...

    def set_rebuilt_at(self, *, epoch_seconds: int) -> None:
        ...

    def get_top_ids(self, *, offset: int, limit: int) -> list[int]:
        ...

    def count(self) -> int:
        ...

    def get_score(self, *, post_id: int) -> float | None:
        ...

    def upsert_scores(self, *, pairs: list[tuple[int, float]]) -> None:
        ...

    def incr_score(self, *, post_id: int, delta: float) -> float:
        ...

    def remove(self, *, post_id: int) -> None:
        ...

    def remove_many(self, *, post_ids: list[int]) -> None:
        ...

    def trim(self, *, max_size: int) -> None:
        ...
