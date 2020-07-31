#!/usr/bin/env python
# -*- coding: utf-8 -*-

from QtViewer import PhotoViewer, ImageSelectWindow
from QtWindows import *
from LanguagePack import *
from FanBlender import FanBlender, getPath, __version__
import threading, time, pickle


class InfoBridge:
    def __init__(self, parent):
        self.parent = parent
        self.value = 0
        self.total = 100
        self.img_cache = None

    def log(self, content=""):
        pass

    def progressbar(self, value, total):
        self.value = value
        self.total = total

    def freeze(self, flag=True):
        if flag:
            self.parent.setWindowTitle(self.parent.windowName + " " + self.parent.lang["(Running...)"])
            self.parent.blendWindow.freezeWindow(True)
        else:
            self.parent.setWindowTitle(self.parent.windowName)
            self.parent.blendWindow.freezeWindow(False)
            self.parent.isRunning = False

    def realTime(self, img):
        self.img_cache = img

    def audioWarning(self):
        self.parent.error_log = 1

    def ffmpegWarning(self):
        self.parent.error_log = 2


class MainWindow(QtWidgets.QWidget):
    def __init__(self, lang_in, vdic_in, lang_code_in, first_run_in):
        super(MainWindow, self).__init__()
        self.lang = lang_in
        self.lang_code = lang_code_in
        self.first_run = first_run_in
        self.windowName = self.lang["Fanseline Visualizer"] + " - v" + __version__
        self.setWindowTitle(self.windowName)
        setWindowIcons(self)

        self.fb = FanBlender()
        self.infoBridge = InfoBridge(self)
        self.fb.setConsole(self.infoBridge)
        self.vdic = vdic_in
        self.vdic_stack = []

        self.audio_formats = " (*.mp3;*.wav;*.ogg;*.aac;*.flac;*.ape;*.m4a;*.m4r;*.wma;*.mp2;*.mmf);;"
        self.audio_formats_arr = getFormats(self.audio_formats)
        self.video_formats = " (*.mp4;*.wmv;*.avi;*.flv;*.mov;*.mkv;*.rm;*.rmvb);;"
        self.video_formats_arr = getFormats(self.video_formats)
        self.image_formats = " (*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.ico;*.dib;*.webp;*.tiff;*.tga);;"
        self.image_formats_arr = getFormats(self.image_formats)

        left = QtWidgets.QFrame(self)
        left.setStyleSheet(viewerStyle)
        VBlayout_l = QtWidgets.QVBoxLayout(left)
        self.viewer = PhotoViewer(self)
        VBlayout_l.addWidget(self.viewer)
        VBlayout_l.setSpacing(0)
        VBlayout_l.setContentsMargins(0, 0, 0, 0)

        self.mainMenu = MainMenu(self)
        self.imageSelector = ImageSelectWindow(self)
        self.audioSetting = AudioSettingWindow(self)
        self.videoSetting = VideoSettingWindow(self)
        self.textWindow = TextWindow(self)
        self.imageSetting = ImageSettingWindow(self)
        self.spectrumColor = SpectrumColorWindow(self)
        self.spectrumStyle = SpectrumStyleWindow(self)
        self.blendWindow = BlendWindow(self)
        self.aboutWindow = AboutWindow(self)

        right = QtWidgets.QFrame(self)
        VBlayout_r = QtWidgets.QVBoxLayout(right)
        VBlayout_r.setAlignment(QtCore.Qt.AlignTop)
        VBlayout_r.addWidget(self.mainMenu)
        VBlayout_r.addWidget(self.imageSelector)
        VBlayout_r.addWidget(self.audioSetting)
        VBlayout_r.addWidget(self.videoSetting)
        VBlayout_r.addWidget(self.textWindow)
        VBlayout_r.addWidget(self.imageSetting)
        VBlayout_r.addWidget(self.spectrumColor)
        VBlayout_r.addWidget(self.spectrumStyle)
        VBlayout_r.addWidget(self.blendWindow)
        VBlayout_r.addWidget(self.aboutWindow)

        mainBox = QtWidgets.QHBoxLayout(self)
        mainBox.setSpacing(0)
        mainBox.setContentsMargins(5, 5, 0, 5)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, -1)
        splitter.setSizes([1, 330])
        mainBox.addWidget(splitter)

        self.setStyleSheet(stylepack)
        self.setAcceptDrops(True)
        self.canDrop = True

        self.resetLang = False
        global first_run, reset_lang
        if first_run or reset_lang:
            self.aboutWindow.show()
            first_run = False
        else:
            # self.aboutWindow.show()
            # self.blendWindow.show()
            self.mainMenu.show()

        self.timer = QtCore.QTimer(self)
        self.timer_ffmpeg = QtCore.QTimer(self)
        self.timer_ffmpeg.timeout.connect(self.ffmpegCheck)
        self.timer_ffmpeg.start(1000)
        self.error_log = 0
        self.isRunning = False
        self.stopWatch = time.time()
        self.time_cache = ""

    def ffmpegCheck(self):
        if not self.fb.ffmpegCheck():
            showInfo(self, self.lang["Notice"], self.lang["FFMPEG not found, please install FFMPEG!"])
        self.timer_ffmpeg.disconnect()
        self.timer_ffmpeg.stop()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.fileEvent(url.toLocalFile())
            break

    def fileEvent(self, path):
        if self.canDrop:
            suffix = getFileSuffix(path)[1:].lower()
            if suffix in self.audio_formats_arr or suffix in self.video_formats_arr:
                self.mainMenu.le_audio_path.setText(path)
                self.mainMenu.checkFilePath()
            elif suffix in self.image_formats_arr:
                self.imageSelector.selector1.fileEvent(path)
            else:
                showInfo(self, self.lang["Notice"], self.lang["Sorry, this file is not supported!"])

    def hideAllMenu(self):
        self.mainMenu.hide()
        self.imageSelector.hide()
        self.audioSetting.hide()
        self.videoSetting.hide()
        self.textWindow.hide()
        self.imageSetting.hide()
        self.spectrumColor.hide()
        self.spectrumStyle.hide()
        self.blendWindow.hide()
        self.aboutWindow.hide()

    def setAll(self):
        self.fb.setFilePath(image_path=self.vdic["image_path"],
                            bg_path=self.vdic["bg_path"],
                            sound_path=self.vdic["sound_path"],
                            logo_path=self.vdic["logo_path"])
        self.fb.setOutputPath(output_path=self.vdic["output_path"],
                              filename=self.vdic["filename"])
        self.fb.setText(text=self.vdic["text"], font=self.vdic["font"], relsize=self.vdic["relsize"],
                        text_color=self.vdic["text_color"], text_glow=self.vdic["text_glow"])
        self.fb.setSpec(bins=self.vdic["bins"], lower=self.vdic["lower"], upper=self.vdic["upper"],
                        color=self.vdic["color"], bright=self.vdic["bright"], saturation=self.vdic["saturation"],
                        scalar=self.vdic["scalar"], smooth=self.vdic["smooth"],
                        style=self.vdic["style"], linewidth=self.vdic["linewidth"])
        self.fb.setVideoInfo(width=self.vdic["width"], height=self.vdic["height"],
                             fps=self.vdic["fps"], br_Mbps=self.vdic["br_Mbps"],
                             blur_bg=self.vdic["blur_bg"], use_glow=self.vdic["use_glow"],
                             bg_mode=self.vdic["bg_mode"], rotate=self.vdic["rotate"])
        self.fb.setAudioInfo(normal=self.vdic["normal"], br_kbps=self.vdic["br_kbps"])

    def refreshAll(self):
        self.setBusy(True)
        self.setAll()
        self.viewer.imshow(self.fb.previewBackground(localViewer=False, forceRefresh=True))
        self.setBusy(False)

    def refreshLocal(self):
        self.setBusy(True)
        self.fb.setText(text=self.vdic["text"], font=self.vdic["font"], relsize=self.vdic["relsize"],
                        text_color=self.vdic["text_color"], text_glow=self.vdic["text_glow"])
        self.fb.setSpec(bins=self.vdic["bins"], lower=self.vdic["lower"], upper=self.vdic["upper"],
                        color=self.vdic["color"], bright=self.vdic["bright"], saturation=self.vdic["saturation"],
                        scalar=self.vdic["scalar"], smooth=self.vdic["smooth"],
                        style=self.vdic["style"], linewidth=self.vdic["linewidth"])
        self.viewer.imshow(self.fb.previewBackground(localViewer=False))
        self.setBusy(False)

    def vdicBackup(self):
        self.vdic_stack.append(self.vdic)

    def setBusy(self, busyFlag):
        if busyFlag:
            self.setWindowTitle(" ".join([self.windowName, self.lang["(Computing...)"]]))
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(self.windowName)

    def getBrief(self):
        brief = "<p>"
        brief += "<font color=#437BB5>" + self.lang["Output Path:"] + "</font><br/>"
        if self.vdic["bg_mode"] >= 0:
            output = self.vdic["output_path"] + convertFileFormat(self.vdic["filename"], "mp4")
        else:
            output = self.vdic["output_path"] + convertFileFormat(self.vdic["filename"], "mov")
        brief += "<u>" + output + "</u><br/><br/>"
        brief += "<font color=#437BB5>" + self.lang["Audio Path:"] + "</font><br/>"
        brief += "<u>" + self.vdic["sound_path"] + "</u><br/></p>"
        brief += "<p>"
        brief += "<font color=#437BB5>" + self.lang["Video Settings:"] + "</font><br/>"
        brief += self.lang["Video Size:"] + " " + str(self.vdic["width"]) + "x" + str(self.vdic["height"]) + "<br/>"
        brief += self.lang["FPS:"] + " " + str(self.vdic["fps"]) + "<br/>"
        brief += self.lang["Video BR:"] + " " + str(self.vdic["br_Mbps"]) + " (Mbps)<br/>"
        brief += self.lang["Audio BR:"] + " " + str(self.vdic["br_kbps"]) + " (kbps)<br/>"
        brief += self.lang["Volume Normalize:"] + " "
        if self.vdic["normal"]:
            brief += "<font color=#40874A>" + self.lang["ON"] + "</font>"
        else:
            brief += self.lang["OFF"]
        brief += "<br/>"
        brief += self.lang["Analyzer Range:"] + " " + str(self.vdic["lower"]) + " ~ " + str(
            self.vdic["upper"]) + " Hz<br/>"
        brief += self.lang["Spectrum Stabilize:"] + " " + str(self.vdic["smooth"]) + "<br/>"
        for key, item in self.imageSetting.items_bg_mode.items():
            if [self.vdic["blur_bg"], self.vdic["bg_mode"]] == item:
                brief += self.lang["BG Mode:"] + " " + key
                break

        brief += "</p>"
        return brief

    def getIntro(self):
        intro = "<h4>" + self.lang["Version: "] + "<font color=#9C9642>" + __version__ + "</font></h4>"
        intro += "{0}<br/>".format(self.lang["Project Website: "])
        intro += """
        <a href="https://github.com/FerryYoungFan/FanselineVisualizer">
        <font color=#437BB5><u> https://github.com/FerryYoungFan/FanselineVisualizer </u></font></a>
        <br/><br/>
        """
        intro += "{0}<br/>".format(self.lang["Support me if you like this application:"])
        intro += """
                <a href="https://afdian.net/@Fanseline">
                <font color=#437BB5><u> https://afdian.net/@Fanseline </u></font></a>
                <br/><br/>
                """
        intro += "{0}<br/>".format(self.lang["About me:"])
        intro += """
                    <a href="https://github.com/FerryYoungFan">
                    <font color=#437BB5><u>GitHub</u></font></a> &nbsp;&nbsp;&nbsp;&nbsp;
                    <a href="https://twitter.com/FanKetchup">
                    <font color=#437BB5><u>Twitter</u></font></a> &nbsp;&nbsp;&nbsp;&nbsp;
                    <a href="https://www.pixiv.net/users/22698030"> 
                    <font color=#437BB5><u>Pixiv</u></font></a>
                    <hr>
                    """
        intro += "{0}<br/>".format(self.lang["Special thanks to:"])
        intro += """
                <a href="https://www.matataki.io/user/526">
                <font color=#437BB5><u>小岛美奈子</u></font></a> &nbsp;&nbsp;&nbsp;&nbsp;
                <a href="https://twitter.com/dougiedoggies">
                <font color=#437BB5><u>Dougie Doggies</u></font></a><br/>
                <a href="https://twitter.com/kagurazakayashi">
                <font color=#437BB5><u>神楽坂雅詩</u></font></a> &nbsp;&nbsp;&nbsp;&nbsp;
                <br/>
                """
        intro += "{0}<br/>".format(self.lang["... and all people who support me!"])
        return intro

    def startBlending(self):
        self.setAll()
        saveConfig()
        self.infoBridge = InfoBridge(self)
        self.fb.setConsole(self.infoBridge)
        self.error_log = 0
        self.isRunning = True
        self.timer.timeout.connect(self.realTimePreview)
        self.timer.start(200)
        self.stopWatch = time.time()
        self.time_cache = ""

        th_blend = threading.Thread(target=self.fb.runBlending)
        th_blend.setDaemon(True)
        th_blend.start()

    def stopBlending(self):
        self.fb.isRunning = False
        self.error_log = -1

    def realTimePreview(self):
        info = self.getBrief()
        if self.infoBridge.total != 0:
            self.blendWindow.prgbar.setValue(int(self.infoBridge.value / self.infoBridge.total * 1000))
        else:
            self.blendWindow.prgbar.setValue(0)
        if self.fb.isRunning or self.isRunning:
            if self.infoBridge.img_cache is not None:
                self.viewer.imshow(self.infoBridge.img_cache)
                self.infoBridge.img_cache = None
                if self.infoBridge.value > 0:
                    elapsed = time.time() - self.stopWatch
                    blended = self.infoBridge.value
                    togo = self.infoBridge.total - self.infoBridge.value
                    time_remain = secondToTime(elapsed / blended * togo)
                    self.time_cache = self.lang["Remaining Time:"] + " " + time_remain + "<br/>"

            if self.time_cache != "":
                info += "<font color=#437BB5>" + self.lang["Rendering:"] + " " + str(
                    self.infoBridge.value) + " / " + str(self.infoBridge.total) + "</font><br/>"
                info += self.time_cache
            else:
                info += "<font color=#437BB5>" + self.lang["Analyzing Audio..."] + "</font><br/>"

            info += self.lang["Elapsed Time:"] + " " + secondToTime(time.time() - self.stopWatch) + "<br/>"

            if self.infoBridge.value >= self.infoBridge.total:
                info += self.lang["Compositing Audio..."]

            self.blendWindow.textview.setHtml(info)
            self.blendWindow.textview.moveCursor(QtGui.QTextCursor.End)
        else:
            print("error log:" + str(self.error_log))
            if self.error_log == -1:
                info += "<h3><font color=#9C9642>" + self.lang["Rendering Aborted!"] + "</font></h3>"
            elif self.error_log == 1:
                showInfo(self, self.lang["Notice"], self.lang["Sorry, this audio file is not supported!"])
                info += "<h3><font color=#B54643>" + self.lang["Rendering Aborted!"] + "</font></h3>"
            elif self.error_log == 2:
                showInfo(self, self.lang["Notice"], self.lang["FFMPEG not found, please install FFMPEG!"])
                info += "<h3><font color=#B54643>" + self.lang["Rendering Aborted!"] + "</font></h3>"
            else:
                info += "<h3><font color=#40874A>" + self.lang["Mission Complete!"] + "</font></h3>"

                self.error_log = 0
            info += self.lang["Elapsed Time:"] + " " + secondToTime(time.time() - self.stopWatch) + "<br/>"
            self.blendWindow.textview.setHtml(info)
            self.blendWindow.textview.moveCursor(QtGui.QTextCursor.End)
            self.timer.stop()
            self.timer.disconnect()

    def closeEvent(self, event):
        global close_app
        if self.isRunning:
            showInfo(self, self.lang["Notice"], self.lang["Please stop rendering before quit!"])
            event.ignore()
        elif self.resetLang:
            global reset_lang
            reset_lang = True
            saveConfig()
            close_app = False
            event.accept()
        else:
            saveConfig()
            close_app = True
            event.accept()


