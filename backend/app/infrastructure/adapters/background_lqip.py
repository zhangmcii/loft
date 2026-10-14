from __future__ import annotations

import io
import logging
import os
from urllib.parse import urlparse

import requests

from ...domain.ports.background_lqip import BackgroundLqipPort

_BACKGROUND_PREFIXES = ("userBackground/mobile/", "userBackground/pc/")
_MAX_IMAGE_BYTES = 5 * 1024 * 1024


class QiniuBackgroundLqipAdapter(BackgroundLqipPort):
    def build(self, image_url: str | None) -> str | None:
        if not image_url or not self._is_allowed_background_url(image_url):
            return None

        try:
            image_bytes = self._download_image(image_url)
            if image_bytes is None:
                return None

            # 延迟导入，避免非图片流程在缺少可选依赖时无法启动。
            from thumbhash import image_to_thumbhash

            return image_to_thumbhash(io.BytesIO(image_bytes))
        except Exception as exc:
            logging.warning("生成背景 ThumbHash 失败: %s", exc)
            return None

    @staticmethod
    def _download_image(image_url: str) -> bytes | None:
        response = requests.get(image_url, timeout=(2, 5), stream=True)
        response.raise_for_status()

        content_length = int(response.headers.get("content-length", 0))
        if content_length > _MAX_IMAGE_BYTES:
            logging.warning("背景图过大，跳过 ThumbHash 生成: %s", image_url)
            return None

        chunks = []
        total_size = 0
        for chunk in response.iter_content(chunk_size=64 * 1024):
            total_size += len(chunk)
            if total_size > _MAX_IMAGE_BYTES:
                logging.warning("背景图过大，跳过 ThumbHash 生成: %s", image_url)
                return None
            chunks.append(chunk)
        return b"".join(chunks)

    @staticmethod
    def _is_allowed_background_url(image_url: str) -> bool:
        parsed_image_url = urlparse(image_url)
        configured_domain = urlparse(os.getenv("QINIU_DOMAIN", "").rstrip("/"))
        if not configured_domain.netloc:
            configured_domain = urlparse(f"https://{configured_domain.path}")

        return (
            parsed_image_url.scheme in {"http", "https"}
            and parsed_image_url.netloc == configured_domain.netloc
            and parsed_image_url.path.lstrip("/").startswith(_BACKGROUND_PREFIXES)
        )
