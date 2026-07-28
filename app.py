import streamlit as st
import requests
import base64
from PIL import Image
import io

# Setup page config
st.set_page_config(page_title="AI Visual & Video Prompt Generator", page_icon="🎨")
st.title("🎨 AI Image & Scene Generator")

# Retrieve API key securely from Streamlit secrets
nvidia_api_key = st.secrets.get("NVIDIA_API_KEY")

if not nvidia_api_key:
    st.error("Missing API Key! Please add NVIDIA_API_KEY in Streamlit Secrets.")
    st.stop()

# User prompt input
prompt_text = st.text_input("Enter a prompt for image/video scene:", "A mysterious Ghibli style village with glowing lanterns at dusk")

if st.button("Generate Image"):
    with st.spinner("Generating image from NVIDIA API..."):
        try:
            # Endpoint for Stable Diffusion XL on NVIDIA Build
            invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl"
            
            headers = {
                "Authorization": f"Bearer {nvidia_api_key}",
                "Accept": "application/json",
            }
            
            payload = {
                "text_prompts": [{"text": prompt_text}],
                "cfg_scale": 7,
                "sampler": "K_DPM_2_ANCESTRAL",
                "seed": 0,
                "steps": 25
            }
            
            response = requests.post(invoke_url, headers=headers, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Decode the base64 image returned by API
            for i, image in enumerate(response_data.get("artifacts", [])):
                image_bytes = base64.b64decode(image["base64"])
                img = Image.open(io.BytesIO(image_bytes))
                st.image(img, caption=f"Generated Scene: {prompt_text}", use_container_width=True)
                st.success("Generation Complete!")
                
        except Exception as e:
            st.error(f"Error generating image: {e}")
