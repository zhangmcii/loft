from __future__ import annotations

from typing import Protocol


class BackgroundLqipPort(Protocol):
    def build(self, image_url: str | None) -> str | None:
        ...
