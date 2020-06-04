from tkinter import *
from PIL import Image, ImageTk
import ctypes
import os
from threading import Thread

import logic


class Window:
    def __init__(self, master, files, position, input_type, resize_to=None):
        # attributes
        self.position = position
        # self.file = file
        self.files = files
        logic.log(f"{'*' * 150} \n{'*' * 150} \nIn Window [__init__]: init with files list of len: {len(files)}", no_time=True)
        # print(f'In Window [__init__]: init with files list of len: {len(files)}')

        self.current_index = 0
        # print('current index', self.current_index)
        logic.log(f"{'=' * 150} \n current index: {self.current_index}", no_time=True)

        self.current_file = files[self.current_index]  # this first file
        self.img_size = resize_to  # could be None if no resize is needed

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
        self.photo = self.resize_if_needed()

        # ======== load the (first) photo in a tkinter label
        self.photo_panel = Label(self.frame, image=self.photo)
        self.photo_panel.pack(side=TOP)

        self.caption_panel = Label(self.frame, text=self.current_file.split(os.path.sep)[-1], font='-size 10')
        self.caption_panel.pack(side=BOTTOM)

    def update_frame(self):
        # ======== update window: show next image
        self.current_index += 1  # index of the next file
        logic.log(f"{'=' * 150} \ncurrent index: {self.current_index}", no_time=True)

        if self.current_index == len(self.files):
            logic.log('In [update_frame]: all images are rated. Terminating the program...\n\n\n\n\n\n')
            exit(0)

        self.current_file = self.files[self.current_index]  # next file path
        self.photo = self.resize_if_needed()  # resize next file
        self.photo_panel.configure(image=self.photo)  # update the image
        self.photo_panel.image = self.photo
        self.caption_panel.configure(text=self.current_file.split(os.path.sep)[-1])  # update the caption

    def keyboard_press(self, event):
        pressed = repr(event.char)
        logic.log(f'In [keyboard_press]: pressed {pressed} for image: "{self.current_file}"')

        # ======== only take action if it is a valid number, otherwise will be ignored
        if eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '3':
            logic.save_rating(img_name=self.current_file.split(os.path.sep)[-1], rate=eval(pressed))

            # ======== upload results regularly
            if self.current_index % 2 == 0:
                thread = Thread(target=logic.email_results)  # make it non-blocking as emailing takes time
                thread.start()
                # logic.email_results()

            self.update_frame()

    def button_click(self, event):
        chosen = 'left_chosen' if self.position == 'left' else 'right_chosen'
        # logic.save_click_result(chosen)

    def resize_if_needed(self):
        if self.img_size is not None:
            img = Image.open(self.current_file)
            resized = img.resize(self.img_size)
            photo = ImageTk.PhotoImage(resized)

        else:  # no resize
            photo = PhotoImage(file=self.current_file)

        return photo


def show_window_with_button_input():
    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text='Which image is harder to read? The left one or the right one?', bg='light blue', font='-size 20')
    title.pack(fill=X)

    # ========= left frame
    left_frame = Window(master=root,
                        file="../tmp/imgs/00000001_000.png",
                        position='left',
                        input_type='button',
                        resize_to=(512, 512))

    # ========= right frame
    right_frame = Window(master=root,
                         file='../tmp/imgs/00000001_001.png',
                         position='right',
                         input_type='button',
                         resize_to=(512, 512))

    root.mainloop()  # run the main window continuously


def show_window_with_keyboard_input(params):
    root = Tk()  # creates a blank window (or main window)
    text = 'How hard is this image? (press the keyboard) \n Obviously easy: 1 \n Obviously hard: 3 \n Not sure: 2'
    title = Label(root, text=text, bg='light blue', font='-size 20')
    title.pack(fill=X)

    # IMPORTANT: the image directory has only images and not any other file, otherwise code must be refactored
    files = logic.get_files_paths(imgs_dir=params['imgs_dir'])
    frame = Window(master=root, files=files,
                   position='top',
                   input_type='keyboard',
                   resize_to=(512, 512))

    root.mainloop()  # run the main window continuously
