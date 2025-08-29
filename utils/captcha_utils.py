import asyncio
import random
import string
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter, ImageFont

COLOR_PALETTE = [
    # Grays
    # [
    #     (100, 100, 100),
    #     (120, 120, 120),
    #     (140, 140, 140),
    #     (160, 160, 160),
    #     (180, 180, 180),
    #     (200, 200, 200),
    # ],
    # Blues
    [(0, 0, 100), (0, 0, 120), (0, 0, 140), (0, 0, 160), (0, 0, 180), (0, 0, 200)],
    # Greens
    [(0, 100, 0), (0, 120, 0), (0, 140, 0), (0, 160, 0), (0, 180, 0), (0, 200, 0)],
    # Reds
    [(100, 0, 0), (120, 0, 0), (140, 0, 0), (160, 0, 0), (180, 0, 0), (200, 0, 0)],
    # Purples
    [
        (100, 0, 100),
        (120, 0, 120),
        (140, 0, 140),
        (160, 0, 160),
        (180, 0, 180),
        (200, 0, 200),
    ],
    # Oranges
    # [
    #     (255, 140, 0),
    #     (255, 165, 0),
    #     (255, 192, 0),
    #     (255, 200, 0),
    #     (255, 215, 0),
    #     (255, 225, 0),
    # ],
]


async def generate_captcha(
    captcha_text: str, width: int = 280, height: int = 90
) -> BytesIO | None:
    
    def _generate():
        try:
            selected_palette = random.choice(COLOR_PALETTE)

            image = Image.new("RGB", (width, height), (240, 240, 240))
            draw = ImageDraw.Draw(image)

            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except IOError:
                font = ImageFont.load_default()

            for _ in range(15):
                start_angle = random.randint(0, 360)
                end_angle = start_angle + random.randint(90, 270)
                fill_color = random.choice(selected_palette)
                line_width = random.randint(1, 3)

                x0 = random.randint(-100, width + 100)
                y0 = random.randint(-100, height + 100)
                x1 = random.randint(-100, width + 100)
                y1 = random.randint(-100, height + 100)

                if x0 > x1:
                    x0, x1 = x1, x0
                if y0 > y1:
                    y0, y1 = y1, y0

                draw.arc(
                    (x0, y0, x1, y1),
                    start=start_angle,
                    end=end_angle,
                    fill=fill_color,
                    width=line_width,
                )

            circle_radius = random.randint(30, 60)

            circle_x_min = circle_radius
            circle_x_max = width - circle_radius
            if circle_x_min < circle_x_max:
                circle_x = random.randint(circle_x_min, circle_x_max)
            else:
                circle_x = circle_radius

            circle_y_min = circle_radius
            circle_y_max = height - circle_radius
            if circle_y_min < circle_y_max:
                circle_y = random.randint(circle_y_min, circle_y_max)
            else:
                circle_y = circle_radius

            # circle_fill_color = (0, 0, 0, 128)
            circle_fill_color = random.choice(selected_palette) + (50,)

            overlay = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.ellipse(
                (
                    circle_x - circle_radius,
                    circle_y - circle_radius,
                    circle_x + circle_radius,
                    circle_y + circle_radius,
                ),
                fill=circle_fill_color,
            )
            image = Image.alpha_composite(image.convert("RGBA"), overlay)
            image = image.convert("RGB")
            draw = ImageDraw.Draw(image)

            x_offset = 30
            for _, char in enumerate(captcha_text[:5]):
                temp_image = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_image)

                char_color = random.choice(selected_palette)
                temp_draw.text((10, 10), char, font=font, fill=char_color)

                rotation_angle = random.randint(-25, 25)
                rotated_char = temp_image.rotate(rotation_angle, expand=True)

                x = x_offset + random.randint(-5, 5)

                y_min = 0
                y_max = height - rotated_char.height - 5
                if y_min < y_max:
                    y = random.randint(y_min, y_max)
                else:
                    y = y_min

                image.paste(rotated_char, (x, y), rotated_char)
                x_offset += 45

            for _ in range(500):
                x_min = 0
                x_max = width
                y_min = 0
                y_max = height

                if x_min < x_max:
                    x = random.randint(x_min, x_max)
                else:
                    x = x_min

                if y_min < y_max:
                    y = random.randint(y_min, y_max)
                else:
                    y = y_min

                dot_color = random.choice(selected_palette)
                draw.point((x, y), fill=dot_color)

            image = image.filter(ImageFilter.SMOOTH)
            image = image.filter(ImageFilter.GaussianBlur(1.5))
            image = image.filter(ImageFilter.EDGE_ENHANCE)

            image_bytes = BytesIO()
            image.save(image_bytes, format="PNG")
            image_bytes.name = "captcha.png"
            image_bytes.seek(0)
            return image_bytes
        except Exception as e:
            print(f"An error occurred during CAPTCHA generation: {e}")
            return None

    return await asyncio.to_thread(_generate)
