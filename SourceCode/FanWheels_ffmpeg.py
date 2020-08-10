#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imageio_ffmpeg
import subprocess


def time2second(time_str):
    hour = int(time_str[:-9])
    minute = int(time_str[-8:-6])
    second = int(time_str[-5:-3])
    msecond = int(time_str[-2:])
    return (hour * 3600) + (minute * 60) + second + (msecond / 1000)


def ffcmd(args="", console=None, task=0):
    ffpath = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = ffpath + " " + args
    print("ffmpeg:", cmd)

    duration = None
    progress = 0
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", shell=True,
                               universal_newlines=True)
    for line in process.stdout:
        input_index = line.find("Input")  # "Duration" in file name
        if duration is None:
            duration_index = line.find("Duration:")
            if input_index == -1 and duration_index != -1:
                duration_time = line.split(": ")[1].split(",")[0]
                duration = time2second(duration_time)
        else:
            time_index = line.find("time=")
            if input_index == -1 and time_index != -1:
                now_time = line.split("time=")[1].split(" ")[0]
                if duration > 0:
                    progress = time2second(now_time) / duration
                    print("Progress: " + str(round(progress * 100)) + "%")
        if console is not None:
            try:
                if task == 1:
                    console.prepare = progress
                elif task == 2:
                    console.combine = progress
                if not console.parent.fb.isRunning:
                    print("terminate!!!")
                    process.kill()
                    break
            except:
                pass

    print("ffmpeg: Done!")


def toTempWaveFile(file_in, file_out, console=None):
    cmd = '-i \"{0}\" -ar 44100 -ac 1 -filter:a loudnorm -y \"{1}\"'.format(file_in, file_out)
    ffcmd(cmd, console, task=1)


def combineVideo(video, audio, file_out, audio_quality="320k", normal=False, console=None):
    cmd = '-i \"{0}\" -itsoffset 0.0 -i \"{1}\" '.format(video, audio)
    cmd += '-map 0:v:0 -c:v copy -map 1:a:0 -b:a {0} -c:a aac '.format(audio_quality)
    if normal:
        cmd += '-filter:a loudnorm '
    cmd += '-metadata description=\"Rendered by Fanseline Visualizer\" '
    cmd += '-y \"{0}\"'.format(file_out)
    ffcmd(cmd, console, task=2)


def cvtFileName(path, new_format=None):
    if new_format is None:
        return path
    last_dot = 0
    for i in range(len(path)):
        if path[i] == ".":
            last_dot = i
    ftype = path[last_dot + 1:]
    if new_format[0] == ".":
        pass
    else:
        new_format = "." + new_format
    if "/" in ftype or "\\" in ftype:
        outpath = path + new_format
    else:
        outpath = path[:last_dot] + new_format
    return outpath


if __name__ == '__main__':
    ffcmd("-version")
