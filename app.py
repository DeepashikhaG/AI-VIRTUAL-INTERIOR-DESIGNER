import streamlit as st
import requests
import base64
import io
import time
from PIL import Image

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
API_TOKEN = "your-hugging-face-api-key-here"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

st.markdown('<h1 style="font-size: 5.5em; text-align: center;">AI Interior Design Inspiration</h1>', unsafe_allow_html=True)
st.markdown("""
    <style>
    .sidebar .sidebar-content { background-color: #f8f9fa; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)
st.write("Upload a room photo for a creative, style-inspired redesign. Note: Results are creative takes, not exact replicas—perfect for design inspiration!")

with st.sidebar:
    st.subheader("Design Options")
    uploaded_file = st.file_uploader("Upload a room photo", type=["jpg", "png"])
    style = st.selectbox("Choose a style", ["Modern", "Traditional", "Minimalist", "Bohemian", "Industrial", "Scandinavian"], help="Modern: Sleek, bold. Traditional: Warm, classic. Minimalist: Clean, simple. Bohemian: Eclectic, colorful. Industrial: Raw, metallic. Scandinavian: Cozy, light.")
    room_type = st.selectbox("Choose a room type", ["Bedroom", "Bathroom", "Living Room", "Playroom", "Hall"])
    simplicity = st.selectbox("Design Complexity", ["Standard", "Simple"], help="Standard: Rich and detailed. Simple: Clean and basic.")

if uploaded_file is not None:
    st.image(uploaded_file, caption="Your Room", use_container_width=True)

if st.button("Generate Inspiration"):
    if uploaded_file is not None:
        with st.spinner("Processing (might take up to 2 minutes)..."):
            image_bytes = uploaded_file.getvalue()
            if len(image_bytes) > 500000:
                img = Image.open(io.BytesIO(image_bytes))
                img = img.resize((512, 512), Image.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                image_bytes = buffer.getvalue()
                st.write("Image compressed for faster processing!")
            if len(image_bytes) > 1000000:
                st.write("File still too big—keep it under 1MB!")
            else:
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
                style_descriptors = {
                    "modern": "sleek lines, bold colors",
                    "traditional": "warm tones, classic decor",
                    "minimalist": "sparse, clean surfaces",
                    "bohemian": "eclectic, colorful patterns",
                    "industrial": "raw metal, exposed brick",
                    "scandinavian": "cozy, light wood"
                }
                if simplicity == "Simple":
                    prompt = f"basic {style.lower()} style {room_type.lower()}, {style_descriptors[style.lower()]}, clean layout, minimal furniture, preserve original structure, inspired by this room"
                else:
                    prompt = f"photorealistic {style.lower()} style {room_type.lower()}, {style_descriptors[style.lower()]}, detailed furniture, exact room layout, rich {style.lower()} details, based on this room"
                payload = {"inputs": prompt, "parameters": {"image": base64_image}}
                progress_bar = st.progress(0)
                for attempt in range(8):
                    try:
                        st.write(f"Attempt {attempt + 1}/8...")
                        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                        progress_bar.progress((attempt + 1) / 8)
                        if response.status_code == 200:
                            result = response.content
                            st.success("Inspiration generated!")
                            st.session_state["original"] = image_bytes
                            st.session_state["generated"] = result
                            st.session_state["style"] = style
                            st.session_state["room_type"] = room_type
                            st.session_state["simplicity"] = simplicity
                            break
                        elif response.status_code == 503:
                            wait_time = 10 + attempt * 10
                            st.write(f"API busy (Code: 503)—retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                        else:
                            wait_time = 10 + attempt * 10
                            st.write(f"API error (Code: {response.status_code})—retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                    except requests.exceptions.ConnectionError as e:
                        wait_time = 10 + attempt * 10
                        st.write(f"Connection failed: {e}—retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    except requests.exceptions.Timeout:
                        wait_time = 10 + attempt * 10
                        st.write(f"API timed out—retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                else:
                    st.error("API unavailable—try again in 5-10 minutes!")
                progress_bar.empty()
    else:
        st.warning("Please upload a photo first!")

if "generated" in st.session_state:
    view = st.radio("View:", ["Original", "Inspired", "Side-by-Side"], horizontal=True)
    if view == "Original":
        st.image(st.session_state["original"], caption="Your Room", use_container_width=True)
    elif view == "Inspired":
        st.image(st.session_state["generated"], caption=f"{st.session_state['style']} {st.session_state['room_type']} ({st.session_state['simplicity']}) Inspiration", use_container_width=True)
        st.download_button(label="Download Inspiration", data=st.session_state["generated"], file_name=f"{st.session_state['style']}_{st.session_state['room_type']}_{st.session_state['simplicity']}_inspiration.jpg", mime="image/jpeg")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.image(st.session_state["original"], caption="Your Room", use_container_width=True)
        with col2:
            st.image(st.session_state["generated"], caption=f"{st.session_state['style']} {st.session_state['room_type']} ({st.session_state['simplicity']}) Inspiration", use_container_width=True)
        st.download_button(label="Download Inspiration", data=st.session_state["generated"], file_name=f"{st.session_state['style']}_{st.session_state['room_type']}_{st.session_state['simplicity']}_inspiration.jpg", mime="image/jpeg")

st.markdown("<footer style='text-align: center; margin-top: 20px;'>Made by [Gavidi Deepashikha] - April 2025</footer>", unsafe_allow_html=True)