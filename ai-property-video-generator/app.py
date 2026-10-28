from pathlib import Path
import json, tempfile
import streamlit as st
from PIL import Image, UnidentifiedImageError
from script_generator import generate_scenes, validate_property
from video_generator import create_video

ROOT = Path(__file__).resolve().parent
SAMPLE_DATA = ROOT / "sample_data.json"
st.set_page_config(page_title="Property Reel Studio", page_icon="🏡", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1250px; padding-top: 2rem;}
.hero {padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#132b35,#245b5a); color:white; margin-bottom:1.2rem;}
.hero h1 {color:white; margin:0; font-size:2.1rem;}
.hero p {color:#d5e9e5; margin:.5rem 0 0 0;}
.small-muted {color:#697982;font-size:.9rem}
</style>
<div class="hero"><h1>🏡 Property Reel Studio</h1><p>Turn a property listing and 4–8 photos into a caption-led MP4 — no API key or video editor required.</p></div>
""", unsafe_allow_html=True)
st.caption("Offline-friendly rule-based demo • Captions only • Synthetic sample listing available")

if "generated_video" not in st.session_state:
    st.session_state.generated_video = None
if "generated_scenes" not in st.session_state:
    st.session_state.generated_scenes = []

with st.sidebar:
    st.header("Quick start")
    st.write("Try the synthetic GreenView Residency example, or upload your own property images.")
    use_sample = st.button("Load sample listing", use_container_width=True)
    st.divider()
    st.markdown("**Video settings**")
    seconds = st.slider("Seconds per scene", 2, 5, 3)
    st.info("This prototype creates a silent MP4 with text captions. It does not generate voice-over or background audio.")

default = {}
if SAMPLE_DATA.exists():
    try: default = json.loads(SAMPLE_DATA.read_text(encoding="utf-8"))
    except Exception: default = {}

if use_sample:
    st.session_state["property_name"] = default.get("property_name", "GreenView Residency")
    st.session_state["location"] = default.get("location", "Chandigarh, India")
    st.session_state["price"] = default.get("price", "₹65 lakh")
    st.session_state["property_type"] = default.get("property_type", "2 BHK Apartment")
    st.session_state["features"] = "\n".join(default.get("features", []))
    st.session_state["cta"] = default.get("cta_text", "Contact us today to enquire")
    st.session_state["sample_images"] = True

col_form, col_preview = st.columns([0.95,1.05], gap="large")
with col_form:
    st.subheader("1. Property details")
    with st.form("property_form"):
        property_name = st.text_input("Property name *", key="property_name", value=st.session_state.get("property_name", default.get("property_name","GreenView Residency")))
        location = st.text_input("Location *", key="location", value=st.session_state.get("location", default.get("location","Chandigarh, India")))
        price = st.text_input("Price *", key="price", value=st.session_state.get("price", default.get("price","₹65 lakh")))
        property_type = st.text_input("Property type *", key="property_type", value=st.session_state.get("property_type", default.get("property_type","2 BHK Apartment")))
        features_text = st.text_area("Key features (one per line) *", key="features", value=st.session_state.get("features","\n".join(default.get("features",[]))), height=120)
        cta = st.text_input("Call to action", key="cta", value=st.session_state.get("cta", default.get("cta_text","Contact us today to enquire")))
        uploaded_files = st.file_uploader("2. Upload 4–8 property images *", type=["jpg","jpeg","png"], accept_multiple_files=True)
        submitted = st.form_submit_button("Generate property video", type="primary", use_container_width=True)

with col_preview:
    st.subheader("Preview & output")
    st.write("The generated video uses the uploaded images in order. Each scene includes the property name, location, a factual caption, and a progress indicator.")
    if st.session_state.generated_video and Path(st.session_state.generated_video).exists():
        video_path = Path(st.session_state.generated_video)
        st.video(str(video_path))
        st.download_button("Download MP4", data=video_path.read_bytes(), file_name="property_promo.mp4", mime="video/mp4", use_container_width=True)
        with st.expander("View generated scene captions"):
            for i, scene in enumerate(st.session_state.generated_scenes, 1):
                st.markdown(f"**Scene {i} · {scene['label']}**")
                st.write(scene["caption"])
    else:
        st.info("Your finished MP4 preview will appear here after generation.")
        sample_img = ROOT / "sample_images" / "01_exterior.jpg"
        if sample_img.exists():
            st.image(str(sample_img), caption="Synthetic sample image", use_container_width=True)

if submitted:
    features = [line.strip() for line in features_text.splitlines() if line.strip()]
    image_sources = []
    temp_dir = None
    try:
        if uploaded_files:
            if not (4 <= len(uploaded_files) <= 8):
                st.error("Upload between 4 and 8 images. Please adjust the selection and try again.")
                st.stop()
            temp_dir = tempfile.TemporaryDirectory(prefix="property_uploads_")
            for i, uploaded in enumerate(uploaded_files):
                dest = Path(temp_dir.name) / f"upload_{i:02d}_{Path(uploaded.name).name}"
                try:
                    with Image.open(uploaded) as im:
                        im.verify()
                except (UnidentifiedImageError, OSError):
                    st.error(f"'{uploaded.name}' is not a readable image. Upload valid JPG or PNG files.")
                    st.stop()
                dest.write_bytes(uploaded.getvalue())
                image_sources.append(dest)
        elif st.session_state.get("sample_images") and default.get("image_files"):
            image_sources = [ROOT / "sample_images" / name for name in default["image_files"]]
        else:
            st.error("Please upload 4–8 property images, or click **Load sample listing** in the sidebar.")
            st.stop()

        errors = validate_property(property_name, location, price, property_type, features, image_sources)
        if errors:
            for error in errors: st.error(error)
            st.stop()
        scenes = generate_scenes(property_name, location, price, property_type, features, cta)
        out_dir = ROOT / "output"
        out_path = out_dir / "property_promo.mp4"
        with st.spinner("Rendering video frames and exporting MP4…"):
            try:
                create_video(image_sources, scenes, property_name, location, price, out_path,
                             seconds_per_scene=seconds)
            except (ValueError, RuntimeError, OSError) as exc:
                st.error(f"Could not create the video: {exc}")
                st.stop()
        st.session_state.generated_video = str(out_path)
        st.session_state.generated_scenes = (scenes[:len(image_sources)-1] + [scenes[-1]]
                                             if len(scenes) > len(image_sources) else scenes[:len(image_sources)])
        st.success(f"Video created successfully: {out_path.name}")
        st.rerun()
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

with st.expander("About this prototype"):
    st.markdown("""
- **Script generation:** deterministic templates; no external AI model or API key.
- **Media processing:** Pillow + FFmpeg via `imageio-ffmpeg`.
- **Data:** synthetic example listing and locally generated illustrative images.
- **Privacy:** uploads are processed locally by the app process; this demo has no database or account system.
- **Limitations:** captions only, no narration/audio, no property verification, and no cloud deployment included.
""")
