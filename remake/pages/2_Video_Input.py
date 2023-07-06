from pytube import YouTube
import requests
import streamlit as st
import streamlit.components.v1 as components
import torch

st.set_page_config(page_title='Transcribe the video', layout='wide')

torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"



with open('remake/style/transcribe.css') as f:
    css = f'<style>{f.read()}</style>' 
    
st.markdown(css, unsafe_allow_html=True)

components.html(
    """
    <p style="text-align:center;"><img src="https://media.tenor.com/G3M0KeCtUv8AAAAi/holo-live.gif" alt="Logo" width = 250 height = 250></p>

    """,
    height=250
)

st.markdown('<p class="pageheader-font">Transcribe the video!</p>', unsafe_allow_html=True)
st.write('Hello!')

def populate_metadata(link):
    yt = YouTube(link)
    author = yt.author
    title = yt.title
    description = yt.description
    thumbnail = yt.thumbnail_url
    length = yt.length
    views = yt.views
    return author, title, description, thumbnail, length, views

print(populate_metadata('https://www.youtube.com/watch?v=BxV14h0kFs0'))