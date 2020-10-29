# RTSPyLapse
RTSP stream timelapse creator

## Requirements
```
apt install ffmpeg
git clone https://github.com/0xz00n/RTSPyLapse.git
cd RTSPyLapse
python3 -m pip install -r requirements.txt
```

## Help Info
```
$ python3 app.py
usage: app.py [-h] [--cli ] [--conf [config.py]] [-u] [-o] [-p] [-cs] [-ce]
              [-d ] [-f ] [-e ]

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

```
