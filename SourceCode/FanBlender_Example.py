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
    # Example of Using FanBlender

    fb = FanBlender()  # Initialize Blender
    fb.setFilePath(image_path=r"./Source/fallback.png",
                   sound_path=r"./Source/test.mp3",
                   logo_path=r"./Source/logo.png")  # Set File Path
    fb.setOutputPath(output_path=r"./Output",
                     filename="test.mp4")  # Set Output Path
    fb.setText(text="Your Text Here", font="./Source/font.otf")  # Set Text at the Bottom
    fb.setSpec(bins=80, lower=20, upper=1500,
               color=fb.color_dic["Gradient: Green - Blue"],
               scalar=1.0, smooth=5)  # Set Spectrum Style:
    """
    bins: Number of spectrums
    lower: Lower Frequency
    upper: Upper Frequency
    color: Color of Spectrum
    scalar: Sensitivity (Scalar) of Analyzer (Default:1.0)
    smooth: Stabilize Spectrum (Range: 0-10)
    """
    fb.setVideoInfo(width=520, height=520, fps=30, br_Mbps=5)  # Video info
    fb.previewBackground()  # Preview before blending
    fb.setAudioInfo(normal=False, br_kbps=192)  # Audio info
    fb.runBlending()  # Blend the Video
