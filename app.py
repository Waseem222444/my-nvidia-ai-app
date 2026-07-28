import streamlit as st
import requests
from PIL import Image
import io
import urllib.parse

# Page Configuration
st.set_page_config(
    page_title="Studio AI Vision",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Light Theme CSS
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }
    
    /* Clean Top Header */
    .main-header {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    
    .sub-header {
        color: #64748B;
        font-size: 1.05rem;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }

    /* Style Popover Container */
    div[data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.03) !important;
        background: #F8FAFC !important;
    }

    /* Input & Chat Customization */
    .stChatMessage {
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">✨ AI Vision & Scene Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Create high-quality scenes, apply styles, and transform images seamlessly.</div>', unsafe_allow_html=True)

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

# Modern Inline Control Bar (+ Options) directly above Chat Bar
with st.expander("➕ Studio Options & Filters (Click to Customize Style, Aspect Ratio & Reference Image)", expanded=False):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        style_preset = st.selectbox(
            "🎨 Image Style Filter",
            ["Studio Ghibli Anime", "Cinematic Photorealistic", "Fantasy Concept Art", "3D Render / Animation", "Cyberpunk Digital Art"]
        )
        
        aspect_ratio_choice = st.selectbox(
            "📐 Frame Size / Aspect Ratio",
            ["16:9 Landscape", "1:1 Square", "9:16 Portrait (Mobile)"]
        )
        
    with col2:
        uploaded_file = st.file_uploader("🖼️ Upload Reference Image (Optional)", type=["png", "jpg", "jpeg"])
        ref_image = None
        if uploaded_file:
            ref_image = Image.open(uploaded_file).convert("RGB")
            st.image(ref_image, caption="Reference Attached", width=120)

# Map aspect ratios to resolution dimensions
aspect_map = {
    "16:9 Landscape": (1280, 720),
    "1:1 Square": (1024, 1024),
    "9:16 Portrait (Mobile)": (720, 1280)
}
width, height = aspect_map[aspect_ratio_choice]

# Bottom Input Form
if prompt := st.chat_input("Describe the scene or image you want to generate..."):
    st.session_state.chat_history.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("✨ Creating visual scene..."):
            try:
                full_prompt = f"{prompt}, {style_preset} style, highly detailed, master piece"
                encoded_prompt = urllib.parse.quote(full_prompt)
                
                # Public generation URL
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42"
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = requests.get(image_url, headers=headers, allow_redirects=True, timeout=60)
                
                if response.status_code == 200:
                    image_bytes = io.BytesIO(response.content)
                    generated_img = Image.open(image_bytes)
                    
                    st.image(generated_img, caption=f"Generated Scene ({aspect_ratio_choice})", use_container_width=True)
                    st.markdown("**📋 Copy Prompt:**")
                    st.code(full_prompt, language="text")
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "type": "image",
                        "content": generated_img,
                        "caption": f"Generated ({style_preset}): {prompt}",
                        "full_prompt": full_prompt
                    })
                else:
                    err_msg = f"Generation Error ({response.status_code}): Could not retrieve image."
                    st.error(err_msg)
                    st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": err_msg})

            except Exception as e:
                err_msg = str(e) if str(e) else repr(e)
                err = f"Execution Error: {err_msg}"
                st.error(err)
                st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": err})
