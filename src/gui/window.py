from tkinter import *
from PIL import Image, ImageTk

import logic


class Window:
    def __init__(self, master, file, position, resized=None):
        # attributes
        self.position = position
        self.file = file

        # ======== frame
        self.frame_pos = LEFT if position == 'left' else RIGHT
        self.frame = Frame(master=master)
        self.frame.pack(side=self.frame_pos)

        # ======== button
        self.button_text = "Left image is harder" if position == 'left' else "Right image is harder"
        self.button_fg = 'green' if position == 'left' else 'blue'
        self.button_fn = self.button_click

        self.button = Button(master=self.frame, text=self.button_text, fg=self.button_fg, height=3, width=20)
        self.button.bind('<Button-1>', self.button_fn)
        self.button.pack(side=BOTTOM)

        # ======== image
        if resized:
            self.photo = ImageTk.PhotoImage(self.resize_img(resized))
        else:
            self.photo = PhotoImage(file=file)

        self.photo_label = Label(self.frame, image=self.photo)
        self.photo_label.pack(side=TOP)

    def resize_img(self, size):
        img = Image.open(self.file)
        resized = img.resize(size)
        return resized

    def button_click(self, event):
        chosen = 'left_chosen' if self.position == 'left' else 'right_chosen'
        logic.save_click_result(chosen)


'''def left_button_click(event):
    logic.save_click_result('left_chosen')


def show_left_img(file, master):
    photo = PhotoImage(file=file)
    label = Label(master, image=photo)
    label.pack()


def right_button_click(event):
    logic.save_click_result('right_chosen')'''


def show_window():
    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text='Which image is harder to read? The left one or the right one?', bg='light blue', font='-size 20')
    title.pack(fill=X)

    # ========= left frame
    left_frame = Window(master=root, file="../tmp/imgs/00000001_000.png", position='left', resized=(512, 512))

    # ========= right frame
    right_frame = Window(master=root, file='../tmp/imgs/00000001_001.png', position='right', resized=(512, 512))

    root.mainloop()  # run the main window continuously


def show_window2():
    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text='Which image is harder to read? The left one or the right one?', bg='light blue')
    title.pack(fill=X)

    # ========= left frame
    left_frame = Frame(master=root)
    left_frame.pack(side=LEFT)

    left_button = Button(master=left_frame, text="Left images is harder", fg='red')
    left_button.bind('<Button-1>', left_button_click)
    left_button.pack()

    # show_left_img(file="../tmp/imgs/00000001_000.png", master=root)

    # import os
    # print(os.listdir('../tmp/'))
    # print(os.path.exists('../tmp/imgs/00000001_000.png'))
    photo = PhotoImage(file="../tmp/imgs/00000001_000.png")
    label = Label(left_frame, image=photo)
    label.pack()

    # ========= right frame
    right_frame = Frame(master=root)
    right_frame.pack(side=RIGHT)

    right_button = Button(master=right_frame, text="Right image is harder", fg='blue')
    right_button.pack()
    right_button.bind('<Button-1>', right_button_click)

    # ========= status bar
    '''status = Label(root,
                   text='2/20 done in this session --- Now Comparing THIS with THAT',
                   bd=1, relief=SUNKEN, anchor=W)
    status.pack(sid=BOTTOM, fill=X)'''

    root.mainloop()  # run the main window continuously
