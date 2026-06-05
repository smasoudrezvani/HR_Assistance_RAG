import streamlit as st
import requests
import re

st.set_page_config(page_title="ABC_Company HR Assistant", page_icon="🏢", layout="centered")
st.title("🏢 ABC_Company Policy Assistant")
st.markdown("Ask me anything about HR policies, onboarding, or company rules!")

API_URL = "http://127.0.0.1:8000/api/v1/query"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("E.g., What is the referral bonus?"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 Searching policies...")
        
        try:
            response = requests.post(API_URL, json={"question": prompt}, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                raw_answer = data.get("answer", "No answer provided.")
                sources = data.get("sources", []) # This will soon be a list of dicts
                
                # UX FIX 1: Clean up the UUIDs using Regex
                # This looks for exactly 32 alphanumeric characters wrapped in brackets
                # and replaces it with a clean visual marker.
                clean_answer = re.sub(r'\[[a-f0-9]{32}\]', '[📌]', raw_answer)
                
                # UX FIX 2: Format clickable sources
                source_markdowns = []
                for source in sources:
                    # If the backend sends a dictionary with a URL, make it clickable
                    if isinstance(source, dict) and "url" in source and source["url"]:
                        source_markdowns.append(f"[{source['filename']}]({source['url']})")
                    # Fallback for old strings
                    elif isinstance(source, dict):
                        source_markdowns.append(source.get("filename", "Unknown"))
                    else:
                        source_markdowns.append(str(source))
                
                full_response = f"{clean_answer}\n\n"
                if source_markdowns:
                    full_response += f"**Sources:** {', '.join(source_markdowns)}"
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Backend Error: Status code {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("🚨 Cannot connect to the backend. Is main.py running on port 8000?")