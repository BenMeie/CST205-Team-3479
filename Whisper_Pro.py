#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Matthew J. Sanchez

Purpose: This functions as the backend for a audio processing application using Whisper
that adds meta data tags to files for searching purposes.
"""

import os
import glob
import whisper
from pytaggit import tag_manager as tm
from meilisearch.client import Client

client = Client('http://localhost:7700') 
index = client.index('audio_tags')

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
    """
    This function takes a directory and scans it for audio file types. 
    It is deprecated and is not in use. Has been replaced with main.select folder and audio_list_translation

     Parameters:
         directory: A directory of audio files to scan.

     Returns:
         audio_files: List of audio file paths
    """
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a')):
                audio_files.append(os.path.join(root, file))
    return audio_files


def whisper_process(audio_list):
    """
    This function takes a list of audio file paths and processes them
    using whisper, generates words from the audio, removes common words,
    and adds tags to files
     Parameters:
         audio_list: List of audio file paths to process

     Returns:
         None
    """
    
    # Load our model
    model = whisper.load_model("base")
    
    # This loop iterates each audio file, transcribes it, removes common words using remove_commons_n_punct()
    for audio in audio_list:
        result = model.transcribe(audio)
        myText = result["text"]
        tags = remove_commons_n_punct(myText)
        tag = tm.Tag(name=("language:" + result["language"]), color=color_tag)
        tm.add_tag(tag, audio)
        
        # Indexing audio file with tags into MeiliSearch (new)
        document = {
            'audio_path': audio,
            'tags': tags
        }
        index.add_documents([document])
        
    # This loop adds tags to the audio file using pytaggit
        for tag in tags:
            tag2add = tm.Tag(name=tag, color=color_tag)
            tm.add_tag(tag2add, audio)
            
def audio_list_translation(audiolist):
    """
    This function takes a dictionary of audio file information, it only grabs the audio file paths
    and returns it as a new list. This is to adapt information for whisper_process.
     Parameters:
         audiolist: A dictionary of audio file information

     Returns:
         paths: A list of just audio file paths
    """
    paths = []
    for entry in audiolist:
        paths.append(entry['path'])
    return paths


def remove_commons_n_punct(word_list):
    """
    This function takes the list of tags that would be added to a audio file and filters out stop words and 
    other common words that wouldnt be useful tags
     Parameters:
         word_list: List of tags to be filtered through

     Returns:
         res: List of tags to be added
    """
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


def search_meilisearch(keyword): #(new)
    # Perform a search in MeiliSearch based on the keyword
    search_results = index.search(keyword)
    
    # Output matching audio files to the user
    matching_audio_files = []
    for hit in search_results['hits']:
        matching_audio_files.append(hit['audio_path'])
    
    return matching_audio_files
