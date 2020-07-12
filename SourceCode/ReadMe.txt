Fanseline Audio Visualizer
By Twitter @FanKetchup

Require:

Python 3.7	    V 3.7.4

numpy		    V 1.19.0
Pillow		    V 7.2.0
imageio		    V 2.9.0
imageio-ffmpeg	V 0.4.2
pydub		    V0.24.1*
(* No need to install ffmpeg for pydub, since it shares ffmpeg with imageio-ffmpeg.)




Linux:

pip3 install Pillow
pip3 install imageio
pip3 install imageio-ffmpeg
pip3 install pydub

If ffmpeg is not installed: (for Ubuntu)
sudo apt update
sudo apt-get install -y ffmpeg

Finally run:
python3 FanBlender_GUI.py




for pyinstaller:
pyinstaller --noconfirm --onedir --windowed --icon ./Source/icon-large_Desktop_256x256.ico --name FanselineVisualizer FanBlender_GUI.py


