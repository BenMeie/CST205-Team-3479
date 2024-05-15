# Audio Transcriber
### Contributors
Ben Meier, Martin Nguyen, Matthew Sanchez

### Class
CST205

### Date
5/15/2024

### Installation
This project requires a few python packages. Install with
```
pip install openai-whisper tinytag pytaggit flask meilisearch
```
then just run
```
python main.py
```

__pytaggit does not work on some Windows computers. Skipping it's installation should not result in any errors__

Download free audio files to test with [here](https://archive.org/details/audio_podcast)

### Repo
https://github.com/BenMeie/CST205-Team-3479

## Future Work
Audio database should be saved between program launches so that files do not have to be processed with Whisper every time the program is launched.
The program should be able to process video files
Support removing files from the application