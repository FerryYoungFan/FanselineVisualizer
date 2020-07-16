Welcome to Fanseline Audio Visualizer!
欢迎使用“帆室邻音频可视化视频制作工具”！

By Twitter @FanKetchup
https://github.com/FerryYoungFan/FanselineVisualizer


****************************************************************************************
****************************************************************************************
Notice:
Recommend Python3 version: 3.7.4

Since v1.0.6: either run "FanBlender.py" or "FanBlender_GUI.py" with python3 will
check and install the required environment automatically. (Network conenction required)

Example:
python3 FanBlender_GUI.py

However, you can still install the environment manually (see followings if you want to do so).

----------------------------------------------------------------------------------------

注意：
推荐使用的 Python3 版本: 3.7.4

在v1.0.6之后：python3 运行"FanBlender.py" or "FanBlender_GUI.py" 都会自动检查
和安装所需环境。（需要联网）

运行例子：
python3 FanBlender_GUI.py

但您仍然可以手动安装环境（如果您想这么做请继续往下看）
****************************************************************************************
****************************************************************************************



----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
Require / 需求:

Python 3.7	    V 3.7.4

numpy		    V 1.19.0
Pillow		    V 7.2.0
imageio		    V 2.9.0
imageio-ffmpeg	V 0.4.2
pydub		    V 0.24.1*
(* No need to install ffmpeg for pydub, since it shares ffmpeg with imageio-ffmpeg.)
(* 无需为pydub专门安装ffmpeg，因为其与imageio-ffmpeg共享ffmpeg)
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------




----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
Linux: Please run these in Terminal:
Linux： 请在终端运行如下内容：

pip3 install numpy
pip3 install Pillow
pip3 install imageio
pip3 install imageio-ffmpeg
pip3 install pydub

If ffmpeg is not installed:
如果 ffmpeg 没有安装：
(Example for Ubuntu)
sudo apt update
sudo apt-get install -y ffmpeg

Finally run:
最后运行：
python3 FanBlender_GUI.py

----------------------------------------------------------------------------------------

macOS & Windows: Please run these in Terminal:
macOS & Windows： 请在终端运行如下内容：

pip3 install numpy
pip3 install Pillow
pip3 install imageio
pip3 install imageio-ffmpeg
pip3 install pydub

python3 FanBlender_GUI.py
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------


