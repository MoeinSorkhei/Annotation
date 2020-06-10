from tkinter import *
from PIL import Image, ImageTk
import os
from threading import Thread
from copy import deepcopy
import pydicom
import numpy as np
from matplotlib import cm

import logic
from logic import log, split_to_lines, pure_name
from logic import *
import globals


class Window:
    def __init__(self, master, mode, cases, input_type, resize_to=None):
        # ======== attributes
        self.input_type = input_type
        self.enable_caption = True
        self.cases = cases
        self.mode = mode

        # ======== log info
        logic.log(f"\n\n\n\n{'*' * 150} \n{'*' * 150} \n{'*' * 150} \n{'*' * 150} \n"
                  f"In Window [__init__]: init with case list of len: {len(cases)}", no_time=True)
        logic.log(f"Mode: {self.mode}\n", no_time=True)

        self.prev_result = None  # tuple (img, rate) or (left_img, right_img, rate) or (low, high, rate)
        self.img_size = resize_to  # could be None if no resize is needed

        # ======== bind keyboard press to function
        master.bind("<Key>", self.keyboard_press)

        # ======== determine file(s) to show
        if input_type == 'single':
            self.current_index = 0
            self.current_file = cases[self.current_index]  # this first file
            multi_log([f'Image: "{pure_name(self.current_file)}"', f'Full path: "{self.current_file}" \n'])

            # ======== frame for putting things into it
            self.frame = Frame(master=master)
            self.frame.pack(side=TOP)

            # ======== show image with caption, if caption enabled
            self.photo = self.read_img_and_resize_if_needed()

            # ==== load the photo in a tkinter label
            self.photo_panel = Label(master, image=self.photo)
            self.photo_panel.pack(side=TOP)

            # ==== caption panel (image name) if enabled
            if self.enable_caption:
                self.caption_panel = Label(self.frame, text=pure_name(self.current_file), font='-size 10')
                self.caption_panel.pack(side=TOP)

        if input_type == 'side_by_side':
            if self.mode == 'binary_insert':
                self.sorted_list = [self.cases[0]]
                self.backup_list = None
                log(f'In Window [__init__]: init sorted_list with len {len(self.sorted_list)} and set backup_list to None')

                self.current_index = 1
                self.low = 0
                self.high = len(self.sorted_list) - 1
                # self.comparisons = 0

                self.curr_left_file = self.cases[self.current_index]  # image with current index
                self.curr_right_file = self.sorted_list[0]  # other images to be compared against

            else:
                self.current_index = 0
                self.curr_left_file = cases[self.current_index][0]
                self.curr_right_file = cases[self.current_index][1]

            multi_log([f'In Window [__init__]: Left Image: "{pure_name(self.curr_left_file)}"',
                       f'In Window [__init__]: Left Full path: "{self.curr_left_file}"\n',
                       f'In Window [__init__]: Right Image: "{pure_name(self.curr_right_file)}"',
                       f'In Window [__init__]: Right Full path: "{self.curr_right_file}"\n'])

            # ======== frame for putting things into it
            self.left_frame = Frame(master=master)
            self.left_frame.pack(side=LEFT)

            self.right_frame = Frame(master=master)
            self.right_frame.pack(side=RIGHT)

            # ======== show left and right images with caption, if caption enabled
            self.left_photo, self.right_photo = self.read_img_and_resize_if_needed()
            self.photos_panel = Label(master)
            self.photos_panel.pack(side=TOP)
            # self.left_photo_panel = Label(master, image=self.left_photo)
            self.left_photo_panel = Label(self.photos_panel, image=self.left_photo)
            self.left_photo_panel.pack(side=LEFT)

            # self.right_photo_panel = Label(master, image=self.right_photo)
            self.right_photo_panel = Label(self.photos_panel, image=self.right_photo)
            self.right_photo_panel.pack(side=RIGHT)

            if self.enable_caption:
                self.left_caption_panel = Label(self.left_frame, text=pure_name(self.curr_left_file),
                                                font='-size 10')
                self.left_caption_panel.pack(side=TOP)

                self.right_caption_panel = Label(self.right_frame, text=pure_name(self.curr_right_file),
                                                 font='-size 10')
                self.right_caption_panel.pack(side=TOP)

        # ======== log the info
        log(f"\n{'=' * 150} \nCurrent index: {self.current_index}", no_time=True)
        log(f'There are {len(self.sorted_list)} images in the sorted_list\n', no_time=True)

        # ======== status panel
        stat_text = f'Case 1 of {len(self.cases)}' + \
                    (f'\nPrevious rating: {self.prev_result[1]}' if self.prev_result is not None else '')
        self.stat_panel = Label(master, text=stat_text, font='-size 15')
        self.stat_panel.pack(side=TOP)

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
                if self.mode == 'binary_insert':
                    mid = (self.low + self.high) // 2
                    # log(f'In [update_photos]: mid: {mid}')
                    self.curr_left_file = self.cases[self.current_index]  # left photo unchanged as reference
                    self.curr_right_file = self.sorted_list[mid]  # right photo changed to be compared against
                    # log(f'In [update_photos]: Updated right photo to show sorted_list[{mid}]')
                    log(f'In [update_photos]: Updated right photo to index: {mid} of sorted_list')

                else:
                    self.curr_left_file = self.cases[self.current_index][0]
                    self.curr_right_file = self.cases[self.current_index][1]

                # logic.log(f'\nLeft Image: "{self.current_left_file.split(os.path.sep)[-1]}"')
                logic.log(f'In [update_photos]: Left Image: "{pure_name(self.curr_left_file)}"')
                logic.log(f'In [update_photos]: Left Full path: "{self.curr_left_file}" \n')
                # logic.log(f'Right Image: "{self.current_right_file.split(os.path.sep)[-1]}"')
                logic.log(f'In [update_photos]: Right Image: "{pure_name(self.curr_right_file)}"')
                logic.log(f'In [update_photos]: Right Full path: "{self.curr_right_file}" \n')

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
        if self.mode == 'binary_insert':
            if direction == 'next' and self.low == 0 and self.high == len(self.sorted_list) - 1:
                self.current_index += 1  # index of the next file

            if direction == 'previous' and self.low == self.high:
                self.current_index -= 1

        else:
            # ======== update current index
            if direction == 'next':
                self.current_index += 1  # index of the next file
            else:
                self.current_index -= 1  # index of the previous file

        # ======== print the current index (except for the final page)
        if self.current_index < len(self.cases):
            log(f"\n\n\n\n{'=' * 150} \nCurrent index: {self.current_index}", no_time=True)
            log(f'There are {len(self.sorted_list)} images in the sorted_list\n', no_time=True)

            # ======== change border of the chosen image
            '''if self.input_type == 'side_by_side' and pressed is not None:
            if self.input_type == 'side_by_side':
                if eval(pressed) == '1':
                    self.left_photo_panel.config(highlightbackground='blue')
                    self.left_photo_panel.pack(side=LEFT)'''

        # ======== update the prev_button
        self.update_prev_button()

        # ======== update the image and caption for finalize page - hide image(s)
        if self.current_index == len(self.cases):
            logic.log(f"{'=' * 150} \n\n\nON THE FINAL PAGE", no_time=True)
            self.update_photos(frame='final')
            self.fin_button.pack(side=TOP)  # show finalize button

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
        # log(f'In [show_previous_case]: Clicked "show_previous_case" ==> prev_result set to None. '
        #    f'Updating frame to show the previous case...')

        if self.mode == 'binary_insert':
            prev_low, prev_high = self.prev_result[0], self.prev_result[1]
            if prev_low == prev_high:  # firs comparison is done for the next image
                self.sorted_list = self.backup_list
                log('Sorted list reverted to backup list')

            self.low, self.high = self.prev_result[0], self.prev_result[1]
            log(f'In [show_previous_case]: Clicked "show_previous_case" ==> reverted indices to: low = {self.low} - high = {self.high} '
                f'==> prev_result set to None. Updating frame to show the previous case...')
            self.prev_result = None  # because now we are in the previous window

        else:
            self.prev_result = None  # because now we are in the previous window
            log(f'In [show_previous_case]: Clicked "show_previous_case" ==> prev_result set to None. '
                f'Updating frame to show the previous case...')

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
            if self.prev_result is not None and self.mode != 'binary_insert':
                log(f'In [keyboard_press]: Saving previous result...')
                logic.save_rating(self.prev_result)

            # ======== update the prev_result to current decision
            if self.input_type == 'single':
                self.prev_result = (pure_name(self.current_file), eval(pressed))

            if self.input_type == 'side_by_side' and self.mode != 'binary_insert':
                self.prev_result = (pure_name(self.curr_left_file), pure_name(self.curr_right_file), eval(pressed))
                log(f'In [keyboard_press]: set prev_result to: \n{split_to_lines(self.prev_result)}\n')

            if self.input_type == 'side_by_side' and self.mode == 'binary_insert':
                '''if self.prev_result is not None:  # if we are not in the previous window (where prev_result is None)
                    prev_low, prev_high = self.prev_result[0], self.prev_result[1]
                    if prev_low == prev_high:  # first comparison is done for the next image
                        log(f'In [keyboard_press]: Confirmed result for previous image has been made. Now saving the list.\n')
                        # self.backup_list = None
                        # save sorted list
                        # set backup list to None'''

                # self.prev_result = (self.low, self.high, eval(pressed))
                self.prev_result = ((self.low + self.high) // 2, '', '')
                # self.binary_search_step(low=prev_low, high=prev_high, pressed=eval(pressed))
                # log(f'In [keyboard_press]: set prev_result to: (low = {self.low} - high = {self.high} - pressed = {eval(pressed)})\n')

                # log(f'In [keyboard_press]: before binary_search_step done: low = {self.low}, high = {self.high}')

                # self.low, self.high = self.update_binary_search_inds(self.low, self.high, pressed)
                self.update_binary_search_inds(pressed)

                # log(f'In [keyboard_press]: binary_search_step done: low = {self.low}, high = {self.high}')

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

    # def update_binary_search_inds(self, low, high, pressed):
    def update_binary_search_inds(self, pressed):
        mid = (self.low + self.high) // 2
        # log(f'In [binary_search_step]: before changing indices: low: {self.low}, high: {self.high}')

        # ====== update the low and high indexes based ond the rating until suitable position is found
        if self.high != self.low:
            if eval(pressed) == '1':  # rated as harder, go to the right half of the list
                self.low = mid if (self.high - self.low) > 1 else self.high
                log(f'In [binary_search_step]: low increased to {self.low}')

            else:  # rated as easier, go to the left half of the list
                self.high = mid
                log(f'In [binary_search_step]: high decreased to {self.high}')

        # ====== suitable position is found (low = high), insert here
        else:  # mid = low = high
            self.backup_list = deepcopy(self.sorted_list)
            log(f'In [binary_search_step]: backup list initialized with deep copy from sorted list')

            mid = self.low
            if eval(pressed) == '1':  # means that the new image is harder
                self.sorted_list.insert(mid + 1, self.curr_left_file)  # insert to the right side if the index
                log(f'In [binary_search_step]: inserted into index {mid + 1} of sorted_list - '
                    f'Now sorted_list has len: {len(self.sorted_list)}\n')

            else:
                self.sorted_list.insert(mid, self.curr_left_file)  # insert to the left side if the index
                log(f'In [binary_search_step]: inserted into index {mid} of sorted_list - '
                    f'Now sorted_list has len: {len(self.sorted_list)}\n')

            self.low = 0  # reset indices
            self.high = len(self.sorted_list) - 1
            log(f'In [binary_search_step]: low and high are reset for the new image: low: {self.low}, high: {self.high}')

            '''log('________________________________', no_time=True)
            log(f'In [binary_search_step]: sorted_list:')
            for item in self.sorted_list:
                log(item, no_time=True)
            log('________________________________', no_time=True)'''
            # return low, high





