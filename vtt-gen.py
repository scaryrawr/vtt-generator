#!/bin/python3

import argparse
import azure.cognitiveservices.speech as azurespeech
import ffmpeg
import time
import yaml
import json
import os

parser = argparse.ArgumentParser(description='Generate VTT for video file')
parser.add_argument('--input', type=str, help='input video file')
parser.add_argument('--output', type=str, help='output file')

args = parser.parse_args()

# Convert to PCM format
audio_file = args.output + '.wav'
ffmpeg.input(args.input).output(audio_file).overwrite_output().run()

with open('config.yml', 'r') as config_file:
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
    print('Closing: {}'.format(evt))
    global speech_recognizer
    speech_recognizer.stop_continuous_recognition()
    global done
    done = True
    global outfile
    outfile.close()

sequence = 0
def recognized_cb(evt):
    global outfile
    result = json.loads(evt.result.json)
    start = format_timestamp(result['Offset'])
    end = format_timestamp(result['Offset'] + result['Duration'])
    timeline = '{} --> {}'.format(start, end)
    global sequence
    sequence += 1
    outfile.write('{}\n{}\n{}\n\n'.format(sequence, timeline, result['DisplayText']))
    print('{}\n{}\n{}\n\n'.format(sequence, timeline, result['DisplayText']))

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
