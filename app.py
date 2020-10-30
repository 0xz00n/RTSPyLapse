#! /usr/bin/env python3

import argparse
import datetime
import ffmpeg
import glob
import time
import sys
import os

def parseArgs():
    parser = argparse.ArgumentParser(description = '...')

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
        required = '--cli' not in sys.argv
    )

    parser.add_argument(
        '-u',
        '--url',
        help = 'RTSP URL. Ex: -u "rtsp://username:password@1.2.3.4/live"',
        metavar = '"rtsp://username:password@1.2.3.4/live"',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-o',
        '--outputfile',
        help = 'Name of the final mp4 file. Ex: -o timelapse1',
        metavar = 'timelapse1',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-p',
        '--path',
        help = 'Full path to the desired working directory. Ex: -p /home/user/timelapse/',
        metavar = '/home/user/timelapse/',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-cs',
        '--capturestart',
        help = 'Time to start captures in 24h format.  Ex: -cs 15:30',
        metavar = '15:30',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-ce',
        '--captureend',
        help = 'Time to end captures in 24h format. Ex: -ce 08:15',
        metavar = '08:15',
        required = '--cli' in sys.argv
    )

    parser.add_argument(
        '-d',
        '--delay',
        help = 'Time between still captures.  Default (And minimum) is ~2.5 seconds. Ex: -d 5',
        metavar = '5',
        required = '--cli' in sys.argv
    )

    args = parser.parse_args()

    return args

def streamCap(url,outputfile,path):
    today = datetime.datetime.now()
    timestamp = today.strftime('%Y-%m-%d_%H-%M-%S')
    stream = ffmpeg.input(url, ss = 0)
    capture = stream.output(path + outputfile + timestamp + '.jpg', vframes = 1, loglevel = 'panic')
    capture.run(capture_stdout = True, capture_stderr = True)

def compileImages(outputfile,path):
    load = ffmpeg.input(path + outputfile + '*.jpg', pattern_type = 'glob', framerate = 15)
    combine = load.output(path + outputfile + '.mp4')
    combine.run(capture_stdout = True, capture_stderr = True)
    print('Compiled', outputfile + '.mp4')

def cleanupDir(outputfile,path):
    filelist = glob.glob(path + outputfile + '*.jpg')
    for filename in filelist:
        try:
            os.remove(filename)
        except:
            print('Error while deleting file: ', filename)
    print('Cleaned up working directory')

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
    else:
        if timeobj >= startobj:
            return True
        elif timeobj < endobj:
            return True
        else:
            return False

args = parseArgs()

if args.cli == 1:
    url = args.url
    outputfile = args.outputfile
    path = args.path
    capturestart = args.capturestart
    captureend = args.captureend
    delay = float(args.delay) - float(2.5)
else:
    from config import *
    delay = float(delay) - float(2.5)
    
if delay < 0:
    print('Delay less than 2.5, setting to default.')
    delay = 0
if not os.path.isdir(path):
    print('Specified path not found')
    sys.exit()

wait = True

print('Beginning job...')
print('Captures start at', capturestart)
print('Captures end at', captureend)
while True:
    while True:
        result = timeLogic(capturestart,captureend)
        if result:
            wait = False
            try:
                streamCap(url,outputfile,path)
                time.sleep(delay)
            except ffmpeg.Error as e:
                print(e.stderr.decode('utf8'))
                raise e
        else:
            break
    if wait == False:
        try:
            compileImages(outputfile,path)
            cleanupDir(outputfile,path)
            wait = True
            time.sleep(5)
        except ffmpeg.Error as e:
            print(e.stderr.decode('utf8'))
            raise e
    else:
        time.sleep(5)
