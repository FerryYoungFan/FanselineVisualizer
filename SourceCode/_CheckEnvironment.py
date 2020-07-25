#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

"""
Python 3.7	    V 3.7.4

numpy		    V 1.19.0
Pillow		    V 7.2.0
imageio		    V 2.9.0
imageio-ffmpeg	V 0.4.2
PyQt5           V 5.15.0
pydub		    V 0.24.1*

(* No need to install ffmpeg for pydub, since it shares ffmpeg with imageio-ffmpeg.)
"""


def checkEnvironment(showInfo=True):
    if showInfo:
        print("Checking Python Environment...")
    try:
        import numpy
    except:
        if showInfo:
            print("Numpy not found, try to install:")
        os.system("pip3 install numpy==1.19.0")

    try:
        import PIL
    except:
        if showInfo:
            print("Pillow not found, try to install:")
        os.system("pip3 install Pillow==7.2.0")

    try:
        import imageio
    except:
        if showInfo:
            print("imageio not found, try to install:")
        os.system("pip3 install imageio==2.9.0")

    try:
        import imageio_ffmpeg
    except:
        if showInfo:
            print("imageio-ffmpeg not found, try to install:")
        os.system("pip3 install imageio-ffmpeg==0.4.2")

    try:
        import PyQt5
    except:
        if showInfo:
            print("PyQt5 not found, try to install:")
        os.system("pip3 install PyQt5==5.15.0")

    try:
        import pydub
        print("↑↑↑ Please ignore this pydub runtime warning ↑↑↑")
    except:
        if showInfo:
            print("pydub not found, try to install:")
        os.system("pip3 install pydub==0.24.1")

    not_install = None
    try:
        not_install = "Numpy"
        import numpy
        not_install = "Pillow"
        import PIL
        not_install = "iamgeio"
        import imageio
        not_install = "imageio-ffmpeg"
        import imageio_ffmpeg
        not_install = "pydub"
        import pydub
        if showInfo:
            print("Check Environment - Done!")
    except:
        print("Error: Environment Error")
        print("{0} not installed.".format(not_install))


if __name__ == '__main__':
    checkEnvironment(True)
