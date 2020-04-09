#!/usr/bin/python3

import argparse
import azure.cognitiveservices.speech as azurespeech
import ffmpeg
import time
import yaml
import json
import os
import wave
import contextlib

parser = argparse.ArgumentParser(description='Generate VTT for video file')
parser.add_argument('--input', type=str, help='input video file')
parser.add_argument('--output', type=str, help='output file')

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
def recognized_cb(evt):
    # Need to load results from json to be able to get offset and duration
    result = json.loads(evt.result.json)

    # Offset is start time
    start = format_timestamp(result['Offset'])

    # Add the duration to get the end time
    end_pos = result['Offset'] + result['Duration']
    end = format_timestamp(end_pos)
    
    global sequence
    global outfile
    
    # Format is:
    # Sequence#
    # Start --> End
    # Captions
    # [blank line]
    sequence += 1
    timeline = '{} --> {}'.format(start, end)
    outfile.write('{}\n{}\n{}\n\n'.format(sequence, timeline, result['DisplayText']))

    global duration
    print('\rProgress: {:.2f}%'.format(end_pos / 100000.0 / duration), end='')
    

speech_config = azurespeech.SpeechConfig(subscription=config['key'], region=config['region'])
audio_config = azurespeech.audio.AudioConfig(filename=audio_file)

speech_recognizer = azurespeech.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

speech_recognizer.recognized.connect(recognized_cb)
speech_recognizer.canceled.connect(stop_cb)
speech_recognizer.speech_end_detected.connect(stop_cb)

speech_recognizer.start_continuous_recognition()

while not done:
    time.sleep(.5)

os.remove(audio_file)
