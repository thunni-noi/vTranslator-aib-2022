import json
import subprocess
import os
import streamlit as st
import torchaudio
import shutil
import numpy as np
import torch
import re
import datetime
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from pathlib import Path
from pytube import YouTube
from pydub import AudioSegment
from pydub.silence import split_on_silence
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from googletrans import Translator

st.set_page_config(
    page_title="vTranslator",
    page_icon='https://s3-ap-northeast-1.amazonaws.com/killy-image/linestamp/1f/1f13/1f131746571cc91986f8b868ed2946789402c741',
    layout='wide',
    menu_items={
        'Report a bug' : 'https://github.com/thunni-noi/vTranslator-japanese/issues',
        'About' : 'https://github.com/thunni-noi/vTranslator-japanese'
    }
)

@st.cache(allow_output_mutation=True)
def web_init():
    #global tokenizer, asrmodel, translator
    v1_tokenizer = Wav2Vec2Processor.from_pretrained('thunninoi/wav2vec2-japanese-hiragana-vtuber')
    v1_asrmodel = Wav2Vec2ForCTC.from_pretrained('thunninoi/wav2vec2-japanese-hiragana-vtuber')
    v2_tokenizer = Wav2Vec2Processor.from_pretrained('thunninoi/wav2vec2-japanese-vtuber')
    v2_asrmodel = Wav2Vec2ForCTC.from_pretrained('thunninoi/wav2vec2-japanese-vtuber')
    translator = Translator()
    return v1_tokenizer, v1_asrmodel,v2_tokenizer, v2_asrmodel, translator
    
@st.cache
def get_srt_line(inferred_text, line_count, limits):
    sep = ','
    d = str(datetime.timedelta(seconds=float(limits[0])))
    try :
        from_dur = str('0') + str(d.split('.')[0]) + sep + str(d.split('.')[-1][:2])
    except :
        from_dur = str('0') + str(d) + sep(d) + sep + '00'
        
    d = str(datetime.timedelta(seconds=float(limits[1])))
    try:
        to_dur = '0' + str(d.split('.')[0]) + sep + str(d.split('.')[-1][:2])
    except :
        to_dur = '0' + str(d) + sep + '00'
    return f'{str(line_count)}\n{from_dur} --> {to_dur}\n{inferred_text}\n\n'

#init
Path('deployment/temp').mkdir(parents=True, exist_ok= True)
Path('deployment/output').mkdir(parents=True, exist_ok= True)
temp_path = ('deployment/temp/')
output_path = ('deployment/output/')
v1_tokenizer, v1_asrmodel,v2_tokenizer, v2_asrmodel, translator = web_init()

# defualt value
has_video = False
sub_preview = False
vid_origin = ''
run_button = False
display_transcript = []
min_silence = ''
silence_threashold = ''
audio_offset =''



font_mitr = ("""
@import url('https://fonts.googleapis.com/css2?family=Mitr&display=swap');

html, body, [class*="css"] {
    font-family: 'Mitr', sans-serif;
    font-weight: 500;
}
""")


 # TITLE
title_left,title_right = st.columns([5,3])
with title_left:
    st.markdown('<p style="font-family: \'Mitr\' ,sans-serif; color:#57ACDC; font-size: 72px;">vTranslator <span style="font-family: \'Mitr\' ,sans-serif; color:white; font-size: 25px;">โปรเจกต์แปลภาษา vtuber </span></p>', unsafe_allow_html=True)
with title_right:
    st.image("https://tenor.com/view/fubuki-fox-gif-19061636.gif",width=95)
# END TITLE

st.markdown(f'<style>{font_mitr}</style>A project to translate Japanese speech into text especially hololive vtuber!\n โปรเจกต์เพื่อที่จะแปลภาษาที่ vtuber พูดจากภาษาญี่ปุ่นเป็นภาษาอื่นๆ', unsafe_allow_html=True)
input_left, input_right = st.columns([4,6])
with input_left:
    uploaded_vid = st.file_uploader("Upload your video[MUST BE MP4] or use youtube link!", type='mp4')
with input_right:
    youtube_link = st.text_input("Put your youtube link here", value = 'https://youtu.be/sFUmPSyG61c')


