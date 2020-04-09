# VTT Generator

Generates VTT files for a video using FFMPEG and Azure Cognitive Services.

## Requirements

- [ffmpeg](https://www.ffmpeg.org)
  - Linux, use your package manager
  - Mac, can use [brew](https://formulae.brew.sh/formula/ffmpeg)
  - Windows, can use [chocolatey](https://chocolatey.org/packages/ffmpeg)
- `pip3 install ffmpeg-python`
- `pip3 install azure-cognitiveservices-speech`
- [Azure Cognitive Services Speech](https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/)

Copy config.example.yml to config.yml and fill with your Azure Information:

```yml
key: azurekey
region: azureregion
```

## Run

`./vtt-gen.py --input path/to/video --output path/to/subtiles.vtt`

VTT file tested with [VLC](https://www.videolan.org/vlc/index.html) and [GNOME Videos](https://wiki.gnome.org/Apps/Videos)

## Validate

- Generation is automatic, so please proofread the output
- Check the file output is valid using [Live WebVTT Validator](https://quuz.org/webvtt/)

## WebVTT Documentation

The output of this script is very basic, but can be customized, please see the following links for working with the vtt file.

- [MDN WebVTT](https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API)
- [W3 WebVTT](https://www.w3.org/TR/webvtt1/)

## Video Services Caption Files

Links to web pages for helping upload caption files:

- [Vimeo](https://vimeo.zendesk.com/hc/en-us/articles/224968828-Captions-and-subtitles)
- [YouTube](https://support.google.com/youtube/answer/2734796?hl=en&ref_topic=7296214)
- [Facebook](https://www.facebook.com/help/261764017354370) - Requires SRT file, can use [amorvincitomnia/vtt-to-srt.py](https://github.com/amorvincitomnia/vtt-to-srt.py) or another tool
