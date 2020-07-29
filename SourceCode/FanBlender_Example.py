#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FanBlender import FanBlender

"""
Audio Visualizer - Example
By Twitter @FanKetchup
https://github.com/FerryYoungFan/FanselineVisualizer
"""

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
    smooth: Stabilize Spectrum (Range: 0 - 10)
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
