from FanBlender import FanBlender
from LanguagePack import *
import threading, os, pickle
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from tkinter import scrolledtext

"""
Audio Visualizer - GUI
By Twitter @FanKetchup

Require:

Python 3.7	    V 3.7.4

numpy		    V 1.19.0
Pillow		    V 7.2.0
imageio		    V 2.9.0
imageio-ffmpeg	V 0.4.2
pydub		    V0.24.1*
(* No need to install ffmpeg for pydub, since it shares ffmpeg with imageio-ffmpeg.)

"""


# GUI Language
lang = lang_en
lang_code = "en"
#lang = lang_cn_s

def clog(content="", insertloc='end'):
    global scr
    scr.configure(state='normal')
    scr.insert(insertloc, content)
    scr.configure(state='disable')


class InfoBridge:
    def __init__(self):
        pass

    def log(self, content=""):
        clog(content + "\n")

    def progressbar(self, value, total):
        global progress
        progress["value"] = (100 * value / total)

    def freeze(self, flag=True):
        global isRunning
        if flag:
            fg = "disabled"
            self.progressbar(0, 100)
            btn_blend["text"] = lang["Stop Blending"]
            isRunning = True
            root.title(lang["Fanseline Audio Visualizer (Running)"])
        else:
            fg = "normal"
            self.progressbar(0, 100)
            btn_blend["text"] = lang["Blend & Export"]
            isRunning = False
            root.title(lang["Fanseline Audio Visualizer"])
        elem = [entry_audio, btn_audio, entry_fname, btn_output, entry_img, btn_img, entry_logo, btn_logo,
                entry_text, entry_font, btn_font, entry_width, entry_height, entry_fps, entry_brv, btn_autob,
                entry_low, entry_up, entry_bins, entry_scalar, list_color, list_bra, check_normal, list_preseta,
                list_presetv, btn_prev, entry_output, label_mp4, label_textplz, label_font, label_size, label_mul,
                label_fps, label_brv, label_range, label_to, label_hz, label_bins, label_scalar, label_color,
                label_bra, label_kbps, label_preseta, label_presetv, list_lang,label_lang]
        for el in elem:
            el["state"] = fg

        if not flag:
            list_color["state"] = "readonly"
            list_preseta["state"] = "readonly"
            list_presetv["state"] = "readonly"
            list_lang["state"] = "readonly"


def selectImage():
    try:
        global tk_image_path
        pathread = askopenfilename(
            filetypes=[(lang["Image files"], "*.jpg *.jpeg *.png *.gif *.bmp"), (lang["All files"], "*.*")])
        if not pathread or not os.path.exists(pathread):
            return
        else:
            tk_image_path.set(pathread)
            clog(lang["Image Selected: "])
            clog(pathread + '\n')
    except:
        return


def selectLogo():
    try:
        global tk_logo_path
        pathread = askopenfilename(
            filetypes=[(lang["Image files"], "*.jpg *.jpeg *.png *.gif *.bmp *.ico"), (lang["All files"], "*.*")])
        if not pathread or not os.path.exists(pathread):
            return
        else:
            tk_logo_path.set(pathread)
            clog(lang["Logo Selected: "])
            clog(pathread + '\n')
    except:
        return


def selectAudio():
    try:
        global tk_sound_path, tk_output_path, tk_filename
        pathread = askopenfilename(
            filetypes=[(lang["Audio files"], "*.mp3 *.wav *.ogg *.aac *.flac"), (lang["All files"], "*.*")])
        if not pathread or not os.path.exists(pathread):
            return
        else:
            tk_sound_path.set(pathread)
            vdic = getAllValues()
            if vdic["output_path"] is None:
                tk_output_path.set(os.path.dirname(os.path.realpath(pathread)).replace("\\", "/") + "/")
            new_name = (os.path.splitext(pathread)[0].split("/")[-1]) + lang["_Visualize"]
            tk_filename.set(new_name)
            clog(lang["Audio Selected: "])
            clog(tk_sound_path.get() + '\n')
    except:
        return


def selectOutput():
    try:
        global tk_output_path
        pathexport = askdirectory()
        pathexport = pathexport + '/'
        if not pathexport or pathexport == "/":
            return
        else:
            tk_output_path.set(pathexport)
            clog(lang["Output Path Selected: "])
            clog(tk_output_path.get() + '\n')
    except:
        return