# PREVIEW VIDEO AND GET VIDEO
if uploaded_vid is None:
    if youtube_link is None or youtube_link is '':
        st.info('Please upload your file or youtube link!')
        has_video = False
    else : 
        preview_vid = youtube_link
        vid_origin = 'youtube'
        has_video = True
else : 
    preview_vid = uploaded_vid
    vid_origin = 'local'
    has_video = True
# END PREVIEW VIDEO
with open('config/langCodeDict.json') as json_file:
    langCodeDict = json.load(json_file)
    langCodeDict = dict((k.lower(), v.lower()) for k,v in langCodeDict.items())
    
#st.write(langCodeDict)
if has_video:
    vPreview, button_sec = st.columns([2,1])
    with vPreview: 
        vid_img_preview_container = st.empty()
        vid_img_preview_container.video(preview_vid)
        #st.write('Generated Transcript will be here!')
        #st.write(display_transcript)
    with button_sec:
        targetLanguage = st.selectbox("Select translation language", [x.capitalize() for x in list(langCodeDict.keys())], index=[x.capitalize() for x in list(langCodeDict.keys())].index('English'))
        targetModel = st.selectbox("Select speech-to-text model", ['model/v1', 'model/v2'], index = 1)
        run_holder = st.empty()
        run_button = run_holder.button('Run the program!', help='it exactly like what it said, press it and it will process your video. DUH', key = 'RunButton') 
        if run_button:
            run_holder.button('Run the program!', help='it exactly like what it said, press it and it will process your video. DUH', disabled = True, key = 'RunButtonDisabled')
        add_sub = st.checkbox('Automaticcally subbed vided? (will take longer to process depend on video length)', value = False)
        advance_setting = st.checkbox('Advance audio segmentation settings?', value = False)
       
                
    with st.sidebar:
        if add_sub:
            st.write('Subtitle Setting!')
            size_text = st.number_input('Subtitle Size', value = 32.0)
            color_text = st.selectbox('Subtitle Color', [str(x)[2:-1] for x in TextClip.list('color')][3:], index = [str(x)[2:-1] for x in TextClip.list('color')][3:].index('white'))
            font_text = st.selectbox('Subtitle Font', [x for x in TextClip.list('font')], index = [x for x in TextClip.list('font')].index('Arial'))
            #text_bg = st.selectbox('Subtitle Background?', (['None'] + [str(x)[2:-1] for x in TextClip.list('color')[3:]]), index = 0)
            text_pos_x = st.select_slider('Subtitle Position (X)', ['left','center','right'], value = 'center')
            text_pos_y = st.slider('Subtitle Position (Y percentage)', min_value = 0, max_value = 100, value = 80, help = 'the more the percentage, the lower the text going to be')
            text_bg = st.checkbox('Subtitle background?', value=True) 
            if text_bg:
                txt_bg_color = (st.color_picker('Pick a color!', value = '#000000')).lstrip('#')
                txt_bg_opacity = st.slider('Subtitle Background Opacity', min_value=1, max_value = 100, value=60)
            
            preview_text = st.text_input('Text Preview', value = 'Glasses are very versatile')
            preview_pic = st.selectbox('Preview Image', [x if x.startswith('subtitle_preview') and x.endswith('.png') else '' for x in os.listdir('deployment\preview')])
            btn_preview_container = st.empty()
            btn_sub_preview = btn_preview_container.button('Generate subtitle preview', key='PreviewSubBTN')
            if btn_sub_preview:
                #vid_img_preview_container.empty
                btn_preview_container.button('Generate subtitle preview', disabled=True, key='PreviewSubBTNdisabled')
                #vid_img_preview_container.empty()
                with st.spinner('Generating preview....'):
                    image_preview = ImageClip(f'deployment\preview\{preview_pic}')
                    #subtitle_preview = TextClip(txt=str(preview_text), size=(min(1920, (len(preview_text)) * size_text), 0), font = font_text, color = color_text, method='caption')
                    subtitle_preview = TextClip(txt=str(preview_text), size=(min(1920, (len(preview_text)) * size_text), 0), font = font_text, color = color_text)
                    subtitle_preview.set_position('center')
                    if text_bg:
                        im_w, im_h = subtitle_preview.size
                        color_clip = ColorClip(size=(int(im_w*1), int(im_h*1.2)),color=(tuple(int(txt_bg_color[i:i+2], 16) for i in (0, 2, 4))))
                        color_clip = color_clip.set_opacity(txt_bg_opacity/100)
                        clip_to_overlay = CompositeVideoClip([color_clip, subtitle_preview])
                    else : clip_to_overlay = subtitle_preview
                    clip_to_overlay = clip_to_overlay.set_position((str(text_pos_x),float(text_pos_y / 100)),relative = True)
                    final_img = CompositeVideoClip([image_preview, clip_to_overlay])
                    final_img.save_frame('deployment/temp/subtitle_preview.png')
                    with st.sidebar : st.success('Done!') 
                    with vid_img_preview_container:
                        vid_img_preview_container.image('deployment/temp/subtitle_preview.png')
                #btn_preview_container.empty()
                if btn_preview_container.button('Back to video preview', key='PreviewVidBTN'):
                    #btn_sub_preview.empty()
                    vid_img_preview_container.video(preview_vid)
        if advance_setting:
            st.write('Advance audio segmentation settings')
            min_silence = st.slider('Minimum audio silence(milliseconds)', min_value = 100, max_value = 2000, value = 500)
            silence_threashold = st.slider('Silence threashold(dBFS)', help = 'The upper bound for how quiet is silent in dBFS', value = -40, max_value = 0, min_value = -100)
            audio_offset = st.slider('Audio segmenting offset(millisecond', min_value = 0, max_value = 2000, value = 500, help = 'Make audio cutting longer all before and after silence')


