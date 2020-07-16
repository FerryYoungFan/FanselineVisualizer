from tkinter import *
from PIL import Image, ImageTk
from tkinter.filedialog import asksaveasfile
import tkinter.messagebox
from LanguagePack import *
import os


class ImageViewer(Frame):
    def __init__(self, master, *pargs):
        Frame.__init__(self, master, *pargs)
        self.master = master
        self.max_w, self.max_h = 1280, 720
        self.img_copy, self.image, self.background_image = None, None, None
        self.background = Label(self,bg="#666666")
        self.background.pack(fill=BOTH, expand=YES)
        self.background.bind('<Configure>', self._resize_image)
        self.place(relx=0, rely=0, relwidth=1, relheight=1, anchor='nw')
        self.ratio = 1.0
        self.background.bind("<MouseWheel>", self._on_mousewheel)
        self.bind_all('<Key>', self.shortCut)
        self.lang = lang_en
        self.menu = None
        self._genMenu()

    def _genMenu(self):
        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(label=self.lang["Save Image as..."], command=self.saveImage)
        # self.menu.add_separator()
        self.master.bind("<Button-3>", self._popupMenu)

    def _on_mousewheel(self, event):
        fac = (event.delta / 120)
        if fac > 0:
            self.ratio = self.ratio * 1.25
        elif fac < 0:
            self.ratio = self.ratio * 0.8
        if self.img_copy:
            img_w, img_h = self.img_copy.size
            ratio = self.ratio
            width = int(round(img_w * ratio))
            height = int(round(img_h * ratio))
            self.image = self.img_copy.resize((width, height))
            self.background_image = ImageTk.PhotoImage(self.image)
            self.background.configure(image=self.background_image)

    def _resize_image(self, event):
        win_w = event.width
        win_h = event.height
        if self.img_copy:
            img_w, img_h = self.img_copy.size
            ratio = min(win_w / img_w, win_h / img_h)
            self.ratio = ratio
            width = int(round(img_w * ratio))
            height = int(round(img_h * ratio))
            self.image = self.img_copy.resize((width, height))
            self.background_image = ImageTk.PhotoImage(self.image)
            self.background.configure(image=self.background_image)

    def _popupMenu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def imshow(self, image):
        self.img_copy = image.copy()
        img_w, img_h = self.img_copy.size
        ratio = min(self.max_w / img_w, self.max_h / img_h)
        if not self.winfo_viewable():
            if ratio < 1:
                width = int(round(img_w * ratio))
                height = int(round(img_h * ratio))
                self.ratio = ratio
            else:
                width = img_w
                height = img_h
                self.ratio = 1.0
            self.master.geometry("{0}x{1}".format(width, height))
            self.image = self.img_copy.resize((width, height))
            self.background_image = ImageTk.PhotoImage(self.image)
            self.background.configure(image=self.background_image)
        else:
            win_w = self.winfo_width()
            win_h = self.winfo_height()
            img_w, img_h = self.img_copy.size
            ratio = min(win_w / img_w, win_h / img_h)
            self.ratio = ratio
            width = int(round(img_w * ratio))
            height = int(round(img_h * ratio))
            self.image = self.img_copy.resize((width, height))
            self.background_image = ImageTk.PhotoImage(self.image)
            self.background.configure(image=self.background_image)

    def setGUI(self, width=1280, height=720):
        self.max_w, self.max_h = width, height

    def shortCut(self, event):
        if event.keysym == "Escape":
            self.master.withdraw()

    def setLanguage(self, lang):
        self.lang = lang
        self._genMenu()

    def saveImage(self):
        allfile = self.lang["All files"]
        if self.img_copy:
            f = asksaveasfile(mode='w', defaultextension=".png", initialfile=self.lang["Snap"],
                              filetypes=(("JPEG", "*.jpg"), ("PNG", "*.png"), ("GIF", "*.gif"), ("BMP", "*.bmp"),
                                         (allfile, "*.*")))
            if f is None:
                return
            fname = f.name
            f.close()
            try:
                if os.path.exists(fname):
                    os.remove(fname)
                self.img_copy.save(fname, quality=100)
            except:
                tkinter.messagebox.showinfo(self.lang["Notice"], self.lang["Cannot Save Image!"])


if __name__ == '__main__':
    root = Tk()
    root.title("Title")
    iv = ImageViewer(root)
    iv.imshow(Image.open("./Source/background.jpg"))
    root.mainloop()