def selectFont():
    global tk_font, tk_text
    try:
        pathread = askopenfilename(filetypes=[(lang["Font files"], "*.ttf *.otf"), (lang["All files"], "*.*")])
        if not pathread:
            return
        else:
            tk_font.set(pathread)
            clog(lang["Font Selected: "])
            clog(pathread + '\n')
    except:
        return


def getAllValues():
    global tk_image_path, tk_sound_path, tk_logo_path, tk_output_path, tk_filename, \
        tk_text, tk_font, tk_bins, tk_fq_low, tk_fq_high, color_dic, list_color, tk_scalar, \
        tk_width, tk_height, tk_fps, tk_br_video, tk_br_audio, tk_audio_normal

    def checkStr(strtk):
        if strtk.get():
            return strtk.get()
        else:
            return None

    def checkFile(strtk):
        path = checkStr(strtk)
        if path is not None:
            if os.path.exists(path):
                return path
        return None

    def checkInt(inttk):
        if inttk.get():
            try:
                num = float(inttk.get())
            except:
                return None
            else:
                return int(round(num))
        else:
            return None

    def checkFloat(floattk):
        if floattk.get():
            try:
                num = float(floattk.get())
            except:
                return None
            else:
                return num
        else:
            return None

    if checkStr(tk_filename) is not None:
        fname = checkStr(tk_filename) + ".mp4"
    else:
        fname = None

    param_dict = {
        "image_path": checkFile(tk_image_path),
        "sound_path": checkFile(tk_sound_path),
        "logo_path": checkFile(tk_logo_path),
        "output_path": checkStr(tk_output_path),
        "filename": fname,
        "text": checkStr(tk_text),
        "font": checkStr(tk_font),
        "bins": checkInt(tk_bins),
        "lower": checkInt(tk_fq_low),
        "upper": checkInt(tk_fq_high),
        "color": color_dic[checkStr(list_color)],
        "scalar": checkFloat(tk_scalar),

        "width": checkInt(tk_width),
        "height": checkInt(tk_height),
        "fps": checkFloat(tk_fps),
        "br_Mbps": checkFloat(tk_br_video),

        "normal": tk_audio_normal.get(),
        "br_kbps": checkInt(tk_br_audio),
    }
    return param_dict


def dict2tuple(dict_input):
    keys = []
    for key in dict_input.keys():
        keys.append(key)
    return tuple(keys)


def autoBitrate():
    vdic = getAllValues()
    global tk_br_video
    if vdic["width"] is not None and vdic["height"] is not None and vdic["fps"] is not None:
        brv = getDefaultBR(vdic["width"], vdic["height"], vdic["fps"], 4)
        tk_br_video.set(round(brv * 100) / 100)


def setBlender(param_dict):
    global fb
    fb.setConsole(InfoBridge())
    fb.setFilePath(image_path=param_dict["image_path"],
                   sound_path=param_dict["sound_path"],
                   logo_path=param_dict["logo_path"])
    fb.setOutputPath(output_path=param_dict["output_path"],
                     filename=param_dict["filename"])
    fb.setText(text=param_dict["text"], font=param_dict["font"])
    fb.setSpec(bins=param_dict["bins"], lower=param_dict["lower"], upper=param_dict["upper"],
               color=param_dict["color"], scalar=param_dict["scalar"])
    fb.setVideoInfo(width=param_dict["width"], height=param_dict["height"],
                    fps=param_dict["fps"], br_Mbps=param_dict["br_Mbps"])
    fb.setAudioInfo(normal=param_dict["normal"], br_kbps=param_dict["br_kbps"])


def getDefaultBR(width, height, fps, quality=3):
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


def showPreview():
    global fb
    saveConfig()
    setBlender(getAllValues())
    th_preview = threading.Thread(target=fb.previewBackground)
    th_preview.setDaemon(True)
    th_preview.start()


def startBlending():
    global fb
    vdic = getAllValues()
    if vdic["sound_path"] is None:
        tkinter.messagebox.showinfo(lang["Cannot Blend"], lang["Please select the correct audio file!"])
        return
    if vdic["output_path"] is None:
        tkinter.messagebox.showinfo(lang["Cannot Blend"], lang["Please select the correct output path!"])
        return
    if vdic["filename"] is None:
        tkinter.messagebox.showinfo(lang["Cannot Blend"], lang["Please input the corrent file name!"])
        return

    if not isRunning:
        setBlender(vdic)
        saveConfig()
        th_blend = threading.Thread(target=fb.runBlending)
        th_blend.setDaemon(True)
        th_blend.start()
    else:
        clog(lang["Stop Blending..."] + "\n")
        fb.isRunning = False


