#!/usr/bin/env python
# -*- coding: utf-8 -*-

from QtWheels import *
from QtImages import img_pack, pil2qt
from PIL import Image


class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self.parent = parent
        self.lang = parent.lang
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = PixmapWithDrop(self, self.parent.fileEvent)
        self._photo.setTransformationMode(1)

        self.lang = parent.lang

        self._scene.addItem(self._photo)
        self.parent = parent
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(10, 10, 10)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.img_cache = None

        self.oldSize = None

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
        self._zoom = 0

    def imshow(self, image=None):
        if image is None:
            image = img_pack["nofile"]
            self._photo.setPixmap(pil2qt(image))
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        else:
            try:
                self._photo.setPixmap(pil2qt(image))
                self.img_cache = image.copy()
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            except:
                image = img_pack["nofile"]
                self._photo.setPixmap(pil2qt(image))
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self._empty = False
        if not self.oldSize == self.img_cache.size:
            self.fitInView()
            self.oldSize = self.img_cache.size

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom <= 0:
                self.fitInView()

    def mousePressEvent(self, event):
        super(PhotoViewer, self).mousePressEvent(event)
        point = self.mapToScene(event.pos()).toPoint()

    def mouseMoveEvent(self, event):
        super(PhotoViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super(PhotoViewer, self).mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(menuStyle)

        if not self.parent.isRunning:
            refresh = menu.addAction(self.lang["Refresh Preview"])
            menu.addSeparator()
        else:
            refresh = None
        savepng = menu.addAction(self.lang["Save as PNG"])
        savejpg = menu.addAction(self.lang["Save as JPG"])
        savebmp = menu.addAction(self.lang["Save as BMP"])

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag and self.img_cache is not None:
            if not self.parent.isRunning and action == refresh:
                self.parent.refreshAll()
            elif action == savepng:
                file_, filetype = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                        self.lang["Save as PNG"],
                                                                        self.lang["Snap"] + ".png",
                                                                        self.lang["PNG Files"] + " (*.png)")
                if file_:
                    self.img_cache.save(file_, quality=100)
            elif action == savejpg:
                file_, filetype = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                        self.lang["Save as JPG"],
                                                                        self.lang["Snap"] + ".jpg",
                                                                        self.lang["JPG Files"] + " (*.jpg)")
                if file_:
                    self.img_cache.save(file_, quality=100)
            elif action == savebmp:
                file_, filetype = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                        self.lang["Save as BMP"],
                                                                        self.lang["Snap"] + ".bmp",
                                                                        self.lang["BMP Files"] + " (*.bmp)")
                if file_:
                    self.img_cache.save(file_, quality=100)

    def getPixmap(self):
        return self._photo.pixmap()

    def resizeEvent(self, event):
        if self.width() > 0:
            self.fitInView()
        super(PhotoViewer, self).resizeEvent(event)


class ThumbViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(ThumbViewer, self).__init__(parent)
        self.parent = parent
        self.lang = parent.lang
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = PixmapWithDrop(self, self.parent.fileEvent)
        self._photo.setTransformationMode(1)

        self._scene.addItem(self._photo)
        self.parent = parent
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(32, 32, 32)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.imshow(None)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
        self._zoom = 0

    def imshow(self, image=None):
        if image is None:
            image = img_pack["nofile"]
            self._photo.setPixmap(pil2qt(image))
        else:
            try:
                self._photo.setPixmap(pil2qt(image))
            except:
                image = img_pack["nofile"]
                self._photo.setPixmap(pil2qt(image))
        self._empty = False
        self.fitInView()

    def getPixmap(self):
        return self._photo.pixmap()

    def resizeEvent(self, event):
        if self.width() > 0:
            self.fitInView()
        super(ThumbViewer, self).resizeEvent(event)


