import imageio_ffmpeg
import subprocess


def ffcmd(args=""):
    ffpath = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = ffpath + " " + args
    print("ffmpeg: ", cmd)

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as p:
        output, errors = p.communicate()
        lines = output.decode('utf-8').splitlines()
        if len(lines) != 0:
            print(lines)
    print("ffmpeg: Done!")


def toTempWaveFile(file_in, file_out):
    cmd = '-i \"{0}\" -ar 44100 -ac 1 -y \"{1}\"'.format(file_in, file_out)
    ffcmd(cmd)


def combineVideo(video, audio, file_out, audio_quality="320k", normal=False):
    cmd1 = '-i \"{0}\" -itsoffset 0.25 -i \"{1}\" '.format(video, audio)
    if not normal:
        cmd2 = '-map 0 -c:v copy -map 1 -b:a {0} -c:a aac -y \"{1}\"'.format(audio_quality, file_out)
    else:
        cmd2 = '-map 0 -c:v copy -map 1 -b:a {0} -c:a aac -filter:a loudnorm -y \"{1}\"'.format(audio_quality, file_out)
    cmd = cmd1 + cmd2
    ffcmd(cmd)


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
    # ffcmd("-version")
    print(cvtFileName("C:/text/xxx.mp4", "mov"))
