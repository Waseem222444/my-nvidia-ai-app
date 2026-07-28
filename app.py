import streamlit as st
import requests
import base64
from PIL import Image
import io

# Page setup
st.set_page_config(page_title="AI Scene Generator", page_icon="🎨")
st.title("🎨 AI Image & Scene Generator")

# Retrieve API key securely from Streamlit secrets
nvidia_api_key = st.secrets.get("NVIDIA_API_KEY")

if not nvidia_api_key:
    st.error("Missing API Key! Please add NVIDIA_API_KEY in Streamlit Secrets.")
    st.stop()

# User prompt input
prompt_text = st.text_input(
    "Enter a prompt for your scene:",
    "A mysterious Ghibli style village with glowing lanterns at dusk"
)

if st.button("Generate Image"):
    with st.spinner("Generating scene with NVIDIA FLUX model..."):
        try:
            # Correct NVIDIA cloud endpoint for FLUX.1 Schnell
            invoke_url = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-schnell"
            
            headers = {
                "Authorization": f"Bearer {nvidia_api_key}",
                "Accept": "application/json",
            }
            
            payload = {
                "prompt": prompt_text
            }
            
            # Send request to NVIDIA
            response = requests.post(invoke_url, headers=headers, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Decode image from NVIDIA base64 response
            base64_image = response_data["artifacts"][0]["base64"]
            image_bytes = base64.b64decode(base64_image)
            img = Image.open(io.BytesIO(image_bytes))
            
            # Display image in Streamlit
            st.image(img, caption=f"Generated Scene: {prompt_text}", use_container_width=True)
            st.success("Image generated successfully!")
            
        except Exception as e:
            st.error(f"Generation Error: {e}")
