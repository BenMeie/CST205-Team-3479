"""
Course: Python CST205
Title: Audio Searcher
Abstract: We input audio files, use whisper to transcribe the audio to text, turn the text into tags/keywords that we are able 
to search for and have it display on our website 
Authors: Benjamin Meier - Flask GUI, Martin Nguyen - Meleisearch API Intergration, Matthew Sanchez - Whisper API And File Scanning, Pablo Gomez - TBA
Date: 5/14/2024
Link to GitHub repository:  https://github.com/BenMeie/CST205-Team-3479
"""


import os
import shutil
import atexit
import platform
import subprocess
from threading import Thread
from tinytag import TinyTag
from flask import Flask, render_template, request
import Whisper_Pro
from meilisearch.client import Client
from Whisper_Pro import search_meilisearch

client = Client('http://localhost:7700')  #melisearch port
index = client.index('audio_tags') #new
def launch_meilisearch():
    '''
        Launches MeiliSearch in a new thread so it doesn't block the main thread - Ben
        - Checks the current platform
        - Downloads Meilisearch for that platform if it was not found
        - Launches Meilisearch
    '''
    if platform.system() == 'Windows':
        try:
            subprocess.run(['.\\meilisearch-windows-amd64.exe'])
        except:
            print("Could not find MeiliSearch executable. Downloading...")
            subprocess.run(['curl', '-L', 'https://github.com/meilisearch/meilisearch/releases/download/v1.8.0/meilisearch-windows-amd64.exe', '-o', 'meilisearch-windows-amd64.exe'])
            subprocess.run(['.\\meilisearch-windows-amd64.exe'])
    elif platform.system() == 'Darwin':
        try:
            subprocess.run(['./meilisearch-macos-apple-silicon'])
        except:
            print("Could not find MeiliSearch executable. Downloading...")
            subprocess.run(['curl', '-L', 'https://github.com/meilisearch/meilisearch/releases/download/v1.8.0/meilisearch-macos-apple-silicon', '-o', 'meilisearch-macos-apple-silicon'])
            subprocess.run(['chmod', '+x', './meilisearch-macos-apple-silicon'])
            subprocess.run(['./meilisearch-macos-apple-silicon'])

Thread(target=launch_meilisearch).start()

def cleanup():
    '''
        Cleans up the static/audio directory when the server is stopped - Ben
    '''
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
completed_files = []
total_files = []

@app.route('/')
def start():
    return render_template('start.html')

#  Browse Route Martin/Ben
@app.route('/browse')
def browse():
    files_to_send = audio_files
    search = request.args.get('search')
    if search:
        # perform MeiliSearch search and get matching audio files
        matching_audio_files = search_meilisearch(search)
        # replace audio_files with matching_audio_files
        files_to_send = matching_audio_files
    return render_template('browse.html', audio_files=files_to_send)


# Details for the audio file including existing metadata and tags from transcription - Ben
@app.route('/details/<int:id>')
def details(id):
    file = {}
    for f in audio_files:
        if f['id'] == id:
            file = f
            break
        
    return render_template('details.html', file=file)

# Select Folder Post Route - Ben 
@app.route('/select_folder', methods=['POST'])
def select_folder():
    # Scan selected folder
    for name in os.listdir(request.json['folder']):
        if name.endswith('.wav') or name.endswith('.mp3') or name.endswith('.m4a') and not os.path.islink('./static/audio/' + name):
            # Create a symlink to the static/audio directory so we can access in the webapp
            os.symlink(request.json['folder'] + '/' + name, './static/audio/' + name)
            metadata = TinyTag.get(request.json['folder'] + '/' + name)
            audio_files.append({'name': name, 'path': request.json['folder'] + '/' + name, 'id': len(audio_files), 'metadata': metadata.as_dict(), 'transcription_info': None})
            total_files.append(True)
    #Process audio files with Whisper - Matthew
    Whisper_Pro.whisper_process(audio_files)
    return ('', 200)

# Reveal the audio file in Finder/File Explorer - Ben
@app.route('/open_file', methods=['POST'])
def open_file():
    if platform.system() == 'Windows':
        subprocess.Popen(r'explorer /select,"' + request.json['path'] + '"')
    if platform.system() == 'Darwin':
        subprocess.call(["open", "-R", request.json['path']])

    
    return ('', 200)

@app.route('/processed_file', methods=['POST'])
def add_processed_file():
    completed_files.append(True)
    return('', 200)
    
@app.route('/progress')
def get_processed_files():
    if(len(completed_files) > 0) and (len(total_files) > 0):
        print(f'{len(completed_files)/len(total_files)}')
        return f'{len(completed_files)/len(total_files)}'
    return '0'

if __name__ == '__main__':
    app.run(debug=True, port=3000)

