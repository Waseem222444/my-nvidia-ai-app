import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image

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
hf_token = st.secrets.get("HF_TOKEN")
if not hf_token:
    st.error("⚠️ Missing HF_TOKEN in Streamlit Secrets!")
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
    
    ref_image = None
    if uploaded_file:
        ref_image = Image.open(uploaded_file)
        st.image(ref_image, caption="Uploaded Reference Photo", use_container_width=True)

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
    st.session_state.chat_history.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("✨ Generating scene with AI..."):
            try:
                full_prompt = f"{prompt}, {style_preset} style, highly detailed, master piece"
                client = InferenceClient(api_key=hf_token.strip())
                
                if ref_image:
                    # SD 2.1 handles serverless image-to-image conversion reliably
                    img = client.image_to_image(
                        image=ref_image,
                        prompt=full_prompt,
                        model="stabilityai/stable-diffusion-2-1"
                    )
                else:
                    # FLUX.1-dev for standard text-to-image
                    img = client.text_to_image(
                        prompt=full_prompt,
                        model="black-forest-labs/FLUX.1-dev"
                    )
                
                st.image(img, caption=f"Generated Scene ({aspect_ratio_choice})", use_container_width=True)
                st.markdown("**📋 Copy Prompt:**")
                st.code(full_prompt, language="text")
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "type": "image",
                    "content": img,
                    "caption": f"Generated ({style_preset}): {prompt}",
                    "full_prompt": full_prompt
                })

            except Exception as e:
                err = f"Execution Error: {str(e)}"
                st.error(err)
                st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": err})
