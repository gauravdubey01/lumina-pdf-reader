"""
Generates all Microsoft Store and MSIX package asset images and desktop icons for OmniPDF.
"""
import os
from PIL import Image, ImageDraw, ImageFont

def draw_omnipdf_logo(size: int, transparent_bg: bool = False, scale: float = 0.85) -> Image.Image:
    """Renders high-quality OmniPDF emblem at exact pixel dimension."""
    # Render at 4x for super sampling antialiasing
    scale_factor = 4
    canvas_size = size * scale_factor
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = int((1.0 - scale) * canvas_size / 2)
    box = [margin, margin, canvas_size - margin, canvas_size - margin]
    radius = int(canvas_size * 0.22)

    # 1. Background Rounded Squircle
    if not transparent_bg:
        # Deep royal blue to electric blue gradient look
        draw.rounded_rectangle(box, radius=radius, fill=(37, 99, 235))
        # Inner subtle gradient inset
        inset = int(canvas_size * 0.02)
        inner_box = [box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset]
        draw.rounded_rectangle(inner_box, radius=radius - inset, fill=(30, 64, 175))

    # 2. Book Pages (Left and Right)
    center_x = canvas_size // 2
    book_top = int(canvas_size * 0.22)
    book_bot = int(canvas_size * 0.78)
    book_w = int(canvas_size * 0.32)

    # Left Page
    left_rect = [center_x - book_w - int(canvas_size * 0.01), book_top,
                 center_x - int(canvas_size * 0.02), book_bot]
    draw.rounded_rectangle(left_rect, radius=int(canvas_size * 0.035), fill=(248, 250, 252))

    # Right Page
    right_rect = [center_x + int(canvas_size * 0.02), book_top,
                  center_x + book_w + int(canvas_size * 0.01), book_bot]
    draw.rounded_rectangle(right_rect, radius=int(canvas_size * 0.035), fill=(241, 245, 249))

    # Center Spine shadow
    spine_rect = [center_x - int(canvas_size * 0.02), book_top,
                  center_x + int(canvas_size * 0.02), book_bot]
    draw.rectangle(spine_rect, fill=(203, 213, 225))

    # Page content lines (Left page)
    line_spacing = int(canvas_size * 0.075)
    line_h = max(2, int(canvas_size * 0.025))
    line_l_start = center_x - book_w + int(canvas_size * 0.05)
    line_l_end = center_x - int(canvas_size * 0.07)
    for y in range(book_top + int(canvas_size * 0.12), book_bot - int(canvas_size * 0.08), line_spacing):
        draw.rounded_rectangle([line_l_start, y, line_l_end, y + line_h], radius=line_h // 2, fill=(148, 163, 184))

    # Page content lines (Right page)
    line_r_start = center_x + int(canvas_size * 0.07)
    line_r_end = center_x + book_w - int(canvas_size * 0.05)
    for y in range(book_top + int(canvas_size * 0.12), book_bot - int(canvas_size * 0.08), line_spacing):
        draw.rounded_rectangle([line_r_start, y, line_r_end, y + line_h], radius=line_h // 2, fill=(148, 163, 184))

    # Red Bookmark Ribbon
    ribbon_w = int(canvas_size * 0.04)
    ribbon_h = int(canvas_size * 0.22)
    ribbon_x = center_x - ribbon_w // 2
    draw.polygon([
        (ribbon_x, book_top),
        (ribbon_x + ribbon_w, book_top),
        (ribbon_x + ribbon_w, book_top + ribbon_h),
        (center_x, book_top + ribbon_h - int(canvas_size * 0.03)),
        (ribbon_x, book_top + ribbon_h)
    ], fill=(239, 68, 68))

    # Downsample with Lanczos filter for extreme crispness
    return img.resize((size, size), Image.Resampling.LANCZOS)

def draw_wide_tile(w: int, h: int) -> Image.Image:
    """Renders Wide310x150 tile with logo and title."""
    scale = 2
    canvas_w, canvas_h = w * scale, h * scale
    img = Image.new("RGBA", (canvas_w, canvas_h), (30, 64, 175))
    draw = ImageDraw.Draw(img)

    # Logo on the left
    logo_size = int(canvas_h * 0.70)
    logo = draw_omnipdf_logo(logo_size, transparent_bg=False)
    img.paste(logo, (int(canvas_h * 0.15), int(canvas_h * 0.15)), logo)

    # Text "OmniPDF" on right
    # Simple block font
    text_x = int(canvas_h * 1.0)
    draw.text((text_x, int(canvas_h * 0.35)), "OmniPDF", fill=(255, 255, 255))

    return img.resize((w, h), Image.Resampling.LANCZOS)

def draw_splash_screen(w: int, h: int) -> Image.Image:
    """Renders SplashScreen image with centered logo."""
    scale = 2
    canvas_w, canvas_h = w * scale, h * scale
    img = Image.new("RGBA", (canvas_w, canvas_h), (20, 21, 23)) # Dark slate background

    logo_size = int(canvas_h * 0.50)
    logo = draw_omnipdf_logo(logo_size, transparent_bg=False)
    img.paste(logo, ((canvas_w - logo_size) // 2, (canvas_h - logo_size) // 2), logo)

    return img.resize((w, h), Image.Resampling.LANCZOS)

def generate_all_assets():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    msix_assets_dir = os.path.join(assets_dir, "StoreAssets")
    os.makedirs(msix_assets_dir, exist_ok=True)

    # 1. Desktop Application Icons
    app_icon_256 = draw_omnipdf_logo(256)
    app_icon_256.save(os.path.join(assets_dir, "icon.png"), "PNG")
    app_icon_256.save(os.path.join(assets_dir, "icon.ico"), format="ICO",
                      sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Saved assets/icon.png and assets/icon.ico")

    # 2. Microsoft Store & MSIX Visual Assets
    store_specs = {
        # Square44x44 (App list, taskbar)
        "Square44x44Logo.png": (44, 44),
        "Square44x44Logo.targetsize-44.png": (44, 44),
        "Square44x44Logo.scale-100.png": (44, 44),
        "Square44x44Logo.scale-200.png": (88, 88),
        "Square44x44Logo.scale-400.png": (176, 176),
        # Square150x150 (Medium tile)
        "Square150x150Logo.png": (150, 150),
        "Square150x150Logo.scale-100.png": (150, 150),
        "Square150x150Logo.scale-200.png": (300, 300),
        # StoreLogo (Store listing)
        "StoreLogo.png": (50, 50),
        "StoreLogo.scale-100.png": (50, 50),
        "StoreLogo.scale-200.png": (100, 100),
        # SmallTile / LargeTile
        "SmallTile.png": (71, 71),
        "SmallTile.scale-100.png": (71, 71),
        "LargeTile.png": (310, 310),
        "LargeTile.scale-100.png": (310, 310),
    }

    for filename, (w, h) in store_specs.items():
        im = draw_omnipdf_logo(w)
        im.save(os.path.join(msix_assets_dir, filename), "PNG")

    # Wide Tile (310x150)
    wide_100 = draw_wide_tile(310, 150)
    wide_100.save(os.path.join(msix_assets_dir, "Wide310x150Logo.png"), "PNG")
    wide_100.save(os.path.join(msix_assets_dir, "Wide310x150Logo.scale-100.png"), "PNG")
    wide_200 = draw_wide_tile(620, 300)
    wide_200.save(os.path.join(msix_assets_dir, "Wide310x150Logo.scale-200.png"), "PNG")

    # Splash Screen
    splash_100 = draw_splash_screen(620, 300)
    splash_100.save(os.path.join(msix_assets_dir, "SplashScreen.png"), "PNG")
    splash_100.save(os.path.join(msix_assets_dir, "SplashScreen.scale-100.png"), "PNG")
    splash_200 = draw_splash_screen(1240, 600)
    splash_200.save(os.path.join(msix_assets_dir, "SplashScreen.scale-200.png"), "PNG")

    print(f"Generated all {len(store_specs) + 5} Microsoft Store visual assets in assets/StoreAssets/")

if __name__ == "__main__":
    generate_all_assets()
