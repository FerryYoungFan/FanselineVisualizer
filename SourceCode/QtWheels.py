#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
from PyQt5 import QtGui, QtCore, QtWidgets
import numpy as np
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication
from QtImages import *
from QtStyle import *


class FSlider(QtWidgets.QWidget):
    def __init__(self, parent, slName="", minv=0.0, maxv=100.0, stepv=1.0, ivalue=0.0, releaseEvent=None,
                 changeEvent=None, sl_type=0):
        super(FSlider, self).__init__(parent)
        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)

        if releaseEvent:
            self.slider.sliderReleased.connect(releaseEvent)

        self.slider.valueChanged.connect(self.do_changeEvent)

        self.do_releaseEvent = releaseEvent
        self.sl_changeEvent = changeEvent

        label_minimum = QtWidgets.QLabel(alignment=QtCore.Qt.AlignLeft)
        label_maximum = QtWidgets.QLabel(alignment=QtCore.Qt.AlignRight)
        self.label_name = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.label_name.setText(slName)
        self.slName = slName
        label_minimum.setNum(minv)
        label_maximum.setNum(maxv)
        label_minimum.setProperty("fontset", 0)
        label_maximum.setProperty("fontset", 0)
        self.label_name.setProperty("fontset", 1)

        VBlayout = QtWidgets.QVBoxLayout(self)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.addWidget(label_minimum)
        HBlayout.addWidget(self.label_name)
        HBlayout.addWidget(label_maximum)
        VBlayout.addLayout(HBlayout)
        VBlayout.addWidget(self.slider)

        self.minv = minv
        self.maxv = maxv
        self.stepv = stepv
        self.divs = 50

        self.intFlag = False

        self.setStyle(sl_type)

        if isinstance(minv, int) and isinstance(maxv, int) and isinstance(stepv, int):
            self.intFlag = True
            self.slider.setMinimum(minv)
            self.slider.setMaximum(maxv)
            self.slider.setSingleStep(stepv)
        else:
            self.intFlag = False
            self.slider.setMinimum(0)
            self.divs = int((self.maxv - self.minv) / self.stepv)
            self.slider.setMaximum(self.divs)
            self.slider.setSingleStep(1)

        self.setValue(ivalue)
        self.slider.keyPressEvent = self.nullEvent
        self.slider.dragMoveEvent = self.nullEvent
        self.slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider.wheelEvent = self.wheelEvent

    def setStyle(self, sl_type):
        if sl_type == 1:
            self.slider.setStyleSheet(sliderStyle1)
        elif sl_type == 2:
            self.slider.setStyleSheet(sliderStyle2)
        elif sl_type == 3:
            self.slider.setStyleSheet(sliderStyle3)
        elif sl_type == 4:
            self.slider.setStyleSheet(sliderStyle4)
        elif sl_type == 5:
            self.slider.setStyleSheet(sliderStyle5)
        else:
            self.slider.setStyleSheet(sliderStyleDefault)

    def wheelEvent(self, event):
        super().wheelEvent(event)
        if event.angleDelta().y() > 0:
            newv = self.getValue() + self.stepv
            if newv > self.maxv:
                self.setValue(self.maxv)
            else:
                self.setValue(self.getValue() + self.stepv)
        else:
            newv = self.getValue() - self.stepv
            if newv < self.minv:
                self.setValue(self.minv)
            else:
                self.setValue(self.getValue() - self.stepv)
        self.do_releaseEvent()

    def nullEvent(self, *args):
        pass

    def getValue(self):
        if self.intFlag:
            return self.slider.value()
        else:
            return round(((self.slider.value() / self.divs) * (self.maxv - self.minv) + self.minv) * 100) / 100

    def setValue(self, ivalue):
        if self.intFlag:
            self.slider.setValue(ivalue)
        else:
            self.slider.setValue(int(round((ivalue - self.minv) / (self.maxv - self.minv) * self.divs)))

    def do_changeEvent(self):
        self.slider.setToolTip(str(self.slName) + ": " + str(self.getValue()))
        self.label_name.setText(str(self.slName) + ": " + str(self.getValue()))
        if self.sl_changeEvent is not None:
            self.sl_changeEvent()


def genLabel(window, content="No Content", fonttype=2):
    label = QtWidgets.QLabel(content, window)
    label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom)
    label.setProperty("fontset", fonttype)
    return label


