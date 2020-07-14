from FanBlender import FanBlender

"""
Audio Visualizer
By Twitter @FanKetchup
https://github.com/FerryYoungFan/FanselineVisualizer

Require:

Python 3.7	    V 3.7.4

numpy		    V 1.19.0
Pillow		    V 7.2.0
imageio		    V 2.9.0
imageio-ffmpeg	V 0.4.2
pydub		    V0.24.1*
(* No need to install ffmpeg for pydub, since it shares ffmpeg with imageio-ffmpeg.)

"""

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

    fb.setSpec(bins=80, lower=20, upper=1500,
               color=fb.color_dic["Gradient: Green - Blue"], bright=0.6,
               scalar=1.0, smooth=5,
               style=1, linewidth=2.0)
    """
    Set Spectrum Style:
    bins: Number of spectrums
    lower: Lower Frequency
    upper: Upper Frequency
    color: Color of Spectrum
    bright: Brightness of Spectrum
    scalar: Sensitivity (Scalar) of Analyzer (Default:1.0)
    smooth: Stabilize Spectrum (Range: 0 - 10)
    style: 0: Solid Line Style, 1: Dot Line Style
    linewidth: Relative Width of Spectrum Line (0.5-20)
    """
    fb.setVideoInfo(width=720, height=1280, fps=30, br_Mbps=5,
                    blur_bg=True, use_glow=True, bg_mode=0)
    """
    Video info
    br_Mbps: Bit Rate of Video (Mbps)
    blur_bg: Blur the background
    use_glow: Add Glow Effect to Spectrum and Text
    bg_mode: 0: Normal Background, 2: Background Only, -1: Transparent Background, -2: Spectrum Only
    """
    fb.previewBackground()  # Preview before blending
    fb.setAudioInfo(normal=False, br_kbps=192)  # Audio info
    fb.runBlending()  # Blend the Video