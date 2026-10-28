AI Property Video Generator — Property Reel Studio
A runnable Streamlit prototype that turns a real-estate listing and 4–8 photos into a caption-led MP4. It uses rule-based templates, so no API key, paid AI service, or internet connection is required after dependencies are installed.

Features
Streamlit form for property name, location, price, type, features, and CTA.
Accepts 4–8 JPG/JPEG/PNG images.
Rule-based scene captions using only the supplied listing details.
Creates a silent MP4 with text overlays, a subtle zoom, scene progress indicator, and readable contrast.
Preview and download the exported MP4.
Validation for missing fields, image counts, unreadable files, and video-export errors.
Synthetic listing data and six generated illustrative sample images.
Unit tests for validation and scene generation.
Project layout
ai-property-video-generator/
├── app.py
├── script_generator.py
├── video_generator.py
├── requirements.txt
├── sample_data.json
├── sample_images/
│   ├── 01_exterior.jpg
│   ├── 02_living_room.jpg
│   ├── 03_kitchen.jpg
│   ├── 04_bedroom.jpg
│   ├── 05_balcony.jpg
│   └── 06_home.jpg
├── output/
│   └── sample_property_video.mp4
└── tests/
    └── test_script_generator.py
Requirements
Python 3.10 or newer
FFmpeg executable provided by imageio-ffmpeg (installed as a Python dependency)
Windows, macOS, or Linux
Install and run
Windows PowerShell
cd ai-property-video-generator
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
macOS / Linux
cd ai-property-video-generator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
Open the local URL printed by Streamlit. Click Load sample listing in the sidebar to use the synthetic demo, or enter your own details and upload 4–8 images. Click Generate property video, preview the result, and use Download MP4.

Generate a sample MP4 from the command line
After installing dependencies, run:

python generate_sample.py
The result is written to output/sample_property_video.mp4.

Tests
python -m unittest discover -s tests -v
How it works
The form collects listing facts and photos.
script_generator.py validates the required fields and creates a sequence of captions using fixed templates.
video_generator.py prepares frames with Pillow, then calls FFmpeg through imageio-ffmpeg to encode a silent H.264 MP4.
Streamlit displays the MP4 and offers it as a download.
The renderer pairs uploaded images with generated scenes in order. For example, an opening scene names the property, following scenes show location, property type, up to four features, price, and a final CTA. If there are more generated scenes than images, the renderer uses as many scenes as there are images. Only facts entered by the user are inserted into generated captions; the app does not infer amenities or make claims about investment returns.

Models, APIs, and external services
AI/ML model: None. Script generation is rule-based, which is permitted by the assignment brief.
External API: None.
Libraries: Streamlit, Pillow, NumPy, imageio-ffmpeg.
Media engine: FFmpeg, invoked through the imageio-ffmpeg package.
Audio: None; captions only, as specified.
Sample data disclaimer
sample_data.json is synthetic. The included property visuals are generated illustrations created for this demo and are not photographs of an actual property. The sample price and location are illustrative, not a verified listing.

Error handling
Required fields and at least one feature are validated.
Fewer than 4 or more than 8 images are rejected with a helpful message.
Unreadable images and missing files produce readable errors.
FFmpeg export failures are surfaced to the UI rather than silently ignored.
Known limitations
This is an assignment prototype, not a production system.
No login, database, cloud storage, analytics, or deployment configuration is included.
Template-based text is predictable but less flexible than an LLM.
The sample visuals are illustrations; replace them with licensed listing photos for a real marketing workflow.
The app creates a silent video; it does not add narration or music.
Demo walkthrough (about 60 seconds)
Launch the Streamlit app.
Load the sample listing.
Review the property details and captions.
Generate the MP4 and play the preview.
Download the MP4.
Explain that captions are generated deterministically from supplied facts, and that the main trade-off is reliability/simplicity versus generative flexibility.
