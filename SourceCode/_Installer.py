#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
If you want to use pyinstaller for this project,
simply run:
"
    python3 _Installer.py
                            "
in terminal
"""

import os, shutil

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

from sys import platform

app_name = "FanselineVisualizer"
main_file = "FanBlender_GUI.py"

if platform == "darwin":
    icon_path = "./Source_/icon-mac.icns"
    output_list = ["--name=%s" % app_name, "--windowed"]
    if os.path.exists("./Source"):
        output_list.append("--add-data=%s" % "./Source:Source/")
    if os.path.exists("./Source_/MacOS_Support"):
        pass
    if os.path.exists(icon_path):
        output_list.append("--icon=%s" % icon_path)
    output_list.append(main_file)
else:
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

excludes = ['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter']
for ex in excludes:
    output_list.append("--exclude-module=" + ex)

PyInstaller.__main__.run(output_list)

print("Removing Unused files...")

if platform == "darwin":
    shutil.rmtree("./dist/"+app_name+".app/Contents/Resources/imageio",True)
else:
    shutil.rmtree("./dist/" + app_name + "/imageio", True)
    if os.name == "nt":
        os.remove("./dist/" + app_name + "/opengl32sw.dll")
        os.remove("./dist/" + app_name + "/d3dcompiler_47.dll")

