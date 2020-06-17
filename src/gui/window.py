from tkinter import *
from threading import Thread
from copy import deepcopy
import time

import logic
from logic import *
import globals


class Window:
    def __init__(self, master, cases, already_sorted, mode, session_name):
        # ======== attributes
        self.master = master
        self.mode = mode
        self.session_name = session_name
        self.cases = cases
        self.start_time = int(time.time() // 60)  # used for stat panel
        self.case_number = None

        # ======== log info
        logic.log(f"{'_' * 150}\nIn Window [__init__]: init with case list of len: {len(cases)}", no_time=True)

        # tuple (img, rate) or (left_img, right_img, rate) or (left_img, right_img, rate, insertion_index, mid_img)
        self.prev_result = None

        # ======== bind keyboard press to function
        master.bind("<Key>", self.keyboard_press)

        # ======== determine file(s) to show
        if mode == 'single':
            self.current_index = 0
            print(f'start time: {self.start_time}')
            self.init_or_update_case_number()
            self.log_current_index(called_from='__init__')

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
            if globals.debug:
                self.caption_panel = Label(self.frame, text=pure_name(self.current_file), font='-size 10')
                self.caption_panel.pack(side=TOP)

        if mode == 'side_by_side':
            # ======== comparisons_list which contains, for very image, lists of images that were compared against it
            self.comparisons = {}

            if len(already_sorted) > 0:  # the file sorted.txt already exists, so create the list based on them
                self.sorted_list = already_sorted
                log(f'In Window [__init__]: there ARE already_sorted images ==> init sorted_list with already_sorted '
                    f'images of len {len(self.sorted_list)}.')
                self.current_index = 0

            else:  # no sorted.txt exists, construct the list from scratch
                self.sorted_list = [self.cases[0]]
                log(
                    f'In Window [__init__]: there are NO already_sorted images ==> init sorted_list with the first image'
                    f'in the cases. sorted_list has len: {len(self.sorted_list)}.')
                self.current_index = 1  # because the first image is used to create the sorted_list

            self.comparisons.update({self.cases[0]: [[], [], []]})  # add the first image (which has no comparisons)
            log(f'In Window [__init__]: init sorted_list with len {len(self.sorted_list)}.')

            # self.current_index = 1
            self.init_or_update_case_number()
            self.log_current_index(called_from='__init__')

            self.low = 0
            self.high = len(self.sorted_list) - 1

            self.curr_left_file = self.cases[self.current_index]  # image with current index (reference image)
            # other images to be compared against - start comparison from the middle of the list
            self.curr_right_file = self.sorted_list[(self.low + self.high) // 2]
            multi_log([f'In Window [__init__]: Left Image: "{pure_name(self.curr_left_file)}"',
                       f'In Window [__init__]: Left Full path: "{self.curr_left_file}"\n',
                       f'In Window [__init__]: Right Image: "{pure_name(self.curr_right_file)}"',
                       f'In Window [__init__]: Right Full path: "{self.curr_right_file}"\n'])

            # ======= define attributes and set to None. They will be initialized in different functions.
            self.left_frame, self.right_frame = None, None
            self.left_photo, self.right_photo = None, None

            self.left_caption_panel, self.right_caption_panel = None, None
            self.photos_panel, self.left_photo_panel, self.right_photo_panel = None, None, None

            self.stat_panel = None
            self.prev_button, self.fin_button = None, None

            self.init_frames_and_photos(master)

            if globals.debug:
                self.init_caption_panels()

        self.init_stat_panel_and_buttons(master)

    def init_frames_and_photos(self, master):
        # ======== frame for putting things into it
        self.photos_panel = Frame(master)
        self.photos_panel.pack(side=TOP)

        self.left_frame = Frame(master=self.photos_panel, background="forest green")
        self.left_frame.pack(side=LEFT)

        self.right_frame = Frame(master=self.photos_panel)
        self.right_frame.pack(side=RIGHT)

        # ======== show left and right images with caption, if caption enabled
        self.left_photo, self.right_photo = self.read_img_and_resize_if_needed()

        self.left_photo_panel = Label(self.left_frame, image=self.left_photo)  # left photo panel inside left frame
        self.left_photo_panel.pack(side=LEFT, padx=5, pady=5)

        self.right_photo_panel = Label(self.right_frame, image=self.right_photo)
        self.right_photo_panel.pack(side=RIGHT)

    def init_caption_panels(self):
        self.left_caption_panel = Label(self.photos_panel, text=pure_name(self.curr_left_file),
                                        font='-size 10')
        self.left_caption_panel.pack(side=LEFT)

        self.right_caption_panel = Label(self.photos_panel, text=pure_name(self.curr_right_file),
                                         font='-size 10')
        self.right_caption_panel.pack(side=RIGHT)

    def init_stat_panel_and_buttons(self, master):
        # ======== status panel
        stat_text = f'Rating for image {self.current_index + 1} of {len(self.cases)} - Case number: {self.case_number}' + \
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
        # if self.current_index == 0:  # hide the prev_button for the first frame
        #    self.prev_button.pack_forget()

        if self.prev_result is not None:  # direction = 'next: show if we are in the next new frame
            self.prev_button.pack(side=BOTTOM)

        else:  # direction = 'previous: hide the prev_button again if we are in the previous window
            self.prev_button.pack_forget()

    def update_photos(self, frame):
        # ======== for the final frame
        if frame == 'final':
            if self.mode == 'single':
                self.photo_panel.pack_forget()
                if globals.debug:
                    self.caption_panel.pack_forget()

            if self.mode == 'side_by_side':
                self.left_frame.configure(background="white")  # remove background on the final page
                self.left_photo_panel.pack_forget()
                self.right_photo_panel.pack_forget()

                if globals.debug:
                    self.left_caption_panel.pack_forget()
                    self.right_caption_panel.pack_forget()

        # ======== for the rest of the frames
        else:
            if self.mode == 'single':
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
                if globals.debug:
                    # self.caption_panel.configure(text=self.current_file.split(os.path.sep)[-1])  # update the caption
                    self.caption_panel.configure(text=pure_name(self.current_file))  # update the caption
                    self.caption_panel.pack(side=TOP)

            if self.mode == 'side_by_side':
                # ======== update left and right files
                mid = (self.low + self.high) // 2
                self.curr_left_file = self.cases[self.current_index]  # left photo unchanged as reference
                self.curr_right_file = self.sorted_list[mid]  # right photo changed to be compared against
                log(f'In [update_photos]: Updated right photo to index: {mid} of sorted_list')

                logic.log(f'In [update_photos]: Left Image: "{pure_name(self.curr_left_file)}"')
                logic.log(f'In [update_photos]: Left Full path: "{self.curr_left_file}" \n')
                logic.log(f'In [update_photos]: Right Image: "{pure_name(self.curr_right_file)}"')
                logic.log(f'In [update_photos]: Right Full path: "{self.curr_right_file}" \n')

                # ======== make background appear on pages other than the final
                self.left_frame.configure(background="forest green")

                # ======== update photos
                self.left_photo, self.right_photo = self.read_img_and_resize_if_needed()
                self.left_photo_panel.configure(image=self.left_photo)
                self.right_photo_panel.configure(image=self.right_photo)

                self.left_photo_panel.pack(side=LEFT, padx=5, pady=5)
                self.right_photo_panel.pack(side=RIGHT)

                # ======== update captions
                if globals.debug:
                    self.left_caption_panel.configure(text=pure_name(self.curr_left_file))
                    self.right_caption_panel.configure(text=pure_name(self.curr_right_file))
                    self.left_caption_panel.pack(side=TOP)
                    self.right_caption_panel.pack(side=TOP)

    def init_or_update_case_number(self):
        self.case_number = f'{self.start_time}-{self.current_index}-{int(time.time() % 1000)}'

    def update_stat(self):
        stat_text = ''
        if self.current_index != len(self.cases):
            if self.mode == 'single':
                stat_text = f'Rating for image {self.current_index + 1} of {len(self.cases)} - Case number: {self.case_number}' + \
                            (f'\nPrevious rating: {self.prev_result[1]}' if self.prev_result is not None else '')

            if self.mode == 'side_by_side':
                stat_text = f'Rating for image {self.current_index + 1} of {len(self.cases)} - Case number: {self.case_number}' + \
                            (f'\nPrevious rating: {self.prev_result[2]}' if self.prev_result is not None else '')
        else:  # do not show case on the final page
            if self.mode == 'single':
                stat_text = f'\nPrevious rating: {self.prev_result[1]}'

            if self.mode == 'side_by_side':
                stat_text = f'\nPrevious rating: {self.prev_result[2]}'

        self.stat_panel.configure(text=stat_text)

    def update_frame(self):
        """
        Important:
            - ALl the logical changes e.g. changing the indexes etc. should be done before calling this function. This
              only changes the stuff related to UI.
        """
        # ======== print the current index (except for the final page)
        if self.current_index < len(self.cases):
            self.init_or_update_case_number()
            self.log_current_index(called_from='update_frame')

        # ======== update the prev_button
        self.update_prev_button()

        # ======== update the image and caption for finalize page - hide image(s)
        if self.current_index == len(self.cases):
            logic.log(f"\n\n\n{'=' * 150}\nON THE FINAL PAGE", no_time=True)
            # if globals.debug:
            #     print_comparisons_lists(self.comparisons)

            self.update_photos(frame='final')
            self.fin_button.pack(side=TOP)  # show finalize button

        # ======== update the image and caption for other pages - show image(s)
        if self.current_index != len(self.cases):
            self.update_photos(frame='others')
            self.fin_button.pack_forget()  # hide finalize button

        # ======== update stat panel
        self.update_stat()

    def finalize_session(self, event):
        log(f'In [finalize_session]: Clicked "finalize_session."\n')
        log(f'In [finalize_session]: saving previous result')
        self.save_prev_rating()

        log(f'In [finalize_session]: Session is finalized. Uploading the result and terminating...')

        logic.email_results()
        exit(0)

    def log_current_index(self, called_from):
        log(f"\n\n\n\n{'=' * 150} \nIn [{called_from}]: "
            f"Current index: {self.current_index} - Case number: {self.case_number}", no_time=True)
        if self.mode != 'single':
            log(f'In [{called_from}]: There are {len(self.sorted_list)} images in the sorted_list\n', no_time=True)

    def possibly_remove_item_from_list(self):
        if self.index_should_be_changed(direction='previous'):
            # only in this case we have insertion index, otherwise it is None
            insertion_index = self.prev_result[3]
            del self.sorted_list[insertion_index]  # delete the wrongly inserted element from the list
            log(f'In [possibly_remove_item_from_list]: index should be decreased ==> '
                f'removed index {insertion_index} from sorted_list - '
                f'Now sorted_list has len: {len(self.sorted_list)}')

            log(f'In [possibly_remove_item_from_list]: saving sorted_list with removed index...')
            write_sorted_list_to_file(self.sorted_list)

            if globals.debug:
                print_list(self.sorted_list)

    def possibly_update_index(self, direction):
        if self.mode == 'side_by_side':
            if direction == 'next' and self.index_should_be_changed('next'):
                self.current_index += 1  # index of the next file
                log('In [possibly_update_index]: Current index increased...')

            if direction == 'previous' and self.index_should_be_changed('previous'):
                self.current_index -= 1
                log('In [possibly_update_index]: Current index decreased...')

        else:
            # ======== update current index
            if direction == 'next':
                self.current_index += 1  # index of the next file
            else:
                self.current_index -= 1  # index of the previous file

    def index_should_be_changed(self, direction):
        """
        This function checks if the current image index should be change base on the current low and high indices.
        :param previously_pressed:
        :param direction:
        :return:

        Notes:
            - If the direction is 'next', we only check if low and high refer to the two ends of the list. They are set
              to the two ends of the list if 1) the binary search has completed, or 2) 9 was pressed.

            - If direction is 'previous', we check: 1) if 9 was previously pressed, the index has already been increased
              and should be decreased now. Otherwise if low and high are equal, it means that we were on the last step
              of the binary search, and the index has been increased, so it should be decreased now.
        """
        if direction == 'next':
            return self.low == 0 and self.high == len(self.sorted_list) - 1
            # return prev_low == prev_high or

        else:  # direction = 'previous' - previously_pressed should be provided
            prev_low, prev_high = self.prev_result[0], self.prev_result[1]
            previously_pressed = self.prev_result[2]  # if 9 was pressed previously, index has been already increased
            # return self.low == self.high or previously_pressed == '9'
            return prev_low == prev_high or previously_pressed == '9'

    def keystroke_is_valid(self, pressed):
        # ======== only take action if it is a valid number, otherwise will be ignored
        key_stroke_is_valid = \
            (self.mode == 'single' and (eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '3')) \
            or \
            (self.mode == 'side_by_side' and (eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '9'))
        return key_stroke_is_valid

    def get_prev_imgs_from_prev_result(self):
        """
        The way this function checks if the index has been changed or not is that is checks if index should would
        changed if we wanted to go to the previous frame.
        :return:
        """
        if self.index_should_be_changed(direction='previous'):
            right_img = self.prev_result[4]  # mid_image, the last image compared to before inserting to the sorted list
            left_img = self.cases[self.current_index - 1]  # the image that was newly inserted

        else:  # index has not been increased
            right_img = self.sorted_list[(self.prev_result[0] + self.prev_result[1]) // 2]  # finding mid_img index
            left_img = self.cases[self.current_index]
        return left_img, right_img

    def save_prev_rating(self):
        if self.mode == 'single':
            imgs = [self.prev_result[0]]
            rate = self.prev_result[1]
            # save_rating(self.session_name, imgs, rate)
            save_rating(imgs, rate)

        if self.mode == 'side_by_side':
            left_img, right_img = self.get_prev_imgs_from_prev_result()
            imgs = [left_img, right_img]
            rate = self.prev_result[2]
            save_rating(imgs, rate)
            self.update_and_save_comparisons_list(left_img, right_img, rate)

    def show_previous_case(self, event):
        if self.mode == 'side_by_side':
            # ======= undo the las index update by binary search
            log(
                f'In [show_previous_case]: Clicked "show_previous_case". Checking if item should be removed from list...')
            self.possibly_remove_item_from_list()

            # previously_pressed = self.prev_result[2]  # need to have it before setting prev_result to None
            # ======= revert low and high indices
            self.low, self.high = self.prev_result[0], self.prev_result[1]
            log(
                f'In [show_previous_case]: Reverted indices to: low = {self.low}, high = {self.high} 'f'==> prev_result set to None.')
            log(f'In [show_previous_case]: checking if index should be decreased...')
            self.possibly_update_index(direction='previous')  # uses prev_result to decide if index should be changed

            self.prev_result = None  # because now we are in the previous window
            log(f'In [show_previous_case]: set prev_result to None. Updating frame to show the previous case...')

        else:
            # previously_pressed = None
            self.prev_result = None  # because now we are in the previous window
            log(f'In [show_previous_case]: Clicked "show_previous_case" ==> prev_result set to None. '
                f'Updating frame to show the previous case...')

        self.update_frame()

    def keyboard_press(self, event):
        if self.current_index == len(self.cases):
            logic.log(f'In [keyboard_press]: Ignoring keyboard press for index "{self.current_index}"')
            return

        pressed = repr(event.char)
        logic.log(f'In [keyboard_press]: pressed {pressed}')

        # ======== take action if keystroke is valid
        if self.keystroke_is_valid(pressed):
            # ======== save the prev_result once confirmed (ie when keyboard is pressed on current window)
            if self.prev_result is not None:  # that is we are not in the prev window
                log(f'In [keyboard_press]: Saving previous result...')
                self.save_prev_rating()

            # ======== update the prev_result to current decision
            if self.mode == 'single':
                # self.prev_result = (pure_name(self.current_file), eval(pressed))
                self.prev_result = (self.current_file, eval(pressed))

            if self.mode == 'side_by_side':
                # ======= keep track of current indices before updating
                self.prev_result = (self.low, self.high, eval(pressed))  # updating prev_result to current choice
                log(
                    f'In [keyboard_press]: set prev_result to: (low: {self.low}, high: {self.high}, eval: {eval(pressed)})\n')

                # ======= after this low and high are changed
                self.update_binary_search_inds_and_possibly_insert(pressed)

            # ======== upload results regularly
            if self.current_index <= 1 or self.current_index % globals.params['email_interval'] == 0:
                # make it non-blocking as emailing takes time
                thread = Thread(target=logic.email_results)
                thread.start()

            self.possibly_update_index(direction='next')  # uses current low and high to decide if index should change
            self.update_frame()

    def update_binary_search_inds_and_possibly_insert(self, pressed):
        """
        This will update the low and high indices for the binary search. In case binary search is completed or 9 is
        pressed by the radiologist, it inserts the image in the right position and resets the low and high indices.
        :param pressed:
        :return:
        """
        mid = (self.low + self.high) // 2

        # ====== update the low and high indexes based ond the rating until suitable position is found
        if self.high != self.low and eval(pressed) != '9':
            if eval(pressed) == '1':  # rated as harder, go to the right half of the list
                self.low = mid if (self.high - self.low) > 1 else self.high
                log(f'In [binary_search_step]: low increased to {self.low}')

            else:  # rated as easier, go to the left half of the list
                self.high = mid
                log(f'In [binary_search_step]: high decreased to {self.high}')

            log(f'In [binary_search_step]: Updated indices: low = {self.low}, high = {self.high}')

        # ====== suitable position is found (low = high), insert here
        else:  # either mid = low = high or 9 is pressed: so we should insert
            # if 9 is pressed, meaning the two images are equal, so we directly insert to the left side of the mid_img
            if eval(pressed) == '9':
                mid_image = self.sorted_list[mid]  # this image will be needed for saving comparisons
                self.sorted_list.insert(mid, self.curr_left_file)  # insert to the left
                self.prev_result = self.prev_result + (mid, mid_image,)

                log(f'In [binary_search_step]: the two images are equal, inserted into index {mid} of sorted_list - '
                    f'Now sorted_list has len: {len(self.sorted_list)}\n')

            # otherwise, it means the binary search is in its last step, ie, low = high
            else:
                mid = self.low
                mid_image = self.sorted_list[mid]  # this image will be needed for saving comparisons
                log(f'In [binary_search_step]: low and high are equal. Inserting into list...')

                if eval(pressed) == '1':  # means that the new image is harder
                    self.sorted_list.insert(mid + 1, self.curr_left_file)  # insert to the right side if the index
                    self.prev_result = self.prev_result + (
                    mid + 1, mid_image,)  # add insertion index in case undo is needed

                    log(f'In [binary_search_step]: inserted into index {mid + 1} of sorted_list - '
                        f'Now sorted_list has len: {len(self.sorted_list)}\n')

                else:
                    self.sorted_list.insert(mid, self.curr_left_file)  # insert to the left side if the index
                    self.prev_result = self.prev_result + (
                    mid, mid_image,)  # add insertion index in case undo is needed

                    log(f'In [binary_search_step]: inserted into index {mid} of sorted_list - '
                        f'Now sorted_list has len: {len(self.sorted_list)}\n')

            # ====== save the updated list
            log(f'In [binary_search_step]: saving sorted_list...')
            write_sorted_list_to_file(self.sorted_list)
            log(
                f'In [binary_search_step]: also updated prev_result to include the insertion index: {self.prev_result[3]}')

            # ====== reset indices because after this a new image will be inserted
            self.low = 0
            self.high = len(self.sorted_list) - 1
            log(
                f'In [binary_search_step]: low and high are reset for the new image: low: {self.low}, high: {self.high}')

            if globals.debug:
                print_list(self.sorted_list)

    def update_and_save_comparisons_list(self, left_img, right_img, rate):
        """
        NOTES: Comparisons are only with respect to the reference image, ie if left image: 4.dcm is harder than right
        image: 2.dcm, since the left image is reference, only 2.dcm is added to the easier_list for 4.dcm and 4.dcm is
        not added to the harder_list for 2.dcm. This is because we only want to keep track of the images that were rated
        against the reference image (the image that is to be inserted into the list).

        ASSUMPTION: we pay attention to the latest choice by the radiologist if two choices are not compatible.
        :param left_img:
        :param right_img:
        :param rate:
        :return:
        """

        def append_item_not_exists(lst, item):
            if item not in lst:
                lst.append(item)

        # ======== add the image as the key for the first time
        if left_img not in self.comparisons.keys():
            self.comparisons.update({left_img: [[], [], []]})

        # ======== obtain the sets. easier_list: set of images that are easier than the dict key img
        easier_list, equal_list, harder_list = self.comparisons[left_img]

        if rate == '1':  # new image is harder, should add right image to easier_list
            if right_img in harder_list:  # if right image in harder set, remove it
                harder_list.remove(right_img)

            append_item_not_exists(easier_list, right_img)
            log(f'In [update_comparison_sets]: added image: "{pure_name(right_img)}" to easier_list for image: "{pure_name(left_img)}"')

        elif rate == '9':
            if right_img in harder_list:
                harder_list.remove(right_img)
            if right_img in easier_list:
                easier_list.remove(right_img)

            append_item_not_exists(equal_list, right_img)
            log(f'In [update_comparison_sets]: added image: "{pure_name(right_img)}" to equal_list for image: "{pure_name(left_img)}"')

        else:  # new image is easier, should add right image to harder_list
            if right_img in easier_list:
                easier_list.remove(right_img)

            append_item_not_exists(harder_list, right_img)
            log(f'In [update_comparison_sets]: added image: "{pure_name(right_img)}" to harder_list for image: "{pure_name(left_img)}"')

        if globals.debug:
            print_comparisons_lists(self.comparisons)

        save_comparisons_list(self.comparisons)
        log(f'In [update_comparison_sets]: saved comparison_sets to file.\n')

    def read_img_and_resize_if_needed(self):
        if self.mode == 'single':
            # return logic.read_dicom_image(self.current_file, self.img_size)
            return logic.read_dicom_and_resize(self.current_file)

        if self.mode == 'side_by_side':
            log(f'In [read_img_and_resize_if_needed]: reading the left file')
            left_photo = logic.read_dicom_and_resize(self.curr_left_file)

            log(f'In [read_img_and_resize_if_needed]: reading the right file')
            right_photo = logic.read_dicom_and_resize(self.curr_right_file)
            return left_photo, right_photo
