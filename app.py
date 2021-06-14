#! /usr/bin/env python3

import argparse
import datetime
import ffmpeg
import shutil
import glob
import time
import sys
import os

def parseArgs():
    parser = argparse.ArgumentParser(description = 'An RTSP stream timelapse creator.',  formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument(
        '--cli',
        nargs = '?',
        const = 1,
        type = int,
        help = 'Used if you want to configure job parameters on the command line.',
        metavar = '',
        required = False
    )

    parser.add_argument(
        '--conf',
        nargs = '?',
        const = 1,
        type = int,
        help = 'Used if you want to configure job parameters via the config.py file.',
        metavar = 'config.py',
        required = False
    )

    parser.add_argument(
        '-u',
        '--url',
        help = 'RTSP URL. Ex: -u "rtsp://username:password@1.2.3.4/live"',
        metavar = '',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-o',
        '--outputfile',
        help = 'Name of the final mp4 file. Ex: -o timelapse1',
        metavar = '',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-p',
        '--path',
        help = 'Full path to the desired working directory. Ex: -p /home/user/timelapse/',
        metavar = '',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-cs',
        '--capturestart',
        help = 'Time to start captures in 24h format.  Ex: -cs 15:30',
        metavar = '',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-ce',
        '--captureend',
        help = 'Time to end captures in 24h format. Ex: -ce 08:15',
        metavar = '',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-d',
        '--delay',
        nargs = '?',
        const = 2.5,
        default = 2.5,
        type = float,
        help = 'Time between still captures.  Default (And minimum) is ~2.5 seconds. Ex: -d 5',
        metavar = '',
        required = False
    )

    parser.add_argument(
        '-f',
        '--framerate',
        nargs = '?',
        const = 25,
        default = 25,
        type = int,
        help = 'Number of frames per second.  Default is 25. Ex: -f 30',
        metavar = '',
        required = False
    )

    parser.add_argument(
        '-e',
        '--encoder',
        nargs = '?',
        const = None,
        type = str,
        help = 'Encoder to use for mp4 creation, uses system default if unspecified.  Ex: -e h264_omx',
        metavar = '',
        required = False
    )

    parser.add_argument(
        '-b',
        '--bitrate',
        nargs = '?',
        const = 12,
        default = 12,
        type = str,
        help = 'Bitrate limit in M.  Default is 12M.  Bufsize is always 1M. Ex: -b 12',
        metavar = '',
        required = False
    )

    parser.add_argument(
        '-c',
        '--chroma',
        nargs = '?',
        const = None,
        type = str,
        help = 'Chroma subsampling scheme, also known in ffmpeg as a pixel format. Sometimes needed for specific encoders. Ex: -c yuv420p',
        metavar = '',
        required = False
    )

    parser.add_argument(
        '-r',
        '--rotate',
        nargs = '?',
        const = None,
        type = int,
        help = 'Rotation option.  Equivalent to ffmpeg transpose option. Ex: -r 1 (This will rotate image 90 degress clockwise)',
        metavar = '',
        required = False
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    return args

def streamCap(url,outputfile,path,rotate=None):
    today = datetime.datetime.now()
    timestamp = today.strftime('%Y-%m-%d_%H-%M-%S')
    stream = ffmpeg.input(url, ss = 0, rtsp_transport = 'tcp', stimeout = 4000000)
    if not rotate == None:
        stream = ffmpeg.filter(stream, 'transpose','' + str(rotate) + '')
    capture = stream.output(path + outputfile + timestamp + '.jpg', vframes = 1)
    capture.run(capture_stdout = True, capture_stderr = True)

def compileImages(outputfile,path,frames,encoder=None,bitrate='12',chroma=None):
    print('Compiling still frames...')
    today = datetime.datetime.now()
    timestamp = today.strftime('_%Y-%m-%d')
    load = ffmpeg.input(path + outputfile + '*.jpg', pattern_type = 'glob', framerate = frames)
    if not chroma == None:
        load = ffmpeg.filter(load, 'format', chroma)
    filename = path + outputfile + timestamp + '.mp4'
    if os.path.isfile(filename):
        if os.stat(filename).st_size == 0:
            print('Detected empty mp4, probably from bad encoder.  Deleting.')
            os.remove(filename)
        else:
            shutil.move(filename, filename + '.old' + timestamp)
    if not encoder == None:
        combine = load.output(path + outputfile + timestamp + '.mp4', **{'c:v': encoder}, **{'b:v': bitrate + 'M'}, maxrate = bitrate + 'M', bufsize = '1M')
    else:
        combine = load.output(path + outputfile + timestamp + '.mp4', **{'b:v': bitrate + 'M'}, maxrate = bitrate + 'M', bufsize = '1M')
    combine.run(capture_stdout = True, capture_stderr = True)
    print('Compiled', filename)

def cleanupDir(outputfile,path):
    print('Cleaning up working directory...')
    filelist = glob.glob(path + outputfile + '*.jpg')
    for filename in filelist:
        try:
            os.remove(filename)
        except:
            print('Error while deleting file: ', filename)
    print('Done.')

def timeLogic(capturestart,captureend):
    try:
        timenow = datetime.datetime.now().strftime('%H:%M')
        timeobj = datetime.datetime.strptime(timenow, '%H:%M')
        startobj = datetime.datetime.strptime(capturestart, '%H:%M')
        endobj = datetime.datetime.strptime(captureend, '%H:%M')
    except Exception as e:
        print('Something is wrong with provided start or end time, please see following error:')
        raise e
    
    if startobj < endobj:
        if timeobj >= startobj and timeobj < endobj:
            return True
        else:
            return False
    elif startobj == endobj:
        print('If you are trying to take a 24 hour timelapse, try something like:')
        print('Start time: 09:00\nEnd time: 08:59')
        sys.exit()
    else:
        if timeobj >= startobj:
            return True
        elif timeobj < endobj:
            return True
        else:
            return False

def failLogic(error,url,outputfile,path):
    tryagain = 0
    if 'Connection refused' in error:
        print('Connection refused.  Is the URL correct?')
    elif 'No route to host' in error:
        print('No route to host.  Is the URL correct?')
    else:
        print(error)
        raise error
    while tryagain < 5: 
        print('Trying ' + str((5 - tryagain)) + ' more times...')
        tryagain += 1
        try:
            streamCap(url,outputfile,path)
            time.sleep(delay)
            break
        except:
            if tryagain == 5:
                print('Failed, quitting.')
                sys.exit()
            else:
                print('Failed.')
                time.sleep(5)
                continue

args = parseArgs()

if args.cli == 1:
    url = args.url
    outputfile = args.outputfile
    path = args.path
    capturestart = args.capturestart
    captureend = args.captureend
    delay = float(args.delay) - float(2.5)
    framerate = int(args.framerate)
    encoder = args.encoder
    rotate = args.rotate
    chroma = args.chroma
    bitrate = str(args.bitrate)

elif args.conf == 1:
    from config import *
    delay = float(delay) - float(2.5)
    framerate = int(framerate)
    
if delay < 0:
    print('Delay less than 2.5, setting to default.')
    delay = 0
if framerate <= 0:
    print('Framerate must be > 0.')
    sys.exit()
if encoder == '':
    encoder = None
if not rotate == None:
    try:
        if int(rotate) > 4:
            print('Rotate can only be 1-4. Please see ffmpeg transpose for details.')
            sys.exit()
    except Exception as e:
        print('Rotate did not have an expected value, see the error below for more details:\n', e)
        sys.exit()
if not bitrate == '12':
    try:
        int(bitrate)
    except Exception as e:
        print('Bitrate did not have an expected value, see the error below for more details:\n', e)
        sys.exit()
if not os.path.isdir(path):
    print('Specified path not found')
    sys.exit()

wait = True

print('Beginning job...')
print('Captures start at:', capturestart)
print('Captures end at:', captureend)
print('Delay between captures:', delay)
print('Selected encoder:', encoder)
print('Output framerate:', framerate)
print('Output bitrate:', bitrate)
if not rotate == None:
    print('Transpose option:', rotate)
if not chroma == None:
    print('Chroma option:', chroma)
while True:
    while True:
        result = timeLogic(capturestart,captureend)
        if result:
            wait = False
            try:
                streamCap(url,outputfile,path,rotate)
                time.sleep(delay)
            except ffmpeg.Error as e:
                print(ffmpeg.Error)
                try:
                    iter(e)
                    if not e.stderr.decod('utf8') == None:
                        print(e)
                        failLogic(e,url,outputfile,path)
                    else:
                        print(e)
                except TypeError as e:
                    print(e)
        else:
            break
    if wait == False:
        try:
            compileImages(outputfile,path,framerate,encoder,bitrate,chroma)
            cleanupDir(outputfile,path)
            wait = True
            time.sleep(5)
        except ffmpeg.Error as e:
            error = e.stderr.decode('utf8')
            if 'Error while opening encoder' in error:
                print('Couldn\'t open selected encoder, trying again with default.')
                try:
                    compileImages(outputfile,path,framerate)
                    cleanupDir(outputfile,path)
                    wait = True
                    time.sleep(5)
                except ffmpeg.Error as e:
                    print(e.stderr.decode('utf8'))
                    raise e
            else:
                print(e.stderr.decode('utf8'))
                raise e
    else:
        time.sleep(5)
