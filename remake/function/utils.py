from pytube import YouTube
import json
import time
import requests

class huggingface_handler:

    def api_test(api_token):
        api_url = "https://api-inference.huggingface.co/models/gpt2"
        headers = {"Authorization": f"Bearer {api_token}"}
        
        test_payload = 'Tell me more about '
        data = json.dumps(test_payload)
        response = requests.request("POST", api_url, headers=headers, data=data)
        output = json.loads(response.content.decode("utf-8"))
        if 'error' in output:
            return False
        else:
            return True

class yt_handler:
    
    def get_metadata(url):
        yt = YouTube(url)
        author = yt.author
        title = yt.title
        desc = yt.description
        pic = yt.thumbnail_url
        length = yt.length
        views = yt.views
        return author, title, desc, pic, length, views
    

    
    
    
class misc_handler:
    
    def time_convert(sec): #convert second into HH/MM/SS
        return time.strftime("%H:%M:%S", time.gmtime(sec))

if __name__ == '__main__':
    
    print(yt_handler.get_metadata('https://youtu.be/BxV14h0kFs0'))