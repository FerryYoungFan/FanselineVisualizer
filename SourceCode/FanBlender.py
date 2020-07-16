try:
    from _CheckEnvironment import checkEnvironment

    checkEnvironment(True)
except:
    pass

from FanWheels_PIL import *
from FanWheels_ffmpeg import *
from FanAudioVisualizer import AudioVisualizer, AudioAnalyzer

import imageio
import imageio_ffmpeg
import numpy as np

import threading, time, os

__version__ = "1.0.6"

"""
Audio Visualizer
By Twitter @FanKetchup
https://github.com/FerryYoungFan/FanselineVisualizer
"""


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
                time.sleep(3.0)
        self.parent.previewRealTime(realTimePrev)
        realTimePrev = None
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

        self.text_bottom = ""
        self.font = "./Source/font.otf"

        self.frame_width = 540
        self.frame_height = 540
        self.fps = 30
        self.bit_rate = 0.6  # in Mb/s
        self.audio_bit_rate = 320  # in kb/s
        self.audio_normal = False

        self.spectrum_color = "color4x"
        self._bright = 1.0
        self.bins = 80
        self.smooth = 0
        self.fq_low = 20
        self.fq_up = 1500
        self.scalar = 1.0

        self._debug_bg = False
        self._temp_audio_path = r"./Temp/temp.wav"
        self._temp_video_path = r"./Temp/temp.mp4"
        self.ensure_dir(self._temp_audio_path)

        self._ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        self._frame_size = min(self.frame_width, self.frame_height)
        self._relsize = 1.0
        self._font_size = int(round(30 / 1080 * self._frame_size * self._relsize))
        # A good ratio for text and frame size

        self._blur = int(round(2 / 1080 * self._frame_size))
        self._blur_bg = int(round(41 / 1080 * self._frame_size))
        self.blur_bg = True
        self.use_glow = True
        self.style = 0
        self.linewidth = 1.0
        self.rotate = 0
        self._line_thick = int(round(self.linewidth * 4 / 1080 * self._frame_size))

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

    def setAmplify(self):
        return self.scalar * 7 * np.sqrt(self.bins / 80) * np.power(1500 / (self.fq_up - self.fq_low), 0.5)

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
        if image_path is not None:
            if os.path.isfile(image_path):
                self.image_path = image_path
            else:
                self.image_path = None
                self.fileError(image_path)
        else:
            self.image_path = None

        if bg_path is not None:
            if os.path.isfile(bg_path):
                self.bg_path = bg_path
            else:
                self.bg_path = None
                self.fileError(bg_path)
        else:
            self.bg_path = None

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
        else:
            self.logo_path = None

    def setOutputPath(self, output_path=None, filename=None):
        if filename is None:
            filename = "Visualize.mp4"
        if output_path is not None:
            self.ensure_dir(os.path.join(output_path, filename))
            self.output_path = cvtFileName(os.path.join(output_path, filename), "mp4")

    def setText(self, text="", font=None, relsize=None):
        self.text_bottom = text
        if font is None or (not os.path.exists(font)):
            if os.path.exists("./Source/font.otf"):
                font = "./Source/font.otf"
            elif os.path.exists("./Source/font.ttf"):
                font = "./Source/font.ttf"
            else:
                font = "Arial.ttf"
        if relsize is not None:
            if relsize < 0.3:
                relsize = 0.1
            elif relsize > 3.1:
                relsize = 3.1
            self._relsize = relsize
            self._font_size = int(round(30 / 1080 * self._frame_size * self._relsize))

        self.font = font
        self.bg_blended = False

    def setSpec(self, bins=None, lower=None, upper=None, color=None, bright=None, scalar=None, smooth=None, style=None,
                linewidth=None):
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

        if bright is not None:
            if bright < 0:
                bright = 0
            elif bright > 1:
                bright = 1
            self._bright = bright

        if scalar is not None:
            if scalar < 0.1:
                scalar = 0.1
            elif scalar > 10:
                scalar = 10
            self.scalar = scalar

        if smooth is not None:
            if smooth < 0:
                smooth = 0
            elif smooth > 10:
                smooth = 10
            self.smooth = int(round(smooth))

        if style is not None:
            self.style = style

        if linewidth is not None:
            if linewidth > 50:
                linewidth = 50
            elif linewidth < 0.01:
                linewidth = 0.01
            self.linewidth = float(linewidth)

        self._amplify = self.setAmplify()
        self._line_thick = self.linewidth * 4 / 1080 * self._frame_size
        self.visualizer = None
        self.bg_blended = False

    def setVideoInfo(self, width=None, height=None, fps=None, br_Mbps=None, blur_bg=None, use_glow=None, bg_mode=None,
                     rotate=None):
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

        if blur_bg is not None:
            self.blur_bg = blur_bg

        if use_glow is not None:
            self.use_glow = use_glow

        if bg_mode is not None:
            self.bg_mode = bg_mode

        if rotate is not None:
            self.rotate = float(rotate)

        self._frame_size = min(self.frame_width, self.frame_height)
        self._font_size = int(round(30 / 1080 * self._frame_size * self._relsize))
        self._blur = int(round(2 / 1080 * self._frame_size))
        self._blur_bg = int(round(41 / 1080 * self._frame_size))
        self._line_thick = int(round(self.linewidth * 4 / 1080 * self._frame_size))

        self.visualizer = None
        self.bg_blended = False

    def setAudioInfo(self, normal=None, br_kbps=None):
        if normal is not None:
            self.audio_normal = normal

        if br_kbps is not None:
            if br_kbps < 5:
                br_kbps = 5
            self.audio_bit_rate = int(round(br_kbps))

    def genBackground(self):
        if self.bg_blended:
            return
        image, bg = None, None
        try:
            image = Image.open(self.image_path).convert('RGBA')
        except:
            self.fileError(self.image_path)

        try:
            bg = Image.open(self.bg_path).convert('RGBA')
        except:
            self.fileError(self.bg_path)

        if not image:
            try:
                image = Image.open("./Source/fallback.png").convert('RGBA')
            except:
                self.fileError("./Source/fallback.png").convert('RGBA')

        if not image:
            try:
                image = Image.open("./Source/fallback.jpg").convert('RGBA')
            except:
                self.fileError("./Source/fallback.jpg")
                image = Image.new('RGB', (512, 512), (127, 127, 127))

        self.log("Blending Background...")
        try:
            fimage = Image.new('RGB', image.size, (64, 64, 64))
            fimage.paste(image, (0, 0), image)
            if fimage:
                image = fimage
        except:
            pass

        try:
            logofile = Image.open(self.logo_path).convert('RGBA')
        except:
            self.fileError(self.logo_path)
            logofile = None

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
        if self.bg_mode >= -1 and not self.bg_mode == 2:
            background = pasteMiddle(foreground, background, glow=self.use_glow, blur=self._blur * 2,
                                     bright=self._bright)
            background = glowText(background, self.text_bottom, self._font_size, self.font, bright=self._bright,
                                  blur=self._blur, logo=logofile, use_glow=self.use_glow)

        gap = self._font_size * 2
        if self.text_bottom is None or self.text_bottom == "":
            if self.logo_path is None or not os.path.exists(self.logo_path):
                gap = 0

        self.visualizer = AudioVisualizer(img=background,
                                          rad_min=self._frame_size / 4 * 1.1,
                                          rad_max=min(self.frame_height / 2 - gap, self._frame_size / 2.1),
                                          line_thick=self._line_thick,
                                          blur=self._blur, style=self.style)
        self.log("Blending Background... Done!")
        self.bg_blended = True

    def previewBackground(self, localViewer=False):
        self.genBackground()
        xs = np.linspace(0, self.bins / 3 * np.pi, self.bins)
        ys = 0.5 + 0.6 * np.cos(xs)
        frame_sample = self.visualizer.getFrame(hist=ys, amplify=1, color_mode=self.spectrum_color, bright=self._bright,
                                                use_glow=self.use_glow)
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
        self.genBackground()
        self.genAnalyzer()
        if self._temp_audio_path is None or not os.path.exists(str(self._temp_audio_path)):
            return

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
        thread_num = 7
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
            self.log("Output path: " + self.output_path)
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
            self.log("Blending Aborted!")

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


