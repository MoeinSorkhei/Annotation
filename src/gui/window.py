from tkinter import *
from PIL import Image, ImageTk

import logic


class Window:
    def __init__(self, master, file, position, input_type, resized=None):
        # attributes
        self.position = position
        self.file = file

        # ======== frame for putting things into it
        self.frame_pos = \
            LEFT if position == 'left' else RIGHT if position == 'right' else TOP if position == 'top' else BOTTOM
        self.frame = Frame(master=master)
        self.frame.pack(side=self.frame_pos)

        # ======== window gets input from keyboard
        if input_type == 'keyboard':
            # self.frame.bind("<Key>", self.keyboard_press)
            master.bind("<Key>", self.keyboard_press)

        # ======== window gets input from button
        if input_type == 'button':
            # ======== button
            self.button_text = "Left image is harder" if position == 'left' else "Right image is harder"
            self.button_fg = 'green' if position == 'left' else 'blue'
            self.button_fn = self.button_click

            self.button = Button(master=self.frame, text=self.button_text, fg=self.button_fg, height=3, width=20)
            self.button.bind('<Button-1>', self.button_fn)
            self.button.pack(side=BOTTOM)

        # ======== image resize
        if resized:
            self.photo = ImageTk.PhotoImage(self.resize_img(resized))
        else:
            self.photo = PhotoImage(file=file)

        # ======== load the photo in a tkinter label
        self.photo_label = Label(self.frame, image=self.photo)
        self.photo_label.pack(side=TOP)

        self.caption = Label(self.frame, text=file.split('/')[-1], font='-size 10')
        self.caption.pack(side=BOTTOM)

    def resize_img(self, size):
        img = Image.open(self.file)
        resized = img.resize(size)
        return resized

    def keyboard_press(self, event):
        pressed = repr(event.char)
        print(f'In [keyboard_press]: pressed {pressed}')

        if eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '3':
            logic.save_keyboard_result(pressed)

    def button_click(self, event):
        chosen = 'left_chosen' if self.position == 'left' else 'right_chosen'
        logic.save_click_result(chosen)


def show_window_with_button_input():
    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text='Which image is harder to read? The left one or the right one?', bg='light blue', font='-size 20')
    title.pack(fill=X)

    # ========= left frame
    left_frame = Window(master=root,
                        file="../tmp/imgs/00000001_000.png",
                        position='left',
                        input_type='button',
                        resized=(512, 512))

    # ========= right frame
    right_frame = Window(master=root,
                         file='../tmp/imgs/00000001_001.png',
                         position='right',
                         input_type='button',
                         resized=(512, 512))

    root.mainloop()  # run the main window continuously


def show_window_with_keyboard_input():
    root = Tk()  # creates a blank window (or main window)
    title = Label(root,
                  text='Which image is harder to read? The left one or the right one?',
                  bg='light blue',
                  font='-size 20')
    title.pack(fill=X)

    frame = Window(master=root, file="../tmp/imgs/00000001_000.png",
                   position='top',
                   input_type='keyboard',
                   resized=(512, 512))

    root.mainloop()  # run the main window continuously