class ImageSelector(QtWidgets.QWidget):
    def __init__(self, parent, title, image_path=None):
        super(ImageSelector, self).__init__()
        self.lang = parent.lang
        self.parent = parent
        self.image_formats = parent.image_formats
        self.image_formats_arr = getFormats(self.image_formats)

        left = QtWidgets.QFrame(self)
        VBlayout_l = QtWidgets.QVBoxLayout(left)

        self.viewer = ThumbViewer(self)
        VBlayout_l.addWidget(self.viewer)
        VBlayout_l.setSpacing(0)
        VBlayout_l.setContentsMargins(0, 0, 0, 0)

        right = QtWidgets.QFrame(self)
        VBlayout_r = QtWidgets.QVBoxLayout(right)
        self.btn_open = genButton(self, self.lang["Open"], None, self.btn_open_release, style=2)
        self.btn_remove = genButton(self, self.lang["Remove"], None, self.btn_remove_release, style=5)
        self.btn_color = genButton(self, self.lang["Use Color"], None, self.btn_color_release)
        tlabel = genLabel(self, title, 1)
        tlabel.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        VBlayout_r.addWidget(tlabel)
        HBlayout_small = QtWidgets.QHBoxLayout()
        HBlayout_small.addWidget(self.btn_open)
        HBlayout_small.addWidget(self.btn_remove)
        VBlayout_r.addLayout(HBlayout_small)
        VBlayout_r.addWidget(self.btn_color)

        right.setMinimumWidth(150)

        mainlayout = QtWidgets.QVBoxLayout(self)

        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setSpacing(0)
        HBlayout.setContentsMargins(0, 0, 0, 0)
        HBlayout.addWidget(left)
        HBlayout.addWidget(right)
        mainlayout.addLayout(HBlayout)

        self.viewer.fitInView()
        if image_path is not None:
            self.image_vidc = image_path
            self.image_path = self.parent.parent.vdic[self.image_vidc]
        self.image = None

    def fileEvent(self, path):
        if getFileSuffix(path)[1:].lower() in self.image_formats_arr:
            self.parent.parent.vdic[self.image_vidc] = path
            self.image_path = path
            self.imshow()
            self.parent.parent.refreshAll()
        else:
            showInfo(self, self.lang["Notice"], self.lang["Sorry, this file is not supported!"])

    def btn_open_release(self):
        selector = self.lang["Image Files"] + self.image_formats
        selector = selector + self.lang["All Files"] + " (*.*)"
        if self.image_path is not None and os.path.exists(self.image_path):
            folder = self.image_path
        else:
            folder = ""
        file_, filetype = QtWidgets.QFileDialog.getOpenFileName(self, self.lang["Select an Image"], folder, selector)
        if not file_:
            print("No File!")
        else:
            self.parent.parent.vdic[self.image_vidc] = file_
            self.image_path = file_
            self.imshow()
            self.parent.parent.refreshAll()

    def btn_color_release(self):
        if isinstance(self.parent.parent.vdic[self.image_vidc], tuple):
            oldColor = self.parent.parent.vdic[self.image_vidc]
        else:
            oldColor = (255, 255, 255, 255)
        colorDialog = QtWidgets.QColorDialog()
        color = colorDialog.getColor(QtGui.QColor(*oldColor), self, self.lang["Select Color"])
        if color.isValid():
            self.parent.parent.vdic[self.image_vidc] = color.getRgb()
            self.imshow()
            self.parent.parent.refreshAll()

    def imshow(self):
        self.image_path = self.parent.parent.vdic[self.image_vidc]
        if isinstance(self.image_path, str):
            try:
                self.image = Image.open(self.image_path).convert('RGBA')
                self.btn_remove.setEnabled(True)
                self.viewer.setToolTip(self.image_path.replace("\\", "/"))
            except:
                self.image_path = None
                self.parent.parent.vdicBackup()
                self.parent.parent.vdic[self.image_vidc] = None
                self.image = None
                self.btn_remove.setEnabled(False)
                self.viewer.setToolTip(self.lang["No Image File"])
                if self.isVisible():
                    showInfo(self, self.lang["Notice"], self.lang["Cannot open this image file!"], False)
        elif isinstance(self.image_path, tuple):
            self.image = Image.new("RGB", (512, 512), self.image_path[:3])
            self.btn_remove.setEnabled(True)
            self.viewer.setToolTip(("#%02x%02x%02x" % self.image_path[:3]).upper())
        else:
            self.image_path = None
            self.parent.parent.vdicBackup()
            self.parent.parent.vdic[self.image_vidc] = None
            self.image = None
            self.btn_remove.setEnabled(False)
            self.viewer.setToolTip(self.lang["No Image File"])
        self.viewer.imshow(self.image)

    def btn_remove_release(self):
        self.parent.parent.vdic[self.image_vidc] = None
        self.image_path = None
        self.imshow()
        self.parent.parent.refreshAll()


class ImageSelectWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ImageSelectWindow, self).__init__()
        self.parent = parent
        self.lang = parent.lang
        self.image_formats = parent.image_formats
        self.selector1 = ImageSelector(self, self.lang["Foreground"], "image_path")
        self.selector2 = ImageSelector(self, self.lang["Background"], "bg_path")
        self.selector3 = ImageSelector(self, self.lang["Logo"], "logo_path")
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        VBlayout.addWidget(genLabel(self, self.lang["Select Images"], 2))
        VBlayout.addWidget(self.selector1)
        VBlayout.addWidget(self.selector2)
        VBlayout.addWidget(self.selector3)
        btn_back = genButton(self, self.lang["Back to Main Menu"], None, self.btn_back_release, "Escape")
        VBlayout.addWidget(btn_back)
        VBlayout.setSpacing(15)
        VBlayout.setContentsMargins(0, 0, 0, 0)

    def btn_back_release(self):
        self.parent.mainMenu.show()

    def show(self):
        self.parent.hideAllMenu()
        self.selector1.imshow()
        self.selector2.imshow()
        self.selector3.imshow()
        super().show()
