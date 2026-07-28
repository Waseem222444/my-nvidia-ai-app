import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="NVIDIA AI Assistant", page_icon="🤖")
st.title("🤖 NVIDIA AI Assistant")

# Retrieve API key securely from Streamlit secrets
nvidia_api_key = st.secrets.get("NVIDIA_API_KEY")

if not nvidia_api_key:
    st.error("Missing API Key! Please add NVIDIA_API_KEY in Streamlit Secrets.")
    st.stop()

# Initialize OpenAI client with NVIDIA endpoint
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=nvidia_api_key
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_box = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                temperature=0.5,
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_box.markdown(full_response + "▌")
            
            response_box.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"API Error: {e}")