# RUN THE MODEL
if run_button:
    display_transcript = []
    #vid_img_preview_container.empty()
    gTransTlang = langCodeDict[str(targetLanguage).lower()]
    vid_img_preview_container.empty()
    with vid_img_preview_container:
        with st.spinner('GETTING VIDEOS!'):
            #download
            if vid_origin == 'youtube':
                vid_name = 'target_video.mp4'
                streams = YouTube(preview_vid).streams.filter(progressive=True)
                stream_list = [{'itag' : info.itag,'res' : int((info.resolution).replace('p',''))} for info in streams]
                target_res = max([i['res'] for i in stream_list])
                index = stream_list.index(next(item for item in stream_list if item['res'] == target_res))
                itag = stream_list[index]['itag']
                download_target = YouTube(preview_vid).streams.get_by_itag(itag)
                download_target.download(output_path=temp_path, filename= vid_name)
            else :
                with open (temp_path + 'target_video.mp4', 'wb') as out_file:
                    bytes_data = preview_vid.read()
                    out_file.write(bytes_data)
        with st.spinner('PROCESSING VIDEOS!'):
            #prep audio
            #extract audio
            command = ["ffmpeg", "-i",temp_path+'target_video.mp4', "-ac", "1", "-ar", "16000","-vn", "-f", "wav", temp_path+'extractedAudio.wav']
            subprocess.run(command)
            #segment audio
            Path(temp_path+'segmented_audio/').mkdir(parents=True, exist_ok=True)
            sound = AudioSegment.from_wav(temp_path+'extractedAudio.wav')
            if min_silence == '': min_silence = 500
            if audio_offset == '' : audio_offset = 500
            if silence_threashold == '' : silence_threashold = -40
            audio_chunks, split_time = split_on_silence(sound, min_silence_len=min_silence, silence_thresh=silence_threashold, offset = audio_offset )
            audio_info = []
            for i, chunk in enumerate(audio_chunks):
                output_file = (temp_path+'segmented_audio/audio{}.wav'.format(i))
                audio_info.append({
                    'audio_path' : (temp_path+'segmented_audio/chunk{}.wav'.format(i)),
                    'audio_array' : np.array(chunk.get_array_of_samples()).astype(np.float32),
                    'audio_time' : "{0} -> {1}".format(int(split_time[i]['start']) + audio_offset,int(split_time[i]['end']) - audio_offset )
                })
                chunk.export(output_file, format="wav")
            line_count = 0
        
        with st.spinner('GENERATING SUBTITLE!'):
            #st.write(display_transcript)
            with open(output_path + 'subtitle.srt', 'w' , encoding='utf-8') as out_file:
                for audio_file in audio_info:
                    #run Wav2Vec2 on each segmented
                    speech = audio_file['audio_array']
                    rate = 16000

                    if targetModel == 'model/v1':
                        input_values = v1_tokenizer(speech, sampling_rate=16000, return_tensors = 'pt', padding = 'longest').input_values
                        logits = v1_asrmodel(input_values).logits
                    elif targetModel == 'model/v2':
                        input_values = v2_tokenizer(speech, sampling_rate=16000, return_tensors = 'pt', padding = 'longest').input_values
                        logits = v2_asrmodel(input_values).logits
                    prediction = torch.argmax(logits, dim = -1)
                    
                    #decode
                    if targetModel == 'model/v1':
                        infered_text = v1_tokenizer.batch_decode(prediction)[0]
                    elif targetModel == 'model/v2':
                        infered_text = v2_tokenizer.batch_decode(prediction)[0]
                    if len(infered_text) > 1:
                        infered_text = re.sub(r'  ', ' ', infered_text)
                        infered_text = re.sub(r'\bi\s', 'I ', infered_text)
                        infered_text = re.sub(r'\si$', ' I', infered_text)
                        infered_text = re.sub(r'i\'', 'I\'', infered_text)
                        print(infered_text)
                    else:
                        infered_text = ''
                    if gTransTlang != 'none' :
                        translated = translator.translate(str(infered_text), src= 'auto' , dest= gTransTlang).text
                        output_text = (translated)
                    else : output_text = str(infered_text)
                    if output_text == '': output_text = '---'
                    display_transcript.append(f'{infered_text} --> {output_text}')
                    #
                    limits = audio_file['audio_time'].split('->')
                    limits = [float(int(limit)/1000) for limit in limits]
                    out_file.write(get_srt_line(output_text, line_count, limits))
                    out_file.flush()
                    line_count += 1
        if add_sub:
            with st.spinner('ADDING SUBTITLES INTO VIDEO!'):
                video = VideoFileClip('deployment/temp/target_video.mp4')
                video_width = video.w
                def sub_template(txt):
                        text = TextClip(txt, size= (min(video_width, len(txt) * size_text), 0) , font = font_text, color = color_text, method = 'label')
                        text.set_position('center')
                        if text_bg:
                            im_w, im_h = text.size
                            color_clip = ColorClip(size=(int(im_w*1), int(im_h*1.2)),color=(tuple(int(txt_bg_color[i:i+2], 16) for i in (0, 2, 4))))
                            color_clip = color_clip.set_opacity(txt_bg_opacity/100)
                            clip_to_overlay = CompositeVideoClip([color_clip, text])
                        else : clip_to_overlay = text
                        return clip_to_overlay.set_position(('center','bottom'))
                #generator = lambda txt: TextClip(txt, size=(size_text * 25, 0), font = font_text, color = color_text)
                generator = sub_template
                subtitles = SubtitlesClip(output_path + 'subtitle.srt', generator)
                result = CompositeVideoClip([video, subtitles.set_position((str(text_pos_x),float(text_pos_y / 100)),relative = True)])
                result.write_videofile(output_path + 'subbed.mp4', fps=video.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
                #remove temp file
        shutil.rmtree('deployment/temp')
        Path('deployment/temp').mkdir(parents=True, exist_ok= True)
        vid_img_preview_container.empty()
        st.success('DONE!')
        vid_img_preview_container.video(preview_vid)
    run_holder.button('Run the program!', help='it exactly like what it said, press it and it will process your video. DUH', key = 'RunButton2') 
    
        
if os.path.exists('deployment\output\subbed.mp4'):
    with button_sec:
        if os.path.exists('deployment\output\subbed.mp4'):
            st.write('Subbed Preview')
            st.video(open('deployment\output\subbed.mp4', 'rb').read())
            st.download_button('Download subbed video',
                            data = (open('deployment\output\subbed.mp4', 'rb').read()),
                            file_name='subbed_vid.mp4',
                            mime="video/mp4")
        with open('deployment\output\subtitle.srt', 'rb') as file:
            st.download_button('Download SRT file',
                                data = file,
                                file_name='subtitle.srt')
                
            