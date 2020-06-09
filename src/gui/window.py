from tkinter import *
from PIL import Image, ImageTk
import os
from threading import Thread
import pydicom
import numpy as np
from matplotlib import cm

import logic
from logic import log, split_to_lines, pure_name
from logic import *
import globals


class Window:
    def __init__(self, master, cases, input_type, resize_to=None):
        # ======== attributes
        self.input_type = input_type
        self.enable_caption = False
        self.cases = cases
        logic.log(f"{'*' * 150} \n{'*' * 150} \nIn Window [__init__]: init with case list of len: {len(cases)}", no_time=True)

        self.current_index = 0
        self.prev_result = None  # tuple (img, rate) or (left_img, right_img, rate)
        self.img_size = resize_to  # could be None if no resize is needed

        # ======== log the info
        logic.log(f"\n{'=' * 150} \nCurrent index: {self.current_index}\n", no_time=True)

        # ======== determine file(s) to show
        if input_type == 'single':
            self.current_file = cases[self.current_index]  # this first file

            multi_log([f'Image: "{pure_name(self.current_file)}"', f'Full path: "{self.current_file}" \n'])

        if input_type == 'side_by_side':
            self.curr_left_file = cases[self.current_index][0]
            self.curr_right_file = cases[self.current_index][1]

            multi_log([f'Left Image: "{pure_name(self.curr_left_file)}"', f'Left Full path: "{self.curr_left_file}"\n',
                       f'Right Image: "{pure_name(self.curr_right_file)}"', f'Right Full path: "{self.curr_right_file}"\n'])

        # ======== frame for putting things into it
        if input_type == 'single':
            self.frame = Frame(master=master)
            self.frame.pack(side=TOP)

        if input_type == 'side_by_side':
            self.left_frame = Frame(master=master)
            self.left_frame.pack(side=LEFT)

            self.right_frame = Frame(master=master)
            self.right_frame.pack(side=RIGHT)

        # ======== bind keyboard press to function
        master.bind("<Key>", self.keyboard_press)

        # ======== show image with caption, if caption enabled
        if input_type == 'single':
            self.photo = self.read_img_and_resize_if_needed()

            # ======== load the (first) photo in a tkinter label
            self.photo_panel = Label(master, image=self.photo)
            self.photo_panel.pack(side=TOP)

            # ======== caption panel (image name) if enabled
            if self.enable_caption:
                self.caption_panel = Label(self.frame, text=pure_name(self.current_file), font='-size 10')
                self.caption_panel.pack(side=TOP)

        # ======== show left and right images with caption, if caption enabled
        if input_type == 'side_by_side':
            self.left_photo, self.right_photo = self.read_img_and_resize_if_needed()
            self.left_photo_panel = Label(master, image=self.left_photo)
            self.left_photo_panel.pack(side=LEFT)

            self.right_photo_panel = Label(master, image=self.right_photo)
            self.right_photo_panel.pack(side=RIGHT)

            if self.enable_caption:
                self.left_caption_panel = Label(self.left_frame, text=pure_name(self.curr_left_file), font='-size 10')
                self.left_caption_panel.pack(side=TOP)

                self.right_caption_panel = Label(self.right_frame, text=pure_name(self.curr_right_file), font='-size 10')
                self.right_caption_panel.pack(side=TOP)

        # ======== status panel
        stat_text = f'Case 1 of {len(self.cases)}' + \
                    (f'\nPrevious rating: {self.prev_result[1]}' if self.prev_result is not None else '')
        self.stat_panel = Label(master, text=stat_text, font='-size 15')
        self.stat_panel.pack(side=BOTTOM)

        # ======== prev_button
        self.prev_button = Button(master, text="Show previous case")
        self.prev_button.bind('<Button-1>', self.show_previous_case)

        # ======== finalize button
        self.fin_button = Button(master, text="Finalize this session \n(Takes a few seconds once clicked)")
        self.fin_button.bind('<Button-1>', self.finalize_session)

    def update_prev_button(self):
        if self.current_index == 0:  # hide the prev_button for the first frame
            self.prev_button.pack_forget()

        elif self.prev_result is not None:  # show if we are in the next new frame
            self.prev_button.pack(side=BOTTOM)

        else:   # hide the prev_button again if we are in the previous window
            self.prev_button.pack_forget()

    def update_photos(self, frame):
        # ======== for the final frame
        if frame == 'final':
            if self.input_type == 'single':
                self.photo_panel.pack_forget()
                if self.enable_caption:
                    self.caption_panel.pack_forget()

            if self.input_type == 'side_by_side':
                self.left_photo_panel.pack_forget()
                self.right_photo_panel.pack_forget()

                if self.enable_caption:
                    self.left_caption_panel.pack_forget()
                    self.right_caption_panel.pack_forget()

        # ======== for the rest of the frames
        else:
            if self.input_type == 'single':
                # ======== update current file
                self.current_file = self.cases[self.current_index]  # next file path
                # logic.log(f'Image: "{self.current_file.split(os.path.sep)[-1]}"')
                logic.log(f'Image: "{pure_name(self.current_file)}"')
                logic.log(f'Full path: "{self.current_file}" \n')

                # ======== update the image
                self.photo = self.read_img_and_resize_if_needed()  # resize next file
                self.photo_panel.configure(image=self.photo)  # update the image
                self.photo_panel.image = self.photo
                self.photo_panel.pack(side=TOP)

                # ======== update caption
                if self.enable_caption:
                    # self.caption_panel.configure(text=self.current_file.split(os.path.sep)[-1])  # update the caption
                    self.caption_panel.configure(text=pure_name(self.current_file))  # update the caption
                    self.caption_panel.pack(side=TOP)

            if self.input_type == 'side_by_side':
                # ======== update left and right files
                self.curr_left_file = self.cases[self.current_index][0]
                self.curr_right_file = self.cases[self.current_index][1]

                # logic.log(f'\nLeft Image: "{self.current_left_file.split(os.path.sep)[-1]}"')
                logic.log(f'Left Image: "{pure_name(self.curr_left_file)}"')
                logic.log(f'Left Full path: "{self.curr_left_file}" \n')
                # logic.log(f'Right Image: "{self.current_right_file.split(os.path.sep)[-1]}"')
                logic.log(f'Right Image: "{pure_name(self.curr_right_file)}"')
                logic.log(f'Right Full path: "{self.curr_right_file}" \n')

                # ======== update photos
                self.left_photo, self.right_photo = self.read_img_and_resize_if_needed()
                self.left_photo_panel.configure(image=self.left_photo)
                self.right_photo_panel.configure(image=self.right_photo)

                self.left_photo_panel.pack(side=LEFT)
                self.right_photo_panel.pack(side=RIGHT)

                # ======== update captions
                if self.enable_caption:
                    # self.left_caption_panel.configure(text=self.current_left_file.split(os.path.sep)[-1])
                    self.left_caption_panel.configure(text=pure_name(self.curr_left_file))
                    # self.right_caption_panel.configure(text=self.current_right_file.split(os.path.sep)[-1])
                    self.right_caption_panel.configure(text=pure_name(self.curr_right_file))
                    self.left_caption_panel.pack(side=TOP)
                    self.right_caption_panel.pack(side=TOP)

    def update_stat(self):
        stat_text = ''
        if self.current_index != len(self.cases):
            if self.input_type == 'single':
                stat_text = f'Case {self.current_index + 1} of {len(self.cases)}' + \
                            (f'\nPrevious rating: {self.prev_result[1]}' if self.prev_result is not None else '')

            if self.input_type == 'side_by_side':
                stat_text = f'Case {self.current_index + 1} of {len(self.cases)}' + \
                            (f'\nPrevious rating: {self.prev_result[2]}' if self.prev_result is not None else '')
        else:  # do not show case on the final page
            if self.input_type == 'single':
                stat_text = f'\nPrevious rating: {self.prev_result[1]}'

            if self.input_type == 'side_by_side':
                stat_text = f'\nPrevious rating: {self.prev_result[2]}'

        self.stat_panel.configure(text=stat_text)

    def update_frame(self, direction):
        # ======== update current index
        if direction == 'next':
            self.current_index += 1  # index of the next file
        else:
            self.current_index -= 1  # index of the previous file

        # ======== print the current index (except for the final page)
        if self.current_index < len(self.cases):
            logic.log(f"\n\n\n\n{'=' * 150} \nCurrent index: {self.current_index}\n", no_time=True)

        # ======== update the prev_button
        self.update_prev_button()

        # ======== update the image and caption for finalize page - hide image(s)
        if self.current_index == len(self.cases):
            logic.log(f"{'=' * 150} \n\n\nON THE FINAL PAGE", no_time=True)
            self.update_photos(frame='final')
            self.fin_button.pack(side=BOTTOM)  # show finalize button

        # ======== update the image and caption for other pages - show image(s)
        if self.current_index != len(self.cases):
            self.update_photos(frame='others')
            self.fin_button.pack_forget()  # hide finalize button

        # ======== update stat panel
        self.update_stat()

    def finalize_session(self, event):
        log(f'In [finalize_session]: Clicked "finalize_session"\n')
        logic.save_rating(self.prev_result)

        log(f'In [finalize_session]: Saved previous result')
        log(f'In [finalize_session]: Session is finalized. Uploading the result and terminating...')

        # ======== upload the results
        logic.email_results()
        exit(0)

    def show_previous_case(self, event):
        log(f'In [show_previous_case]: Clicked "show_previous_case" ==> prev_result set to None. '
            f'Updating frame to show the previous case...')
        self.prev_result = None  # because now we are in the previous window
        self.update_frame(direction='previous')

    def keystroke_is_valid(self, pressed):
        # ======== only take action if it is a valid number, otherwise will be ignored
        key_stroke_is_valid = \
            (self.input_type == 'single' and (eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '3')) \
            or \
            (self.input_type == 'side_by_side' and (eval(pressed) == '1' or eval(pressed) == '2'))
        return key_stroke_is_valid

    def keyboard_press(self, event):
        if self.current_index == len(self.cases):
            logic.log(f'In [keyboard_press]: Ignoring keyboard press for index "{self.current_index}"')
            return

        pressed = repr(event.char)
        logic.log(f'In [keyboard_press]: pressed {pressed}')

        # ======== take action if keystroke is valid
        if self.keystroke_is_valid(pressed):
            # ======== save the prev_result if we are not in the previous window (where prev_result is None)
            if self.prev_result is not None:
                log(f'In [keyboard_press]: Saving previous result...')
                logic.save_rating(self.prev_result)

            # ======== update the prev_result to current decision
            if self.input_type == 'single':
                self.prev_result = (pure_name(self.current_file), eval(pressed))

            if self.input_type == 'side_by_side':
                self.prev_result = (pure_name(self.curr_left_file), pure_name(self.curr_right_file), eval(pressed))

            log(f'In [keyboard_press]: set prev_result to: \n{split_to_lines(self.prev_result)}\n')

            # ======== upload results regularly
            if self.current_index > 0 and self.current_index % globals.params['email_interval'] == 0:
                thread = Thread(target=logic.email_results)  # make it non-blocking as emailing takes time
                thread.start()

            self.update_frame(direction='next')

    def read_img_and_resize_if_needed(self):
        if self.input_type == 'single':
            return logic.read_dicom_image(self.current_file, self.img_size)

        if self.input_type == 'side_by_side':
            log(f'In [read_img_and_resize_if_needed]: reading the left file')
            left_photo = logic.read_dicom_image(self.curr_left_file, self.img_size)

            log(f'In [read_img_and_resize_if_needed]: reading the right file')
            right_photo = logic.read_dicom_image(self.curr_right_file, self.img_size)

            return left_photo, right_photo
