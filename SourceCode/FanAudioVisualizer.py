#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FanWheels_PIL import *
import numpy as np
from pydub import AudioSegment


class AudioAnalyzer:
    def __init__(self, file_path, ffmpeg_path, fps=30, fq_low=20, fq_up=6000, bins=80, smooth=0, beat_detect=60,
                 low_range=10):
        AudioSegment.ffmpeg = ffmpeg_path
        sound = AudioSegment.from_file(file_path)
        self.samples = np.asarray(sound.get_array_of_samples(), dtype=np.float)
        self.fq_low = fq_low
        self.fq_up = fq_up
        self.bins = bins
        self.low_range = np.clip(low_range / 100, 0.0, 1.0)
        if not smooth:
            self.smooth = smooth
        else:
            self.smooth = 0
        if np.max(self.samples) != 0:
            self.samples = self.samples / np.max(self.samples)
        self.sample_rate = sound.frame_rate
        self.T = 1.0 / self.sample_rate

        self.fps = fps
        self.totalFrames = self.getTotalFrames()
        self.hist_stack = [None] * self.totalFrames

        self.beat_stack = np.ones(self.totalFrames)
        self.beat_calc_stack = [None] * self.totalFrames
        self.beat_detect = beat_detect
        self.beat_thres = (100 - beat_detect) / 100

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
        xf = np.linspace(0.0, 1.0 / (2.0 * self.T), N // 2)  # Frequency domain: 0 to 1/(2T)
        yf_cut = yf_fq[np.where(np.logical_and(xf >= fq_low, xf <= fq_up))]
        xf_cut = xf[np.where(np.logical_and(xf >= fq_low, xf <= fq_up))]
        xf_log = squareSpace(1, len(yf_cut) + 1, bins + 1)
        for i in range(bins):
            win_low, win_up = int(xf_log[i]), int(xf_log[i + 1])
            if win_low < 0:
                win_low = 0
            if win_up > len(yf_cut) - 1:
                win_up = len(yf_cut) - 1
            if win_up - win_low > 0:
                freq_array[i] = np.sum(yf_cut[win_low:win_up]) * psyModel((xf_cut[win_low] + xf_cut[win_low]) / 2)
            else:
                freq_array[i] = 0
        return freq_array

    def getSampleRate(self):
        return self.sample_rate

    def getLength(self):
        return self.samples.shape[0]

    def getTotalFrames(self):
        return int(self.fps * self.getLength() / self.getSampleRate()) + 1

    def getHistAtFrame(self, index):
        smooth = int(round(self.smooth * self.fps / 30))
        if smooth >= 1 + 4:
            fcount = 0
            freq_acc = np.zeros(self.bins)
            for i in range(smooth - 4 + 1):
                fcount = fcount + 2
                if index - i < 0:
                    pass
                else:
                    if self.hist_stack[index - i] is None:
                        left, right = self.getRange(index - i, smooth)
                        self.hist_stack[index - i] = self.fftAnalyzer(left, right, self.fq_low, self.fq_up, self.bins)
                    freq_acc += self.hist_stack[index - i]
                if index + i > len(self.hist_stack) - 1:
                    pass
                else:
                    if self.hist_stack[index + i] is None:
                        left, right = self.getRange(index + i, smooth)
                        self.hist_stack[index + i] = self.fftAnalyzer(left, right, self.fq_low, self.fq_up, self.bins)
                    freq_acc += self.hist_stack[index + i]
            return freq_acc / fcount

        else:
            if self.hist_stack[index] is None:
                left, right = self.getRange(index, smooth)
                self.hist_stack[index] = self.fftAnalyzer(left, right, self.fq_low, self.fq_up, self.bins)
            return self.hist_stack[index]

    def getBeatAtFrame(self, index):
        if self.beat_detect > 0:
            index = self.clipRange(index)
            left = self.clipRange(index - self.fps / 6)
            right = self.clipRange(index + self.fps / 6)
            for i in range(left, right + 1):
                if self.hist_stack[i] is None:
                    self.getHistAtFrame(i)
                if self.beat_calc_stack[i] is None:
                    calc_nums = self.bins * self.low_range  # Frequency range for the bass
                    maxv = np.max(self.hist_stack[i][0:int(np.ceil(calc_nums))]) ** 2
                    avgv = np.average(self.hist_stack[i][0:int(np.ceil(calc_nums))])
                    self.beat_calc_stack[i] = np.sqrt(max(maxv, avgv))

            slice_stack = self.beat_calc_stack[left:right + 1]
            current_max = np.max(slice_stack)
            index_max = np.where(slice_stack == current_max)[0][0]
            standby = np.sum(self.beat_stack[index:right + 1] == 1.0) == len(self.beat_stack[index:right + 1])

            if self.beat_calc_stack[index] >= self.beat_thres and index - left == index_max and standby:
                self.beat_stack[index:right + 1] = list(1 + 0.05 * (np.linspace(1, 0, right + 1 - index) ** 2))
        return self.beat_stack[index]

    def clipRange(self, index):
        if index >= self.totalFrames:
            return self.totalFrames - 1
        if index < 0:
            return 0
        return int(round(index))

    def getRange(self, idx, smooth=0):  # Get FFT range
        if idx < 0:
            idx = -5
        if idx > self.totalFrames:
            idx = -5
        middle = idx * self.getSampleRate() / self.fps
        offset = self.sample_rate / 20
        if smooth == 1:
            lt = int(round(middle - 1 * offset))
            rt = int(round(middle + 2 * offset))
        elif smooth == 2:
            lt = int(round(middle - 2 * offset))
            rt = int(round(middle + 2 * offset))
        elif 2 < smooth <= 5:
            lt = int(round(middle - 2 * offset))
            rt = int(round(middle + 4 * offset))
        elif smooth > 5:
            lt = int(round(middle - 3 * offset))
            rt = int(round(middle + 6 * offset))
        else:
            lt = int(round(middle - 1 * offset))
            rt = int(round(middle + 1 * offset))
        return lt, rt


def circle(draw, center, radius, fill):
    draw.ellipse((center[0] - radius + 1, center[1] - radius + 1, center[0] + radius - 1, center[1] + radius - 1),
                 fill=fill, outline=None)


def rectangle(draw, center, radius, fill):
    draw.rectangle((center[0] - radius + 1, center[1] - radius + 1, center[0] + radius - 1, center[1] + radius - 1),
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

    try:
        clist = tuple(color_mode)
        if len(clist) == 3:
            return clist + (255,)
        else:
            return clist
    except:
        return hsv_to_rgb(0, 0, brt) + (255,)


class AudioVisualizer:
    def __init__(self, img, rad_min, rad_max, line_thick=1.0, blur=5, style=0):
        self.background = img.copy()
        self.width, self.height = self.background.size
        self.mdpx = self.width / 2
        self.mdpy = self.height / 2
        self.line_thick = line_thick
        if style in [1, 2, 4, 6, 7, 11, 12, 15, 16, 21, 22]:
            self.rad_min = rad_min + line_thick * 1.5
            self.rad_max = rad_max - line_thick * 1.5
        elif style in [3, 5]:
            self.rad_min = rad_min + line_thick / 2
            self.rad_max = rad_max - line_thick * 1.5
        elif style in [8]:
            self.rad_min = rad_min + line_thick * 1.5
            self.rad_max = rad_max
        elif style in [18]:
            self.rad_min = rad_min
            self.rad_max = rad_max
        else:
            self.rad_min = rad_min + line_thick / 2
            self.rad_max = rad_max - line_thick / 2
        self.rad_div = self.rad_max - self.rad_min
        self.blur = blur
        self.style = style

    def getFrame(self, hist, amplify=5, color_mode="color4x", bright=1.0, saturation=1.0, use_glow=True, rotate=0.0,
                 fps=30.0, frame_pt=0, bg_mode=0, fg_img=None, fg_resize=1.0, quality=3):
        bins = hist.shape[0]

        quality_list = [1, 1, 2, 2, 4, 8]
        ratio = quality_list[quality]  # Antialiasing ratio

        line_thick = int(round(self.line_thick * ratio))
        line_thick_bold = int(round(self.line_thick * ratio * 1.5))
        line_thick_slim = int(round(self.line_thick * ratio / 2))

        brt = int(round(bright * 255))
        if brt > 255:
            brt = 255
        elif brt < 0:
            brt = 0
        canvas = Image.new('RGBA', (self.width * ratio, self.height * ratio), (brt, brt, brt, 0))
        draw = ImageDraw.Draw(canvas)

        line_graph_prev = None

        if self.style in [0, 1, 2, 3, 4, 5, 6, 7, 18, 19, 20, 21, 22]:
            hist = np.power(hist * 1.5, 1.5)
        hist = np.clip(hist * amplify, 0, 1)

        for i in range(bins):  # Draw Spectrum
            color = getColor(bins, i, color_mode, bright, saturation)
            if self.style == 0:  # Solid Line
                line_points = [self.getAxis(bins, i, self.rad_min, ratio),
                               self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio)]
                draw.line(line_points, width=line_thick, fill=color)
                circle(draw, line_points[0], line_thick_slim, color)
                circle(draw, line_points[1], line_thick_slim, color)

            elif self.style == 1:  # Dot Line
                p_gap = line_thick_bold
                p_size = line_thick_bold
                if p_gap + p_size > 0:
                    p_n = int(((hist[i] * self.rad_div) + p_gap) / (p_gap + p_size))
                    circle(draw, self.getAxis(bins, i, self.rad_min, ratio), line_thick_bold, color)
                    for ip in range(p_n):
                        p_rad = (p_gap + p_size) * ip
                        circle(draw, self.getAxis(bins, i, self.rad_min + p_rad, ratio), line_thick_bold, color)

            elif self.style == 2:  # Single Dot
                circle(draw, self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio), line_thick_bold,
                       color)

            elif self.style == 3:  # Stem Plot: Solid Single
                line_points = [self.getAxis(bins, i, self.rad_min, ratio),
                               self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio)]
                draw.line(line_points, width=line_thick, fill=color)
                circle(draw, line_points[0], line_thick_slim, color)
                circle(draw, line_points[1], line_thick_bold, color)

            elif self.style == 4:  # Stem Plot: Solid Double
                line_points = [self.getAxis(bins, i, self.rad_min, ratio),
                               self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio)]
                draw.line(line_points, width=line_thick, fill=color)
                circle(draw, line_points[0], line_thick_bold, color)
                circle(draw, line_points[1], line_thick_bold, color)

            elif self.style == 5:  # Stem Plot: Dashed Single
                p_gap = line_thick_slim
                p_size = line_thick_slim
                if p_gap + p_size > 0:
                    p_n = int(((hist[i] * self.rad_div) + p_size) / (p_gap + p_size))
                    for ip in range(p_n):
                        p_rad = (p_gap + p_size) * ip
                        circle(draw, self.getAxis(bins, i, self.rad_min + p_rad, ratio), line_thick_slim, color)
                    circle(draw, self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio), line_thick_bold,
                           color)

            elif self.style == 6:  # Stem Plot: Dashed Double
                p_gap = line_thick_slim
                p_size = line_thick_slim
                if p_gap + p_size > 0:
                    p_n = int(((hist[i] * self.rad_div) + p_size) / (p_gap + p_size))
                    for ip in range(p_n):
                        p_rad = (p_gap + p_size) * ip
                        circle(draw, self.getAxis(bins, i, self.rad_min + p_rad, ratio), line_thick_slim, color)
                    circle(draw, self.getAxis(bins, i, self.rad_min, ratio), line_thick_bold, color)
                    circle(draw, self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio), line_thick_bold,
                           color)

            elif self.style == 7:  # Double Dot
                circle(draw, self.getAxis(bins, i, self.rad_min, ratio), line_thick_bold, color)
                circle(draw, self.getAxis(bins, i, self.rad_min + hist[i] * self.rad_div, ratio), line_thick_bold,
                       color)

            elif self.style == 8:  # Concentric
                if i % 12 == 0:
                    lower = i
                    upper = i + 11
                    if upper >= len(hist):
                        upper = len(hist) - 1
                    local_mean = np.mean(hist[-upper - 1:-lower - 1]) * 2
                    if local_mean > 1:
                        local_mean = 1
                    radius = self.rad_min + local_mean * self.rad_div
                    left = (self.mdpx - radius) * ratio
                    right = (self.mdpx + radius) * ratio
                    up = (self.mdpy - radius) * ratio
                    down = (self.mdpy + radius) * ratio
                    draw.ellipse((left, up, right, down), fill=None, outline=color, width=line_thick_bold)

            elif self.style == 9:  # Classic Line: Center
                mid_y = self.mdpy * ratio
                y_scale = 0.85
                low = mid_y + self.rad_max * ratio * hist[i] * y_scale
                up = mid_y - self.rad_max * ratio * hist[i] * y_scale
                gap = self.rad_max * ratio * 2 / (bins - 1)
                x_offset = gap * i + self.mdpx * ratio - self.rad_max * ratio
                line_points = [(x_offset, low), (x_offset, up)]
                draw.line(line_points, width=line_thick, fill=color)
                circle(draw, line_points[0], line_thick_slim, color)
                circle(draw, line_points[1], line_thick_slim, color)

            elif self.style == 10:  # Classic Line: Bottom
                mid_y = self.mdpy * ratio
                y_scale = 0.85
                low = mid_y + self.rad_max * ratio * y_scale
                up = low - self.rad_max * ratio * hist[i] * y_scale * 2
                gap = self.rad_max * ratio * 2 / (bins - 1)
                x_offset = gap * i + self.mdpx * ratio - self.rad_max * ratio
                line_points = [(x_offset, low), (x_offset, up)]
                draw.line(line_points, width=line_thick, fill=color)
                circle(draw, line_points[0], line_thick_slim, color)
                circle(draw, line_points[1], line_thick_slim, color)

            elif self.style == 11:  # Classic Round Dot: Center
                mid_y = self.mdpy * ratio
                y_scale = 0.85
                low = mid_y + self.rad_max * ratio * hist[i] * y_scale
                gap = self.rad_max * ratio * 2 / (bins - 1)
                x_offset = gap * i + self.mdpx * ratio - self.rad_max * ratio
                p_gap = line_thick_bold * 2
                p_size = line_thick_bold
                if p_gap + p_size > 0:
                    p_n = int((low - mid_y + p_gap) / (p_gap + p_size))
                    if p_n < 1:
                        p_n = 1
                    for ip in range(p_n):
                        d_y = ip * (p_gap + p_size)
                        circle(draw, (x_offset, mid_y + d_y), line_thick_bold, color)
                        circle(draw, (x_offset, mid_y - d_y), line_thick_bold, color)

            elif self.style == 12:  # Classic Round Dot: Bottom
                mid_y = self.mdpy * ratio
                y_scale = 0.85
                low = mid_y + self.rad_max * ratio * y_scale
                up = low - self.rad_max * ratio * hist[i] * y_scale * 2
                gap = self.rad_max * ratio * 2 / (bins - 1)
                x_offset = gap * i + self.mdpx * ratio - self.rad_max * ratio
                p_gap = line_thick_bold * 2
                p_size = line_thick_bold
                if p_gap + p_size > 0:
                    p_n = int((low - up + p_gap) / (p_gap + p_size))
                    if p_n < 1:
                        p_n = 1
                    for ip in range(p_n):
                        p_y = low - ip * (p_gap + p_size)
                        circle(draw, (x_offset, p_y), line_thick_bold, color)

            elif self.style == 13:  # Classic Square Dot: Center
                mid_y = self.mdpy * ratio
                y_scale = 0.85
                low = mid_y + self.rad_max * ratio * hist[i] * y_scale
                gap = self.rad_max * ratio * 2 / (bins - 1)
                x_offset = gap * i + self.mdpx * ratio - self.rad_max * ratio
                p_gap = line_thick_bold * 2
                p_size = line_thick_bold
                if p_gap + p_size > 0:
                    p_n = int((low - mid_y + p_gap) / (p_gap + p_size))
                    if p_n < 1:
                        p_n = 1
                    for ip in range(p_n):
                        d_y = ip * (p_gap + p_size)
                        rectangle(draw, (x_offset, mid_y + d_y), line_thick_bold, color)
                        rectangle(draw, (x_offset, mid_y - d_y), line_thick_bold, color)

            elif self.style == 14:  # Classic Square Dot: Bottom
                mid_y = self.mdpy * ratio
                y_scale = 0.85
                low = mid_y + self.rad_max * ratio * y_scale
                up = low - self.rad_max * ratio * hist[i] * y_scale * 2
                gap = self.rad_max * ratio * 2 / (bins - 1)
                x_offset = gap * i + self.mdpx * ratio - self.rad_max * ratio
                p_gap = line_thick_bold * 2
                p_size = line_thick_bold
                if p_gap + p_size > 0:
                    p_n = int((low - up + p_gap) / (p_gap + p_size))
                    if p_n < 1:
                        p_n = 1
                    for ip in range(p_n):
                        p_y = low - ip * (p_gap + p_size)
                        rectangle(draw, (x_offset, p_y), line_thick_bold, color)

            elif self.style == 15:  # Classic Rectangle: Center
                mid_y = self.mdpy * ratio
                y_scale = 0.85
                low = mid_y + self.rad_max * ratio * hist[i] * y_scale
                up = mid_y - self.rad_max * ratio * hist[i] * y_scale
                gap = self.rad_max * ratio * 2 / (bins - 1)
                x_offset = gap * i + self.mdpx * ratio - self.rad_max * ratio
                draw.rectangle((x_offset - line_thick_bold, low + line_thick_bold, x_offset + line_thick_bold,
                                up - line_thick_bold), fill=color)

            elif self.style == 16:  # Classic Rectangle: Bottom
                mid_y = self.mdpy * ratio
                y_scale = 0.85
                low = mid_y + self.rad_max * ratio * y_scale
                up = low - self.rad_max * ratio * hist[i] * y_scale * 2
                gap = self.rad_max * ratio * 2 / (bins - 1)
                x_offset = gap * i + self.mdpx * ratio - self.rad_max * ratio
                draw.rectangle((x_offset - line_thick_bold, low + line_thick_bold, x_offset + line_thick_bold,
                                up - line_thick_bold), fill=color)

            elif self.style == 17:  # Line Graph
                mid_y = self.mdpy * ratio
                y_scale = 0.85
                low = mid_y + self.rad_max * ratio * y_scale
                up = low - self.rad_max * ratio * hist[i] * y_scale * 2
                gap = self.rad_max * ratio * 2 / (bins - 1)
                x_offset = gap * i + self.mdpx * ratio - self.rad_max * ratio
                if line_graph_prev is None:
                    line_graph_prev = [(x_offset, low), (x_offset, up)]
                    draw.line(((x_offset, low), (x_offset, up)), width=line_thick, fill=color)
                    circle(draw, (x_offset, low), line_thick_slim, color)
                    circle(draw, (x_offset, up), line_thick_slim, color)

                draw.line((line_graph_prev[1], (x_offset, up)), width=line_thick, fill=color)
                circle(draw, line_graph_prev[1], line_thick_slim, color)
                circle(draw, (x_offset, up), line_thick_slim, color)

                if i >= bins - 1:
                    draw.line(((x_offset, low), (x_offset, up)), width=line_thick, fill=color)
                    circle(draw, (x_offset, low), line_thick_slim, color)
                    circle(draw, (x_offset, up), line_thick_slim, color)
                line_graph_prev = [(x_offset, low), (x_offset, up)]

            elif self.style == 18:  # Zooming Circles
                center_rad = (self.rad_max - self.rad_min) / 2 + self.rad_min
                center = self.getAxis(bins, i, center_rad, ratio)
                center_next = self.getAxis(bins, i + 1, center_rad, ratio)
                center_gap = np.sqrt((center_next[0] - center[0]) ** 2 + (center_next[1] - center[1]) ** 2) / 2 * ratio
                max_gap = min(self.rad_div * ratio, center_gap)
                factor = np.power(np.clip(self.line_thick * 20 / min(self.width, self.height), 0.0, 1.0), 0.3)
                rad_draw = int(round(hist[i] * factor * max_gap / 2))
                circle(draw, center, rad_draw, color)

            elif self.style == 19:  # Solid Line: Center
                line_points = [
                    self.getAxis(bins, i, self.rad_min + self.rad_div / 2 - hist[i] * self.rad_div / 2, ratio),
                    self.getAxis(bins, i, self.rad_min + self.rad_div / 2 + hist[i] * self.rad_div / 2, ratio)]
                draw.line(line_points, width=line_thick, fill=color)
                circle(draw, line_points[0], line_thick_slim, color)
                circle(draw, line_points[1], line_thick_slim, color)

            elif self.style == 20:  # Solid Line: Reverse
                line_points = [
                    self.getAxis(bins, i, self.rad_min + self.rad_div - hist[i] * self.rad_div, ratio),
                    self.getAxis(bins, i, self.rad_min + self.rad_div, ratio)]
                draw.line(line_points, width=line_thick, fill=color)
                circle(draw, line_points[0], line_thick_slim, color)
                circle(draw, line_points[1], line_thick_slim, color)

            elif self.style == 21:  # Double Dot: Center
                circle(draw, self.getAxis(bins, i, self.rad_min + self.rad_div / 2 - hist[i] * self.rad_div / 2, ratio),
                       line_thick_bold, color)
                circle(draw, self.getAxis(bins, i, self.rad_min + self.rad_div / 2 + hist[i] * self.rad_div / 2, ratio),
                       line_thick_bold,
                       color)

            elif self.style == 22:  # Double Dot: Reverse
                circle(draw,
                       self.getAxis(bins, i, self.rad_min + self.rad_div - hist[i] * self.rad_div, ratio),
                       line_thick_bold, color)
                circle(draw, self.getAxis(bins, i, self.rad_min + self.rad_div, ratio), line_thick_bold,
                       color)

            else:  # Othewise (-1): No Spectrum
                pass

        if use_glow:
            canvas = glowFx(canvas, self.blur * ratio, 1.5)

        canvas = canvas.resize((self.width, self.height), Image.ANTIALIAS)

        output = self.background.copy()
        output.paste(canvas, (0, 0), canvas)

        if fg_img is not None and bg_mode > -2 and (not bg_mode == 2):
            if rotate != 0:
                angle = -(rotate * frame_pt / fps / 60) * 360
                rotate_img = fg_img.rotate(angle, resample=Image.BICUBIC)
                if fg_resize != 1.0:
                    rotate_img = resizeRatio(rotate_img, fg_resize)
                output = pasteMiddle(rotate_img, output, glow=False, blur=0, bright=1)

            if rotate == 0:
                if self.style in [9, 10, 11, 12, 13, 14, 15, 16, 17] or fg_resize != 0:
                    if fg_resize != 1.0:
                        output = pasteMiddle(resizeRatio(fg_img, fg_resize), output, glow=False, blur=0, bright=1)
                    else:
                        output = pasteMiddle(fg_img, output, glow=False, blur=0, bright=1)

        return output

    def getAxis(self, bins, index, radius, ratio):
        div = 2 * np.pi / bins
        angle = div * index - np.pi / 2 - np.pi * 5 / 6
        ox = (self.mdpx + radius * np.cos(angle)) * ratio
        oy = (self.mdpy + radius * np.sin(angle)) * ratio
        return ox, oy


def squareSpace(start, end, num):
    sqrt_start = np.sqrt(start)
    sqrt_end = np.sqrt(end)
    sqrt_space = np.linspace(sqrt_start, sqrt_end, num=num)
    return np.round(np.power(sqrt_space, 2)).astype(int)


def linearRange(startx, endx, starty, endy, x):
    return (endy - starty) / (endx - startx) * (x - startx) + starty


psy_map = [[10, 32, 3.0, 0.8],
           [32, 64, 0.8, 1.0],
           [64, 150, 1.0, 1.3],
           [150, 2000, 1.3, 1.0],
           [2000, 8000, 1.0, 1.2],
           [8000, 24000, 1.2, 4.0]]


def psyModel(freq):  # Get psychoacoustical model
    for item in psy_map:
        if item[0] <= freq < item[1]:
            return linearRange(item[0], item[1], item[2], item[3], freq)
    return 0


if __name__ == '__main__':
    print(linearRange(8000, 20000, 1, 0, 10000))