def secondToTime(time_sec):
    hour = int(time_sec // 3600)
    minute = int((time_sec - hour * 3600) // 60)
    second = int((time_sec - hour * 3600 - minute * 60) // 1)
    if hour < 10:
        hour = "0" + str(hour)
    if minute < 10:
        minute = "0" + str(minute)
    if second < 10:
        second = "0" + str(second)
    return str(hour) + ":" + str(minute) + ":" + str(second)


config_path = getPath("FVConfig.fconfig")
config = None
lang_code = "en"
lang = lang_en
vdic_pre = {
    "image_path": getPath("Source/fallback.png"),
    "bg_path": None,
    "sound_path": None,
    "logo_path": getPath("Source/logo.png"),
    "output_path": None,
    "filename": None,
    "text": "Fanseline Visualizer",
    "font": getPath("Source/font.otf"),
    "relsize": 1.0,
    "text_color": (255, 255, 255, 255),
    "text_glow": True,
    "bins": 48,
    "lower": 48,
    "upper": 4000,
    "color": "color4x",
    "bright": 0.6,
    "saturation": 0.5,
    "scalar": 1.0,
    "smooth": 5,
    "style": 0,
    "linewidth": 1.0,
    "width": 480,
    "height": 480,
    "fps": 30.0,
    "br_Mbps": 1.0,
    "blur_bg": True,
    "use_glow": False,
    "bg_mode": 0,
    "rotate": 0,
    "normal": False,
    "br_kbps": 320,
}
vdic = vdic_pre
close_app = False
first_run = True
reset_lang = False


def loadConfig():
    global config, lang, lang_code, vdic, first_run
    try:
        with open(config_path, "rb") as handle:
            config = pickle.load(handle)
            if config["__version__"] != __version__:
                raise Exception("VersionError")
            lang_code = config["lang_code"]
            print(config)
            first_run = False
    except:
        print("no config")
        return False
    vdic = config["vdic"]
    if lang_code == "cn_s":
        lang = lang_cn_s
    else:
        lang = lang_en


def saveConfig():
    global config, lang, lang_code, vdic, vdic_pre, appMainWindow
    try:
        lang_code = appMainWindow.lang_code
        vdic = appMainWindow.vdic
    except:
        vdic = vdic_pre
        lang_code = "en"

    config = {
        "__version__": __version__,
        "lang_code": lang_code,
        "vdic": vdic,
    }
    try:
        with open(config_path, 'wb') as handle:
            pickle.dump(config, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(config_path, "rb") as handle:
            config_test = pickle.load(handle)
            if config_test["__version__"] != __version__:
                raise Exception("AuthorityError")
    except:
        showInfo(appMainWindow, appMainWindow.lang["Notice"], appMainWindow.lang["Error! Cannot save config!"])


if __name__ == '__main__':
    appMainWindow = None
    app = QtWidgets.QApplication(sys.argv)


    def startMain():
        global appMainWindow, lang, vdic, first_run
        loadConfig()
        appMainWindow = MainWindow(lang, vdic, lang_code, first_run)
        appMainWindow.resize(1024, 700)
        appMainWindow.show()
        appMainWindow.refreshAll()


    while not close_app:
        startMain()
        app.exec_()

    sys.exit()
