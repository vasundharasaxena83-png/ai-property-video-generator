"""Create a caption-only MP4 using Pillow-rendered frames and FFmpeg."""
from __future__ import annotations
import os, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import imageio_ffmpeg

WIDTH, HEIGHT = 1280, 720
FPS = 12
SECONDS_PER_SCENE = 3

def _font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def _wrap(draw, text: str, font, max_width: int):
    words = str(text).split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width or not current:
            current = candidate
        else:
            lines.append(current); current = word
    if current: lines.append(current)
    return lines

def _render_frame(image_path: Path, scene: dict, property_name: str, location: str,
                  price: str, index: int, total: int, frame_number: int, output_path: Path):
    with Image.open(image_path) as source:
        source = source.convert("RGB")
        # Gentle zoom over each scene for motion while keeping text crisp.
        progress = (frame_number % (FPS * SECONDS_PER_SCENE)) / max(1, FPS * SECONDS_PER_SCENE - 1)
        scale = 1.0 + 0.035 * progress
        crop_w, crop_h = int(WIDTH / scale), int(HEIGHT / scale)
        left = max(0, (source.width - crop_w) // 2)
        top = max(0, (source.height - crop_h) // 2)
        crop = source.crop((left, top, left + crop_w, top + crop_h))
        bg = ImageOps.fit(crop, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
    # Soft dark overlays for legible text.
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    d.rectangle((0,0,WIDTH,112), fill=(12,25,34,205))
    d.rectangle((0,HEIGHT-205,WIDTH,HEIGHT), fill=(12,25,34,205))
    d.text((48,25), property_name, font=_font(32, True), fill=(255,255,255,255))
    d.text((50,70), location, font=_font(20), fill=(224,235,239,255))
    label = str(scene.get("label","PROPERTY")).upper()
    d.text((50, HEIGHT-180), label, font=_font(19, True), fill=(117,220,185,255))
    caption_font = _font(37, True)
    lines = _wrap(d, scene.get("caption",""), caption_font, WIDTH-100)
    if len(lines) > 2:
        caption_font = _font(31, True)
        lines = _wrap(d, scene.get("caption",""), caption_font, WIDTH-100)
    y = HEIGHT-143
    for line in lines[:2]:
        d.text((48,y), line, font=caption_font, fill=(255,255,255,255), stroke_width=1, stroke_fill=(0,0,0,100))
        y += 48
    if price:
        price_text = f"PRICE  {price}"
        d.rounded_rectangle((WIDTH-360, 28, WIDTH-42, 82), radius=14, fill=(117,220,185,245))
        d.text((WIDTH-342, 40), price_text, font=_font(20, True), fill=(15,36,37,255))
    # progress indicator
    bar_w = int((WIDTH-96) * ((index + progress) / max(total,1)))
    d.rounded_rectangle((48, HEIGHT-16, WIDTH-48, HEIGHT-8), radius=4, fill=(255,255,255,85))
    d.rounded_rectangle((48, HEIGHT-16, 48+max(1,bar_w), HEIGHT-8), radius=4, fill=(117,220,185,255))
    final = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    final.save(output_path, quality=90)

def create_video(images, scenes, property_name: str, location: str, price: str,
                 output_path: str | Path, fps: int = FPS, seconds_per_scene: int = SECONDS_PER_SCENE) -> Path:
    """Render scenes into a silent MP4. Raises ValueError/RuntimeError with useful messages."""
    images = [Path(p) for p in images]
    if len(images) < 4:
        raise ValueError("Please provide at least 4 valid property images.")
    if len(images) > 8:
        raise ValueError("Please provide no more than 8 property images.")
    if not scenes:
        raise ValueError("No scenes were generated. Add property details and try again.")
    for image_path in images:
        if not image_path.is_file():
            raise ValueError(f"Image file was not found: {image_path}")
        try:
            with Image.open(image_path) as im: im.verify()
        except Exception as exc:
            raise ValueError(f"Cannot read image '{image_path.name}'. Use a valid JPG or PNG.") from exc
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Preserve the final call-to-action when there are fewer images than generated scenes.
    if len(scenes) > len(images):
        selected_scenes = list(scenes[:len(images)-1]) + [scenes[-1]]
    else:
        selected_scenes = list(scenes[:len(images)])
    scene_count = len(selected_scenes)
    with tempfile.TemporaryDirectory(prefix="property_video_") as tmp:
        frame_dir = Path(tmp)
        frame_no = 0
        for i in range(scene_count):
            for _ in range(max(1, int(fps)) * max(1, int(seconds_per_scene))):
                frame_path = frame_dir / f"frame_{frame_no:06d}.jpg"
                _render_frame(images[i], selected_scenes[i], property_name, location, price,
                              i, scene_count, frame_no, frame_path)
                frame_no += 1
        command = [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
            "-framerate", str(int(fps)), "-i", str(frame_dir / "frame_%06d.jpg"),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output_path)
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=240)
        if result.returncode != 0 or not output_path.exists() or output_path.stat().st_size == 0:
            detail = (result.stderr or result.stdout or "Unknown FFmpeg error").strip()[-1200:]
            raise RuntimeError("Video export failed. Check that FFmpeg is available. " + detail)
    return output_path
