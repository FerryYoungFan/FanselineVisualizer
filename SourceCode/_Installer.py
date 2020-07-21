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

from sys import platform

app_name = "FanselineVisualizer"
main_file = "FanBlender_GUI.py"

if platform == "darwin":
    icon_path = "./Source/icon-mac.icns"
    output_list = ["--name=%s" % app_name,"--windowed"]
    if os.path.exists("./Source"):
        output_list.append("--add-data=%s" % "./Source:Source/")
    if os.path.exists("./Source_/MacOS_Support"):
        # output_list.append("--add-data=%s" % "./Source_/MacOS_Support/Tcl_Tk_Replace/tclResources:tclResources/")
        # output_list.append("--add-data=%s" % "./Source_/MacOS_Support/Tcl_Tk_Replace/tkResources:tkResources/")
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

PyInstaller.__main__.run(output_list)
