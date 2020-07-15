import PyInstaller.__main__

PyInstaller.__main__.run([
    "--noconfirm",
    '--name=%s' % "FanselineVisualizer",
    "--add-data=%s"% "./Source;Source/",
    '--onedir',
    '--windowed',
    '--icon=%s' % "./Source/icon-large_Desktop_256x256.ico",
    "FanBlender_GUI.py",
])