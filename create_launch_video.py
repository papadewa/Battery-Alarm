#!/usr/bin/env python3
"""
Battery Cat Grand Launching Video Generator

Creates an animated promotional video showcasing Battery Cat 1.1.2
features: multi-skin support, battery monitoring, alarms, and widget sizes.
"""

from moviepy import (
    VideoClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    ColorClip,
    CompositeAudioClip,
)
from PIL import Image, ImageDraw, ImageFont
import os
import math

# Configuration
OUTPUT_FILE = "battery-cat-grand-launching.mp4"
WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 30  # seconds

# Colors from DESIGN.md
CREAM = "#FFF9EF"
INK = "#512B1D"
MUTED = "#795646"
LINE = "#DFC9B7"
ACCENT = "#8C4126"
WHITE = "#FFFFFF"
BUTTON = "#F6E5D6"
LOW = "#A8342B"
GOOD = "#32664A"

# Asset paths
ASSETS_DIR = "/workspace/assets"
MAIN_CAT = os.path.join(ASSETS_DIR, "cat-clock.png")
SKINS_DIR = os.path.join(ASSETS_DIR, "skins")
FONT_PATH = os.path.join(ASSETS_DIR, "Nunito.ttf")

# Skins
SKINS = [
    ("Kucing", MAIN_CAT),
    ("Beruang", os.path.join(SKINS_DIR, "Beruang.png")),
    ("Kelinci", os.path.join(SKINS_DIR, "Kelinci.png")),
    ("Katak", os.path.join(SKINS_DIR, "Katak.png")),
    ("Panda", os.path.join(SKINS_DIR, "Panda.png")),
]


def create_background(t):
    """Create gradient background"""
    img = Image.new("RGB", (WIDTH, HEIGHT), CREAM)
    draw = ImageDraw.Draw(img)
    
    # Subtle gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(255 * (1 - ratio * 0.05))
        g = int(249 * (1 - ratio * 0.05))
        b = int(239 * (1 - ratio * 0.05))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    
    return img


def create_title_frame():
    """Create opening title frame"""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype(FONT_PATH, 72)
        font_medium = ImageFont.truetype(FONT_PATH, 36)
        font_small = ImageFont.truetype(FONT_PATH, 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Title
    title = "Battery Cat"
    bbox = draw.textbbox((0, 0), title, font=font_large)
    title_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_w) / 2, 150), title, fill=INK, font=font_large)
    
    # Version
    version = "Version 1.1.2"
    bbox = draw.textbbox((0, 0), version, font=font_medium)
    version_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - version_w) / 2, 240), version, fill=MUTED, font=font_medium)
    
    # Tagline
    tagline = "Widget kepala kucing untuk mengingatkan baterai laptop"
    bbox = draw.textbbox((0, 0), tagline, font=font_small)
    tagline_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - tagline_w) / 2, 300), tagline, fill=INK, font=font_small)
    
    return img


def create_feature_text(feature_num, title, description):
    """Create feature text overlay"""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype(FONT_PATH, 48)
        font_desc = ImageFont.truetype(FONT_PATH, 28)
    except:
        font_title = ImageFont.load_default()
        font_desc = ImageFont.load_default()
    
    # Feature number badge
    badge_x = WIDTH // 2 - 300
    badge_y = 400
    
    # Draw badge circle
    draw.ellipse([badge_x, badge_y, badge_x + 60, badge_y + 60], fill=ACCENT)
    draw.text((badge_x + 15, badge_y + 8), str(feature_num), fill=WHITE, font=font_title)
    
    # Title
    draw.text((badge_x + 80, badge_y + 10), title, fill=INK, font=font_title)
    
    # Description
    desc_y = badge_y + 70
    lines = []
    words = description.split()
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font_desc)
        if bbox[2] - bbox[0] < 800:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    for i, line in enumerate(lines[:3]):
        draw.text((badge_x + 80, desc_y + i * 35), line, fill=MUTED, font=font_desc)
    
    return img


def create_closing_frame():
    """Create closing call-to-action frame"""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype(FONT_PATH, 56)
        font_medium = ImageFont.truetype(FONT_PATH, 32)
        font_small = ImageFont.truetype(FONT_PATH, 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Main message
    msg1 = "Download Sekarang!"
    bbox = draw.textbbox((0, 0), msg1, font=font_large)
    msg1_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - msg1_w) / 2, 400), msg1, fill=ACCENT, font=font_large)
    
    msg2 = "Battery-Cat-1.1.2-Windows-x64-Setup.exe"
    bbox = draw.textbbox((0, 0), msg2, font=font_medium)
    msg2_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - msg2_w) / 2, 480), msg2, fill=INK, font=font_medium)
    
    # Features list
    features = [
        "✓ 5 Skin Hewan (Kucing, Beruang, Kelinci, Katak, Panda)",
        "✓ 3 Ukuran Widget (240px, 120px Mini, 72px Mungil)",
        "✓ Alarm Baterai Rendah & Target Pengisian",
        "✓ Offline - Tanpa Akun, Server, atau Telemetri",
        "✓ Windows 10/11 x64"
    ]
    
    y = 580
    for feat in features:
        bbox = draw.textbbox((0, 0), feat, font=font_small)
        feat_w = bbox[2] - bbox[0]
        draw.text(((WIDTH - feat_w) / 2, y), feat, fill=MUTED, font=font_small)
        y += 35
    
    return img