if __name__ == '__main__':
    # Example of Using FanBlender

    fb = FanBlender()  # Initialize Blender
    fb.setFilePath(image_path=r"./Source/fallback.png",
                   bg_path=r"./Source/background.jpg",
                   sound_path=r"./Source/test.mp3",
                   logo_path=r"./Source/logo.png")  # Set File Path
    fb.setOutputPath(output_path=r"./Output",
                     filename="test.mp4")  # Set Output Path
    fb.setText(text="Your Text Here", font="./Source/font.otf", relsize=1.0)
    # Set Text at the Bottom (Relative Font Size: 0.3 - 3.1)

    fb.setSpec(bins=60, lower=20, upper=1500,
               color=fb.color_dic["Gradient: Green - Blue"], bright=0.6,
               scalar=1.0, smooth=2,
               style=1, linewidth=1.0)
    """
    Set Spectrum:
    bins: Number of spectrums
    lower: Lower Frequency
    upper: Upper Frequency
    color: Color of Spectrum
    bright: Brightness of Spectrum
    scalar: Sensitivity (Scalar) of Analyzer (Default:1.0)
    smooth: Stabilize Spectrum (Range: 0 - 10)
    style: 0-7 for Different Spectrum Styles
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
    fb.previewBackground(localViewer=True)  # Preview before blending
    fb.setAudioInfo(normal=False, br_kbps=192)  # Audio info
    fb.runBlending()  # Blend the Video
