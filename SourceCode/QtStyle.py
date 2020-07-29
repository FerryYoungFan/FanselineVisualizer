#!/usr/bin/env python
# -*- coding: utf-8 -*-

stylepack = """
    QWidget {
        background-color: #202020;
        font-family: "Microsoft Yahei",Helvetica,Arial,"Hiragino Sans GB","Heiti SC","WenQuanYi Micro Hei",sans-serif;
    }

    QToolTip { 
        background-color: #898B8D; 
        color: #222222; 
        border:None;
    }
    QLabel[fontset="0"]{
        font-size:15px;
        color:#666666;
    }
    QLabel[fontset="1"]{
        font-size:15px;
        color:#999999;
    }
    QLabel[fontset="2"]{
        font-size:15px;
        color:#4A88C7;
        font-weight: 500;
        margin:10px 5px 0px;
    }
    QLabel[fontset="3"]{
        font-size:15px;
        color:#5A98D7;
    }
    QLabel[fontset="4"]{
        font-size:15px;
        color:#999999;
        font-weight: 500;
        margin:10px 5px 0px;
    }
    QComboBox {
        border: 1px solid gray;
        border-radius: 3px;
        padding: 5px;
        font-size:16px;
        font-weight:500;
        color:#222222;
        background:#898B8D;
        margin:3px 3px 3px;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left-width: 1px;
        border-left-color: darkgray;
        border-left-style: solid;
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
    }
    QComboBox::down-arrow {
        image: url(./GUI/Image/down_arrow.png);
    }
    QComboBox QAbstractItemView{
        border: 0px;
        margin: 0px;
        color:#222222;
        font-weight:500;
        background:#898B8D;
        selection-background-color:#437BB5;
        outline: none;
    }
    QListView{
        font-size:16px;
        font-weight:500;
    }
    QListView::item {
        height: 40px;
    }
    QColorDialog QWidget{
    background-color: #898B8D;
}
      QColorDialog {
    background-color: #898B8D;
}  
    """

sliderStyleDefault = """
        QSlider{
        margin: 0px 10px 10px;
    }
    QSlider::groove:horizontal {
        height: 20px;
        border-radius: 10px;
        margin: -5px 0;
    }

    QSlider::handle:horizontal {
        background: #898B8D;
        width: 30px;
        height: 30px;
        border-radius: 5;
    }

    QSlider::handle:hover {
        background: #5E6264;
    }

    QSlider::handle:pressed {
        background: #3D3F40;
    }

    QSlider::add-page:horizontal {
        background: #313335;
    }

    QSlider::sub-page:horizontal {
        background: #4A88C7;
    }


"""
sliderStyle1 = """
        QSlider{
        margin: 0px 10px 10px;
    }
    QSlider::groove:horizontal {
        height: 20px;
        border-radius: 10px;
        margin: -5px 0;
    }

    QSlider::handle:horizontal {
        background: #898B8D;
        width: 30px;
        height: 30px;
        border-radius: 5;
    }

    QSlider::handle:hover {
        background: #5E6264;
    }

    QSlider::handle:pressed {
        background: #3D3F40;
    }
     QSlider::add-page:horizontal {
        background: #313335;
    }

    QSlider::sub-page:horizontal {
        background: #405368;
    }
"""
sliderStyle2 = """
        QSlider{
        margin: 0px 10px 10px;
    }
    QSlider::groove:horizontal {
        height: 20px;
        border-radius: 10px;
        margin: -5px 0;
    }

    QSlider::handle:horizontal {
        background: #898B8D;
        width: 30px;
        height: 30px;
        border-radius: 5;
    }

    QSlider::handle:hover {
        background: #5E6264;
    }

    QSlider::handle:pressed {
        background: #3D3F40;
    }
    QSlider::add-page:horizontal {
        background: #405368;
    }

    QSlider::sub-page:horizontal {
        background: #313335;
    }
"""
sliderStyle3 = """
        QSlider{
        margin: 0px 10px 10px;
    }
    QSlider::groove:horizontal {
        height: 20px;
        border-radius: 10px;
        margin: -5px 0;
    }

    QSlider::handle:horizontal {
        background: #898B8D;
        width: 30px;
        height: 30px;
        border-radius: 5;
    }

    QSlider::handle:hover {
        background: #5E6264;
    }

    QSlider::handle:pressed {
        background: #3D3F40;
    }
    QSlider::add-page:horizontal {
        background: #9C9642;
    }
    QSlider::sub-page:horizontal {
        background: #437BB5;
    }
"""
sliderStyle4 = """
        QSlider{
        margin: 0px 10px 10px;
    }
    QSlider::groove:horizontal {
        height: 20px;
        border-radius: 10px;
        margin: -5px 0;
    }

    QSlider::handle:horizontal {
        background: #898B8D;
        width: 30px;
        height: 30px;
        border-radius: 5;
    }

    QSlider::handle:hover {
        background: #5E6264;
    }

    QSlider::handle:pressed {
        background: #3D3F40;
    }
    QSlider::add-page:horizontal {
        background: #A343B5;
    }
    QSlider::sub-page:horizontal {
        background: #40874A;
    }
"""
sliderStyle5 = """
        QSlider{
        margin: 0px 10px 10px;
    }
    QSlider::groove:horizontal {
        height: 20px;
        border-radius: 10px;
        margin: -5px 0;
    }

    QSlider::handle:horizontal {
        background: #898B8D;
        width: 30px;
        height: 30px;
        border-radius: 5;
    }

    QSlider::handle:hover {
        background: #5E6264;
    }

    QSlider::handle:pressed {
        background: #3D3F40;
    }
    QSlider::add-page:horizontal {
        background: #4A88C7;
    }
    QSlider::sub-page:horizontal {
        background: #405368;
    }
"""
pushButtonStyle1 = """
    QPushButton {
        background: #898B8D;
        padding:8px 3px 5px;
        margin:3px 3px 3px;
        border-radius: 3;
        font-size:15px;
        font-weight: 500;
        color:#222222;
    }
    QPushButton:hover {
        background: #5E6264;
    }
    QPushButton:pressed {
        background: #3D3F40;
    }
    QPushButton:disabled{
        background: #111111;
        color:#444444;
    }
"""

