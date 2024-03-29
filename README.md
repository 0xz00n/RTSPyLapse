# RTSPyLapse
An RTSP stream timelapse creator.  Captures stills from an RTSP stream between specified times and creates an mp4 file using the captured stills.

## Requirements
>Note that this has only been tested on Linux systems.
```
apt install ffmpeg
git clone https://github.com/0xz00n/RTSPyLapse.git
cd RTSPyLapse
python3 -m pip install -r requirements.txt
```

## Help Info
This program can be used from either the command line or via the config.py file.

> Command line options
```
$ python3 app.py
usage: app.py [-h] [--cli ] [--conf [config.py]] [-u] [-o] [-p] [-cs] [-ce]
              [-d ] [-f ] [-e ] [-b ] [-c ] [-r ]

An RTSP stream timelapse creator.

optional arguments:
  -h, --help            show this help message and exit
  --cli []              Used if you want to configure job parameters on the command line.
  --conf [config.py]    Used if you want to configure job parameters via the config.py file.
  -u , --url            RTSP URL. Ex: -u "rtsp://username:password@1.2.3.4/live"
  -o , --outputfile     Name of the final mp4 file. Ex: -o timelapse1
  -p , --path           Full path to the desired working directory. Ex: -p /home/user/timelapse/
  -cs , --capturestart
                        Time to start captures in 24h format.  Ex: -cs 15:30
  -ce , --captureend    Time to end captures in 24h format. Ex: -ce 08:15
  -d [], --delay []     Time between still captures.  Default (And minimum) is ~2.5 seconds. Ex: -d 5
  -f [], --framerate []
                        Number of frames per second.  Default is 25. Ex: -f 30
  -e [], --encoder []   Encoder to use for mp4 creation, uses system default if unspecified.  Ex: -e h264_omx
  -b [], --bitrate []   Bitrate limit in M.  Default is 12M.  Bufsize is always 1M. Ex: -b 12
  -c [], --chroma []    Chroma subsampling scheme, also known in ffmpeg as a pixel format. Sometimes needed for specific encoders. Ex: -c yuv420p
  -r [], --rotate []    Rotation option.  Equivalent to ffmpeg transpose option. Ex: -r 1 (This will rotate image 90 degress clockwise)
```

> Config.py file
```
# RTSP URL. Ex: 'rtsp://username:password@1.2.3.4/live'
url = ''
# Name of the final mp4 file. Ex: 'timelapse1'
outputfile = ''
# Full path to the desired working directory. Ex: '/home/usr/timelapse/'
path = ''
# Time to start captures in 24h format.  Ex: '15:30'
capturestart = ''
# Time to end captures in 24h format. Ex: '08:15'
captureend = ''
# Time between still captures.  Default (And minimum) is 2.5 seconds. Ex: 5
delay = 2.5
# Number of frames per second.  Default is 25.
framerate = 25
# Encoder to use for mp4 creation.  Leave empty for default.
encoder = ''
# Bitrate limit in M.  Default is 12M.  Bufsize is always 1M. Ex: -b 12
bitrate = 12
# Chroma subsampling scheme, also known in ffmpeg as a pixel format. Sometimes needed for specific encoders. Ex: -c yuv420p
chroma = None
# Rotation option.  Equivalent to ffmpeg transpose option. Ex: -r 1 (This will rotate image 90 degress clockwise)
rotate = None
```

