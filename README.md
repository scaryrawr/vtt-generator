# VTT Generator

Generates VTT files for a video using FFMPEG and Azure Cognitive Services.

# Requirements

- [ffmpeg](https://www.ffmpeg.org)
- `pip install ffmpeg-python`
- `pip install azure-cognitiveservices-speech`

# Run

`./vtt-gen.py --input path/to/video --output path/to/subtiles.vtt`

VTT file tested with [VLC](https://www.videolan.org/vlc/index.html)

# VTT to SRT

Output file contains sequence number and works with [amorvincitomnia/vtt-to-srt](https://github.com/amorvincitomnia/vtt-to-srt.py)

Tested SRT file with [GNOME Videos](https://wiki.gnome.org/Apps/Videos)