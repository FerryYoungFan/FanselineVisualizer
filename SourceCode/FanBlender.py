from FanWheels_PIL import *
from FanWheels_ffmpeg import *
from FanAudioVisualizer import AudioVisualizer, AudioAnalyzer

import imageio
import imageio_ffmpeg
import numpy as np

import threading, time, os

"""
Audio Visualizer
By Twitter @FanKetchup

Require:

Python 3.7	    V 3.7.4

numpy		    V 1.19.0
Pillow		    V 7.2.0
imageio		    V 2.9.0
imageio-ffmpeg	V 0.4.2
pydub		    V0.24.1*
(* No need to install ffmpeg for pydub, since it shares ffmpeg with imageio-ffmpeg.)

"""

__version__ = "1.0.5"

class blendingThread(threading.Thread):
    def __init__(self, threadID, name, counter, parent):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.parent = parent

    def run(self):
        while self.parent.frame_pt < self.parent.total_frames and self.parent.isRunning:
            self.parent.frame_buffer.append(
                self.parent.visualizer.getFrame(
                    self.parent.analyzer.getHistAtFrame(self.parent.frame_pt, self.parent.fq_low, self.parent.fq_up,
                                                        self.parent.bins), self.parent._amplify,
                    self.parent.spectrum_color))
            self.parent.frame_pt = self.parent.frame_pt + 1


class encodingThread(threading.Thread):
    def __init__(self, threadID, name, counter, parent):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.parent = parent

    def run(self):
        while self.parent.encoder_pt < self.parent.total_frames and self.parent.isRunning:
            if len(self.parent.frame_buffer) > 0:
                self.parent.encoder_pt = self.parent.encoder_pt + 1
                self.parent.writer.append_data(np.asarray(self.parent.frame_buffer.pop(0)))
            else:
                self.parent.log("Processing:{0}/{1}".format(self.parent.encoder_pt, self.parent.total_frames))
                self.parent.progress(self.parent.encoder_pt,self.parent.total_frames)
                time.sleep(3.0)
        self.parent.log("Processing:{0}/{1}".format(self.parent.encoder_pt, self.parent.total_frames))
        self.parent.progress(self.parent.encoder_pt, self.parent.total_frames)
        if self.parent.encoder_pt >= self.parent.total_frames:
            self.parent.log("Blending Done!")


