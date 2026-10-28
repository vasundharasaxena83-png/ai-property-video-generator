from pathlib import Path
import json
from script_generator import generate_scenes
from video_generator import create_video

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "sample_data.json").read_text(encoding="utf-8"))
images = [ROOT / "sample_images" / name for name in data["image_files"]]
scenes = generate_scenes(data["property_name"], data["location"], data["price"],
                         data["property_type"], data["features"], data["cta_text"])
out = ROOT / "output" / "sample_property_video.mp4"
create_video(images, scenes, data["property_name"], data["location"], data["price"], out)
print(f"Created: {out} ({out.stat().st_size:,} bytes)")
