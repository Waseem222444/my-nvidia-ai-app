import streamlit as st
import requests
import base64
from PIL import Image
import io

# Page Configuration
st.set_page_config(
    page_title="Studio AI Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #7F56D9, #00D2FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #94A3B8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# API Key Validation
nvidia_api_key = st.secrets.get("NVIDIA_API_KEY")
if not nvidia_api_key:
    st.error("⚠️ Missing NVIDIA_API_KEY in Streamlit Secrets!")
    st.stop()

# Header
st.markdown('<div class="main-header">✨ AI Vision & Scene Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate cinematic scenes, upload reference images, and create AI visuals.</div>', unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Studio Controls")
    
    style_preset = st.selectbox(
        "🎨 Style Preset",
        ["Studio Ghibli Anime", "Cinematic Photorealistic", "Fantasy Concept Art", "3D Render / Animation"]
    )
    
    aspect_ratio_choice = st.selectbox(
        "📐 Aspect Ratio",
        ["16:9", "1:1", "9:16"]
    )
    
    st.divider()
    st.markdown("### 🖼️ Reference Image")
    uploaded_file = st.file_uploader("Upload reference photo (Optional)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Photo", use_container_width=True)

# Initialize Session Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message.get("type") == "text":
            st.markdown(message["content"])
        elif message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", ""), use_container_width=True)
            if "full_prompt" in message:
                st.markdown("**📋 Copy Prompt:**")
                st.code(message["full_prompt"], language="text")

# Chat Input Field
if prompt := st.chat_input("Describe the scene or image you want to generate..."):
    # Save user message to chat history
    st.session_state.chat_history.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Image Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("✨ Crafting visual scene via NVIDIA FLUX..."):
            try:
                full_prompt = f"{prompt}, {style_preset} style, highly detailed, master piece"
                
                # Correct NVIDIA GenAI endpoint URL
                invoke_url = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-schnell"
                
                headers = {
                    "Authorization": f"Bearer {nvidia_api_key.strip()}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "prompt": full_prompt
                }
                
                response = requests.post(invoke_url, headers=headers, json=payload, timeout=90)
                
                if response.status_code != 200:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "type": "text",
                        "content": f"⚠️ API Error ({response.status_code}): {response.text}"
                    })
                else:
                    response_data = response.json()
                    
                    if "artifacts" in response_data and len(response_data["artifacts"]) > 0:
                        base64_image = response_data["artifacts"][0]["base64"]
                        image_bytes = base64.b64decode(base64_image)
                        img = Image.open(io.BytesIO(image_bytes))
                        
                        # Display Image and Copyable Code Block
                        st.image(img, caption=f"Generated Scene ({aspect_ratio_choice})", use_container_width=True)
                        st.markdown("**📋 Copy Prompt:**")
                        st.code(full_prompt, language="text")
                        
                        # Store in chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "type": "image",
                            "content": img,
                            "caption": f"Generated ({style_preset}): {prompt}",
                            "full_prompt": full_prompt
                        })
                    else:
                        st.error(f"Unexpected response format: {response_data}")

            except requests.exceptions.Timeout:
                err = "⏱️ Request timed out. NVIDIA server took longer than expected. Please try again."
                st.error(err)
                st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": err})
            except Exception as e:
                err = f"Execution Error: {str(e)}"
                st.error(err)
                st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": err})
