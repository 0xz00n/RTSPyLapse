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

