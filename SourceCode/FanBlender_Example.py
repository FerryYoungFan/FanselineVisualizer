from FanBlender import FanBlender
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