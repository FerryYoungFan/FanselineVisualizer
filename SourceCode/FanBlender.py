#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fanseline Audio Visualizer
帆室邻音频可视化视频制作工具
By Twitter @FanKetchup
https://github.com/FerryYoungFan/FanselineVisualizer
"""

__version__ = "1.1.3"  # Work with PYQT5

from FanWheels_PIL import *
from FanWheels_ffmpeg import *
from FanAudioVisualizer import AudioVisualizer, AudioAnalyzer

import imageio
import imageio_ffmpeg
import numpy as np

import threading, os, sys
from PyQt5 import QtCore  # Notice: You can use time.sleep() if you are not using PyQt5


class blendingThread(threading.Thread):
    def __init__(self, threadID, name, counter, parent, total_thread, thread_num):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.parent = parent
        self.total_thread = total_thread
        self.thread_num = thread_num
        self.frame_pt = thread_num

    def run(self):
        while self.frame_pt < self.parent.total_frames and self.parent.isRunning:
            self.parent.frame_lock[self.frame_pt] = self.thread_num + 1
            self.parent.frame_buffer[self.frame_pt] = self.parent.visualizer.getFrame(
                hist=self.parent.analyzer.getHistAtFrame(self.frame_pt, self.parent.fq_low,
                                                         self.parent.fq_up, self.parent.bins, self.parent.smooth),
                amplify=self.parent._amplify,
                color_mode=self.parent.spectrum_color,
                bright=self.parent._bright,
                saturation=self.parent._saturation,
                use_glow=self.parent.use_glow,
                rotate=self.parent.rotate,
                fps=self.parent.fps,
                frame_pt=self.frame_pt,
                bg_mode=self.parent.bg_mode,
                fg_img=self.parent.fg_img)
            self.frame_pt = self.frame_pt + self.total_thread
        print("Thread {0} -end".format(self.thread_num))


class encodingThread(threading.Thread):
    def __init__(self, threadID, name, counter, parent):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.parent = parent

    def run(self):
        realTimePrev = None
        while self.parent.encoder_pt < self.parent.total_frames and self.parent.isRunning:
            if self.parent.frame_buffer[self.parent.encoder_pt] is not None:
                self.parent.writer.append_data(np.asarray(self.parent.frame_buffer[self.parent.encoder_pt]))
                realTimePrev = self.parent.frame_buffer[self.parent.encoder_pt]
                self.parent.frame_buffer[self.parent.encoder_pt] = None
                self.parent.encoder_pt = self.parent.encoder_pt + 1
            else:
                if realTimePrev:
                    self.parent.previewRealTime(realTimePrev)
                    realTimePrev = None
                self.parent.log("Processing:{0}/{1}".format(self.parent.encoder_pt, self.parent.total_frames))
                self.parent.progress(self.parent.encoder_pt, self.parent.total_frames)

                # The following 3 lines can be replaced by time.sleep(0.5) if you are not using PyQt5
                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(500, loop.quit)
                loop.exec_()

        self.parent.previewRealTime(realTimePrev)
        realTimePrev = None
        self.parent.log("Processing:{0}/{1}".format(self.parent.encoder_pt, self.parent.total_frames))
        self.parent.progress(self.parent.encoder_pt, self.parent.total_frames)
        if self.parent.encoder_pt >= self.parent.total_frames:
            self.parent.log("Rendering Done!")


class FanBlender:
    def __init__(self):
        self.color_dic = {
            "Rainbow 4x": "color4x",
            "Rainbow 2x": "color2x",
            "Rainbow 1x": "color1x",
            "White": "white",
            "Black": "black",
            "Gray": "gray",
            "Red": "red",
            "Green": "green",
            "Blue": "blue",
            "Yellow": "yellow",
            "Magenta": "magenta",
            "Purple": "purple",
            "Cyan": "cyan",
            "Light Green": "lightgreen",
            "Gradient: Green - Blue": "green-blue",
            "Gradient: Magenta - Purple": "magenta-purple",
            "Gradient: Red - Yellow": "red-yellow",
            "Gradient: Yellow - Green": "yellow-green",
            "Gradient: Blue - Purple": "blue-purple",
        }
        self.image_path = None
        self.bg_path = None
        self.sound_path = None
        self.logo_path = None
        self.output_path = None
        self.bg_img = None
        self.logofile = None

        self.text_bottom = ""
        self.font = getPath("Source/font.otf")

        self.frame_width = 540
        self.frame_height = 540
        self.fps = 30
        self.bit_rate = 0.6  # in Mb/s
        self.audio_bit_rate = 320  # in kb/s
        self.audio_normal = False

        self.spectrum_color = "color4x"
        self._bright = 1.0
        self._saturation = 1.0
        self.bins = 80
        self.smooth = 0
        self.fq_low = 20
        self.fq_up = 1500
        self.scalar = 1.0

        self._debug_bg = False
        self._temp_audio_path = getPath("Temp/temp.wav")
        self._temp_video_path = getPath("Temp/temp.mp4")
        self.ensure_dir(self._temp_audio_path)

        try:
            self._ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        except:
            self._ffmpeg_path = None

        self._frame_size = 0
        self._relsize = 1.0
        self._font_size = 0
        self._text_color = (0, 0, 0, 0)
        self._text_glow = False
        self._yoffset = 0
        # A good ratio for text and frame size

        self._blur = 0
        self._blur_bg = 0
        self.blur_bg = True
        self.use_glow = False
        self.style = 0
        self.linewidth = 1.0
        self.rotate = 0
        self._line_thick = 0

        self._amplify = self.setAmplify()

        self.visualizer = None
        self.analyzer = None
        self.fg_img = None

        self.writer = None
        self.total_frames = None
        self.frame_buffer = []
        self.frame_pt = 0
        self.encoder_pt = 0

        self.isRunning = False
        self._console = None

        self.frame_lock = None

        self.bg_mode = 0
        self.bg_blended = False
        self.ffmpegCheck()

    def calcRel(self):
        self._frame_size = min(self.frame_width, self.frame_height)
        self._font_size = int(round(30 / 1080 * self._frame_size * self._relsize))
        self._blur = int(round(2 / 1080 * self._frame_size))
        self._blur_bg = int(round(41 / 1080 * self._frame_size))
        self._line_thick = self.linewidth * 4 / 1080 * self._frame_size
        self._yoffset = clip(self.frame_height - self._font_size * 2.1, self.frame_height * 0.95,
                             self.frame_height * 0.95 - self._font_size)

    def ffmpegCheck(self):
        if self._ffmpeg_path is None:
            self.log("Error: FFMPEG not found!")
            if self._console:
                try:
                    self._console.ffmpegWarning()
                except:
                    pass
            return False
        else:
            return True

    def setAmplify(self):
        return self.scalar * 5 * np.sqrt(self.bins / 80) * np.power(1500 / (self.fq_up - self.fq_low), 0.5)

    def ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def fileError(self, filepath):
        if filepath is not None:
            self.log("Error: File {0} does not exist.".format(filepath))

    def setConsole(self, console=None):
        if console:
            self._console = console

    def audioError(self):
        if self._console:
            try:
                self._console.audioWarning()
            except:
                pass

    def log(self, content=""):
        print(content)
        if self._console:
            try:
                self._console.log(content)
            except:
                pass

    def progress(self, value, total):
        if self._console:
            try:
                self._console.progressbar(value, total)
            except:
                return

    def freezeConsole(self, flag=True):
        if self._console:
            try:
                self._console.freeze(flag)
            except:
                return

    def setFilePath(self, image_path=None, bg_path=None, sound_path=None, logo_path=None):
        self.image_path = self.imgFileCheck(image_path)
        self.bg_path = self.imgFileCheck(bg_path)
        self.logo_path = self.imgFileCheck(logo_path)

        if sound_path is not None:
            if os.path.isfile(sound_path):
                self.sound_path = sound_path
            else:
                self.fileError(sound_path)

    def imgFileCheck(self, file_path):
        if file_path is None:
            return None
        if isinstance(file_path, tuple) and (len(file_path) in [3, 4]):
            self.visualizer = None
            self.bg_blended = False
            if len(file_path) == 3:
                return file_path + (255,)
            return file_path  # RGBA Color Tuple
        if os.path.isfile(file_path):
            self.visualizer = None
            self.bg_blended = False
            return file_path
        return None

    def setOutputPath(self, output_path="", filename=""):
        if not filename:
            filename = "Visualize.mp4"
        if output_path:
            self.ensure_dir(os.path.join(output_path, filename))
            self.output_path = cvtFileName(os.path.join(output_path, filename), "mp4")

    def setText(self, text="", font="", relsize=None, text_color=(255, 255, 255, 255), text_glow=None):
        self.text_bottom = text
        if not font:
            if os.path.exists(getPath("Source/font.otf")):
                font = getPath("Source/font.otf")
            elif os.path.exists(getPath("Source/font.ttf")):
                font = getPath("Source/font.ttf")
            else:
                font = "Arial.ttf"
        if relsize is not None:
            self._relsize = clip(relsize, 0.1, 5)
        if text_color is not None:
            self._text_color = text_color
        if text_glow is not None:
            self._text_glow = text_glow
        self.font = font

    def setSpec(self, bins=None, lower=None, upper=None, color=None, bright=None, saturation=None, scalar=None,
                smooth=None, style=None, linewidth=None):
        if bins is not None:
            self.bins = int(clip(bins, 2, 250))

        if lower is not None:
            self.fq_low = int(clip(lower, 16, 22000))

        if upper is not None:
            upper = int(clip(upper, 16, 22000))
            if upper <= self.fq_low:
                upper = self.fq_low + 1
            self.fq_up = int(upper)

        if color is not None:
            self.spectrum_color = color

        if bright is not None:
            self._bright = clip(bright, 0, 1)

        if saturation is not None:
            self._saturation = clip(saturation, 0, 1)

        if scalar is not None:
            self.scalar = clip(scalar, 0.1, 10)

        if smooth is not None:
            self.smooth = int(round(clip(smooth, 0, 15)))

        if style is not None:
            self.style = style

        if linewidth is not None:
            self.linewidth = clip(linewidth, 0.01, 50)

        self._amplify = self.setAmplify()
        self.visualizer = None

    def setVideoInfo(self, width=None, height=None, fps=None, br_Mbps=None, blur_bg=None, use_glow=None, bg_mode=None,
                     rotate=None):
        if width is not None:
            self.frame_width = int(clip(width, 16, 4096))
        if height is not None:
            self.frame_height = int(clip(height, 16, 4096))
        if fps is not None:
            self.fps = int(clip(fps, 1, 120))
        if br_Mbps is None:
            br_Mbps = 15 * (self.frame_width * self.frame_height * self.fps) / (1920 * 1080 * 30)
            self.bit_rate = br_Mbps
        else:
            self.bit_rate = clip(br_Mbps, 0.01, 200)

        if blur_bg is not None:
            self.blur_bg = blur_bg

        if use_glow is not None:
            self.use_glow = use_glow

        if bg_mode is not None:
            self.bg_mode = bg_mode

        if rotate is not None:
            self.rotate = float(rotate)

        self.visualizer = None
        self.bg_blended = False

    def setAudioInfo(self, normal=None, br_kbps=None):
        if normal is not None:
            self.audio_normal = normal

        if br_kbps is not None:
            self.audio_bit_rate = int(round(clip(br_kbps, 5, 10000)))

    def genBackground(self, forceRefresh=False):
        self.calcRel()
        if not self.bg_blended or forceRefresh:
            self.log("Rendering Background...")

            image = openImage(self.image_path, "RGBA", ["Source/fallback.png", "Source/fallback.jpg", (127, 127, 127)])
            bg = openImage(self.bg_path, "RGB", [None])
            self.logofile = openImage(self.logo_path, "RGBA", [None])
            try:
                fimage = Image.new('RGB', image.size, (65, 65, 65))
                fimage.paste(image, (0, 0), image)
                if fimage:
                    image = fimage
            except:
                pass

            foreground = cropCircle(image, size=self._frame_size // 2)
            self.fg_img = foreground

            if bg is None:
                bg = image.copy()

            if self.bg_mode < 0:
                background = Image.new("RGBA", (self.frame_width, self.frame_height), (0, 0, 0, 0))
            else:
                if self.blur_bg:
                    background = genBG(bg, size=(self.frame_width, self.frame_height), blur=self._blur_bg, bright=0.3)
                else:
                    background = genBG(bg, size=(self.frame_width, self.frame_height), blur=0, bright=1.0)
            self.bg_img = background
            self.log("Rendering Background... Done!")

        background = self.bg_img.copy()
        if self.bg_mode >= -1 and not self.bg_mode == 2:
            if self.rotate == 0:
                background = pasteMiddle(self.fg_img, background, glow=self.use_glow, blur=self._blur * 2,
                                         bright=self._bright)

        background = glowText(background, self.text_bottom, self._font_size, self.font, color=self._text_color,
                              blur=self._blur, logo=self.logofile, use_glow=self._text_glow, yoffset=self._yoffset)

        rad_max = (self._yoffset - self.frame_height / 2) * 0.97
        if self.text_bottom is None or self.text_bottom == "":
            if self.logo_path is None or not os.path.exists(self.logo_path):
                rad_max = self.frame_height / 2
        self.visualizer = AudioVisualizer(img=background,
                                          rad_min=self._frame_size / 4 * 1.1,
                                          rad_max=min(rad_max, self._frame_size / 2.1),
                                          line_thick=self._line_thick,
                                          blur=self._blur, style=self.style)
        self.bg_blended = True

    def previewBackground(self, localViewer=False, forceRefresh=False):
        self.genBackground(forceRefresh)
        xs = np.linspace(0, 10 * np.pi, self.bins)
        ys = (0.5 + 0.5 * np.cos(xs)) * self.scalar
        frame_sample = self.visualizer.getFrame(hist=ys, amplify=1, color_mode=self.spectrum_color, bright=self._bright,
                                                saturation=self._saturation, use_glow=self.use_glow, rotate=self.rotate,
                                                fps=30, frame_pt=90, fg_img=self.fg_img, bg_mode=self.bg_mode)
        if localViewer:
            frame_sample.show()
        return frame_sample

    def previewRealTime(self, img):
        if self._console:
            try:
                self._console.realTime(img)
            except:
                return

    def genAnalyzer(self):
        if not self.ffmpegCheck():
            return
        if self.sound_path is None or not os.path.exists(str(self.sound_path)):
            self.log("Error: Audio file not found!")
            return
        try:
            toTempWaveFile(self.sound_path, self._temp_audio_path)
        except:
            self.fileError(self.sound_path)
            self.analyzer = None
            return
        try:
            self.analyzer = AudioAnalyzer(self._temp_audio_path, self._ffmpeg_path, self.fps)
        except:
            self.fileError(self._temp_audio_path)
            self.analyzer = None
            return

    def runBlending(self):
        if self.isRunning:
            return
        self.removeTemp()
        self.freezeConsole(True)
        self.genBackground(forceRefresh=True)
        if not self.ffmpegCheck():
            self.freezeConsole(False)
            return
        self.isRunning = True
        self.genAnalyzer()
        if self._temp_audio_path is None or not os.path.exists(str(self._temp_audio_path)):
            self.freezeConsole(False)
            self.audioError()
            self.isRunning = False
            return

        if self.analyzer is None:
            self.log("Error: Analyzer not found")
            self.isRunning = False
            self.freezeConsole(False)
            return
        if self.visualizer is None:
            self.log("Error: Visualizer not found")
            self.isRunning = False
            self.freezeConsole(False)
            return

        if self.bg_mode < 0:
            self.writer = imageio.get_writer(cvtFileName(self._temp_video_path, "mov"),
                                             fps=self.fps,
                                             macro_block_size=None,
                                             format='FFMPEG', codec="png", pixelformat="rgba")
        else:
            self.writer = imageio.get_writer(self._temp_video_path, fps=self.fps, macro_block_size=None,
                                             bitrate=int(self.bit_rate * 1000000))
        self.total_frames = self.analyzer.getTotalFrames()
        self.frame_buffer = [None] * self.total_frames
        self.encoder_pt = 0

        thread_encode = encodingThread(1, "Thread-1", 1, self)
        thread_stack = []
        thread_num = 4
        cpu_count = os.cpu_count()
        if cpu_count is not None:
            thread_num = cpu_count // 2
        if thread_num < 2:
            thread_num = 2

        print("CPU Thread for Rendering: " + str(thread_num))

        self.frame_lock = np.zeros(self.total_frames, dtype=np.uint8)

        for ith in range(thread_num):
            thread_stack.append(blendingThread(ith + 2, "Thread-" + str(ith + 2), ith + 2, self, thread_num, ith))
        thread_encode.start()
        for ith in range(thread_num):
            thread_stack[ith].start()
        thread_encode.join()
        for ith in range(thread_num):
            thread_stack[ith].join()
        self.writer.close()
        if self.isRunning:
            self.log("Output path: ")
            self.log(str(self.output_path))
            self.log("Combining Videos...")
            audio_br = str(self.audio_bit_rate) + "k"
            if self.bg_mode < 0:
                combineVideo(cvtFileName(self._temp_video_path, "mov"),
                             self.sound_path,
                             cvtFileName(self.output_path, "mov"), audio_br, self.audio_normal)
            else:
                combineVideo(self._temp_video_path, self.sound_path, self.output_path, audio_br, self.audio_normal)
            self.log("Combining Videos... Done!")
        else:
            self.log("Rendering Aborted!")

        self.removeTemp()
        self.freezeConsole(False)
        self.isRunning = False

    def getOutputPath(self):
        if self.bg_mode < 0:
            return cvtFileName(self.output_path, "mov")
        else:
            return cvtFileName(self.output_path, "mp4")

    def removeTemp(self):
        def removeFile(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        removeFile(self._temp_audio_path)
        removeFile(self._temp_video_path)
        removeFile(cvtFileName(self._temp_video_path, "mov"))


def clip(value, low_in=0.0, up_in=0.0):
    if value is None:
        return 0
    if low_in > up_in:
        low, up = up_in, low_in
    else:
        low, up = low_in, up_in
    if value < low:
        return low
    if value > up:
        return up
    return value


def getPath(fileName):  # for different operating systems
    path = os.path.join(os.path.dirname(sys.argv[0]), fileName)
    path = path.replace("\\", "/")
    return path


if __name__ == '__main__':
    # Example of Using FanBlender

    fb = FanBlender()  # Initialize Blender (Render)

    fb.setFilePath(image_path="Source/fallback.png",
                   bg_path="Source/background.jpg",
                   sound_path="Source/test.mp3",
                   logo_path="Source/logo.png")
    """
    Set file path.
    You can also use RGBA color as path to generate a monocolor image: e.g. image_path=(255,0,0,255)
    """

    fb.setOutputPath(output_path="./Output",
                     filename="test.mp4")  # Set Output Path

    fb.setText(text="Your Text Here", font="Source/font.otf",
               relsize=1.0, text_color=(255, 255, 255, 255), text_glow=True)
    """
    Set text at the Bottom (Relative Font Size: 0.3 - 5.0)
    Text color format: RGBA
    """

    fb.setSpec(bins=60, lower=20, upper=1500,
               color=fb.color_dic["Gradient: Green - Blue"], bright=0.6, saturation=0.8,
               scalar=1.0, smooth=2,
               style=1, linewidth=1.0)
    """
    Set Spectrum:
    bins: Number of spectrums
    lower: Lower Frequency
    upper: Upper Frequency
    color: Color of Spectrum
    bright: Brightness of Spectrum
    saturation: Color Saturation of Spectrum
    scalar: Sensitivity (Scalar) of Analyzer (Default:1.0)
    smooth: Stabilize Spectrum (Range: 0 - 15)
    style: 0-22 for Different Spectrum Styles (-1 for None)
    linewidth: Relative Width of Spectrum Line (0.5-20)
    """
    fb.setVideoInfo(width=480, height=480, fps=30.0, br_Mbps=1.0,
                    blur_bg=True, use_glow=True, bg_mode=0, rotate=1.5)
    """
    Video info
    br_Mbps: Bit Rate of Video (Mbps)
    blur_bg: Blur the background
    use_glow: Add Glow Effect to Spectrum and Text
    bg_mode: 0: Normal Background, 2: Background Only, -1: Transparent Background, -2: Spectrum Only
    rotate: Rotate Foreground (r/min, Positive for Clockwise)
    """
    fb.setAudioInfo(normal=False, br_kbps=192)  # Audio info

    fb.previewBackground(localViewer=True)  # Preview before rendering

    fb.runBlending()  # Render the video
