import os
import shutil
import atexit
from flask import Flask, render_template, request

def cleanup():
    shutil.rmtree('./static/audio')
    
atexit.register(cleanup)
try: 
    os.mkdir('./static/audio')
except FileExistsError:
    pass

app = Flask(__name__)

# {
#   name: The file name
#   path: The file's full path
#   existing_tags[]: An array of tags that already exist for the file, mostly in the comments
#   transcription_info: information returned by the Whisper Library
# }
audio_files = []

@app.route('/')
def start():
    return render_template('start.html')

@app.route('/browse')
def browse():
    return render_template('browse.html', audio_files=audio_files)

@app.route('/details')
def details():
    return render_template('details.html')

@app.route('/select_folder', methods=['POST'])
def select_folder():
    for name in os.listdir(request.json['folder']):
        if name.endswith('.wav') or name.endswith('.mp3'):
            shutil.copy(request.json['folder'] + '/' + name, './static/audio/')
            audio_files.append({'name': name, 'path': request.json['folder'] + '/' + name, 'id': len(audio_files)})
    return ('', 200)
    

if __name__ == '__main__':
    app.run(debug=True, port=3000)