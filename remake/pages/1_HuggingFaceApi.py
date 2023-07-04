import streamlit as st
import function.api_handler as api_handler
import streamlit.components.v1 as components
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout='wide',
    page_title="API-Key"
    )

#
if 'api_key' not in st.session_state: st.session_state['api_key'] = ""


#homepage style
with open('remake/style/apipage.css') as f:
    css = f'<style>{f.read()}</style>'
st.markdown(css, unsafe_allow_html=True)
components.html(
    """
    <p style="text-align:center;"><img src="https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.png" alt="Logo" width = 250 height = 250></p>

    """,
    height=250
)
st.markdown('<p class="pageheader-font">Register HuggingFace API!</p>', unsafe_allow_html=True)

api_key = st.text_input('Huggingface API Key',placeholder='Put your huggingface api token here')

if api_key:
    with st.spinner('Verifying the api token...'):
            key_valid = api_handler.api_test(api_key)
            if key_valid : 
                st.success('Token valid!')
                st.session_state['api_key'] = api_key
            else: 
                st.error('Token invalid! Try Again!')
                st.session_state['api_key'] = ""


null, left, right, null = st.columns([1,2,2,1])
with left:
    if st.button('<Home page'): switch_page('frontpage')
with right:
    if st.button('Transcribe>', disabled=st.session_state['api_key'] == ""): switch_page('frontpage')

        
    