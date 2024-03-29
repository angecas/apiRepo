# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 22:19:09 2022

@author: angec
"""


from xgboost.sklearn import XGBClassifier
from pydub import AudioSegment
import os
import librosa
import numpy as np
import pandas as pd
from collections import Counter
import math
import json

# carregar o model
model = XGBClassifier()
model.load_model('model.json')
# carregar o som
# processamento de sinal

#sound_file= "audio.wav"


def largest_indices(ary, n):
    flat = ary.flatten()

    indices = np.argpartition(flat, -n)[-n:]
    indices = indices[np.argsort(-flat[indices])]

    return indices


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def slice_audio(sound_file):
    #audio= AudioSegment.from_file_using_temporary_files(sound_file)
    audio = AudioSegment.from_wav(sound_file)
    # durac=audio.duration_seconds
    audio_slice = audio[0*1000:5*1000]
    return audio_slice


def matrix_features(sound_file, data, samplerate):

    features_extraction = []
    header = ['filename', 'label', 'chroma_stft',
              'mel_spectogram', 'spectral_contrast', 'tonnetz']
    for i in range(1, 41):
        header.append(f' mfcc{i}')
    sound_data = [sound_file, 3]
    #X, sr = librosa.load(sound_file)
    # o data e o sample rate sao novos args
    X, sr = data, samplerate

    stft = np.abs(librosa.stft(X))
    sound_data.append(np.mean(librosa.feature.chroma_stft(S=stft, sr=sr)))
    sound_data.append(np.mean(librosa.feature.melspectrogram(X, sr=sr)))
    sound_data.append(
        np.mean(librosa.feature.spectral_contrast(S=stft, sr=sr)))
    sound_data.append(np.mean(librosa.feature.tonnetz(
        y=librosa.effects.harmonic(X), sr=sr)))
    mfcc = librosa.feature.mfcc(y=X, sr=sr, n_mfcc=40)
    for e in mfcc:
        sound_data.append(np.mean(e))
    features_extraction.append(sound_data)
    df = pd.DataFrame(features_extraction, columns=header)
    # droping first column, filename column and label column
    X_TEST = df.drop([df.columns[0], 'filename', 'label'], axis=1)
    Y_TEST = df['label']
    return (X_TEST, Y_TEST)


def convert_label(previs):
    prev = ''
    if previs == 1:
        prev = 'positive'
    elif previs == 0:
        prev = 'negative'
    else:
        prev = 'unknown'

    return prev


def convert_percent(no):
    percent = str(round(no*100))+'%'
    return percent


def prev_label(sound_file, data, samplerate):
    # passei os novos args
    (sound, label) = matrix_features(sound_file, data, samplerate)
    sounds = []
    #first_preds = []
    #first_percent = []
    #second_preds = []
    #second_percent = []
    #third_preds = []
    #third_percent = []
    prev = ''
    predictions = model.predict_proba(sound)
    predic = largest_indices(predictions, 3)
    percentage = predictions[0][predic]
    sounds.append(label[0])

    # first_preds.append((predic)[0])
    # first_percent.append(truncate(percentage[0],3)) #percentagem de label 0

    first_prev = (predic)[0]
    fst_percent = truncate(percentage[0], 3)

    # second_preds.append((predic)[1])
    # second_percent.append(truncate(percentage[1],3)) #percentagem de label 1

    second_prev = (predic)[1]
    sec_percent = truncate(percentage[1], 3)

    # third_preds.append((predic)[2])
    # third_percent.append(truncate(percentage[2],3)) #percentagem de label 2

    third_prev = (predic)[2]
    trd_percent = truncate(percentage[2], 3)
    mode = []
    test_list1 = Counter([first_prev])
    temp = test_list1.most_common(1)[0][1]
    for ele in [first_prev]:
        if [first_prev].count(ele) == temp:
            mode.append(ele)

    # ---------------------------
    mode = list(set(mode))[0]

    prev = convert_label(mode)

    # -------------------------------

    first_prev = convert_label(first_prev)
    second_prev = convert_label(second_prev)
    third_prev = convert_label(third_prev)
    fst_percent = convert_percent(fst_percent)
    sec_percent = convert_percent(sec_percent)
    trd_percent = convert_percent(trd_percent)

    previsionResults = {"previsionLabel": prev,
                        "firstPrevisionLabel": first_prev,
                        "firstPrevisionPercent":  fst_percent,
                        "secondPrevisionLabel": second_prev,
                        "secondPrevisionPercent": sec_percent,
                        "thirdPrevisionLabel": third_prev,
                        "thirdPrevisionPercent":  trd_percent}
    print(previsionResults)

    return previsionResults

# prev_label(sound_file)
