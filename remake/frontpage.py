import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout='wide',
    page_title="Main"
    )


#homepage style
with open('remake\style\home.css') as f:
    css = f'<style>{f.read()}</style>'
st.markdown(css, unsafe_allow_html=True)

#title 

st.markdown('<p class="title-font">vTranslator</p>', unsafe_allow_html=True)
st.markdown('<p class="pageheader-font">Transcribe your favorite vtubers with a click of a button!</p>', unsafe_allow_html=True)
components.html(
    """
    <p style="text-align:center;"><img src="https://github.com/thunni-noi/vTranslator-aib-2022/blob/main/remake/assets/frontpage_bg.gif?raw=true" alt="Logo"></p>

    """,
    height=1080
)
#with st.columns(3)[1]:
 #   st.image('./remake/assets/frontpage_bg.gif')
    #st.markdown("![Alt Text](https://github.com/thunni-noi/vTranslator-aib-2022/blob/main/remake/assets/frontpage_bg.gif?raw=true)", unsafe_allow_html=True)

#next page
with st.columns([1,1,1])[1]:
    next_page = st.button("Let's go!", )
    if next_page:
        switch_page("huggingfaceapi")