def presetVideo(*args):
    global video_dic, list_presetv, tk_width, tk_height, tk_fps, tk_br_video
    w, h, fps, brv = video_dic[list_presetv.get()]
    tk_width.set(w)
    tk_height.set(h)
    tk_fps.set(fps)
    tk_br_video.set(round(brv * 100) / 100)


def presetAudio(*args):
    global audio_dic, tk_br_audio, tk_fq_low, tk_fq_high, tk_audio_normal, tk_scalar
    bra, low, up, normal, scale = audio_dic[list_preseta.get()]
    tk_br_audio.set(bra)
    tk_fq_low.set(low)
    tk_fq_high.set(up)
    tk_audio_normal.set(normal)
    tk_scalar.set(scale)


def saveConfig():
    vdic = getAllValues()
    with open('./Source/config.pickle', 'wb') as handle:
        pickle.dump(vdic, handle, protocol=pickle.HIGHEST_PROTOCOL)


def loadConfig():
    try:
        with open('./Source/config.pickle', 'rb') as handle:
            vdic = pickle.load(handle)
    except:
        print("No config")
        saveConfig()
        return

    global tk_image_path, tk_sound_path, tk_logo_path, tk_output_path, tk_filename, \
        tk_text, tk_font, tk_bins, tk_fq_low, tk_fq_high, color_dic, list_color, tk_scalar, \
        tk_width, tk_height, tk_fps, tk_br_video, tk_br_audio, tk_audio_normal

    def fileCheck(dicv, tk_value):
        path = vdic[dicv]
        if path is not None and os.path.exists(path):
            tk_value.set(path)
        else:
            tk_value.set("")

    def strCheck(dicv, tk_value, trunc=False):
        strv = vdic[dicv]
        if strv is not None:
            if not trunc:
                tk_value.set(strv)
            else:
                tk_value.set("".join(strv.split(".")[:-1]))
        else:
            tk_value.set("")

    def numCheck(dicv, tk_value):
        num = vdic[dicv]
        if num is not None:
            tk_value.set(num)
        else:
            tk_value.set(0)

    fileCheck("image_path", tk_image_path)
    fileCheck("sound_path", tk_sound_path)
    fileCheck("logo_path", tk_logo_path)
    fileCheck("output_path", tk_output_path)
    strCheck("filename", tk_filename, True)
    strCheck("text", tk_text)
    fileCheck("font", tk_font)
    numCheck("bins", tk_bins)
    numCheck("lower", tk_fq_low)
    numCheck("upper", tk_fq_high)
    numCheck("scalar", tk_scalar)
    numCheck("width", tk_width)
    numCheck("height", tk_height)
    numCheck("fps", tk_fps)
    numCheck("br_Mbps", tk_br_video)
    numCheck("br_kbps", tk_br_audio)
    numCheck("normal", tk_audio_normal)

def saveLanguage():
    global lang, lang_code
    with open('./Source/language.pickle', 'wb') as handle:
        pickle.dump(lang_code, handle, protocol=pickle.HIGHEST_PROTOCOL)

def loadLanguage():
    global lang,lang_code
    lang_code = "en"
    try:
        with open('./Source/language.pickle', 'rb') as handle:
            lang_code = pickle.load(handle)
    except:
        print("No language config")

    if lang_code == "cn_s":
        lang = lang_cn_s
    else:
        lang = lang_en

def resetGUI(*args):
    global lang_code,exit_flag,root,list_lang
    #lang_code = lc
    if list_lang.get() == "简体中文":
        lang_code = "cn_s"
    else:
        lang_code = "en"
    saveConfig()
    saveLanguage()
    exit_flag=False
    root.destroy()



