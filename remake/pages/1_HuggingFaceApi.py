import streamlit as st

st.set_page_config(
    layout='wide',
    page_title="API-Key"
    )

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Kanit&display=swap');

			html, body, [class*="css"]  {
			font-family: 'Kanit', sans-serif;
			}
   
.title-font {
    font-size:100px;
    color:#57ACDC;
    text-align:center;
}
.pageheader-font {
    font-size: 50px !important;
    text-align:center;
}
.gif-container{
    display: flex;
    justify-content: conter;
    alighn-item: center;
}
.middle-align {
    text-align:center;
}
.large-font {
    font-size: 50px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="pageheader-font">Register HuggingFace API!</p>', unsafe_allow_html=True)