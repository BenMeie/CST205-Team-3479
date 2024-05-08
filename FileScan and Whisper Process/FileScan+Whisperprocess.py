#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:08:18 2024

@author: matthewsanchez090401
"""

import os
import glob
import whisper
from pytaggit import tag_manager as tm

common_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "you're", "you've", "you'll",
                "you'd", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "she's",
                "her", "hers", "herself", "it", "it's", "its", "itself", "they", "them", "their", "theirs",
                "themselves", "what", "which", "who", "whom", "this", "that", "that'll", "these", "those",
                "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having",
                "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as",
                "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
                "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in",
                "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there",
                "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
                "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t",
                "can", "will", "just", "should", "should've", "now","", "i'm", "i'll", "same", "okay", "hey", "trying",
                "kinda", "we're", "says", "say", "what'd", "could", "enough", "never", "ever", "said", "still", "sitting", "watching", "doing"
                ]
color_tag = "blue"



def audio_file_scan(directory):
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a')):
                audio_files.append(os.path.join(root, file))
    return audio_files


def whisper_process(audio_list):
    for audio in audio_list:
        model = whisper.load_model("base")
        result = model.transcribe(audio)
        myText = result["text"]
        # Tags to add Here
        tags = remove_commons_n_punct(myText)
        print(tags)
        tag = tm.Tag(name=("language:" + result["language"]), color=color_tag)
        tm.add_tag(tag, audio)
        for tag in tags:
            tag2add = tm.Tag(name=tag, color=color_tag)
            tm.add_tag(tag2add, audio)
        

def remove_commons_n_punct(word_list):
    Newlist = word_list.replace(",", "")
    Newlist = Newlist.replace(".", "")
    Newlist = Newlist.replace("?", "")
    Newlist = Newlist.replace("!", "")
    Newlist = Newlist.split(" ")
    
    res = list(map(lambda x:x.lower(),Newlist))
        
    for word in common_words:
        if(word in res):
            while(word in res):
                res.remove(word)
    return res


if __name__ == "__main__":
    # Replace with path on your machine
    directory_path = '/Users/matthewsanchez090401/Documents/CST205/Final Whisper Pro/TST'
    audio_files_list = audio_file_scan(directory_path)
    whisper_process(audio_files_list)