pushButtonStyle2 = """
    QPushButton {
        background: #437BB5;
        padding:8px 3px 5px;
        margin:3px 3px 3px;
        border-radius: 3;
        font-size:15px;
        font-weight: 500;
        color:#CCCCCC;
    }
    QPushButton:hover {
        background: #3C6691;
    }
    QPushButton:pressed {
        background: #2E363F;
        color:#666666;
    }
    QPushButton:disabled{
        background: #111111;
        color:#444444;
    }
"""

pushButtonStyle3 = """
    QPushButton {
        background: #B54643;
        padding:8px 3px 5px;
        margin:3px 3px 3px;
        border-radius: 3;
        font-size:15px;
        font-weight: 500;
        color:#CCCCCC;
    }
    QPushButton:hover {
        background: #913A37;
    }
    QPushButton:pressed {
        background: #3F2E2E;
        color:#666666;
    }
    QPushButton:disabled{
        background: #111111;
        color:#444444;
    }
"""

pushButtonStyle4 = """
    QPushButton {
        background: #40874A;
        padding:8px 3px 5px;
        margin:3px 3px 3px;
        border-radius: 3;
        font-size:15px;
        font-weight: 500;
        color:#CCCCCC;
    }
    QPushButton:hover {
        background: #3E7746;
    }
    QPushButton:pressed {
        background: #354F39;
        color:#666666;
    }
    QPushButton:disabled{
        background: #111111;
        color:#444444;
    }
"""

pushButtonStyle5 = """
    QPushButton {
        background: #9C9642;
        padding:8px 3px 5px;
        margin:3px 3px 3px;
        border-radius: 3;
        font-size:15px;
        font-weight: 500;
        color:#2C2C2C;
    }
    QPushButton:hover {
        background: #7F7B43;
    }
    QPushButton:pressed {
        background: #545030;
    }
    QPushButton:disabled{
        background: #111111;
        color:#444444;
    }
"""

pushButtonStyle6 = """
    QPushButton {
        background: #898B8D;
        padding:8px 3px 5px;
        margin:3px 3px 3px;
        border-radius: 3;
        font-size:15px;
        font-weight: 500;
        color:#B52222;
    }
    QPushButton:hover {
        background: #5E6264;
    }
    QPushButton:pressed {
        background: #3D3F40;
    }
    QPushButton:disabled{
        background: #111111;
        color:#444444;
    }
"""

viewerStyle = """
    QFrame{
        border: 1px solid #437BB5;
        border-top:0px;
        border-bottom:0px;
        border-left:0px;
    }
"""

