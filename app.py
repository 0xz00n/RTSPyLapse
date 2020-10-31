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
        type = bool,
        help = 'Encoder to use for mp4 creation, uses system default if unspecified.  Ex: -e h264_omx',
        metavar = '',
        required = False
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    return args

def streamCap(url,outputfile,path):
    today = datetime.datetime.now()
    timestamp = today.strftime('%Y-%m-%d_%H-%M-%S')
    stream = ffmpeg.input(url, ss = 0)
    capture = stream.output(path + outputfile + timestamp + '.jpg', vframes = 1)
    capture.run(capture_stdout = True, capture_stderr = True)

def compileImages(outputfile,path,frames,encoder=None):
    today = datetime.datetime.now()
    timestamp = today.strftime('_%Y-%m-%d')
    load = ffmpeg.input(path + outputfile + '*.jpg', pattern_type = 'glob', framerate = frames)
    filename = path + outputfile + timestamp + '.mp4'
    if os.path.isfile(filename):
        if os.stat(filename).st_size == 0:
            print('Detected empty mp4, probably from bad encoder.  Deleting.')
            os.remove(filename)
        else:
            shutil.move(filename, filename + '.old' + timestamp)
    if not encoder == None:
        combine = load.output(path + outputfile + timestamp + '.mp4', **{'c:v': encoder})
    else:
        combine = load.output(path + outputfile + timestamp + '.mp4')
    combine.run(capture_stdout = True, capture_stderr = True)
    print('Compiled', filename)

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
while True:
    while True:
        result = timeLogic(capturestart,captureend)
        if result:
            wait = False
            try:
                streamCap(url,outputfile,path)
                time.sleep(delay)
            except ffmpeg.Error as e:
                error = e.stderr.decode('utf8')
                failLogic(error,url,outputfile,path)
        else:
            break
    if wait == False:
        try:
            compileImages(outputfile,path,framerate,encoder)
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
