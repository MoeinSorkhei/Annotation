from tkinter import *
from PIL import Image, ImageTk
import ctypes
import os
from threading import Thread
import pydicom
import numpy as np
from matplotlib import cm

import logic
from logic import log
import globals


class Window:
    def __init__(self, master, files, position, input_type, resize_to=None):
        # attributes
        # self.logic_params = logic_params
        self.position = position
        self.enable_caption = False
        self.files = files
        logic.log(f"{'*' * 150} \n{'*' * 150} \nIn Window [__init__]: init with files list of len: {len(files)}", no_time=True)

        self.current_index = 0
        self.prev_result = None  # tuple (file name, result)

        self.current_file = files[self.current_index]  # this first file
        self.img_size = resize_to  # could be None if no resize is needed

        # ======== log the info
        logic.log(f"{'=' * 150} \ncurrent index: {self.current_index}", no_time=True)
        logic.log(f'Image: "{self.current_file.split(os.path.sep)[-1]}"')
        logic.log(f'Full path: "{self.current_file}" \n')

        # ======== frame for putting things into it
        self.frame_pos = \
            LEFT if position == 'left' else RIGHT if position == 'right' else TOP if position == 'top' else BOTTOM
        self.frame = Frame(master=master)
        self.frame.pack(side=self.frame_pos)

        # ======== window gets input from keyboard
        if input_type == 'keyboard':
            # ======== bind keyboard press to function
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
        self.photo = self.read_img_and_resize_if_needed()

        # ======== load the (first) photo in a tkinter label
        self.photo_panel = Label(self.frame, image=self.photo)
        self.photo_panel.pack(side=TOP)

        if self.enable_caption:
            self.caption_panel = Label(self.frame, text=self.current_file.split(os.path.sep)[-1], font='-size 10')
            self.caption_panel.pack(side=TOP)

        stat_text = f'Case 1 of {len(self.files)}' + \
                    (f'\nPrevious choice: {self.prev_result[1]}' if self.prev_result is not None else '')

        self.stat_panel = Label(self.frame, text=stat_text, font='-size 15')
        self.stat_panel.pack(side=RIGHT)

        # ======== prev_button
        self.prev_button = Button(master=self.frame, text="Show previous case")
        self.prev_button.bind('<Button-1>', self.show_previous_case)

        # ======== finalize button
        self.fin_button = Button(master=self.frame, text="Finalize this session \n(Takes a few seconds once clicked)")
        self.fin_button.bind('<Button-1>', self.finalize_session)

    def update_frame(self, direction):
        # ======== update current index
        if direction == 'next':
            self.current_index += 1  # index of the next file
        else:
            self.current_index -= 1  # index of the previous file

        # ======== update the buttons
        if self.current_index == 0:  # hide the prev_button for the first frame
            self.prev_button.pack_forget()

        elif self.prev_result is not None:  # show if we are in the next new frame
            self.prev_button.pack(side=BOTTOM)

        else:   # hide the prev_button again if we are in the previous window
            self.prev_button.pack_forget()

        # ======== update the image and caption
        if self.current_index == len(self.files):  # hide image and caption on the final page
            logic.log(f"{'=' * 150} \nON THE FINAL PAGE", no_time=True)
            self.photo_panel.pack_forget()
            if self.enable_caption:
                self.caption_panel.pack_forget()
            self.fin_button.pack(side=BOTTOM)

        if self.current_index != len(self.files):
            # ======== update the rest of the window
            self.current_file = self.files[self.current_index]  # next file path
            self.photo = self.read_img_and_resize_if_needed()  # resize next file
            self.photo_panel.configure(image=self.photo)  # update the image
            self.photo_panel.image = self.photo

            if self.enable_caption:
                self.caption_panel.configure(text=self.current_file.split(os.path.sep)[-1])  # update the caption

            # ======== log info
            logic.log(f"{'=' * 150} \ncurrent index: {self.current_index}", no_time=True)
            logic.log(f'Image: "{self.current_file.split(os.path.sep)[-1]}"')
            logic.log(f'Full path: "{self.current_file}" \n')

            # ======== show them (useful e.g., if they have been hidden)
            self.photo_panel.pack(side=TOP)

            if self.enable_caption:
                self.caption_panel.pack(side=TOP)

            self.fin_button.pack_forget()  # hide finalize

        # ======== update stat panel
        if self.current_index != len(self.files):
            stat_text = f'Case {self.current_index + 1} of {len(self.files)}' + \
                        (f'\nPrevious choice: {self.prev_result[1]}' if self.prev_result is not None else '')
        else:  # do not show case on the final page
            stat_text = f'\nPrevious choice: {self.prev_result[1]}'
        self.stat_panel.configure(text=stat_text)

    def finalize_session(self, event):
        log(f'\nIn [finalize_session]: Clicked "finalize_session"')
        logic.save_rating(img_name=self.prev_result[0], rate=self.prev_result[1])
        log(f'In [finalize_session]: \nSaved previous result: "{self.prev_result}"')
        logic.log('In [finalize_session]: Session is finalized. Uploading the result and terminating...\n')

        # upload the results
        logic.email_results()
        # thread = Thread(target=logic.email_results)
        # thread.start()
        # thread.join()  # waiting for it to complete
        exit(0)

    def show_previous_case(self, event):
        log(f'\nIn [show_previous_case]: Clicked "show_previous_case" ==> prev_result set to None. '
            f'Updating frame to show the previous case...')
        self.prev_result = None  # because now we are in the previous window
        self.update_frame(direction='previous')

    def keyboard_press(self, event):
        if self.current_index == len(self.files):
            logic.log(f'In [keyboard_press]: Ignoring keyboard press for index "{self.current_index}"')
            return

        pressed = repr(event.char)
        # logic.log(f'In [keyboard_press]: pressed {pressed} for image: "{self.current_file}"')
        logic.log(f'In [keyboard_press]: pressed {pressed}')

        # ======== only take action if it is a valid number, otherwise will be ignored
        if eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '3':
            # ======== save the prev result if we are not in the previous window
            if self.prev_result is not None:
                logic.save_rating(img_name=self.prev_result[0], rate=self.prev_result[1])
                log(f'In [keyboard_press]: Saved previous result: "{self.prev_result}"')

            # ======== update the prev result to current decision
            self.prev_result = (self.current_file.split(os.path.sep)[-1], eval(pressed))
            log(f'In [keyboard_press]: set prev_result to: "{self.prev_result}"')

            # ======== upload results regularly
            if self.current_index > 0 and self.current_index % globals.params['email_interval'] == 0:
                thread = Thread(target=logic.email_results)  # make it non-blocking as emailing takes time
                thread.start()

            self.update_frame(direction='next')

    def button_click(self, event):
        chosen = 'left_chosen' if self.position == 'left' else 'right_chosen'
        # logic.save_click_result(chosen)

    def read_img_and_resize_if_needed(self):
        # ======== read dicom file
        dataset = pydicom.dcmread(self.current_file)
        pixels = dataset.pixel_array
        pixels = pixels / np.max(pixels)  # normalize to 0-1

        orientation = str(dataset.get('PatientOrientation', "(missing)"))
        print(f'\nIn [read_img_and_resize_if_needed]: orientation: "{orientation}"')
        if 'A' in orientation:  # anterior view, should be flipped
            log(f'In [read_img_and_resize_if_needed]: the view is Anterior. Image is flipped when shown.')
            pixels = np.flip(pixels, axis=1)

        # apply color map, rescale to 0-255, convert to int
        image = Image.fromarray(np.uint8(cm.bone(pixels) * 255))

        if self.img_size is not None:
            # img = Image.open(self.current_file)
            resized = image.resize(self.img_size)
            photo = ImageTk.PhotoImage(resized)

        else:  # no resize
            photo = ImageTk.PhotoImage(image)
            # photo = PhotoImage(file=self.current_file)

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


def show_window_with_keyboard_input():
    root = Tk()  # creates a blank window (or main window)
    text = 'How hard is this image? (press the keyboard) \n Obviously easy: 1 \n Obviously hard: 3 \n Not sure: 2'
    title = Label(root, text=text, bg='light blue', font='-size 20')
    title.pack(fill=X)

    # IMPORTANT: the image directory has only images and not any other file, otherwise code must be refactored
    files = logic.get_files_paths(imgs_dir=globals.params['imgs_dir'])
    frame = Window(master=root, files=files,
                   position='top',
                   input_type='keyboard',
                   # logic_params=params,
                   resize_to=globals.params['img_size'])

    root.mainloop()  # run the main window continuously
