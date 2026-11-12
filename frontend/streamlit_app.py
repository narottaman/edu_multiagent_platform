import os, requests, streamlit as st
st.set_page_config(page_title="Edu Multi-Agent", layout="wide")
st.title("Edu Multi-Agent Learning & Research")
api=os.getenv("API_URL","http://localhost:8000")
intent=st.selectbox("Mode", ["auto","qa","learn","quiz","research"])
course=st.text_input("Canvas course ID (required for Canvas-grounded learning/quiz)")
q=st.text_area("Ask, learn, quiz, or explore research")
if st.button("Run") and q:
    payload={"message":q,"course_id":course or None,"intent":None if intent=="auto" else intent}
    r=requests.post(f"{api}/v1/chat",json=payload,timeout=120); r.raise_for_status()
    st.markdown(r.json()["answer"])
    with st.expander("Evidence / agent trace"): st.json(r.json()["agent_results"])
