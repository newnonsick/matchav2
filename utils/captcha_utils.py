import asyncio
from io import BytesIO
from captcha.image import ImageCaptcha


async def generate_captcha(captcha_text: str) -> BytesIO:
    def _generate():
        image = ImageCaptcha(width=280, height=90)
        data = image.generate(captcha_text)
        image_bytes = BytesIO(data.read())
        image_bytes.name = "captcha.png"
        image_bytes.seek(0)
        return image_bytes

    return await asyncio.to_thread(_generate)
