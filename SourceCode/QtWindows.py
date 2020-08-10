#!/usr/bin/env python
# -*- coding: utf-8 -*-

from QtWheels import *
import os
from FanWheels_PIL import hsv_to_rgb, rgb_to_hsv


class MainMenu(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MainMenu, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        VBlayout = QtWidgets.QVBoxLayout(self)

        VBlayout.addWidget(genLabel(self, self.lang["Audio"]))
        self.le_audio_path = LineEdit(self, self.lang["<Please open an audio file>"], self.checkFilePath)
        VBlayout.addWidget(self.le_audio_path)

        self.btn_audio = genButton(self, self.lang["Select Audio"], None, self.btn_audio_release, style=2)
        self.btn_audio.setIcon(pil2icon(img_pack["select_audio"]))
        VBlayout.addWidget(self.btn_audio)

        self.btn_audio_set = genButton(self, self.lang["Audio Settings"], None, self.btn_audio_set_release)
        self.btn_audio_set.setIcon(pil2icon(img_pack["audio_settings"]))
        VBlayout.addWidget(self.btn_audio_set)

        VBlayout.addWidget(genLabel(self, self.lang["Video"]))

        self.btn_images = genButton(self, self.lang["Select Images"], None, self.btn_images_release, style=2)
        self.btn_images.setIcon(pil2icon(img_pack["select_image"]))
        VBlayout.addWidget(self.btn_images)

        self.btn_image_set = genButton(self, self.lang["Image Settings"], None, self.btn_image_set_release)
        self.btn_image_set.setIcon(pil2icon(img_pack["image_settings"]))
        VBlayout.addWidget(self.btn_image_set)

        self.btn_text_set = genButton(self, self.lang["Text Settings"], None, self.btn_text_set_release)
        self.btn_text_set.setIcon(pil2icon(img_pack["text"]))
        VBlayout.addWidget(self.btn_text_set)

        self.btn_video_set = genButton(self, self.lang["Video Settings"], None, self.btn_video_set_release)
        self.btn_video_set.setIcon(pil2icon(img_pack["video_settings"]))
        VBlayout.addWidget(self.btn_video_set)

        VBlayout.addWidget(genLabel(self, self.lang["Spectrum"]))

        self.btn_spec_style = genButton(self, self.lang["Spectrum Style"], None, self.btn_spec_style_release)
        self.btn_spec_style.setIcon(pil2icon(img_pack["spectrum"]))
        VBlayout.addWidget(self.btn_spec_style)

        self.btn_spec_color = genButton(self, self.lang["Spectrum Color"], None, self.btn_spec_color_release)
        self.btn_spec_color.setIcon(pil2icon(img_pack["color"]))
        VBlayout.addWidget(self.btn_spec_color)

        VBlayout.addWidget(genLabel(self, self.lang["Render"]))

        self.btn_blend = genButton(self, self.lang["Ready to Render"], None, self.btn_blend_release, "F5", style=4)
        self.btn_blend.setIcon(pil2icon(img_pack["run"]))
        VBlayout.addWidget(self.btn_blend)

        self.btn_about = genButton(self, self.lang["About FVisualizer"], None, self.btn_about_release)
        self.btn_about.setIcon(pil2icon(img_pack["info"]))
        VBlayout.addWidget(self.btn_about)

        VBlayout.setSpacing(4)
        VBlayout.setContentsMargins(0, 0, 0, 0)

        self.audio_formats = self.parent.audio_formats
        self.audio_formats_arr = self.parent.audio_formats_arr
        self.video_formats = self.parent.video_formats
        self.video_formats_arr = self.parent.video_formats_arr

    def show(self):
        self.parent.hideAllMenu()
        self.showAudioFilePath()
        super().show()

    def checkFilePath(self):
        if self.le_audio_path.text() == "":
            self.parent.vdic["sound_path"] = None
            return
        isAudio = isValidFormat(self.le_audio_path.text(), self.audio_formats_arr)
        isVideo = isValidFormat(self.le_audio_path.text(), self.video_formats_arr)
        if (not (isAudio or isVideo)) or (not os.path.isfile(self.le_audio_path.text())):
            showInfo(self, self.lang["Cannot Render"], self.lang["Please select the correct audio file!"], False)
            self.le_audio_path.setText(self.parent.vdic["sound_path"])
        else:
            self.parent.vdic["sound_path"] = self.le_audio_path.text()
            self.parent.vdic["filename"] = getFileName(self.le_audio_path.text(), False) + self.lang[
                "_Visualize"] + ".mp4"
            if not self.parent.vdic["output_path"]:
                self.parent.vdic["output_path"] = getFilePath(self.le_audio_path.text())

    def btn_images_release(self):
        self.parent.imageSelector.show()

    def btn_image_set_release(self):
        self.parent.imageSetting.show()

    def btn_audio_release(self):
        selector = self.lang["Audio Files"] + self.audio_formats
        selector = selector + self.lang["Video Files"] + self.video_formats
        selector = selector + self.lang["All Files"] + " (*.*)"
        if self.parent.vdic["sound_path"]:
            dir_in = getFilePath(self.parent.vdic["sound_path"])
        else:
            dir_in = ""

        file_, filetype = QtWidgets.QFileDialog.getOpenFileName(self, self.lang["Select Audio File"], dir_in, selector)
        if not file_:
            print("No File!")
        else:
            self.parent.vdic["sound_path"] = file_
            self.parent.vdic["filename"] = getFileName(file_, False) + self.lang["_Visualize"] + ".mp4"
            self.showAudioFilePath()

    def btn_audio_set_release(self):
        self.parent.audioSetting.show()

    def btn_text_set_release(self):
        self.parent.textWindow.show()

    def btn_spec_color_release(self):
        self.parent.spectrumColor.show()

    def btn_spec_style_release(self):
        self.parent.spectrumStyle.show()

    def btn_video_set_release(self):
        self.parent.videoSetting.show()

    def btn_blend_release(self):
        self.checkFilePath()
        if self.parent.vdic["sound_path"] is not None:
            if os.path.isfile(self.parent.vdic["sound_path"]):
                self.parent.blendWindow.show()
                return
        else:
            showInfo(self, self.lang["Cannot Render"], self.lang["Please select the correct audio file!"])

    def btn_about_release(self):
        self.parent.aboutWindow.show()

    def showAudioFilePath(self):
        if self.parent.vdic["sound_path"] is not None:
            self.le_audio_path.setText(self.parent.vdic["sound_path"].replace("\\", "/"))
        else:
            self.le_audio_path.setText("")


class AudioSettingWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(AudioSettingWindow, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setAlignment(QtCore.Qt.AlignTop)

        items_bra = [("320 kbps", 320), ("256 kbps", 256), ("192 kbps", 192),
                     ("128 kbps", 128), ("96 kbps", 96), ("64 kbps", 64), ("48 kbps", 48)]
        self.combo_bra = ComboBox(self, items_bra, self.combo_bra_select, self.lang["Audio Bit Rate"])
        VBlayout.addWidget(self.combo_bra)

        VBlayout.addWidget(HintLabel(self, self.lang["Volume Normalize"], 2, img_pack["what"],
                                     self.lang["Adjust audio volume according to EBU R128 loudness standard."]))

        self.ck_normal = QSwitch(self)
        self.ck_normal.released.connect(self.ck_normal_release)
        VBlayout.addWidget(self.ck_normal)

        items_prea = {
            self.lang["-Please Select-"]: -1,
            self.lang["Pop Music"]: [32, 12000, False],
            self.lang["Classical Music"]: [40, 7200, False],
            self.lang["Calm Music"]: [56, 2400, False],
            self.lang["Orchestral Music"]: [42, 12000, False],
            self.lang["Piano: Narrow Band"]: [55, 2100, False],
            self.lang["Piano: Wide Band"]: [42, 4400, False],
            self.lang["Violin"]: [150, 4000, False],
            self.lang["Guitar"]: [80, 2200, False],
            self.lang["Natural Sound"]: [32, 15000, False],
            self.lang["Voice"]: [100, 2200, True],
        }
        self.combo_prea = ComboBox(self, items_prea, self.combo_prea_select, self.lang["Frequency Analyzer Preset"])
        VBlayout.addWidget(self.combo_prea)

        VBlayout.addWidget(HintLabel(self, self.lang["Analyzer Frequency Range (Hz)"], 2, img_pack["what"],
                                     self.lang[
                                         "Visualized spectrum will be generated according to this frequency range."]))

        self.le_lower = LineEdit(self, self.lang["<FFT Lower>"], self.crossCheckLower, [16, 22050], True, scroll=50)
        self.le_upper = LineEdit(self, self.lang["<FFT Upper>"], self.crossCheckUpper, [16, 22050], True, scroll=50)

        HBlayout = QtWidgets.QHBoxLayout()

        HBlayout.addWidget(self.le_lower)
        label_to = genLabel(self, self.lang["to"])
        label_to.setAlignment(QtCore.Qt.AlignTop)
        HBlayout.addWidget(label_to)
        HBlayout.addWidget(self.le_upper)

        VBlayout.addLayout(HBlayout)

        VBlayout.setAlignment(QtCore.Qt.AlignBottom)
        btn_back = genButton(self, self.lang["Back to Main Menu"], None, self.btn_back_release, "Escape")
        btn_back.setIcon(pil2icon(img_pack["back"]))
        VBlayout.addWidget(btn_back)

        VBlayout.setSpacing(15)
        VBlayout.setContentsMargins(0, 0, 0, 0)

    def combo_prea_select(self):
        preseta = self.combo_prea.getValue()
        if preseta != -1:
            self.le_lower.setText(str(preseta[0]))
            self.le_upper.setText(str(preseta[1]))
            self.ck_normal.setChecked(preseta[2])
            self.parent.vdic["br_kbps"] = self.combo_bra.getValue()
            self.parent.vdic["lower"] = self.le_lower.numCheck()
            self.parent.vdic["upper"] = self.le_upper.numCheck()
            self.parent.vdic["normal"] = self.ck_normal.isChecked()

    def combo_bra_select(self):
        self.parent.vdic["br_kbps"] = self.combo_bra.getValue()

    def show(self):
        self.parent.hideAllMenu()
        self.combo_bra.setValue(self.parent.vdic["br_kbps"])
        self.combo_prea.setValue(-1)
        self.combo_prea.setValue([self.parent.vdic["lower"], self.parent.vdic["upper"], self.parent.vdic["normal"]])
        self.ck_normal.setChecked(self.parent.vdic["normal"])
        self.le_lower.setText(str(self.parent.vdic["lower"]))
        self.le_upper.setText(str(self.parent.vdic["upper"]))
        super().show()

    def crossCheckLower(self):
        if self.le_lower.numCheck() >= self.le_upper.numCheck():
            self.le_upper.setText(str(self.le_lower.numCheck() + 1))
        self.parent.vdic["lower"] = self.le_lower.numCheck()
        self.parent.vdic["upper"] = self.le_upper.numCheck()

    def crossCheckUpper(self):
        if self.le_lower.numCheck() >= self.le_upper.numCheck():
            self.le_lower.setText(str(self.le_upper.numCheck() - 1))
        self.parent.vdic["lower"] = self.le_lower.numCheck()
        self.parent.vdic["upper"] = self.le_upper.numCheck()

    def ck_normal_release(self):
        self.parent.vdic["normal"] = self.ck_normal.isChecked()

    def btn_back_release(self):
        self.parent.mainMenu.show()


class VideoSettingWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(VideoSettingWindow, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setAlignment(QtCore.Qt.AlignTop)

        items_prev = {
            self.lang["-Please Select-"]: -1,
            self.lang["Square"] + " (1080x1080)": [1080, 1080, 30, self.getDefaultBR(1080, 1080, 30, 5)],
            self.lang["Square"] + " (1024x1024)": [1024, 1024, 30, self.getDefaultBR(1024, 1024, 30, 5)],
            self.lang["Square"] + " (720x720)": [720, 720, 30, self.getDefaultBR(720, 720, 30, 4)],
            self.lang["Square"] + " (512x512)": [512, 512, 30, self.getDefaultBR(512, 512, 30, 4)],
            self.lang["Square"] + " (480x480)": [480, 480, 30, self.getDefaultBR(480, 480, 30, 4)],
            self.lang["Landscape"] + " (1920x1080)": [1920, 1080, 30, self.getDefaultBR(1920, 1080, 30, 5)],
            self.lang["Landscape"] + " (1280x720)": [1280, 720, 30, self.getDefaultBR(1280, 720, 30, 4)],
            self.lang["Landscape"] + " (854x480)": [854, 480, 30, self.getDefaultBR(854, 480, 30, 4)],
            self.lang["Portrait"] + " (1080x1920)": [1080, 1920, 30, self.getDefaultBR(1920, 1080, 30, 5)],
            self.lang["Portrait"] + " (720x1280)": [720, 1280, 30, self.getDefaultBR(1280, 720, 30, 4)],
            self.lang["Portrait"] + " (480x854)": [480, 854, 30, self.getDefaultBR(854, 480, 30, 4)],
            "2k (2560x1440)": [2560, 1440, 30, self.getDefaultBR(2560, 1440, 30, 5)],
        }
        self.combo_prev = ComboBox(self, items_prev, self.combo_prev_select, self.lang["Video Preset"])
        VBlayout.addWidget(self.combo_prev)

        self.items_quality = {
            self.lang["Very Low"] + " (1x, 1x)": 1,
            self.lang["Low"] + " (2x, 2x)": 2,
            self.lang["Medium - Default"] + " (2x, 4x)": 3,
            self.lang["High"] + " (4x, 8x)": 4,
            self.lang["Very High"] + " (8x, 8x)": 5,
        }
        self.combo_quality = ComboBox(self, self.items_quality, self.combo_quality_select, self.lang["Render Quality"])
        VBlayout.addWidget(self.combo_quality)

        VBlayout.addWidget(genLabel(self, self.lang["Frame Size"]))
        self.le_width = LineEdit(self, self.lang["<Width>"], self.setVideoSize, [16, 4096], True, scroll=100)
        self.le_height = LineEdit(self, self.lang["<Height>"], self.setVideoSize, [16, 4096], True, scroll=100)

        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.addWidget(self.le_width)
        label_to = genLabel(self, "x")
        label_to.setAlignment(QtCore.Qt.AlignTop)
        HBlayout.addWidget(label_to)
        HBlayout.addWidget(self.le_height)
        VBlayout.addLayout(HBlayout)

        VBlayout.addWidget(genLabel(self, self.lang["Frame Rate (FPS)"]))
        self.le_fps = LineEdit(self, self.lang["<FPS>"], self.setFps, [1.0, 120], False, scroll=1)
        VBlayout.addWidget(self.le_fps)

        VBlayout.addWidget(genLabel(self, self.lang["Video Bit Rate (Mbps)"]))
        self.le_brv = LineEdit(self, self.lang["<Bit Rate>"], self.setBRV, [0.01, 200], False, scroll=0.1)
        VBlayout.addWidget(self.le_brv)

        VBlayout.addWidget(genLabel(self, self.lang["Auto Video Bit Rate"]))
        self.ck_auto = QSwitch(self)
        self.ck_auto.released.connect(self.autoBitRate)
        VBlayout.addWidget(self.ck_auto)
        self.ck_auto.setChecked(True)

        VBlayout.setAlignment(QtCore.Qt.AlignBottom)
        btn_back = genButton(self, self.lang["Back to Main Menu"], None, self.btn_back_release, "Escape")
        btn_back.setIcon(pil2icon(img_pack["back"]))
        VBlayout.addWidget(btn_back)

        VBlayout.setContentsMargins(0, 0, 0, 0)

    def combo_quality_select(self):
        quality = self.combo_quality.getValue()
        self.parent.vdic["quality"] = quality
        if self.isVisible():
            self.parent.refreshAll()

    def combo_prev_select(self):
        presetv = self.combo_prev.getValue()
        if presetv != -1:
            self.le_width.setText(str(presetv[0]))
            self.le_height.setText(str(presetv[1]))
            self.le_fps.setText(str(presetv[2]))
            self.le_brv.setText(str(presetv[3]))

            self.parent.vdic["width"] = self.le_width.numCheck()
            self.parent.vdic["height"] = self.le_height.numCheck()
            self.parent.vdic["fps"] = self.le_fps.numCheck()
            self.parent.vdic["br_Mbps"] = self.le_brv.numCheck()

            self.le_brv.focusOutEvent()
            if self.isVisible():
                self.parent.refreshAll()

    def setVideoSize(self):
        self.parent.vdic["width"] = self.le_width.numCheck()
        self.parent.vdic["height"] = self.le_height.numCheck()
        if self.isVisible():
            self.parent.refreshAll()
        self.autoBitRate()

    def setFps(self):
        self.parent.vdic["fps"] = self.le_fps.numCheck()
        self.autoBitRate()

    def setBRV(self):
        self.parent.vdic["br_Mbps"] = self.le_brv.numCheck()

    def autoBitRate(self):
        if self.ck_auto.isChecked():
            brv = self.getDefaultBR(self.le_width.numCheck(), self.le_height.numCheck(), self.le_fps.numCheck(), 4)
            self.le_brv.setText(str(brv))
            self.le_brv.setText(str(self.le_brv.numCheck()))
            self.le_brv.clearFocus()

    def getDefaultBR(self, width, height, fps, quality=3):
        if quality == 5:
            return 20 * (width * height * fps) / (1920 * 1080 * 30)
        elif quality == 4:
            return 12 * (width * height * fps) / (1920 * 1080 * 30)
        elif quality == 3:
            return 7 * (width * height * fps) / (1920 * 1080 * 30)
        elif quality == 2:
            return 2 * (width * height * fps) / (1920 * 1080 * 30)
        elif quality == 1:
            return (width * height * fps) / (1920 * 1080 * 30)
        elif quality == 0:
            return 0.5 * (width * height * fps) / (1920 * 1080 * 30)
        else:
            return 12 * (width * height * fps) / (1920 * 1080 * 30)

    def show(self):
        self.parent.hideAllMenu()
        self.combo_prev.setValue(-1)
        self.combo_quality.setValue(self.parent.vdic["quality"])
        self.le_width.setText(str(self.parent.vdic["width"]))
        self.le_height.setText(str(self.parent.vdic["height"]))
        self.le_brv.setText(str(self.parent.vdic["br_Mbps"]))
        self.le_fps.setText(str(self.parent.vdic["fps"]))
        super().show()

    def btn_back_release(self):
        self.parent.mainMenu.show()


class TextWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(TextWindow, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        self.oldColor = self.parent.vdic["text_color"]
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setAlignment(QtCore.Qt.AlignTop)

        VBlayout.addWidget(genLabel(self, self.lang["Edit Text"]))

        self.le_text = LineEdit(self, self.lang["<Your text here>"], self.setMainText)
        VBlayout.addWidget(self.le_text)

        self.btn_filename = genButton(self, self.lang["Use File Name"], None, self.btn_filename_release)
        self.btn_filename.setIcon(pil2icon(img_pack["file"]))
        VBlayout.addWidget(self.btn_filename)

        self.btn_clear = genButton(self, self.lang["Clear Text"], None, self.btn_clear_release, style=5)
        self.btn_clear.setIcon(pil2icon(img_pack["delete"]))
        VBlayout.addWidget(self.btn_clear)

        VBlayout.addWidget(genLabel(self, self.lang["Text Settings"]))

        self.sl_font = FSlider(self, self.lang["Font Size"], 0.3, 5.0, 0.1, 1.0, self.sl_font_release, None)
        VBlayout.addWidget(self.sl_font)

        self.btn_color = genButton(self, self.lang["Select Color"], None, self.btn_color_release)
        self.btn_color.setIcon(pil2icon(img_pack["color"]))
        VBlayout.addWidget(self.btn_color)

        self.le_font_path = LineEdit(self, self.lang["<Please open a font file>"], self.checkFont)
        VBlayout.addWidget(self.le_font_path)

        self.btn_font = genButton(self, self.lang["Select Font"], None, self.btn_font_release, style=2)
        self.btn_font.setIcon(pil2icon(img_pack["font"]))
        VBlayout.addWidget(self.btn_font)

        VBlayout.addWidget(genLabel(self, self.lang["Glow Text"]))
        self.ck_glow_text = QSwitch(self)
        self.ck_glow_text.released.connect(self.ck_glow_text_release)
        VBlayout.addWidget(self.ck_glow_text)

        btn_back = genButton(self, self.lang["Back to Main Menu"], None, self.btn_back_release, "Escape")
        btn_back.setIcon(pil2icon(img_pack["back"]))
        VBlayout.addWidget(btn_back)

        VBlayout.setContentsMargins(0, 0, 0, 0)

    def setMainText(self):
        self.parent.vdic["text"] = self.le_text.text()
        self.parent.refreshLocal()

    def btn_filename_release(self):
        if self.parent.vdic["filename"]:
            self.le_text.setText(getFileName(self.parent.vdic["sound_path"], False))
            self.setMainText()

    def btn_clear_release(self):
        self.le_text.setText("")
        self.setMainText()

    def sl_font_release(self):
        self.parent.vdic["relsize"] = self.sl_font.getValue()
        self.parent.refreshLocal()

    def checkFont(self):
        if self.le_font_path.text() is not None:
            self.parent.vdic["font"] = self.le_font_path.text()
        self.parent.refreshLocal()

    def btn_font_release(self):
        selector = self.lang["Font Files"] + " (*.ttf;*.otf);;"
        selector = selector + self.lang["All Files"] + " (*.*)"

        font_dir = ""
        if os.path.exists(self.parent.vdic["font"]):
            font_dir = self.parent.vdic["font"]

        file_, filetype = QtWidgets.QFileDialog.getOpenFileName(self, self.lang["Select Font File"], font_dir, selector)
        if not file_:
            print("No File!")
        else:
            self.parent.vdic["font"] = file_
            self.le_font_path.setText(file_)
            self.parent.refreshLocal()

    def btn_color_release(self):
        self.oldColor = self.parent.vdic["text_color"]
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(*self.oldColor), self, self.lang["Select Color"],
                                                options=QtWidgets.QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.parent.vdic["text_color"] = color.getRgb()
            self.parent.refreshLocal()

    def ck_glow_text_release(self):
        self.parent.vdic["text_glow"] = self.ck_glow_text.isChecked()
        self.parent.refreshLocal()

    def show(self):
        self.parent.hideAllMenu()
        self.le_text.setText(self.parent.vdic["text"])
        self.sl_font.setValue(self.parent.vdic["relsize"])
        self.oldColor = self.parent.vdic["text_color"]
        self.le_font_path.setText(self.parent.vdic["font"])
        self.ck_glow_text.setChecked(self.parent.vdic["text_glow"])
        super().show()

    def btn_back_release(self):
        self.parent.mainMenu.show()


class ImageSettingWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ImageSettingWindow, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        self.oldColor = self.parent.vdic["text_color"]
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setAlignment(QtCore.Qt.AlignTop)

        self.items_bg_mode = {
            self.lang["Blurred BG Image"] + " (MP4, H264)": [True, 0],
            self.lang["Normal BG Image"] + " (MP4, H264)": [False, 0],
            self.lang["Blurred BG Only"] + " (MP4, H264)": [True, 2],
            self.lang["Normal BG Only"] + " (MP4, H264)": [False, 2],
            self.lang["Transparent"] + " (MOV, PNG)": [False, -1],
            self.lang["Spectrum Only"] + " (MOV, PNG)": [False, -2],
        }

        self.combo_bg_mode = ComboBox(self, self.items_bg_mode, self.combo_bg_mode_select, self.lang["Background Mode"])
        VBlayout.addWidget(self.combo_bg_mode)

        items_spin = {
            self.lang["No Spin"]: 0,
            self.lang["Clockwise"]: 1,
            self.lang["Counterclockwise"]: -1,
        }
        self.combo_spin = ComboBox(self, items_spin, self.combo_spin_select, self.lang["Spin Foreground"])

        VBlayout.addWidget(self.combo_spin)
        VBlayout.addWidget(genLabel(self, self.lang["Spin Speed (rpm)"]))

        self.le_speed = LineEdit(self, self.lang["<Spin Speed>"], self.combo_spin_select, [-200, 200], False, 1.0)
        VBlayout.addWidget(self.le_speed)

        VBlayout.addWidget(HintLabel(self, self.lang["Oscillate Foreground"], 2, img_pack["what"],
                                     self.lang["Oscillate FG image accroding to the bass."] + "\n\n" + \
                                     self.lang["Oscillate FG to Bass (%)"] + ": " + \
                                     self.lang["Sensitivity of the bass (beat) detector."] + "\n" + \
                                     self.lang["Bass Frequency Range (%)"] + ": " + \
                                     self.lang["Relative frequency of bass to analyzer frequency range."]
                                     ))

        self.sl_beat_detect = FSlider(self, self.lang["Oscillate FG to Bass (%)"], 0, 100, 1, 1,
                                      self.sl_beat_detect_release, None)
        VBlayout.addWidget(self.sl_beat_detect)

        self.sl_low_range = FSlider(self, self.lang["Bass Frequency Range (%)"], 0, 100, 1, 1,
                                    self.sl_low_range_release, None)
        VBlayout.addWidget(self.sl_low_range)

        btn_back = genButton(self, self.lang["Back to Main Menu"], None, self.btn_back_release, "Escape")
        btn_back.setIcon(pil2icon(img_pack["back"]))
        VBlayout.addWidget(btn_back)
        VBlayout.setContentsMargins(0, 0, 0, 0)

    def combo_bg_mode_select(self):
        bg_setv = self.combo_bg_mode.getValue()
        self.parent.vdic["blur_bg"] = bg_setv[0]
        self.parent.vdic["bg_mode"] = bg_setv[1]
        self.parent.refreshAll()

    def combo_spin_select(self):
        if self.isVisible():
            direction = self.combo_spin.getValue()
            speed = self.le_speed.numCheck()
            if speed < 0:
                speed = speed * -1
                self.le_speed.setText(str(speed))
                self.combo_spin.setValue(-1)
                direction = -1
            self.parent.vdic["rotate"] = direction * speed
            self.parent.refreshLocal()

    def sl_low_range_release(self):
        self.parent.vdic["low_range"] = self.sl_low_range.getValue()

    def sl_beat_detect_release(self):
        self.parent.vdic["beat_detect"] = self.sl_beat_detect.getValue()
        if self.sl_beat_detect.getValue() > 0:
            self.sl_low_range.setStyle(0)
        else:
            self.sl_low_range.setStyle(1)
        self.parent.refreshLocal()

    def show(self):
        self.parent.hideAllMenu()
        bg_modev = [self.parent.vdic["blur_bg"], self.parent.vdic["bg_mode"]]
        self.combo_bg_mode.setValue(bg_modev)
        if self.parent.vdic["rotate"] == 0:
            direction = 0
            speed = 0
        else:
            direction = int(abs(self.parent.vdic["rotate"]) / self.parent.vdic["rotate"])
            speed = abs(self.parent.vdic["rotate"])
        self.combo_spin.setValue(direction)
        self.le_speed.setText(str(speed))
        self.sl_low_range.setValue(self.parent.vdic["low_range"])
        self.sl_beat_detect.setValue(self.parent.vdic["beat_detect"])
        if self.sl_beat_detect.getValue() > 0:
            self.sl_low_range.setStyle(0)
        else:
            self.sl_low_range.setStyle(1)
        super().show()

    def btn_back_release(self):
        self.parent.mainMenu.show()


class SpectrumColorWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(SpectrumColorWindow, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        self.oldColor = None
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setAlignment(QtCore.Qt.AlignTop)

        color_dic = {
            self.lang["Customize"]: None,
            self.lang["Gray"]: "gray",
            self.lang["White"]: "white",
            self.lang["Black"]: "black",
            self.lang["Red"]: "red",
            self.lang["Green"]: "green",
            self.lang["Blue"]: "blue",
            self.lang["Yellow"]: "yellow",
            self.lang["Magenta"]: "magenta",
            self.lang["Purple"]: "purple",
            self.lang["Cyan"]: "cyan",
            self.lang["Light Green"]: "lightgreen",
            self.lang["Green - Blue"]: "green-blue",
            self.lang["Magenta - Purple"]: "magenta-purple",
            self.lang["Red - Yellow"]: "red-yellow",
            self.lang["Yellow - Green"]: "yellow-green",
            self.lang["Blue - Purple"]: "blue-purple",
            self.lang["Rainbow 1x"]: "color1x",
            self.lang["Rainbow 2x"]: "color2x",
            self.lang["Rainbow 4x"]: "color4x",

        }
        self.combo_color = ComboBox(self, color_dic, self.combo_color_select, self.lang["Spectrum Color"])
        VBlayout.addWidget(self.combo_color)

        self.btn_color = genButton(self, self.lang["Customize Color"], None, self.btn_color_release)
        self.btn_color.setIcon(pil2icon(img_pack["color"]))
        VBlayout.addWidget(self.btn_color)

        self.sl_sat = FSlider(self, self.lang["Spectrum Saturation"], 0.0, 1.0, 0.01, 0.8, self.sl_sat_release, None)
        VBlayout.addWidget(self.sl_sat)

        self.sl_brt = FSlider(self, self.lang["Spectrum Brightness"], 0.0, 1.0, 0.01, 0.8, self.sl_brt_release, None)
        VBlayout.addWidget(self.sl_brt)

        VBlayout.addWidget(genLabel(self, self.lang["Glow Effect (Slow)"]))
        self.ck_glow = QSwitch(self)
        self.ck_glow.released.connect(self.ck_glow_release)
        VBlayout.addWidget(self.ck_glow)

        btn_goto = genButton(self, self.lang["Spectrum Style"], None, self.btn_goto_release)
        btn_goto.setIcon(pil2icon(img_pack["spectrum"]))
        VBlayout.addWidget(btn_goto)

        btn_back = genButton(self, self.lang["Back to Main Menu"], None, self.btn_back_release, "Escape")
        btn_back.setIcon(pil2icon(img_pack["back"]))
        VBlayout.addWidget(btn_back)
        VBlayout.setContentsMargins(0, 0, 0, 0)

    def combo_color_select(self, color_by_slider=False):
        vcolor = self.combo_color.getValue()
        if vcolor is not None:
            self.parent.vdic["color"] = vcolor
            if self.isVisible():
                self.parent.refreshLocal()
            self.sl_sat.setStyle(0)
            self.sl_brt.setStyle(0)
            self.btn_color.hide()
        else:
            self.btn_color.show()
            if not isinstance(self.parent.vdic["color"], tuple):
                self.parent.vdic["color"] = (0, 255, 255, 255)
            if color_by_slider:
                old_color = self.parent.vdic["color"]
                old_color_hsv = rgb_to_hsv(*old_color[:3])
                new_color_hsv = old_color_hsv[0], self.parent.vdic["saturation"], self.parent.vdic["bright"]
                new_color = hsv_to_rgb(*new_color_hsv)
                self.parent.vdic["color"] = new_color + (old_color[3],)
            else:
                self.sl_sat.setStyle(1)
                self.sl_brt.setStyle(1)
                color_hsv = rgb_to_hsv(*(self.parent.vdic["color"][:3]))
                self.sl_sat.setValue(color_hsv[1])
                self.sl_brt.setValue(color_hsv[2])
            if self.isVisible():
                self.parent.refreshLocal()

    def sl_sat_release(self):
        self.parent.vdic["saturation"] = self.sl_sat.getValue()
        if self.combo_color.getValue() is None:
            self.combo_color_select(True)
        else:
            self.combo_color_select()

    def sl_brt_release(self):
        self.parent.vdic["bright"] = self.sl_brt.getValue()
        if self.combo_color.getValue() is None:
            self.combo_color_select(True)
        else:
            self.combo_color_select()

    def btn_color_release(self):
        self.combo_color.setValue(None)
        if isinstance(self.parent.vdic["color"], tuple):
            self.oldColor = self.parent.vdic["color"]
        else:
            self.oldColor = (255, 255, 255, 255)
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(*self.oldColor), self, self.lang["Select Color"],
                                                options=QtWidgets.QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.parent.vdic["color"] = color.getRgb()
            color_hsv = rgb_to_hsv(*(self.parent.vdic["color"][:3]))
            self.sl_sat.setValue(color_hsv[1])
            self.sl_brt.setValue(color_hsv[2])
            self.sl_sat.setStyle(1)
            self.sl_brt.setStyle(1)
            if self.isVisible():
                self.parent.refreshLocal()

    def ck_glow_release(self):
        self.parent.vdic["use_glow"] = self.ck_glow.isChecked()
        if self.isVisible():
            self.parent.refreshAll()

    def show(self):
        self.parent.hideAllMenu()
        if isinstance(self.parent.vdic["color"], tuple):
            self.combo_color.setValue(None)
            self.sl_sat.setStyle(1)
            self.sl_brt.setStyle(1)
            color_hsv = rgb_to_hsv(*(self.parent.vdic["color"][:3]))
            self.sl_sat.setValue(color_hsv[1])
            self.sl_brt.setValue(color_hsv[2])
        else:
            self.combo_color.setValue(self.parent.vdic["color"])
            self.sl_sat.setStyle(0)
            self.sl_brt.setStyle(0)
        self.sl_sat.setValue(self.parent.vdic["saturation"])
        self.sl_brt.setValue(self.parent.vdic["bright"])
        self.ck_glow.setChecked(self.parent.vdic["use_glow"])
        super().show()

    def btn_goto_release(self):
        self.parent.spectrumStyle.show()

    def btn_back_release(self):
        self.parent.mainMenu.show()


class SpectrumStyleWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(SpectrumStyleWindow, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        self.oldColor = None
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setAlignment(QtCore.Qt.AlignTop)

        style_dic = {
            self.lang["Solid Line"]: 0,
            self.lang["Solid Line: Center"]: 19,
            self.lang["Solid Line: Reverse"]: 20,
            self.lang["Dot Line"]: 1,
            self.lang["Single Dot"]: 2,
            self.lang["Double Dot"]: 7,
            self.lang["Double Dot: Center"]: 21,
            self.lang["Double Dot: Reverse"]: 22,
            self.lang["Concentric"]: 8,
            self.lang["Line Graph"]: 17,
            self.lang["Zooming Circles"]: 18,
            self.lang["Classic Line: Center"]: 9,
            self.lang["Classic Line: Bottom"]: 10,
            self.lang["Classic Rectangle: Center"]: 15,
            self.lang["Classic Rectangle: Bottom"]: 16,
            self.lang["Classic Round Dot: Center"]: 11,
            self.lang["Classic Round Dot: Bottom"]: 12,
            self.lang["Classic Square Dot: Center"]: 13,
            self.lang["Classic Square Dot: Bottom"]: 14,
            self.lang["Stem Plot: Solid Single"]: 3,
            self.lang["Stem Plot: Solid Double"]: 4,
            self.lang["Stem Plot: Dashed Single"]: 5,
            self.lang["Stem Plot: Dashed Double"]: 6,
            self.lang["No Spectrum"]: -1,
        }

        self.combo_style = ComboBox(self, style_dic, self.combo_style_select, self.lang["Spectrum Style"])
        VBlayout.addWidget(self.combo_style)

        self.sl_bins = FSlider(self, self.lang["Spectrum Number"], 4, 200, 3, 48, self.sl_bins_release, None)
        VBlayout.addWidget(self.sl_bins)

        self.sl_linewidth = FSlider(self, self.lang["Spectrum Thickness"], 0.1, 15, 0.05, 1.0,
                                    self.sl_linewidth_release,
                                    None)
        VBlayout.addWidget(self.sl_linewidth)

        self.sl_scalar = FSlider(self, self.lang["Spectrum Scalar"], 0.02, 5.0, 0.02, 1.0, self.sl_scalar_release, None)
        VBlayout.addWidget(self.sl_scalar)

        self.sl_smooth = FSlider(self, self.lang["Spectrum Stabilize"], 0, 15, 1, 0, self.sl_smooth_release, None)
        VBlayout.addWidget(self.sl_smooth)

        btn_goto = genButton(self, self.lang["Spectrum Color"], None, self.btn_goto_release)
        btn_goto.setIcon(pil2icon(img_pack["color"]))
        VBlayout.addWidget(btn_goto)

        btn_back = genButton(self, self.lang["Back to Main Menu"], None, self.btn_back_release, "Escape")
        btn_back.setIcon(pil2icon(img_pack["back"]))
        VBlayout.addWidget(btn_back)
        VBlayout.setContentsMargins(0, 0, 0, 0)

    def combo_style_select(self):
        self.parent.vdic["style"] = self.combo_style.getValue()
        self.parent.refreshLocal()

    def sl_bins_release(self):
        self.parent.vdic["bins"] = self.sl_bins.getValue()
        self.parent.refreshLocal()

    def sl_linewidth_release(self):
        self.parent.vdic["linewidth"] = self.sl_linewidth.getValue()
        self.parent.refreshLocal()

    def sl_scalar_release(self):
        self.parent.vdic["scalar"] = self.sl_scalar.getValue()
        self.parent.refreshLocal()

    def sl_smooth_release(self):
        self.parent.vdic["smooth"] = self.sl_smooth.getValue()

    def show(self):
        self.parent.hideAllMenu()

        self.combo_style.setValue(self.parent.vdic["style"])
        self.sl_bins.setValue(self.parent.vdic["bins"])
        self.sl_linewidth.setValue(self.parent.vdic["linewidth"])
        self.sl_scalar.setValue(self.parent.vdic["scalar"])
        self.sl_smooth.setValue(self.parent.vdic["smooth"])

        super().show()

    def btn_goto_release(self):
        self.parent.spectrumColor.show()

    def btn_back_release(self):
        self.parent.mainMenu.show()


class BlendWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(BlendWindow, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setAlignment(QtCore.Qt.AlignTop)

        VBlayout.addWidget(genLabel(self, self.lang["Output Path"]))

        self.le_path = LineEdit(self, self.lang["<Output Path>"], self.enterPathCheck)
        VBlayout.addWidget(self.le_path)

        self.btn_output_path = genButton(self, self.lang["Select Path"], None, self.btn_output_path_release, style=2)
        self.btn_output_path.setIcon(pil2icon(img_pack["folder"]))
        VBlayout.addWidget(self.btn_output_path)

        VBlayout.addWidget(genLabel(self, self.lang["Output Config"]))

        self.textview = QtWidgets.QTextBrowser(self)
        VBlayout.addWidget(self.textview)
        self.textview.setStyleSheet(textBrowserStyle)
        self.textview.zoomIn(1)

        self.prgbar = QtWidgets.QProgressBar(self)
        self.prgbar.setMaximum(1000)
        self.prgbar.setMinimum(0)
        self.prgbar.setValue(0)
        self.prgbar.setStyleSheet(progressbarStyle)
        VBlayout.addWidget(self.prgbar)
        self.prgbar.hide()

        self.btn_stop = genButton(self, self.lang["Stop Rendering"], None, self.btn_stop_release, style=3)
        self.btn_stop.setIcon(pil2icon(img_pack["stop"]))
        VBlayout.addWidget(self.btn_stop)
        self.btn_stop.hide()

        self.btn_blend = genButton(self, self.lang["Start Rendering"], None, self.btn_blend_release, "Ctrl+F5", style=4)
        self.btn_blend.setIcon(pil2icon(img_pack["run"]))
        VBlayout.addWidget(self.btn_blend)

        self.btn_back = genButton(self, self.lang["Back to Main Menu"], None, self.btn_back_release, "Escape")
        self.btn_back.setIcon(pil2icon(img_pack["back"]))

        VBlayout.addWidget(self.btn_back)
        VBlayout.setContentsMargins(0, 0, 0, 0)

    def btn_output_path_release(self):
        if self.parent.vdic["bg_mode"] >= 0:
            suffix = ".mp4"
        else:
            suffix = ".mov"
        if self.parent.vdic["filename"] is not None:
            fname = self.parent.vdic["filename"]
        else:
            fname = self.lang["Untitled_Video"]
        fname = convertFileFormat(fname, suffix)
        selector = suffix[1:].upper() + " " + self.lang["Files"] + " (*" + suffix + ")"
        if self.parent.vdic["output_path"]:
            dir_out = joinPath(self.parent.vdic["output_path"], fname)
        else:
            dir_out = fname
        file_, filetype = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                self.lang["Select Path"],
                                                                dir_out,
                                                                selector)
        if file_:
            self.parent.vdic["output_path"] = getFilePath(file_)
            self.parent.vdic["filename"] = getFileName(file_, True)
            self.showFilePath()

    def showFilePath(self):
        if (self.parent.vdic["output_path"] is not None) and \
                (self.parent.vdic["filename"] is not None):
            fullpath = joinPath(self.parent.vdic["output_path"], self.parent.vdic["filename"])
            if self.parent.vdic["bg_mode"] >= 0:
                fullpath = convertFileFormat(fullpath, "mp4")
            else:
                fullpath = convertFileFormat(fullpath, "mov")
            self.le_path.setText(fullpath)
            self.textview.setHtml(self.parent.getBrief())
            self.textview.moveCursor(QtGui.QTextCursor.End)

    def enterPathCheck(self):
        path = self.le_path.text()
        if path == "":
            self.parent.vdic["output_path"] = None
            self.parent.vdic["filename"] = None
        elif not os.path.exists(getFilePath(path)):
            showInfo(self, self.lang["Notice"], self.lang["This folder is not exist!"], False)
            self.showFilePath()
        else:
            self.parent.vdic["output_path"] = getFilePath(path)
            if self.parent.vdic["bg_mode"] >= 0:
                self.parent.vdic["filename"] = convertFileFormat(getFileName(path, True), "mp4")
            else:
                self.parent.vdic["filename"] = convertFileFormat(getFileName(path, True), "mov")
            self.showFilePath()
        self.le_path.clearFocus()

    def btn_blend_release(self):
        self.le_path.clearFocus()
        path = self.le_path.text()
        if not os.path.exists(getFilePath(path)):
            showInfo(self, self.lang["Notice"], self.lang["Output folder is not exist!"], False)
            self.showFilePath()
            return
        path = self.le_path.getText()
        if os.path.exists(path):
            reply = showInfo(self, self.lang["Notice"], self.lang["Are you sure to overwrite this file?"], True)
            if not reply:
                return
        self.parent.startBlending()
        self.prgbar.setValue(0)

    def btn_stop_release(self):
        reply = showInfo(self, self.lang["Notice"], self.lang["Are you sure to stop rendering?"], True)
        if reply:
            self.parent.stopBlending()
            self.btn_stop.setEnabled(False)

    def freezeWindow(self, flag=True):
        if flag:
            self.btn_back.hide()
            self.btn_blend.hide()
            self.le_path.setEnabled(False)
            self.btn_output_path.setEnabled(False)
            self.btn_output_path.setIcon(pil2icon(img_pack["folder_black"]))
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(100, loop.quit)
            loop.exec_()
            self.prgbar.show()
            self.btn_stop.show()
            self.btn_stop.setEnabled(True)

        else:
            self.btn_stop.hide()
            self.prgbar.hide()
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(100, loop.quit)
            loop.exec_()
            self.btn_back.show()
            self.btn_blend.show()
            self.le_path.setEnabled(True)
            self.btn_output_path.setEnabled(True)
            self.btn_output_path.setIcon(pil2icon(img_pack["folder"]))
            self.textview.moveCursor(QtGui.QTextCursor.End)

    def show(self):
        self.parent.hideAllMenu()
        self.parent.canDrop = False
        self.showFilePath()

        super().show()

    def btn_back_release(self):
        self.parent.mainMenu.show()
        self.parent.canDrop = True


class AboutWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(AboutWindow, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setAlignment(QtCore.Qt.AlignTop)

        items_lang = {
            "English": "en",
            "简体中文": "cn_s"
        }
        self.combo_lang = ComboBox(self, items_lang, self.combo_lang_select, "Language / 语言")
        VBlayout.addWidget(self.combo_lang)

        self.logo = QtWidgets.QLabel(self)
        self.logo.setPixmap(pil2qt(img_pack["about_logo"]))
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        VBlayout.addWidget(self.logo)

        self.textview = QtWidgets.QTextBrowser(self)
        VBlayout.addWidget(self.textview)
        self.textview.setHtml(self.parent.getIntro())
        self.textview.setOpenExternalLinks(True)
        self.textview.setStyleSheet(textBrowserStyle)
        self.textview.zoomIn(1)

        btn_back = genButton(self, self.lang["Back to Main Menu"], None, self.btn_back_release, "Escape")
        btn_back.setIcon(pil2icon(img_pack["back"]))
        VBlayout.addWidget(btn_back)

        VBlayout.setSpacing(15)
        VBlayout.setContentsMargins(0, 0, 0, 0)

    def combo_lang_select(self):
        if self.isVisible():
            lang_code = self.combo_lang.getValue()
            self.parent.lang_code = lang_code
            self.parent.resetLang = True
            self.parent.close()

    def show(self):
        self.parent.hideAllMenu()
        self.combo_lang.setValue(self.parent.lang_code)
        super().show()

    def btn_back_release(self):
        self.parent.mainMenu.show()