lineEditStyle = """
    QLineEdit{
        outline: none;
        border:2px solid #437BB5;
        background: #B9BBBD;
        padding:8px 3px 5px;
        margin:3px 3px 3px;
        border-radius: 3;
        font-size:15px;
        font-weight: 500;
        color:#222222;
    }
"""

scrollBarStyle = """
    QScrollBar:horizontal {
        border: none;
        background: none;
        height: 20px;
        margin: 0px 20px 0 20px;
    }

    QScrollBar::handle:horizontal {
        background: #898B8D;
        min-width: 20px;
    }

    QScrollBar::add-line:horizontal {
        background: none;
        width: 20px;
        subcontrol-position: right;
        subcontrol-origin: margin;

    }

    QScrollBar::sub-line:horizontal {
        background: none;
        width: 20px;
        subcontrol-position: top left;
        subcontrol-origin: margin;
        position: absolute;
    }

    QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
        width: 20px;
        height: 20px;
        background: #898B8D;
    }

    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: #202020;
    }

    /* VERTICAL */
    QScrollBar:vertical {
        border: none;
        background: none;
        width: 20px;
        margin: 20px 0 20px 0;
    }

    QScrollBar::handle:vertical {
        background: #898B8D;
        min-height: 20px;
    }

    QScrollBar::add-line:vertical {
        background: none;
        height: 20px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:vertical {
        background: none;
        height: 20px;
        subcontrol-position: top left;
        subcontrol-origin: margin;
        position: absolute;
    }

    QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {
        width: 20px;
        height: 20px;
        background: #898B8D;
    }

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: #202020;
    }
"""

scrollBarStyle2 = """
    /* VERTICAL */
    QScrollBar:vertical {
        border: none;
        background: none;
        width: 20px;
        margin: 0 0 0 0;
    }

    QScrollBar::handle:vertical {
        background: #437BB5;
        min-height: 20px;
    }

    QScrollBar::add-line:vertical {
        background: none;
        height: 0px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:vertical {
        background: none;
        height: 0px;
        subcontrol-position: top left;
        subcontrol-origin: margin;
        position: absolute;
    }

    QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {
        width: 20px;
        height: 0px;
        background: #898B8D;
    }

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: #202020;
    }
"""

menuStyle = """
    QMenu {
        background: #898B8D;
        padding:8px 3px 5px;
        font-size:15px;
        font-weight: 500;
        color:#222222;
    }
    QMenu::item{
        margin:2px;
        padding:5px;
    }
    QMenu::item::selected {
        background-color: #5E6264;
    }
"""

progressbarStyle = """
    QProgressBar{
        border: 2px solid #898B8D;
      border-radius: 3px;
      background-color: #222222;
      margin:3px 3px 3px;
      text-align: center;
      color:#CCCCCC;
    }
     QProgressBar::chunk {
     background-color: #40874A;
     width: 1px;
 }
"""

textBrowserStyle = """
    
    QTextBrowser{
        background: #202020;
        color: #898B8D;
        font-family: "Microsoft Yahei",Helvetica,Arial,"Hiragino Sans GB","Heiti SC","WenQuanYi Micro Hei",sans-serif;
        font-weight:400;
        font-size:20em;
    }
    
    QTextBrowser hr{
        color:red;
        background:red;
    }
    
        QScrollBar:horizontal {
        border: none;
        background: none;
        height: 20px;
        margin: 0;
    }

    QScrollBar::handle:horizontal {
        background: #437BB5;
        min-width: 20px;
    }

    QScrollBar::add-line:horizontal {
        background: none;
        width: 20px;
        subcontrol-position: right;
        subcontrol-origin: margin;

    }

    QScrollBar::sub-line:horizontal {
        background: none;
        width: 20px;
        subcontrol-position: top left;
        subcontrol-origin: margin;
        position: absolute;
    }

    QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
        width: 0px;
        height: 20px;
        background: #898B8D;
    }

    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: #202020;
    }
    
    
    QScrollBar:vertical {
        border: none;
        background: none;
        width: 20px;
        margin: 0 0 0 0;
    }

    QScrollBar::handle:vertical {
        background: #437BB5;
        min-height: 20px;
    }

    QScrollBar::add-line:vertical {
        background: none;
        height: 0px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }

    QScrollBar::sub-line:vertical {
        background: none;
        height: 0px;
        subcontrol-position: top left;
        subcontrol-origin: margin;
        position: absolute;
    }

    QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {
        width: 20px;
        height: 0px;
        background: #898B8D;
    }

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: #202020;
    }
    
"""
