#!/usr/bin/python3

import argparse
import contextlib
import json
import math
import os
import time
import wave

import azure.cognitiveservices.speech as azurespeech
import ffmpeg
import yaml

parser = argparse.ArgumentParser(description='Generate VTT for video file')
parser.add_argument('--input', type=str, help='input video file')
parser.add_argument('--output', type=str, help='output file')
parser.add_argument('--maxlinetime', type=float, help='max line time in seconds', default=2.5)

args = parser.parse_args()

# Convert to PCM format
audio_file = args.output + '.wav'
ffmpeg.input(args.input).output(audio_file).overwrite_output().run()

with contextlib.closing(wave.open(audio_file, 'r')) as wave_file:
    duration = wave_file.getnframes() / wave_file.getframerate()

configPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yml')
with open(configPath, 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)

outfile = open(args.output, 'w')

# Add file header
outfile.write('WEBVTT\n\n')
done = False

def format_timestamp(ticks):
    seconds = ticks / 10000000.0
    hours = int(seconds // 60 // 60)
    seconds -= hours * 60 * 60
    minutes = int(seconds // 60)
    seconds -= minutes * 60
    return '{:02d}:{:02d}:{:06.3f}'.format(hours, minutes, seconds)

def stop_cb(evt):
    global speech_recognizer
    speech_recognizer.stop_continuous_recognition()

    global outfile
    outfile.close()
    print()

    global done
    done = True

sequence = 0

def write_chunk(chunk):
    global sequence
    global outfile    
    sequence += 1
    timeline = '{} --> {}'.format(format_timestamp(chunk['start']), format_timestamp(chunk['end']))
    outfile.write('{}\n{}\n{}\n\n'.format(sequence, timeline, chunk['text'].strip()))

max_chunk_length = args.maxlinetime * 10000000.0
def recognized_cb(evt):
    global max_chunk_length

    # Need to load results from json to be able to get offset and duration
    result = json.loads(evt.result.json)

    # Offset is start time
    chunk = {}
    chunk['start'] = result['Offset']
    chunk['text'] = ''
    
    confidences_in_nbest = [item['Confidence'] for item in result['NBest']]
    best_index = confidences_in_nbest.index(max(confidences_in_nbest))

    # Assuming words and dispaly words length are the same...
    words = result['NBest'][best_index]['Words']
    display_words = result['DisplayText'].split(' ')

    end_time = result['Duration'] + result['Offset']

    # Min of half a second or the set max chunk length
    min_chunk_trail = min(max_chunk_length, 10000000.0 / 2)
    last_end = 0
    for i in range(len(words)):
        word = words[i]
        chunk['end'] = word['Offset'] + word['Duration']
        chunk['text'] = f"{chunk['text']} {display_words[i]}"
        # If there's tiny bits of text at the end, just include it in the previous line
        if ((chunk['end'] - chunk['start'] > max_chunk_length) and
            (end_time - chunk['end'] >= min_chunk_trail)):
            write_chunk(chunk)
            chunk['start'] = chunk['end']
            chunk['text'] = ''
            last_end = chunk['end']

    # the last bit of text might not be a "full" line
    if (last_end != chunk['end']):
        write_chunk(chunk)

    # Add the duration to get the end time
    end_pos = result['Offset'] + result['Duration']
    global duration
    print('\rProgress: {:.2f}%'.format(end_pos / 100000.0 / duration), end='')

speech_config = azurespeech.SpeechConfig(subscription=config['key'], region=config['region'])
speech_config.request_word_level_timestamps()

audio_config = azurespeech.audio.AudioConfig(filename=audio_file)

speech_recognizer = azurespeech.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

speech_recognizer.recognized.connect(recognized_cb)
speech_recognizer.canceled.connect(stop_cb)
speech_recognizer.speech_end_detected.connect(stop_cb)

speech_recognizer.start_continuous_recognition()

while not done:
    time.sleep(.5)

os.remove(audio_file)