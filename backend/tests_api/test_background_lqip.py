from io import BytesIO

from app.infrastructure.adapters.background_lqip import QiniuBackgroundLqipAdapter
from PIL import Image


class FakeResponse:
    def __init__(self, image_bytes):
        self.headers = {"content-length": str(len(image_bytes))}
        self.image_bytes = image_bytes

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size):
        yield self.image_bytes


def test_builds_thumbhash_for_configured_background(monkeypatch):
    image_buffer = BytesIO()
    Image.new("RGB", (8, 8), color="#405060").save(image_buffer, format="PNG")
    response = FakeResponse(image_buffer.getvalue())
    monkeypatch.setenv("QINIU_DOMAIN", "cdn.example.com")
    monkeypatch.setattr(
        "app.infrastructure.adapters.background_lqip.requests.get",
        lambda *args, **kwargs: response,
    )

    result = QiniuBackgroundLqipAdapter().build(
        "https://cdn.example.com/userBackground/mobile/image.webp"
    )

    assert isinstance(result, str)
    assert result


def test_rejects_untrusted_background_url(monkeypatch):
    monkeypatch.setenv("QINIU_DOMAIN", "cdn.example.com")

    result = QiniuBackgroundLqipAdapter().build(
        "https://untrusted.example.com/userBackground/mobile/image.webp"
    )

    assert result is None
