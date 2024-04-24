import os
from flask import Flask, render_template, request

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
    return render_template('browse.html')

@app.route('/details')
def details():
    return render_template('details.html')

@app.route('/select_folder', methods=['POST'])
def select_folder():
    for name in os.listdir(request.json['folder']):
        if name.endswith('.wav'):
            audio_files.append({'name': name, 'path': request.json['folder'] + '/' + name})
    return ('', 200)
    

if __name__ == '__main__':
    app.run(debug=True)