class FanBlender:
    def __init__(self):
        self.color_dic = {
            "Rainbow 4x": "color4x",
            "Rainbow 2x": "color2x",
            "Rainbow 1x": "color1x",
            "White": "white",
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
        self.sound_path = None
        self.logo_path = None
        self.output_path = None

        self.text_bottom = ""
        self.font = "./Source/font.otf"
        self.font_alpha = 0.85

        self.frame_width = 540
        self.frame_height = 540
        self.fps = 30
        self.bit_rate = 0.6  # in Mb/s
        self.audio_bit_rate = 320  # in kb/s
        self.audio_normal = False

        self.spectrum_color = "color4x"
        self.bins = 80
        self.fq_low = 20
        self.fq_up = 1500
        self.scalar = 1.0

        self._debug_bg = False
        self._temp_audio_path = r"./Temp/temp.wav"
        self._temp_video_path = r"./Temp/temp.mp4"
        self.ensure_dir(self._temp_audio_path)

        self._ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        self._frame_size = min(self.frame_width, self.frame_height)
        self._font_size = int(round(30 / 1080 * self._frame_size))  # A good ratio for text and frame size
        self._blur = int(round(2 / 1080 * self._frame_size))
        self._blur_bg = int(round(41 / 1080 * self._frame_size))
        self._line_thick = int(round(4 / 1080 * self._frame_size))
        self._amplify = self.scalar * 3 / 80 * self.bins * np.power(1500 / (self.fq_up - self.fq_low), 0.5)

        self.visualizer = None
        self.analyzer = None

        self.writer = None
        self.total_frames = None
        self.frame_buffer = []
        self.frame_pt = 0
        self.encoder_pt = 0

        self.isRunning = False
        self._console=None

    def ensure_dir(self,file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)


    def fileError(self, filepath):
        if filepath is not None:
            self.log("Error: File {0} does not exist.".format(filepath))

    def setConsole(self,console=None):
        if console:
            self._console = console

    def log(self,content=""):
        print(content)
        if self._console:
            try:
                self._console.log(content)
            except:
                pass

    def progress(self,value,total):
        if self._console:
            try:
                self._console.progressbar(value,total)
            except:
                return

    def freezeConsole(self,flag=True):
        if self._console:
            try:
                self._console.freeze(flag)
            except:
                return

    def setFilePath(self, image_path=None, sound_path=None, logo_path=None):
        if image_path is not None:
            if os.path.isfile(image_path):
                self.image_path = image_path
            else:
                self.logo_path = None
                self.fileError(image_path)

        if sound_path is not None:
            if os.path.isfile(sound_path):
                self.sound_path = sound_path
            else:
                self.fileError(sound_path)

        if logo_path is not None:
            if os.path.isfile(logo_path):
                self.logo_path = logo_path
            else:
                self.logo_path = None
                self.fileError(logo_path)

    def setOutputPath(self, output_path=None, filename=None):
        if filename is None:
            filename = "Visualize.mp4"
        if output_path is not None:
            self.ensure_dir(os.path.join(output_path, filename))
            self.output_path = os.path.join(output_path, filename)

    def setText(self, text="", font=None, font_alpha=0.85):
        self.text_bottom = text
        if font is None or (not os.path.exists(font)):
            if os.path.exists("./Source/font.otf"):
                font = "./Source/font.otf"
            elif os.path.exists("./Source/font.ttf"):
                font = "./Source/font.ttf"
            else: font = "Arial.ttf"
        self.font = font
        self.font_alpha = font_alpha

    def setSpec(self, bins=None, lower=None, upper=None, color=None, scalar=None):
        if bins is not None:
            if bins < 2:
                bins = 2
            elif bins > 250:
                bins = 250
            self.bins = int(bins)

        if lower is not None:
            if lower > 22000:
                lower = 22000
            elif lower < 16:
                lower = 16
            self.fq_low = int(lower)

        if upper is not None:
            if upper > 22000:
                upper = 22000
            elif upper < 16:
                upper = 16
            if upper < self.fq_low:
                upper = self.fq_low
            self.fq_up = int(upper)

        if color is not None:
            self.spectrum_color = color

        if scalar is not None:
            if scalar < 0.1:
                scalar = 0.1
            elif scalar > 10:
                scalar = 10
            self.scalar = scalar

        self._amplify = self.scalar * 7 / 80 * self.bins * np.power(1500 / (self.fq_up - self.fq_low), 0.5)
        self.visualizer = None

    def getSpec(self):
        info_dic = {
            "Sections": self.bins,
            "Lower Frequency": self.fq_low,
            "Upper Frequency": self.fq_up,
            "Color": self.spectrum_color,
            "Scalar":self.scalar
        }
        return info_dic

    def setVideoInfo(self, width=None, height=None, fps=None, br_Mbps=None):
        minwidth = 16
        if width is not None:
            if width < minwidth:
                width = minwidth
            self.frame_width = int(width)
        if height is not None:
            if height < minwidth:
                height = minwidth
            self.frame_height = int(height)
        if fps is not None:
            if fps < 1:
                fps = 1
            self.fps = int(fps)
        if br_Mbps is None:
            br_Mbps = 15 * (self.frame_width * self.frame_height * self.fps) / (1920 * 1080 * 30)
            self.bit_rate = br_Mbps
        else:
            if br_Mbps < 0.01:
                br_Mbps = 0.01
            self.bit_rate = br_Mbps

        self._frame_size = min(self.frame_width, self.frame_height)
        self._font_size = int(round(30 / 1080 * self._frame_size))  # A good ratio for text and frame size
        self._blur = int(round(2 / 1080 * self._frame_size))
        self._blur_bg = int(round(41 / 1080 * self._frame_size))
        self._line_thick = int(round(4 / 1080 * self._frame_size))

        self.visualizer = None

    def getVideoInfo(self):
        info_dic = {
            "width": self.frame_width,
            "height": self.frame_height,
            "FPS": self.fps,
            "bit-rate": self.bit_rate
        }
        return info_dic

    def setAudioInfo(self,normal=None, br_kbps=None):
        if normal is not None:
            self.audio_normal = normal

        if br_kbps is not None:
            if br_kbps < 5:
                br_kbps = 5
            self.audio_bit_rate = int(round(br_kbps))

    def getAudioBitRate(self):
        return self.audio_bit_rate

    def genBackground(self):
        image = None
        try:
            image = Image.open(self.image_path)

        except:
            self.fileError(self.image_path)

        if not image:
            try:
                image = Image.open("./Source/fallback.png")
            except:
                self.fileError("./Source/fallback.png")

        if not image:
            try:
                image = Image.open("./Source/fallback.jpg")
            except:
                self.fileError("./Source/fallback.jpg")
                image = Image.new('RGB', (512, 512), (127, 127, 127))

        self.log("Blending Background...")
        try:
            fimage = Image.new('RGB', image.size, (64,64,64))
            fimage.paste(image,(0,0),image)
            if fimage:
                image = fimage
        except:
            pass

        try:
            logofile = Image.open(self.logo_path)
        except:
            self.fileError(self.logo_path)
            logofile = None

        foreground = cropCircle(image, size=self._frame_size // 2)
        background = genBG(image, size=(self.frame_width, self.frame_height), blur=self._blur_bg, bright=0.3)
        background = pasteMiddle(foreground, background, True)
        background = glowText(background, self.text_bottom, self._font_size, self.font, alpha=self.font_alpha, blur=self._blur,
                              logo=logofile)
        self.visualizer = AudioVisualizer(background, self._frame_size / 4 * 1.1,
                                          self._frame_size / 2 - self._font_size * 2.5, self._line_thick,
                                          self._blur)
        self.log("Blending Background... Done!")

    def previewBackground(self):
        self.genBackground()
        xs = np.linspace(0, self.bins / 3 * np.pi, self.bins)
        ys = 0.5 + 0.6 * np.cos(xs)
        frame_sample = self.visualizer.getFrame(ys, 1, self.spectrum_color)
        frame_sample.show()

    def genAnalyzer(self):
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
        self.freezeConsole(True)
        self.genBackground()
        self.genAnalyzer()
        self.isRunning = True

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

        self.writer = imageio.get_writer(self._temp_video_path, fps=self.fps, macro_block_size=None,
                                         bitrate=int(self.bit_rate * 1000000))
        self.total_frames = self.analyzer.getTotalFrames()
        self.frame_buffer = []
        self.frame_pt = 0
        self.encoder_pt = 0

        thread_encode = encodingThread(1, "Thread-1", 1, self)
        thread_stack = []
        thread_num = 7
        for ith in range(thread_num):
            thread_stack.append(blendingThread(ith + 2, "Thread-" + str(ith + 2), ith + 2, self))
        thread_encode.start()
        for ith in range(thread_num):
            thread_stack[ith].start()
        thread_encode.join()
        for ith in range(thread_num):
            thread_stack[ith].join()
        self.writer.close()
        if self.isRunning:
            self.log("Output path: " + self.output_path)
            self.log("Combining Videos...")
            audio_br = str(self.audio_bit_rate) + "k"
            combineVideo(self._temp_video_path, self.sound_path, self.output_path, audio_br,self.audio_normal)
            self.log("Combining Videos... Done!")
        else:
            self.log("Blending Aborted!")

        self.removeTemp()
        self.freezeConsole(False)
        self.isRunning = False

    def removeTemp(self):
        def removeFile(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        removeFile(self._temp_audio_path)
        removeFile(self._temp_video_path)


if __name__ == '__main__':
    # Example of using FanBlender

    fb = FanBlender() #  the blender
    fb.setFilePath(image_path=r"./Source/fallback.png",
                   sound_path=r"./Source/test.mp3",
                   logo_path=r"./Source/logo.png") # Set File Path
    fb.setOutputPath(output_path=r"./Output",
                     filename="test.mp4") # Set Output Path
    fb.setText(text="Your Text Here", font="./Source/font.otf") # Set text at the bottom
    fb.setSpec(bins=80, lower=20, upper=1500,
               color=fb.color_dic["Gradient: Green - Blue"],scalar=1.0) # Set Spectrum Style
    fb.setVideoInfo(width=520, height=520, fps=30, br_Mbps=5) # Video info
    fb.previewBackground() # Preview before blending
    fb.setAudioInfo(normal=False, br_kbps=192) # Audio info
    fb.runBlending() # Blend the Video
