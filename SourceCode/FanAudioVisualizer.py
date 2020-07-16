from FanWheels_PIL import *
import numpy as np
from pydub import AudioSegment


class AudioAnalyzer:
    def __init__(self, file_path, ffmpeg_path, fps=30):
        AudioSegment.ffmpeg = ffmpeg_path
        sound = AudioSegment.from_file(file_path)
        self.samples = np.asarray(sound.get_array_of_samples(), dtype=np.float)
        if np.max(self.samples) != 0:
            self.samples = self.samples / np.max(self.samples)
        self.sample_rate = sound.frame_rate
        self.T = 1.0 / self.sample_rate

        self.fps = fps
        self.totalFrames = self.getTotalFrames()

    def fftAnalyzer(self, start_p, stop_p, fq_low=20, fq_up=6000, bins=80):
        freq_array = np.zeros(bins)
        if stop_p <= 0:
            return freq_array
        if start_p < 0:
            start_p = 0
        if start_p >= self.samples.shape[0] - self.sample_rate / fq_low:
            return freq_array
        if stop_p >= self.samples.shape[0]:
            stop_p = self.samples.shape[0] - 1
        y = self.samples[start_p:stop_p]
        N = y.shape[0]
        yf = np.fft.fft(y)
        yf_fq = 2.0 / N * np.abs(yf[:N // 2])
        xf = np.linspace(0.0, 1.0 / (2.0 * self.T), N // 2)
        freq_step = (fq_up - fq_low) / bins
        freq_chunck = xf[1] - xf[0]
        for i in range(bins):
            win_low = fq_low + freq_step * i
            win_up = win_low + freq_step
            win_low = round(win_low / freq_chunck / 2)
            win_up = round(win_up / freq_chunck / 2)
            if win_low >= xf.shape[0]:
                break
            if win_up >= xf.shape[0]:
                win_up = xf.shape[0] - 1
            freq_array[i] = np.sum(yf_fq[win_low:win_up])
        return loopAverage(freq_array)

    def getSampleRate(self):
        return self.sample_rate

    def getLength(self):
        return self.samples.shape[0]

    def getTotalFrames(self):
        return int(self.fps * self.getLength() / self.getSampleRate()) + 1

    def getHistAtFrame(self, index, fq_low=20, fq_up=6000, bins=80, smooth=0):
        def getRange(parent, idx, low):
            if idx < 0:
                idx = -5
            if idx > parent.totalFrames:
                idx = -5
            middle = idx * parent.getSampleRate() / parent.fps
            offset = parent.sample_rate / low
            lt = int(round(middle) - 0.5 * offset)
            rt = int(round(middle + 2.5 * offset))
            return lt, rt

        if smooth is None:
            smooth = 0

        smooth = int(round(smooth * self.fps / 30))
        if smooth > 1:
            fcount = 0
            freq_acc = np.zeros(bins)
            for i in range(smooth):
                fcount = fcount + 2
                left, right = getRange(self, index - i, fq_low)
                freq_acc += self.fftAnalyzer(left, right, fq_low, fq_up, bins)
                left, right = getRange(self, index + i, fq_low)
                freq_acc += self.fftAnalyzer(left, right, fq_low, fq_up, bins)
            return freq_acc / fcount

        else:
            left, right = getRange(self, index, fq_low)
            return self.fftAnalyzer(left, right, fq_low, fq_up, bins)


def circle(draw, center, radius, fill):
    draw.ellipse((center[0] - radius + 1, center[1] - radius + 1, center[0] + radius - 1, center[1] + radius - 1),
                 fill=fill, outline=None)


def getCycleHue(start, end, bins, index, cycle=1):
    div = end - start
    fac = index / bins * cycle
    ratio = abs(round(fac) - fac) * 2
    return (div * ratio + start) / 360


def getColor(bins, index, color_mode="color4x", bright=1.0, sat=0.8):
    brt = 0.4 + bright * 0.6
    if color_mode == "color4x":
        return hsv_to_rgb(4 * index / bins, sat, brt) + (255,)
    if color_mode == "color2x":
        return hsv_to_rgb(2 * index / bins, sat, brt) + (255,)
    if color_mode == "color1x":
        return hsv_to_rgb(1 * index / bins, sat, brt) + (255,)
    if color_mode == "white":
        return hsv_to_rgb(0, 0, 1.0) + (255,)
    if color_mode == "black":
        return hsv_to_rgb(0, 0, 0) + (255,)
    if color_mode == "gray":
        return hsv_to_rgb(0, 0, brt) + (255,)
    if color_mode == "red":
        return hsv_to_rgb(0, sat, brt) + (255,)
    if color_mode == "green":
        return hsv_to_rgb(120 / 360, sat, brt) + (255,)
    if color_mode == "blue":
        return hsv_to_rgb(211 / 360, sat, brt) + (255,)
    if color_mode == "yellow":
        return hsv_to_rgb(49 / 360, sat, brt) + (255,)
    if color_mode == "magenta":
        return hsv_to_rgb(328 / 360, sat, brt) + (255,)
    if color_mode == "purple":
        return hsv_to_rgb(274 / 360, sat, brt) + (255,)
    if color_mode == "cyan":
        return hsv_to_rgb(184 / 360, sat, brt) + (255,)
    if color_mode == "lightgreen":
        return hsv_to_rgb(135 / 360, sat, brt) + (255,)
    if color_mode == "green-blue":
        return hsv_to_rgb(getCycleHue(122, 220, bins, index, 4), sat, brt) + (255,)
    if color_mode == "magenta-purple":
        return hsv_to_rgb(getCycleHue(300, 370, bins, index, 4), sat, brt) + (255,)
    if color_mode == "red-yellow":
        return hsv_to_rgb(getCycleHue(-5, 40, bins, index, 4), sat, brt) + (255,)
    if color_mode == "yellow-green":
        return hsv_to_rgb(getCycleHue(42, 147, bins, index, 4), sat, brt) + (255,)
    if color_mode == "blue-purple":
        return hsv_to_rgb(getCycleHue(208, 313, bins, index, 4), sat, brt) + (255,)
    return hsv_to_rgb(0, 0, brt) + (255,)


class AudioVisualizer:
    def __init__(self, img, rad_min, rad_max, line_thick, blur=5, style=0):
        self.background = img.copy()
        self.width, self.height = self.background.size
        self.mdpx = self.width / 2
        self.mdpy = self.height / 2
        self.line_thick = line_thick
        if style in [1, 2, 4, 6, 7]:
            self.rad_min = rad_min + line_thick * 1.5
            self.rad_max = rad_max - line_thick * 1.5
        elif style in [3, 5]:
            self.rad_min = rad_min + line_thick / 2
            self.rad_max = rad_max - line_thick * 1.5
        else:
            self.rad_min = rad_min + line_thick / 2
            self.rad_max = rad_max - line_thick / 2
        self.rad_div = self.rad_max - self.rad_min
        self.blur = blur
        self.style = style

    def getFrame(self, hist, amplify=5, color_mode="color4x", bright=1.0, use_glow=True, rotate=0.0, fps=30.0,
                 frame_pt=0, bg_mode=0, fg_img=None):
        bins = hist.shape[0]
        hist = np.clip(hist * amplify, 0, 1)

        ratio = 2  # antialiasing ratio
        line_thick = self.line_thick * ratio
        print("line_thick:",line_thick)

        brt = int(round(bright * 255))
        if brt > 255:
            brt = 255
        elif brt < 0:
            brt = 0
        canvas = Image.new('RGBA', (self.width * ratio, self.height * ratio), (brt, brt, brt, 0))
        draw = ImageDraw.Draw(canvas)

        for i in range(bins):
            color = getColor(bins, i, color_mode, bright)
            if self.style == 1:
                p_gap = line_thick * 1.5
                p_size = line_thick * 1.5
                p_n = int(((hist[i] * self.rad_div) + p_size) / (p_gap + p_size))
                circle(draw, self.getAxis(bins, i, self.rad_min, ratio), line_thick * 1.5, color)
                for ip in range(p_n):
                    p_rad = (p_gap + p_size) * ip
                    circle(draw, self.getAxis(bins, i, self.rad_min + p_rad, ratio), line_thick * 1.5, color)
            elif self.style == 2:
                circle(draw, self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio), line_thick * 1.5,
                       color)
            elif self.style == 3:
                line_points = [self.getAxis(bins, i, self.rad_min, ratio),
                               self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio)]
                draw.line(line_points, width=line_thick, fill=color, joint='curve')
                circle(draw, line_points[0], line_thick / 2, color)
                circle(draw, line_points[1], line_thick * 1.5, color)
            elif self.style == 4:
                line_points = [self.getAxis(bins, i, self.rad_min, ratio),
                               self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio)]
                draw.line(line_points, width=line_thick, fill=color, joint='curve')
                circle(draw, line_points[0], line_thick * 1.5, color)
                circle(draw, line_points[1], line_thick * 1.5, color)
            elif self.style == 5:
                p_gap = line_thick / 2
                p_size = line_thick / 2
                p_n = int(((hist[i] * self.rad_div) + p_size) / (p_gap + p_size))
                for ip in range(p_n):
                    p_rad = (p_gap + p_size) * ip
                    circle(draw, self.getAxis(bins, i, self.rad_min + p_rad, ratio), line_thick / 2, color)
                circle(draw, self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio), line_thick * 1.5,
                       color)
            elif self.style == 6:
                p_gap = line_thick / 2
                p_size = line_thick / 2
                p_n = int(((hist[i] * self.rad_div) + p_size) / (p_gap + p_size))
                for ip in range(p_n):
                    p_rad = (p_gap + p_size) * ip
                    circle(draw, self.getAxis(bins, i, self.rad_min + p_rad, ratio), line_thick / 2, color)
                circle(draw, self.getAxis(bins, i, self.rad_min, ratio), line_thick * 1.5, color)
                circle(draw, self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio), line_thick * 1.5,
                       color)
            elif self.style == 7:
                circle(draw, self.getAxis(bins, i, self.rad_min, ratio), line_thick * 1.5, color)
                circle(draw, self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio), line_thick * 1.5,
                       color)
            else:
                line_points = [self.getAxis(bins, i, self.rad_min, ratio),
                               self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio)]
                draw.line(line_points, width=line_thick, fill=color, joint='curve')
                circle(draw, line_points[0], line_thick / 2, color)
                circle(draw, line_points[1], line_thick / 2, color)
        if use_glow:
            canvas_blur = canvas.filter(ImageFilter.GaussianBlur(radius=self.blur / 2 * ratio))
            canvas = ImageChops.add(canvas, canvas_blur)

        canvas = canvas.resize((self.width, self.height), Image.ANTIALIAS)

        output = self.background.copy()
        if rotate != 0 and fg_img is not None and bg_mode > -2 and (not bg_mode == 2):
            angle = -(rotate * frame_pt / fps / 60) * 360
            rotate_img = fg_img.rotate(angle, resample=Image.BICUBIC)
            output = pasteMiddle(rotate_img, output, glow=False, blur=0, bright=1)

        output.paste(canvas, (0, 0), canvas)
        return output

    def getAxis(self, bins, index, radius, ratio):
        div = 2 * np.pi / bins
        angle = div * index - np.pi / 2 - np.pi / 3
        ox = (self.mdpx + radius * np.cos(angle)) * ratio
        oy = (self.mdpy + radius * np.sin(angle)) * ratio
        return ox, oy


def loopAverage(arr_in, ratio=0.01):
    if ratio < 0:
        ratio = 0
    elif ratio > 1:
        ratio = 1
    avg_size = round(len(arr_in) * ratio)
    norm_sig = avg_size * 0.5
    k_size = int(2 * avg_size + 1)
    if k_size <= 0 or norm_sig <= 0:
        return arr_in

    arr = np.concatenate((arr_in[-avg_size:], arr_in, arr_in[:avg_size]), axis=None)
    arr_out = arr_in.copy()

    norm_x = np.arange(-avg_size, avg_size + 1)

    norm_y = 1 / (norm_sig * np.sqrt(2 * np.pi)) * np.exp(-norm_x * norm_x / (2 * norm_sig * norm_sig))
    for i in range(len(arr_out)):
        arr_out[i] = np.sum(arr[i:i + k_size] * norm_y)
    return arr_out


if __name__ == '__main__':
    loopAverage([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.1)