if __name__ == '__main__':
    exit_flag = False
    while not exit_flag:
        exit_flag =True

        root = tk.Tk()
        loadLanguage()

        tk_image_path = tk.StringVar(value="./Source/fallback.png")
        tk_sound_path = tk.StringVar()
        tk_logo_path = tk.StringVar(value="./Source/Logo.png")
        tk_output_path = tk.StringVar()
        tk_filename = tk.StringVar(value="output")

        tk_text = tk.StringVar()
        tk_font = tk.StringVar(value="./Source/font.otf")

        tk_bins = tk.IntVar(value=80)
        tk_fq_low = tk.IntVar()
        tk_fq_high = tk.IntVar()
        tk_scalar = tk.DoubleVar()
        tk_color = tk.StringVar()

        tk_width = tk.IntVar()
        tk_height = tk.IntVar()
        tk_fps = tk.DoubleVar()
        tk_br_video = tk.DoubleVar()
        tk_br_audio = tk.IntVar()
        tk_audio_normal = tk.BooleanVar()

        tk_preseta = tk.StringVar()
        tk_presetv = tk.StringVar()

        tk_lang = tk.StringVar()

        isRunning = False

        fb = FanBlender()

        root.title(lang["Fanseline Audio Visualizer"])
        canvas = tk.Canvas(root, width=960, height=720)
        canvas.pack()
        frame1 = tk.Frame(master=root)
        frame1.place(relx=0, rely=0, relwidth=1, relheight=1, anchor='nw')
        rely, devy = 0.01, 0.06
        relh = 0.04

        label_lang = tk.Label(master=frame1, textvariable=tk.StringVar(value="Language/语言:"))
        label_lang.place(relwidth=0.1, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        list_lang = ttk.Combobox(master=frame1, textvariable=tk_lang, state="readonly")
        list_lang["values"] = ("English","简体中文")
        if lang_code == "cn_s":
            list_lang.current(1)
        else:
            list_lang.current(0)
        list_lang.place(relwidth=0.08, relheight=relh, relx=0.15, rely=rely, anchor='nw')
        list_lang.bind("<<ComboboxSelected>>", resetGUI)

        rely += devy
        entry_audio = tk.Entry(master=frame1, textvariable=tk_sound_path)
        entry_audio.place(relwidth=0.7, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        btn_audio = tk.Button(master=frame1, text=lang["Audio File(REQUIRED)"], command=selectAudio)
        btn_audio.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy
        entry_output = tk.Entry(master=frame1, textvariable=tk_output_path)
        entry_output.place(relwidth=0.4, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        entry_fname = tk.Entry(master=frame1, textvariable=tk_filename)
        entry_fname.place(relwidth=0.23, relheight=relh, relx=0.48, rely=rely, anchor='nw')
        label_mp4 = tk.Label(master=frame1, textvariable=tk.StringVar(value=".mp4"))
        label_mp4.place(relwidth=0.05, relheight=relh, relx=0.71, rely=rely, anchor='nw')
        btn_output = tk.Button(master=frame1, text=lang["Output Path(REQUIRED)"], command=selectOutput)
        btn_output.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy
        entry_img = tk.Entry(master=frame1, textvariable=tk_image_path)
        entry_img.place(relwidth=0.7, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        btn_img = tk.Button(master=frame1, text=lang["FG & BG Image"], command=selectImage)
        btn_img.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy
        entry_logo = tk.Entry(master=frame1, textvariable=tk_logo_path)
        entry_logo.place(relwidth=0.7, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        btn_logo = tk.Button(master=frame1, text=lang["Logo File"], command=selectLogo)
        btn_logo.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy
        label_textplz = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Your Text Here:"]))
        label_textplz.place(relwidth=0.1, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        entry_text = tk.Entry(master=frame1, textvariable=tk_text)
        tk_text.set("")
        entry_text.place(relwidth=0.25, relheight=relh, relx=0.15, rely=rely, anchor='nw')

        label_font = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Font File:"]))
        label_font.place(relwidth=0.1, relheight=relh, relx=0.4, rely=rely, anchor='nw')
        entry_font = tk.Entry(master=frame1, textvariable=tk_font)
        entry_font.place(relwidth=0.25, relheight=relh, relx=0.5, rely=rely, anchor='nw')
        btn_font = tk.Button(master=frame1, text=lang["Select Font File"], command=selectFont)
        btn_font.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy
        label_size = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Video Size:"]))
        label_size.place(relwidth=0.1, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        entry_width = tk.Entry(master=frame1, textvariable=tk_width)
        entry_width.place(relwidth=0.05, relheight=relh, relx=0.15, rely=rely, anchor='nw')
        label_mul = tk.Label(master=frame1, textvariable=tk.StringVar(value="x"))
        label_mul.place(relwidth=0.03, relheight=relh, relx=0.2, rely=rely, anchor='nw')
        entry_height = tk.Entry(master=frame1, textvariable=tk_height)
        entry_height.place(relwidth=0.05, relheight=relh, relx=0.23, rely=rely, anchor='nw')

        label_fps = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Video FPS:"]))
        label_fps.place(relwidth=0.1, relheight=relh, relx=0.3, rely=rely, anchor='nw')
        entry_fps = tk.Entry(master=frame1, textvariable=tk_fps)
        entry_fps.place(relwidth=0.05, relheight=relh, relx=0.4, rely=rely, anchor='nw')

        label_brv = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Video BR (Mbps):"]))
        label_brv.place(relwidth=0.15, relheight=relh, relx=0.50, rely=rely, anchor='nw')
        entry_brv = tk.Entry(master=frame1, textvariable=tk_br_video)
        entry_brv.place(relwidth=0.1, relheight=relh, relx=0.65, rely=rely, anchor='nw')

        btn_autob = tk.Button(master=frame1, text=lang["Auto Bit Rate"], command=autoBitrate)
        btn_autob.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy
        label_range = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Analyze Freq:"]))
        label_range.place(relwidth=0.1, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        entry_low = tk.Entry(master=frame1, textvariable=tk_fq_low)
        entry_low.place(relwidth=0.05, relheight=relh, relx=0.15, rely=rely, anchor='nw')
        label_to = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["to"]))
        label_to.place(relwidth=0.03, relheight=relh, relx=0.2, rely=rely, anchor='nw')
        entry_up = tk.Entry(master=frame1, textvariable=tk_fq_high)
        entry_up.place(relwidth=0.05, relheight=relh, relx=0.23, rely=rely, anchor='nw')
        label_hz = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Hz"]))
        label_hz.place(relwidth=0.03, relheight=relh, relx=0.28, rely=rely, anchor='nw')

        label_bins = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Spectrum Num:"]))
        label_bins.place(relwidth=0.1, relheight=relh, relx=0.35, rely=rely, anchor='nw')
        entry_bins = tk.Entry(master=frame1, textvariable=tk_bins)
        entry_bins.place(relwidth=0.05, relheight=relh, relx=0.45, rely=rely, anchor='nw')
        label_scalar = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Spectrum Scalar:"]))
        label_scalar.place(relwidth=0.1, relheight=relh, relx=0.53, rely=rely, anchor='nw')
        entry_scalar = tk.Entry(master=frame1, textvariable=tk_scalar)
        entry_scalar.place(relwidth=0.05, relheight=relh, relx=0.63, rely=rely, anchor='nw')

        label_color = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Spectrum Color:"]))
        label_color.place(relwidth=0.1, relheight=relh, relx=0.7, rely=rely, anchor='nw')
        list_color = ttk.Combobox(master=frame1, textvariable=tk_color, state="readonly")
        color_dic = {
            lang["Rainbow 4x"]: "color4x",
            lang["Rainbow 2x"]: "color2x",
            lang["Rainbow 1x"]: "color1x",
            lang["White"]: "white",
            lang["Red"]: "red",
            lang["Green"]: "green",
            lang["Blue"]: "blue",
            lang["Yellow"]: "yellow",
            lang["Magenta"]: "magenta",
            lang["Purple"]: "purple",
            lang["Cyan"]: "cyan",
            lang["Light Green"]: "lightgreen",
            lang["Gradient: Green - Blue"]: "green-blue",
            lang["Gradient: Magenta - Purple"]: "magenta-purple",
            lang["Gradient: Red - Yellow"]: "red-yellow",
            lang["Gradient: Yellow - Green"]: "yellow-green",
            lang["Gradient: Blue - Purple"]: "blue-purple",
        }

        list_color["values"] = dict2tuple(color_dic)
        list_color.current(0)
        list_color.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy
        label_bra = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Audio BR:"]))
        label_bra.place(relwidth=0.1, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        list_bra = ttk.Combobox(master=frame1, textvariable=tk_br_audio)
        list_bra["values"] = (320, 256, 192, 128, 96, 64, 48)
        list_bra.current(2)
        list_bra.place(relwidth=0.08, relheight=relh, relx=0.15, rely=rely, anchor='nw')
        label_kbps = tk.Label(master=frame1, textvariable=tk.StringVar(value="Kbps"))
        label_kbps.place(relwidth=0.05, relheight=relh, relx=0.23, rely=rely, anchor='nw')

        check_normal = tk.Checkbutton(master=frame1, text=lang["Normalize Volume"],
                                      variable=tk_audio_normal, onvalue=True, offvalue=False)
        check_normal.place(relwidth=0.15, relheight=relh, relx=0.3, rely=rely, anchor='nw')

        rely += devy
        label_preseta = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Audio Preset:"]))
        label_preseta.place(relwidth=0.1, relheight=relh, relx=0.05, rely=rely, anchor='nw')
        list_preseta = ttk.Combobox(master=frame1, textvariable=tk_preseta, state="readonly")
        audio_dic = {
            lang["Music-HQ"]+" (320 kbps)": [320, 20, 2500, False, 1.0],
            lang["Music-MQ"]+" (128 kbps)": [128, 20, 2500, False, 1.0],
            lang["Music-LQ"]+" (48 kbps)": [48, 20, 2500, False, 1.0],
            lang["Voice-HQ"]+" (320 kbps)": [320, 80, 2000, True, 0.5],
            lang["Voice-MQ"]+" (128 kbps)": [128, 80, 2000, True, 0.5],
            lang["Voice-LQ"]+" (48 kbps)": [48, 80, 2000, True, 0.5],
        }
        list_preseta["values"] = dict2tuple(audio_dic)
        list_preseta.current(0)
        list_preseta.bind("<<ComboboxSelected>>", presetAudio)
        presetAudio()
        list_preseta.place(relwidth=0.2, relheight=relh, relx=0.15, rely=rely, anchor='nw')

        label_presetv = tk.Label(master=frame1, textvariable=tk.StringVar(value=lang["Video Preset:"]))
        label_presetv.place(relwidth=0.1, relheight=relh, relx=0.4, rely=rely, anchor='nw')
        list_presetv = ttk.Combobox(master=frame1, textvariable=tk_presetv, state="readonly")
        video_dic = {
            lang["Square"]+"720p(720x720:30)": [720, 720, 30, getDefaultBR(720, 720, 30, 4)],
            lang["Square"]+"1080p(1080x1080:30)": [1080, 1080, 30, getDefaultBR(1080, 1080, 30, 5)],
            lang["Square"]+"1024p(1024x1024:30)": [1024, 1024, 30, getDefaultBR(1024, 1024, 30, 5)],
            lang["Square"]+"512p(512x512:30)": [512, 512, 30, getDefaultBR(512, 512, 30, 4)],
            lang["Square"]+"480p(480x480:30)": [480, 480, 30, getDefaultBR(480, 480, 30, 4)],
            "1080p (1920x1080:30)": [1920, 1080, 30, getDefaultBR(1920, 1080, 30, 5)],
            "720p (1280x720:30)": [1280, 720, 30, getDefaultBR(1280, 720, 30, 4)],
            "480p (854x480:30)": [854, 480, 30, getDefaultBR(854, 480, 30, 4)],
            lang["Portrait"]+"1080p (1080x1920:30)": [1080, 1920, 30, getDefaultBR(1920, 1080, 30, 5)],
            lang["Portrait"]+"720p (720x1280:30)": [720, 1280, 30, getDefaultBR(1280, 720, 30, 4)],
            lang["Portrait"]+"480p (480x854:30)": [480, 854, 30, getDefaultBR(854, 480, 30, 4)],
            "2k"+lang["(Slow)"] +"(2560x1440:30)": [2560, 1440, 30, getDefaultBR(2560, 1440, 30, 5)],
        }
        list_presetv["values"] = dict2tuple(video_dic)
        list_presetv.current(0)
        list_presetv.bind("<<ComboboxSelected>>", presetVideo)
        presetVideo()
        list_presetv.place(relwidth=0.2, relheight=relh, relx=0.5, rely=rely, anchor='nw')

        btn_prev = tk.Button(master=frame1, text=lang["Preview"], command=showPreview)
        btn_prev.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        rely += devy
        scr = scrolledtext.ScrolledText(master=frame1, width=20, height=10)
        scr.place(relwidth=0.9, relheight=0.3, relx=0.05, rely=rely, anchor='nw')

        rely += 0.33

        progress = ttk.Progressbar(master=frame1, orient=tk.HORIZONTAL, mode='determinate', value=0)
        progress.place(relwidth=0.7, relheight=relh, relx=0.05, rely=rely, anchor='nw')

        btn_blend = tk.Button(master=frame1, text=lang["Blend & Export"], command=startBlending)
        btn_blend.place(relwidth=0.15, relheight=relh, relx=0.8, rely=rely, anchor='nw')

        loadConfig()

        clog("*"*35+ " "+ lang["Welcome to use"]+" "+lang["Fanseline Audio Visualizer"]+"!"\
             +" "+"*"*35+"\n"+"\n")

        frame1.tkraise()
        root.iconphoto(False, tk.PhotoImage(file='./Source/icon-small.png'))
        root.mainloop()

