"""تولید تصویر کارت بانکی - داینامیک با اطلاعات پرداخت"""

import os
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "webapp" / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# Card template colors
CARD_GRADIENT_START = (41, 128, 185)
CARD_GRADIENT_END = (44, 62, 80)
TEXT_COLOR = (255, 255, 255)
LABEL_COLOR = (189, 195, 199)


async def generate_card_image(
    card_number: str,
    card_holder: str,
    bank_name: str,
    amount: float,
    output_path: Optional[str] = None,
) -> str:
    """تولید تصویر کارت بانکی با اطلاعات تراکنش"""

    # Create image (800x500)
    width, height = 800, 500
    img = Image.new("RGB", (width, height), CARD_GRADIENT_END)
    draw = ImageDraw.Draw(img)

    # Draw gradient background
    for y in range(height):
        r = int(CARD_GRADIENT_START[0] + (CARD_GRADIENT_END[0] - CARD_GRADIENT_START[0]) * y / height)
        g = int(CARD_GRADIENT_START[1] + (CARD_GRADIENT_END[1] - CARD_GRADIENT_START[1]) * y / height)
        b = int(CARD_GRADIENT_START[2] + (CARD_GRADIENT_END[2] - CARD_GRADIENT_START[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Draw decorative circle
    draw.ellipse([550, -100, 850, 200], fill=(255, 255, 255, 30))
    draw.ellipse([-100, 300, 200, 600], fill=(255, 255, 255, 20))

    # Load font (fallback to default if not found)
    try:
        font_large = ImageFont.truetype(str(FONTS_DIR / "Vazir-Bold.ttf"), 36)
        font_medium = ImageFont.truetype(str(FONTS_DIR / "Vazir-Medium.ttf"), 24)
        font_small = ImageFont.truetype(str(FONTS_DIR / "Vazir-Medium.ttf"), 18)
    except (IOError, OSError):
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except (IOError, OSError):
            font_large = ImageFont.load_default()
            font_medium = font_large
            font_small = font_large

    # Bank name
    draw.text((50, 40), bank_name, fill=TEXT_COLOR, font=font_large)

    # Chip icon (simplified)
    draw.rounded_rectangle([50, 120, 100, 160], radius=5, fill=(241, 196, 15))
    draw.text((58, 128), "💳", fill=(0, 0, 0), font=font_small)

    # Card number (formatted)
    formatted_number = " ".join([card_number[i:i+4] for i in range(0, len(card_number), 4)])
    draw.text((50, 200), formatted_number, fill=TEXT_COLOR, font=font_large)

    # Card holder
    draw.text((50, 280), "CARD HOLDER", fill=LABEL_COLOR, font=font_small)
    draw.text((50, 305), card_holder.upper(), fill=TEXT_COLOR, font=font_medium)

    # Amount box
    draw.rounded_rectangle([50, 370, 350, 450], radius=10, fill=(0, 0, 0, 100))
    draw.text((70, 380), "مبلغ قابل پرداخت", fill=LABEL_COLOR, font=font_medium)
    amount_text = f"{amount:,.0f} تومان"
    draw.text((70, 410), amount_text, fill=TEXT_COLOR, font=font_large)

    # Save image
    if output_path is None:
        output_path = str(BASE_DIR / "temp" / f"card_{card_number[-4:]}_{int(amount)}.png")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img.save(output_path, "PNG")
    return output_path


def generate_qr_code(data: str, output_path: Optional[str] = None) -> str:
    """تولید QR Code از متن ورودی"""
    import qrcode

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if output_path is None:
        output_path = str(BASE_DIR / "temp" / f"qr_{hash(data)}.png")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img.save(output_path)
    return output_path
