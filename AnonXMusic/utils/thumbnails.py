import os
import re
import math
import aiofiles
import aiohttp
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode

from AnonXMusic import app
from config import YOUTUBE_IMG_URL # Fallback photo ke liye

# ── Helpers (Dominant Color & Neon Effects) ──────────────────────────────────

def get_dominant_color(img: Image.Image, n=4):
    small = img.convert("RGB").resize((120, 120))
    arr = np.array(small).reshape(-1, 3).astype(float)
    np.random.seed(42)
    centers = arr[np.random.choice(len(arr), n, replace=False)]
    for _ in range(12):
        dists = np.linalg.norm(arr[:, None] - centers[None], axis=2)
        labels = np.argmin(dists, axis=1)
        for k in range(n):
            pts = arr[labels == k]
            if len(pts): centers[k] = pts.mean(axis=0)
    best, best_sat = centers[0], 0
    for c in centers:
        r, g, b = c / 255.0
        mx, mn = max(r, g, b), min(r, g, b)
        sat = (mx - mn) / (mx + 1e-9)
        lum = (mx + mn) / 2
        score = sat * (1 - abs(lum - 0.5))
        if score > best_sat: best_sat, best = score, c
    return tuple(int(x) for x in best)

def make_neon_glow_border(size, bbox, dominant, radius=30, stroke=6, glow_layers=10):
    br, bg, bb = dominant
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    x0, y0, x1, y1 = bbox
    ld = ImageDraw.Draw(layer)
    for i in range(glow_layers, 0, -1):
        alpha = int(5 + (1 - i/glow_layers)**2 * 130)
        ld.rounded_rectangle((x0-i*2, y0-i*2, x1+i*2, y1+i*2), radius=radius, outline=(br, bg, bb, alpha), width=stroke+i)
    ld.rounded_rectangle(bbox, radius=radius, outline=(min(255, br+80), min(255, bg+80), min(255, bb+80), 255), width=stroke)
    return layer

# ── JioSaavn Thumbnail Generator ─────────────────────────────────────────────

async def get_thumb(videoid, user_id, title=None, duration=None, thumbnail=None, views=None, channel=None):
    # Filename sanitize (Saavn IDs me symbols ho sakte hain)
    clean_id = re.sub(r"\W+", "", str(videoid))
    cache_path = f"cache/{clean_id}_{user_id}.png"
    
    if os.path.isfile(cache_path):
        return cache_path

    # Agar thumbnail URL nahi mila toh default image dikhayega
    if not thumbnail:
        return YOUTUBE_IMG_URL

    try:
        # Step 1: Download Saavn Cover Art
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/temp{clean_id}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # Step 2: Set Canvas (2X SCALE for HD Quality)
        SCALE = 2
        W, H = 1280 * SCALE, 720 * SCALE
        canvas = Image.new("RGBA", (W, H), (15, 15, 30, 255))
        
        # Load Downladed Cover
        cover_raw = Image.open(f"cache/temp{clean_id}.png").convert("RGBA")
        dominant = get_dominant_color(cover_raw)
        
        # Step 3: Background Design (Blurred)
        bg = cover_raw.resize((W, H), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(30 * SCALE))
        bg = Image.alpha_composite(bg, Image.new("RGBA", (W, H), (0, 0, 0, 180)))
        canvas.paste(bg, (0, 0))

        # Step 4: Center Square Cover Art
        CV_SIZE = 430 * SCALE
        cover_main = cover_raw.resize((CV_SIZE, CV_SIZE), Image.LANCZOS)
        
        # Rounded Corners
        mask = Image.new("L", (CV_SIZE, CV_SIZE), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, CV_SIZE, CV_SIZE), radius=45*SCALE, fill=255)
        cover_main.putalpha(mask)

        # Step 5: Neon Glow Effects
        CX, CY = (W - CV_SIZE) // 2, (H - CV_SIZE) // 2 - 70 * SCALE
        # Outer Glowing Frame
        canvas.alpha_composite(make_neon_glow_border((W, H), (CX-8, CY-8, CX+CV_SIZE+8, CY+CV_SIZE+8), dominant, radius=50*SCALE, stroke=10*SCALE))
        canvas.alpha_composite(cover_main, (CX, CY))

        # Step 6: Typography (Text)
        try:
            font_title = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 52 * SCALE)
            font_artist = ImageFont.truetype("AnonXMusic/assets/font.ttf", 28 * SCALE)
        except:
            font_title = font_artist = ImageFont.load_default()

        draw = ImageDraw.Draw(canvas)
        
        # Clean Title (Saavn names can be long)
        song_title = unidecode(str(title)).upper()
        if len(song_title) > 30:
            song_title = song_title[:27] + "..."
            
        # Draw Title
        draw.text((W//2, CY + CV_SIZE + 80*SCALE), song_title, fill="white", font=font_title, anchor="mm")
        
        # Draw Artist / Source
        artist_name = channel if channel else "JioSaavn Artist"
        draw.text((W//2, CY + CV_SIZE + 135*SCALE), f"MUSIC VIA JIOSAAVN • {artist_name}", fill=(220, 220, 220), font=font_artist, anchor="mm")

        # Step 7: Progress Bar (Static UI)
        BAR_W, BAR_H = 800 * SCALE, 12 * SCALE
        BX0, BY0 = (W - BAR_W) // 2, CY + CV_SIZE + 190 * SCALE
        # Track Background
        draw.rounded_rectangle((BX0, BY0, BX0 + BAR_W, BY0 + BAR_H), radius=6*SCALE, fill=(70, 70, 90, 150))
        # Active Progress (40% for visual)
        draw.rounded_rectangle((BX0, BY0, BX0 + (BAR_W * 0.4), BY0 + BAR_H), radius=6*SCALE, fill=dominant)
        
        # Timestamps
        dur_text = duration if duration else "03:45"
        draw.text((BX0, BY0 + 40*SCALE), "01:10", fill="white", font=font_artist)
        draw.text((BX0 + BAR_W, BY0 + 40*SCALE), dur_text, fill="white", font=font_artist, anchor="ra")

        # Step 8: Final Resize (Antialiasing) and Save
        canvas = canvas.resize((1280, 720), Image.LANCZOS)
        canvas.save(cache_path)
        
        # Clean up temp file
        if os.path.exists(f"cache/temp{clean_id}.png"):
            os.remove(f"cache/temp{clean_id}.png")
            
        return cache_path

    except Exception as e:
        print(f"JioSaavn Thumb Error: {e}")
        return YOUTUBE_IMG_URL
