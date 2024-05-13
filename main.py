import os
import shutil
import atexit
import platform
import subprocess
from tinytag import TinyTag
from flask import Flask, render_template, request
import Whisper_Pro
from meilisearch.client import Client
from Whisper_Pro import search_meilisearch


client = Client('http://localhost:7700')  #melisearch port
index = client.index('audio_tags') #new



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
#   metadata: Existing file metadata
#   transcription_info: information returned by the Whisper Library
# }
audio_files = []

@app.route('/')
def start():
    return render_template('start.html')

# test route martin
@app.route('/browse')
def browse():
    search = request.args.get('search')
    if search:
        # Perform MeiliSearch search and get matching audio files
        matching_audio_files = search_meilisearch(search)
        # Replace audio_files with matching_audio_files
        audio_files = matching_audio_files
    return render_template('browse.html', audio_files=audio_files)



@app.route('/details/<int:id>')
def details(id):
    file = {}
    for f in audio_files:
        if f['id'] == id:
            file = f
            break
        
    return render_template('details.html', file=file)

@app.route('/select_folder', methods=['POST'])
def select_folder():
    for name in os.listdir(request.json['folder']):
        if name.endswith('.wav') or name.endswith('.mp3') or name.endswith('.m4a') and not os.path.islink('./static/audio/' + name):
            os.symlink(request.json['folder'] + '/' + name, './static/audio/' + name)
            metadata = TinyTag.get('./static/audio/' + name)
            audio_files.append({'name': name, 'path': request.json['folder'] + '/' + name, 'id': len(audio_files), 'metadata': metadata.as_dict(), 'transcription_info': None})
    #Translates dictionary of audio files to a list of just audio file paths
    audio_files_list = Whisper_Pro.audio_list_translation(audio_files)
    #Process audio files with Whisper
    Whisper_Pro.whisper_process(audio_files_list)
    return ('', 200)

@app.route('/open_file', methods=['POST'])
def open_file():
    if platform.system() == 'Windows':
        subprocess.Popen(r'explorer /select,"' + request.json['path'] + '"')
    if platform.system() == 'Darwin':
        subprocess.call(["open", "-R", request.json['path']])

    
    return ('', 200)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