def genButton(window, text="", press_event=None, release_event=None, shortcut=None, style=1, tooltip=None):
    btn = QtWidgets.QPushButton(window)
    btn.setText(text)
    btn.setFocusPolicy(QtCore.Qt.NoFocus)
    if press_event is not None:
        btn.pressed.connect(press_event)
    if release_event is not None:
        btn.released.connect(release_event)
    if shortcut is not None:
        btn.setShortcut(QtGui.QKeySequence(shortcut))

    if style == 2:
        btn.setStyleSheet(pushButtonStyle2)
    elif style == 3:
        btn.setStyleSheet(pushButtonStyle3)
    elif style == 4:
        btn.setStyleSheet(pushButtonStyle4)
    elif style == 5:
        btn.setStyleSheet(pushButtonStyle5)
    elif style == 6:
        btn.setStyleSheet(pushButtonStyle6)
    else:
        btn.setStyleSheet(pushButtonStyle1)

    btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
    if tooltip is None and shortcut is not None:
        if shortcut == "Return":
            shortcut = "Enter"
        elif shortcut == "Escape":
            shortcut = "Esc"
        btn.setToolTip(text + ": (" + shortcut + ")")
    return btn


class _ComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(_ComboBox, self).__init__(parent)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.drawPixmap(QtCore.QPoint(self.width() - 26, 7), pil2qt(img_pack["down_arrow"]))


class ComboBox(QtWidgets.QWidget):
    def __init__(self, parent, items, combo_event=None, title=""):
        super(ComboBox, self).__init__()
        self.parent = parent
        self.items = items
        self.combo_event = combo_event
        VBlayout = QtWidgets.QVBoxLayout(self)
        self.combo = _ComboBox(self)

        if title:
            VBlayout.addWidget(genLabel(self, title))
        VBlayout.addWidget(self.combo)
        VBlayout.setSpacing(0)
        VBlayout.setContentsMargins(0, 0, 0, 0)
        self.setItems(self.items)
        self.combo.currentIndexChanged.connect(self.combo_select)
        self.combo.setView(QtWidgets.QListView())
        self.setStyleSheet(scrollBarStyle2)

    def combo_select(self):
        if self.combo_event is not None:
            self.combo_event()

    def setValue(self, value_in):
        index = 0
        for name, value in self.items:
            if str(value_in) == str(name) or str(value_in) == str(value):
                self.combo.setCurrentIndex(index)
                break
            index = index + 1

    def getValue(self):
        return self.items[self.combo.currentIndex()][1]

    def getText(self):
        return self.items[self.combo.currentIndex()][0]

    def setItems(self, items):
        cvt_items = []
        if isinstance(items, dict):
            for kname, value in items.items():
                cvt_items.append((kname, value))
                self.combo.addItem(kname)
            self.items = cvt_items
            return
        for item in items:
            if not isinstance(item, list) and not isinstance(item, tuple):
                cvt_items.append([item, item])
                self.combo.addItem(str(item))
            else:
                self.combo.addItem(item[0])
                cvt_items.append(item)
        self.items = cvt_items


class QSwitch(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = parent.lang
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(40)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def paintEvent(self, event):
        label = self.lang["ON"] if self.isChecked() else self.lang["OFF"]
        bg_color = QtGui.QColor(67, 123, 181) if self.isChecked() else QtGui.QColor(137, 139, 141)

        radius = 15
        width = 40
        pen_width = 2
        center = self.rect().center()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(QtGui.QColor(20, 20, 20))
        if not self.isChecked():
            pen = QtGui.QPen(QtGui.QColor(137, 139, 141))
        else:
            pen = QtGui.QPen(QtGui.QColor(67, 123, 181))
        pen.setWidth(pen_width)
        painter.setPen(pen)
        painter.drawRoundedRect(QtCore.QRect(-width, -radius, 2 * width, 2 * radius), radius, radius)
        painter.setBrush(QtGui.QBrush(bg_color))
        sw_rect = QtCore.QRect(-radius, -radius, width + radius, 2 * radius)

        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)

        if not self.isChecked():
            pen = QtGui.QPen(QtGui.QColor(20, 20, 20))
        else:
            pen = QtGui.QPen(QtGui.QColor(200, 200, 200))
        pen.setWidth(pen_width)
        painter.setPen(pen)

        painter.drawText(sw_rect, QtCore.Qt.AlignCenter, label)


class Spacing(QtWidgets.QWidget):
    def __init__(self, parent, size):
        super(Spacing, self).__init__()
        self.parent = parent
        space = QtWidgets.QWidget()
        space.setFixedHeight(size)
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(space)


class LineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent, place_holder=None, fo_event=None, num_range=None, isInt=False, scroll=None):
        super(LineEdit, self).__init__()
        self.parent = parent
        self.setStyleSheet(lineEditStyle)
        self.isInt = isInt
        self.fo_event = fo_event
        self.scroll_delta = scroll
        if place_holder is not None:
            self.setPlaceholderText(place_holder)

        self.num_range = num_range
        if self.num_range is not None:
            if self.isInt:
                validator = QtGui.QIntValidator()
            else:
                validator = QtGui.QDoubleValidator()
            self.setValidator(validator)

        self.returnPressed.connect(self.enterPressEvent)

    def focusOutEvent(self, QFocusEvent=None):
        if QFocusEvent:
            super().focusOutEvent(QFocusEvent)
        self.setText(str(self.numCheck()))
        if self.fo_event:
            self.fo_event()

    def enterPressEvent(self, *args):
        self.clearFocus()

    def numCheck(self):
        if self.num_range is not None:
            txt = self.text()
            if not txt:
                txt = 0
            else:
                try:
                    txt = float(txt)
                except:
                    txt = 0
            if txt < min(self.num_range):
                txt = min(self.num_range)
            elif txt > max(self.num_range):
                txt = max(self.num_range)
            if self.isInt:
                return int(round(txt))
            else:
                return round(txt * 100) / 100
        else:
            return self.text()

    def getText(self):
        return super().text()

    def wheelEvent(self, event):
        if self.scroll_delta is not None:
            delta = self.scroll_delta if event.angleDelta().y() > 0 else -self.scroll_delta
            val = self.numCheck() + delta
            self.setText(str(val))
            self.focusOutEvent()
            event.accept()


class PixmapWithDrop(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent, fileEvent=None):
        super(PixmapWithDrop, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        self.setAcceptDrops(True)
        self.fileEvent = fileEvent
        self.setShapeMode(1)  # For Drop Event

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if self.fileEvent is not None:
                self.fileEvent(url.toLocalFile())
            break


def showInfo(parent, title="", msg="", question=False):
    if question:
        box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, title, msg)
        qyes = box.addButton(parent.lang["Yes"], QtWidgets.QMessageBox.YesRole)
        qno = box.addButton(parent.lang["No"], QtWidgets.QMessageBox.NoRole)
        setWindowIcons(box)
        box.exec_()
        if box.clickedButton() == qyes:
            return True
        else:
            return False
    else:
        box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, title, msg)
        qyes = box.addButton(parent.lang["OK"], QtWidgets.QMessageBox.YesRole)
        setWindowIcons(box)
        box.exec_()
        if box.clickedButton() == qyes:
            return True
        else:
            return False


def getFormats(strv):
    arrv = strv.replace(" ", "").replace(";", "").replace("(", "").replace(")", "").replace("*", "")
    arrv = arrv.split(".")[1:]
    return arrv


def isValidFormat(path, format_arr):
    if not os.path.exists(path):
        return False
    elif path[-1] in ["/", "\\"] or not "." in path.replace("\\", "/").split("/")[-1]:
        return False
    elif not path.replace("\\", "/").split("/")[-1].split(".")[-1] in format_arr:
        return False
    return True


def ensureDir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def convertFileFormat(path, new_format=None):
    if not path:
        return ""
    if new_format is None:
        return path
    if not "." in path:
        if new_format[0] == ".":
            return path + new_format
        else:
            return path + "." + new_format

    last_dot = 0
    for i in range(len(path)):
        if path[i] == ".":
            last_dot = i
    ftype = path[last_dot + 1:]
    if new_format[0] == ".":
        pass
    else:
        new_format = "." + new_format
    if "/" in ftype or "\\" in ftype:
        outpath = path + new_format
    else:
        outpath = path[:last_dot] + new_format
    return outpath


def getFileName(path="", suffix=True):
    if not path:
        return ""
    fname = path.replace("\\", "/").split("/")[-1]
    if not suffix:
        fname = ".".join(fname.split(".")[:-1])
    return fname


def getFileSuffix(fname=""):
    if not fname:
        return ""
    if not "." in fname:
        return ""
    return "." + fname.split(".")[-1]


def getFilePath(path=""):
    if not path:
        return ""
    fname = path.replace("\\", "/").split("/")[-1]
    if "." in fname:
        path = "/".join(path.replace("\\", "/").split("/")[:-1])
    else:
        path = "/".join(path.replace("\\", "/").split("/"))

    if path[-1] != "/":
        path = path + "/"
    return path


def makeLegalFileName(fname=""):
    if not fname:
        return "untitled"
    illegal_dict = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
    for char in illegal_dict:
        fname.replace(char, "_")
    return fname


def protectPath(path=""):
    if not os.path.exists(path):
        return path
    else:
        fpath = getFilePath(path)
        fname = getFileName(path, False)
        suffix = getFileSuffix(getFileName(path, True))
        name_counter = 1
        new_path = fpath + fname + "(" + str(name_counter) + ")" + suffix
        while os.path.exists(new_path):
            name_counter = name_counter + 1
            new_path = fpath + fname + "(" + str(name_counter) + ")" + suffix
        return new_path


def joinPath(path="", filename=""):
    path = path.replace("\\", "/")
    if path[-1] != "/":
        path = path + "/"
    return str(path) + str(filename)


def testFunc(*args):
    print("test!!!")


if __name__ == '__main__':
    print(getFormats(" (*.mp3;*.wav;*.ogg;*.aac;*.flac;*.ape;*.m4a;*.m4r;*.wma;*.mp2;*.mmf);;"))
