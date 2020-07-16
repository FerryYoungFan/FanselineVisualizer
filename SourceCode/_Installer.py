"""
If you want to use pyinstaller for this project,
simply run:
"
    python3 _Installer.py
                            "
in terminal
"""

import os

try:
    from _CheckEnvironment import checkEnvironment

    checkEnvironment(True)
except:
    pass

try:
    import PyInstaller.__main__
except:
    print("check pyinstaller: not installed. Now install pyinstaller:")
    os.system('pip3 install pyinstaller')
    import PyInstaller.__main__

app_name = "FanselineVisualizer"
main_file = "FanBlender_GUI.py"
icon_path = "./Source/icon-large_Desktop_256x256.ico"

output_list = ["--noconfirm", "--name=%s" % app_name]
if os.path.exists("./Source"):
    if os.name == "nt":
        output_list.append("--add-data=%s" % "./Source;Source/")
    else:
        output_list.append("--add-data=%s" % "./Source:Source/")
output_list.append("--onedir")
output_list.append("--windowed")
if os.path.exists(icon_path):
    output_list.append("--icon=%s" % icon_path)
output_list.append(main_file)

PyInstaller.__main__.run(output_list)