def make_frame(t):
    """Generate frame at time t"""
    bg = create_background(t)
    
    # Scene timing
    if t < 3:
        # Opening title fade in
        alpha = min(1.0, t / 2.0)
        title_img = create_title_frame()
        bg.paste(title_img, (0, 0), title_img)
        
    elif t < 8:
        # Show main cat with title
        title_img = create_title_frame()
        bg.paste(title_img, (0, 0), title_img)
        
        # Load and position cat
        if os.path.exists(MAIN_CAT):
            cat = Image.open(MAIN_CAT).convert("RGBA")
            scale = 0.6
            new_size = (int(cat.width * scale), int(cat.height * scale))
            cat = cat.resize(new_size, Image.Resampling.LANCZOS)
            
            # Gentle bounce animation
            bounce = math.sin(t * 2) * 10
            cat_x = WIDTH // 2 - new_size[0] // 2
            cat_y = HEIGHT // 2 - new_size[1] // 2 + bounce
            
            bg.paste(cat, (cat_x, int(cat_y)), cat)
    
    elif t < 13:
        # Feature 1: Multi-skin showcase
        feature_text = create_feature_text(1, "5 Skin Hewan", 
            "Ganti tampilan dengan Beruang, Kelinci, Katak, dan Panda")
        bg.paste(feature_text, (0, 0), feature_text)
        
        # Cycle through skins
        skin_idx = int((t - 8) / 1.0) % len(SKINS)
        skin_name, skin_path = SKINS[skin_idx]
        
        if os.path.exists(skin_path):
            skin = Image.open(skin_path).convert("RGBA")
            scale = 0.4
            new_size = (int(skin.width * scale), int(skin.height * scale))
            skin = skin.resize(new_size, Image.Resampling.LANCZOS)
            
            skin_x = WIDTH // 2 - new_size[0] // 2
            skin_y = HEIGHT // 2 + 50
            
            bg.paste(skin, (skin_x, skin_y), skin)
    
    elif t < 18:
        # Feature 2: Widget sizes
        feature_text = create_feature_text(2, "3 Ukuran Widget",
            "240px Normal • 120px Mini • 72px Mungil")
        bg.paste(feature_text, (0, 0), feature_text)
        
        # Show size comparison circles
        sizes = [240, 120, 72]
        labels = ["Normal", "Mini", "Mungil"]
        colors = [GOOD, ACCENT, LOW]
        
        start_x = WIDTH // 2 - 200
        for i, (size, label, color) in enumerate(zip(sizes, labels, colors)):
            x = start_x + i * 200
            y = HEIGHT // 2 + 50
            
            # Draw circle
            draw = ImageDraw.Draw(bg)
            draw.ellipse([x - size//2, y - size//2, x + size//2, y + size//2], 
                        outline=color, width=3)
            draw.text((x - 30, y - 10), label, fill=INK)
    
    elif t < 23:
        # Feature 3: Smart alarms
        feature_text = create_feature_text(3, "Alarm Pintar",
            "Baterai Rendah & Target Pengisian dengan 3 Nada")
        bg.paste(feature_text, (0, 0), feature_text)
        
        # Draw alarm indicators
        draw = ImageDraw.Draw(bg)
        
        # Low battery indicator
        x1, y1 = WIDTH // 2 - 150, HEIGHT // 2
        draw.rounded_rectangle([x1, y1, x1 + 120, y1 + 60], radius=10, fill=LOW)
        draw.text((x1 + 15, y1 + 18), "LOW", fill=WHITE)
        
        # Target indicator
        x2, y2 = WIDTH // 2 + 30, HEIGHT // 2
        draw.rounded_rectangle([x2, y2, x2 + 120, y2 + 60], radius=10, fill=GOOD)
        draw.text((x2 + 15, y2 + 18), "TARGET", fill=WHITE)
    
    elif t < 28:
        # Feature 4: Privacy focused
        feature_text = create_feature_text(4, "100% Offline",
            "Tanpa Akun • Tanpa Server • Tanpa Telemetri")
        bg.paste(feature_text, (0, 0), feature_text)
        
        # Privacy icons
        draw = ImageDraw.Draw(bg)
        cx, cy = WIDTH // 2, HEIGHT // 2 + 80
        
        # Lock icon
        draw.rectangle([cx - 30, cy - 20, cx + 30, cy + 30], fill=ACCENT)
        draw.arc([cx - 20, cy - 35, cx + 20, cy - 10], 180, 0, fill=WHITE, width=5)
        
    else:
        # Closing frame
        closing = create_closing_frame()
        bg.paste(closing, (0, 0), closing)
    
    # Convert to numpy array for moviepy
    import numpy as np
    return np.array(bg.convert("RGB"))


def main():
    print("Creating Battery Cat Grand Launching Video...")
    print(f"Resolution: {WIDTH}x{HEIGHT}")
    print(f"Duration: {DURATION} seconds")
    print(f"FPS: {FPS}")
    
    # Create video clip
    video = VideoClip(make_frame, duration=DURATION).with_fps(FPS)
    
    # Write output
    print(f"Rendering to {OUTPUT_FILE}...")
    video.write_videofile(
        OUTPUT_FILE,
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="medium",
        bitrate="5000k"
    )
    
    print(f"\n✓ Video created successfully: {OUTPUT_FILE}")
    print("\nFeatures showcased:")
    print("  • Opening title with version 1.1.2")
    print("  • Main cat-clock character")
    print("  • 5 animal skins rotation")
    print("  • 3 widget size comparison")
    print("  • Smart alarm system")
    print("  • Privacy-focused messaging")
    print("  • Call-to-action closing")


if __name__ == "__main__":
    main()
