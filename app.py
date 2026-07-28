import streamlit as st
from openai import OpenAI

# Page Configuration
st.set_page_config(page_title="AI Scene & Image Generator", page_icon="🎨")
st.title("🎨 AI Image & Scene Generator")

# Get API key securely from Streamlit secrets
nvidia_api_key = st.secrets.get("NVIDIA_API_KEY")

if not nvidia_api_key:
    st.error("Missing API Key! Please add NVIDIA_API_KEY in Streamlit Secrets.")
    st.stop()

# Initialize OpenAI client with NVIDIA endpoint
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=nvidia_api_key
)

# User prompt input
prompt_text = st.text_input(
    "Enter a prompt for your scene:",
    "A mysterious Ghibli style village with glowing lanterns at dusk"
)

if st.button("Generate Image"):
    with st.spinner("Generating scene with NVIDIA AI..."):
        try:
            # Generate image using NVIDIA's standard image endpoint
            response = client.images.generate(
                model="black-forest-labs/flux-1-schnell",
                prompt=prompt_text,
                response_format="url"
            )
            
            # Get the image URL from response
            image_url = response.data[0].url
            
            # Display image in Streamlit
            st.image(image_url, caption=f"Generated Scene: {prompt_text}", use_container_width=True)
            st.success("Image generated successfully!")
            
        except Exception as e:
            st.error(f"Generation Error: {e}")
