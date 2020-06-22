from tkinter import *
from threading import Thread
from copy import deepcopy
import time

import logic
from logic import *
import globals


class Window:
    def __init__(self, master, cases, already_sorted, already_comparisons, show_mode, data_mode, train_bins=None):
        """
        :param master:
        :param cases:
        :param already_sorted:
        :param already_comparisons:
        :param show_mode:
        :param data_mode:
        :param train_bins:

        Notes:
            - Regarding prev_results:
              it is tuple (img, rate) for 'single' show_mode (which will not be used)

              or (low, high, rate, insertion_index, mid_img) for test data where insertion index refers to the index
              we used for inserting an image into the sorted_list and mid_image is the final middle image used for comparison
              before insertion. The last two are available only if insertion has occurred, otherwise the tuple would
              only have (low, high, rate) values.

              or (low, high, rate, bin, pos) for train where bin refers to the bin we inserted and the position for
              insertion ONLY if insertions has occurred. Otherwise the tuple would be (low, high, rate).
        """
        # ======== attributes
        self.master = master
        self.show_mode = show_mode
        self.data_mode = data_mode  # test or train
        # self.session_name = session_name
        self.cases = cases
        self.start_time = int(time.time() // 60)  # used for stat panel
        self.case_number = None

        self.prev_result = None  # 'single' show_mode will not be used ==>  no longer used

        logic.log(f"{'_' * 150}\nIn Window [__init__]: init with case list of len: {len(cases)}", no_time=True)
        master.bind("<Key>", self.keyboard_press)  # bind keyboard press to function

        # init attributes
        if show_mode == 'single':
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

        if show_mode == 'side_by_side':
            # ======== comparisons_list which contains, for very image, lists of images that were compared against it
            # this file only has comparisons in a structured way, nothing more
            self.comparisons = already_comparisons

            if self.data_mode == 'test':
                if len(already_sorted) > 0:  # the file sorted.txt already exists, so create the list based on them
                    self.sorted_list = already_sorted
                    log(f'In Window [__init__]: there ARE already_sorted images ==> init sorted_list with already_sorted '
                        f'images of len {len(self.sorted_list)}.')
                    self.current_index = 0

                else:  # no sorted.txt exists, construct the list from scratch
                    self.sorted_list = [self.cases[0]]
                    log(f'In Window [__init__]: there are NO already_sorted images ==> init sorted_list with the first image'
                        f'in the cases. sorted_list has len: {len(self.sorted_list)}.')
                    self.current_index = 1  # because the first image is used to create the sorted_list

                self.comparisons.update({self.cases[0]: [[], [], []]})  # add the first ref image (which has no comparisons so far)
                log(f'In Window [__init__]: init sorted_list with len {len(self.sorted_list)}.')

                self.low = 0
                self.high = len(self.sorted_list) - 1
                self.curr_left_file = self.cases[self.current_index]  # image with current index (reference image)
                # other images to be compared against - start comparison from the middle of the list
                self.curr_right_file = self.sorted_list[(self.low + self.high) // 2]

            else:  # for train bins
                self.bins_list = list(range(train_bins))
                self.current_index = 0
                log(f'In Window [__init__]: init bins_list with len: {len(self.bins_list)}.')  # ony used for comparing indices

                self.low = 0
                self.high = len(self.bins_list) - 1
                self.curr_left_file = self.cases[self.current_index]  # image with current index (reference image)
                which_bin = self.bins_list[(self.low + self.high) // 2]  # get the bin number to show its last img
                # read the last image (most difficult one) in the bin
                self.curr_right_file = last_img_in_bin(which_bin)  # which_bin = 0 ==> read from bin_1 file

            self.init_or_update_case_number()
            self.log_current_index(called_from='__init__')

            # self.curr_left_file = self.cases[self.current_index]  # image with current index (reference image)
            # other images to be compared against - start comparison from the middle of the list
            # self.curr_right_file = self.sorted_list[(self.low + self.high) // 2]
            if data_mode == 'train':
                log(f'In Window [__init__]: Starting comparison with the last image in bin: {which_bin + 1}')

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

    # ========== UI-level functions
    def init_frames_and_photos(self, master):
        # ======== frame for putting things into it
        self.photos_panel = Frame(master)
        self.photos_panel.pack(side=TOP)

        self.left_frame = Frame(master=self.photos_panel, background="red")
        self.left_frame.pack(side=LEFT, padx=10, pady=10)

        self.right_frame = Frame(master=self.photos_panel)
        self.right_frame.pack(side=RIGHT, padx=10, pady=10)

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
        stat_text = f'Rating for image {self.current_index + 1} (with border around it) of {len(self.cases)} - Case number: {self.case_number}' + \
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
        """
        :param frame:
        :return:

        Notes:
            - This function is a UI-level function, In this function, there is no need to check prev_result, all the
              logical values e.g. indices have already been changed in the previous functions (e.g. show_previous_case
              or keyboard_press). It only needs the current low and high indices to update the images.

            - For either 'previous' or 'next' directions, this function is called once the low and high indices are updated and the
              recent item added to the list is removed (if index has changed), so it simply used the low and high inds
              to again show the right image.
        """
        # ======== for the final frame
        if frame == 'final':
            if self.show_mode == 'single':
                self.photo_panel.pack_forget()
                if globals.debug:
                    self.caption_panel.pack_forget()

            if self.show_mode == 'side_by_side':
                self.left_frame.configure(background="white")  # remove background on the final page
                self.left_photo_panel.pack_forget()
                self.right_photo_panel.pack_forget()

                if globals.debug:
                    self.left_caption_panel.pack_forget()
                    self.right_caption_panel.pack_forget()

        # ======== for the rest of the frames
        else:
            if self.show_mode == 'single':
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

            if self.show_mode == 'side_by_side':
                # ======== update left and right files
                mid = (self.low + self.high) // 2
                self.curr_left_file = self.cases[self.current_index]  # left photo unchanged as reference

                if self.data_mode == 'test':
                    self.curr_right_file = self.sorted_list[mid]  # right photo changed to be compared against
                    log(f'In [update_photos]: Updated right photo to index: {mid} of sorted_list')

                else:
                    self.curr_right_file = last_img_in_bin(which_bin=mid)
                    log(f'In [update_photos]: Updated right photo to last image of bin: {mid + 1}.\n')

                logic.log(f'In [update_photos]: Left Image: "{pure_name(self.curr_left_file)}"')
                logic.log(f'In [update_photos]: Left Full path: "{self.curr_left_file}" \n')
                logic.log(f'In [update_photos]: Right Image: "{pure_name(self.curr_right_file)}"')
                logic.log(f'In [update_photos]: Right Full path: "{self.curr_right_file}" \n')

                # ======== make background appear on pages other than the final
                self.left_frame.configure(background="red")

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
            if self.show_mode == 'single':
                stat_text = f'Rating for image {self.current_index + 1} of {len(self.cases)} - Case number: {self.case_number}' + \
                            (f'\nPrevious rating: {self.prev_result[1]}' if self.prev_result is not None else '')

            if self.show_mode == 'side_by_side':
                stat_text = f'Rating for image {self.current_index + 1} (with border around it) of {len(self.cases)} - Case number: {self.case_number}' + \
                            (f'\nPrevious rating: {self.prev_result[2]}' if self.prev_result is not None else '')
        else:  # do not show case on the final page
            if self.show_mode == 'single':
                stat_text = f'\nPrevious rating: {self.prev_result[1]}'

            if self.show_mode == 'side_by_side':
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
            log(f"\n\n\n{'=' * 150}\nON THE FINAL PAGE", no_time=True)
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

    # ========== functions for saving previous state
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

        def add_to_ref_img_easier_list_and_save(ref_img, compared_to, comparisons):
            easier_list, equal_list, harder_list = comparisons[ref_img]
            if compared_to in harder_list:  # if right image in harder set, remove it
                harder_list.remove(compared_to)

            append_item_not_exists(easier_list, compared_to)
            log(f'In [update_comparison_sets]: added image: "{pure_name(compared_to)}" to easier_list for image: "{pure_name(ref_img)}"')
            return comparisons

        def add_to_ref_img_harder_list_and_save(ref_img, compared_to, comparisons):
            easier_list, equal_list, harder_list = comparisons[ref_img]
            if compared_to in easier_list:
                easier_list.remove(compared_to)

            append_item_not_exists(harder_list, compared_to)
            log(f'In [update_comparison_sets]: added image: "{pure_name(compared_to)}" to harder_list for image: "{pure_name(ref_img)}"')
            return comparisons

        def add_to_ref_img_equal_and_save(ref_img, compared_to, comparisons):
            easier_list, equal_list, harder_list = comparisons[ref_img]
            if compared_to in harder_list:
                harder_list.remove(compared_to)

            if compared_to in easier_list:
                easier_list.remove(compared_to)

            append_item_not_exists(equal_list, compared_to)
            log(f'In [update_comparison_sets]: added image: "{pure_name(compared_to)}" to equal_list for image: "{pure_name(ref_img)}"')
            return comparisons

        # ======== add the images as the keys for the first time
        if left_img not in self.comparisons.keys():
            self.comparisons.update({left_img: [[], [], []]})
        if right_img not in self.comparisons.keys():
            self.comparisons.update({right_img: [[], [], []]})

        if rate == '1':  # ref image is harder, should add right image to easier_list
            # add right_img to easier_list for left img
            self.comparisons = add_to_ref_img_easier_list_and_save(ref_img=left_img,
                                                                   compared_to=right_img,
                                                                   comparisons=self.comparisons)
            # add left_img to harder_list for right img
            self.comparisons = add_to_ref_img_harder_list_and_save(ref_img=right_img,
                                                                   compared_to=left_img,
                                                                   comparisons=self.comparisons)

        elif rate == '9':
            self.comparisons = add_to_ref_img_equal_and_save(ref_img=left_img,
                                                             compared_to=right_img,
                                                             comparisons=self.comparisons)
            self.comparisons = add_to_ref_img_equal_and_save(ref_img=right_img,
                                                             compared_to=left_img,
                                                             comparisons=self.comparisons)

        else:  # ref image is easier, should add right image to harder_list
            self.comparisons = add_to_ref_img_harder_list_and_save(ref_img=left_img,
                                                                   compared_to=right_img,
                                                                   comparisons=self.comparisons)
            self.comparisons = add_to_ref_img_easier_list_and_save(ref_img=right_img,
                                                                   compared_to=left_img,
                                                                   comparisons=self.comparisons)

        if globals.debug:
            print_comparisons_lists(self.comparisons)

        save_comparisons_list(self.comparisons)
        log(f'In [update_comparison_sets]: saved comparison_sets to file.\n')

    def get_prev_imgs_from_prev_result(self):
        """
        The way this function checks if the index has been changed or not is that is checks if index should would
        changed if we wanted to go to the previous frame.
        :return:

        Notes:
            - This function is called for saving the previous result once it is confirmed. Since the current indices
              are changed based on the keyboard button pressed on the current window, it needs the prev_result to retrieve
              the previous low and high indices and the rate. And since the sorted_list or the bin might have been updated
              if the index was increased, it needs to do some calculation to get the previous indices.
        """
        if self.data_mode == 'test':
            if self.index_should_be_changed(direction='previous'):
                right_img = self.prev_result[4]  # mid_image, the last image compared to before inserting to the sorted list
                left_img = self.cases[self.current_index - 1]  # the image that was newly inserted

            else:
                prev_mid = (self.prev_result[0] + self.prev_result[1]) // 2
                right_img = self.sorted_list[prev_mid]  # finding mid_img index, sorted_list has not changed
                left_img = self.cases[self.current_index]

        else:
            # prev_bin could always be specified by the mid index, no matter an image has been inserted or not
            prev_bin = (self.prev_result[0] + self.prev_result[1]) // 2

            if self.index_should_be_changed(direction='previous'):
                left_img = self.cases[self.current_index - 1]
                prev_bin_imgs, insert_pos = read_imgs_from_bin(prev_bin), self.prev_result[4]
                # in case item has been inserted: get the correct last item if a new item has been inserted into the bin
                right_img = prev_bin_imgs[-1] if insert_pos == 'before_last' else prev_bin_imgs[-2]

            else:  # index has not changed
                left_img = self.cases[self.current_index]
                right_img = last_img_in_bin(prev_bin)

        return left_img, right_img

    def save_prev_rating(self):
        if self.show_mode == 'single':
            imgs = [self.prev_result[0]]
            rate = self.prev_result[1]
            # save_rating(self.session_name, imgs, rate)
            save_rating(imgs, rate)

        if self.show_mode == 'side_by_side':
            left_img, right_img = self.get_prev_imgs_from_prev_result()
            imgs = [left_img, right_img]
            rate = self.prev_result[2]
            save_rating(imgs, rate)
            self.update_and_save_comparisons_list(left_img, right_img, rate)

    # ========== functions for checking things
    def index_should_be_changed(self, direction):
        """
        This function checks if the current image index should be change base on the current low and high indices.
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
            if self.data_mode == 'test':
                return self.low == 0 and self.high == len(self.sorted_list) - 1
            else:
                return self.low == 0 and self.high == len(self.bins_list) - 1

        else:  # direction = 'previous' - previously_pressed should be provided
            prev_low, prev_high = self.prev_result[0], self.prev_result[1]
            previously_pressed = self.prev_result[2]  # if 9 was pressed previously, index has been already increased
            return prev_low == prev_high or previously_pressed == '9'

    def keystroke_is_valid(self, pressed):
        # ======== only take action if it is a valid number, otherwise will be ignored
        key_stroke_is_valid = \
            (self.show_mode == 'single' and (eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '3')) \
            or \
            (self.show_mode == 'side_by_side' and (
                    eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '9'))
        return key_stroke_is_valid

    # ========== functions for updating indices and the list
    def possibly_remove_item_from_list(self):
        if self.index_should_be_changed(direction='previous'):
            if self.data_mode == 'test':
                insertion_index = self.prev_result[3]  # only in this case we have insertion index, otherwise it is None
                del self.sorted_list[insertion_index]  # delete the wrongly inserted element from the list
                log(f'In [possibly_remove_item_from_list]: index should be decreased ==> '
                    f'removed index {insertion_index} from sorted_list - '
                    f'Now sorted_list has len: {len(self.sorted_list)}')

                log(f'In [possibly_remove_item_from_list]: saving sorted_list with removed index...')
                write_sorted_list_to_file(self.sorted_list)

                if globals.debug:
                    print_list(self.sorted_list)

            else:  # e.g. prev_result: (left_img, right_img, rate, bin, 'last')
                which_bin, insert_pos = self.prev_result[3], self.prev_result[4]
                log(f'In [possibly_remove_item_from_list]: removing the "{insert_pos}" element from bin {which_bin + 1}')
                del_from_bin_and_save(which_bin, insert_pos)

    def possibly_update_index(self, direction):
        if self.show_mode == 'side_by_side':
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

    # ========== functions for showing the next/previous case
    def show_previous_case(self, event):
        """
        :param event:
        :return:
        Notes:
            - ALL the logical steps (updating indices and the list) happen in this function before updating the frame
              to show the previous case.

        Procedure: We undo all the steps that have been done in the keyboard_press function.
            1. If an item has been added to the list, we remove it.
            2. We revert the low and high indices to the previous state.
            3. We decrement the index of the reference image (left image) if the index was increased the previous step.
            4. Once all the indices and the list have been reverted, we update the frame.
        """
        if self.show_mode == 'side_by_side':
            # ======= undo the las index update by binary search
            log(f'In [show_previous_case]: Clicked "show_previous_case". Checking if item should be removed from list...')
            self.possibly_remove_item_from_list()

            # ======= revert low and high indices
            self.low, self.high = self.prev_result[0], self.prev_result[1]
            log(f'In [show_previous_case]: Reverted indices to: low = {self.low}, high = {self.high} 'f'==> prev_result set to None.')
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
        """
        :param event:
        :return:

        Notes:
            - ALL the logical steps (saving previous result, keeping track of current indices, updating indices and list etc.)
              happen in this function before updating the frame to show the next case.

        Procedure:
            1. If a button is pressed, it means that the previous result is confirmed, ie, the radiologist does not want
               to go to the previous window. So the prev_result will be saved.
            2. Once the previous result is saved, current indices (along with the rate) will replace the previous result.
            3. Once we take note of current indices and keep them in prev_result, we update the indices using binary search.
            4. The binary search function updates the indices and if the search has completed (or 9 is pressed), it inserts
               the new image to the list, and adds the insertion index and the previous mid_img to prev_result so we could
               use them again if the radiologist wants to get back in the next window.
            5. If insertion has occurred, the index of the current left image will be incremented to show the next image.
            6. Now that the indices are updated, update_frame function updates the window in a UI-level based on the
               updated low and high indices.
        """
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
            if self.show_mode == 'single':
                # self.prev_result = (pure_name(self.current_file), eval(pressed))
                self.prev_result = (self.current_file, eval(pressed))

            if self.show_mode == 'side_by_side':
                self.prev_result = (self.low, self.high, eval(pressed))  # updating prev_result to current choice
                log(f'In [keyboard_press]: set prev_result to: (low: {self.low}, high: {self.high}, eval: {eval(pressed)})\n')

                # now that we keep indices in prev_result, we can update them
                self.update_binary_search_inds_and_possibly_insert(pressed)

            # ======== upload results regularly
            if self.current_index <= 1 or self.current_index % globals.params['email_interval'] == 0:
                thread = Thread(target=logic.email_results)  # make it non-blocking as emailing takes time
                thread.start()

            self.possibly_update_index(direction='next')  # uses current low and high to decide if index should change
            self.update_frame()  # update the frame and photos based in the new low and high indices

    # ========== very logical functions
    def update_binary_search_inds_and_possibly_insert(self, pressed):
        """
        This will update the low and high indices for the binary search. In case binary search is completed or 9 is
        pressed by the radiologist, it inserts the image in the right position and resets the low and high indices.
        :param pressed:
        :return:
        """
        mid = (self.low + self.high) // 2  # for train data, this represents bin number
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
        else:
            # for test data
            if self.data_mode == 'test':
                mid_image = self.sorted_list[mid]
                # if both images are equal
                if eval(pressed) == '9':  # 9 is pressed, so we insert directly
                    self.sorted_list.insert(mid, self.curr_left_file)  # insert to the left
                    self.prev_result = self.prev_result + (mid, mid_image,)
                    log(f'In [binary_search_step]: the two images are equal, inserted into index {mid} of sorted_list - '
                        f'Now sorted_list has len: {len(self.sorted_list)}\n')

                # if ref image is harder (and binary search is completed)
                if eval(pressed) == '1':
                    log(f'In [binary_search_step]: low and high are equal. '
                        f'Inserting into list...')
                    self.sorted_list.insert(mid + 1, self.curr_left_file)  # insert to the right side if the index
                    self.prev_result = self.prev_result + (mid + 1, mid_image,)  # add insertion index in case undo is needed
                    log(f'In [binary_search_step]: inserted into index {mid + 1} of sorted_list - '
                        f'Now sorted_list has len: {len(self.sorted_list)}\n')

                # if ref image is easier (and binary search is completed)
                if eval(pressed) == '2':
                    log(f'In [binary_search_step]: low and high are equal. '
                        f'Inserting into list...')
                    self.sorted_list.insert(mid, self.curr_left_file)  # insert to the left side if the index
                    self.prev_result = self.prev_result + (mid, mid_image,)  # add insertion index in case undo is needed
                    log(f'In [binary_search_step]: inserted into index {mid} of sorted_list - '
                        f'Now sorted_list has len: {len(self.sorted_list)}\n')

                # save the modified list
                log(f'In [binary_search_step]: saving '
                    f'sorted_list...')
                write_sorted_list_to_file(self.sorted_list)
                log(f'In [binary_search_step]: also updated prev_result to include the '
                    f'insertion index: {self.prev_result[3]}')

                # reset the indices for the next round of binary search
                log(f'In [binary_search_step]: also updated prev_result to have '
                    f'mid index and img_img.')
                self.low = 0
                self.high = len(self.sorted_list) - 1
                log(f'In [binary_search_step]: low and high are reset for the new image: '
                    f'low: {self.low}, high: {self.high}\n')

                if globals.debug:
                    print_list(self.sorted_list)

            # for train data
            else:
                # if both images are equal
                if eval(pressed) == '9':
                    insert_into_bin_and_save(which_bin=mid, pos='before_last', img=self.curr_left_file)
                    self.prev_result = self.prev_result + (mid, 'before_last',)  # mid represent the bin here
                    log(f'In [binary_search_step]: the two images are equal, inserted into pos '
                        f'"before_last" of bin {mid + 1}')
                    log(f'In [binary_search_step]: also updated prev_result to have bin number '
                        f'and insertion pos.\n')

                # if ref image is harder (and binary search is completed)
                if eval(pressed) == '1':
                    log(f'In [binary_search_step]: low and high are equal. '
                        f'Inserting into bin...')
                    insert_into_bin_and_save(which_bin=mid, pos='last', img=self.curr_left_file)
                    self.prev_result = self.prev_result + (mid, 'last',)  # bin and the insertion position
                    log(f'In [binary_search_step]: inserted into pos "last" of '
                        f'bin {mid + 1} and saved bin.')

                # if ref image is easier (and binary search is completed)
                if eval(pressed) == '2':
                    log(f'In [binary_search_step]: low and high are equal. '
                        f'Inserting into bin...')
                    insert_into_bin_and_save(which_bin=mid, pos='before_last', img=self.curr_left_file)
                    self.prev_result = self.prev_result + (mid, 'before_last',)  # bin and the insertion position
                    log(f'In [binary_search_step]: inserted into pos '
                        f'"before_last" of bin {mid + 1} and saved bin.')

                log(f'In [binary_search_step]: also updated prev_result to have bin number '
                    f'and insertion pos.')
                self.low = 0
                self.high = len(self.bins_list) - 1
                log(f'In [binary_search_step]: low and high are reset for the new image: '
                    f'low: {self.low}, high: {self.high}\n')

    def read_img_and_resize_if_needed(self):
        if self.show_mode == 'single':
            # return logic.read_dicom_image(self.current_file, self.img_size)
            return logic.read_dicom_and_resize(self.current_file)

        if self.show_mode == 'side_by_side':
            log(f'In [read_img_and_resize_if_needed]: reading the left file')
            left_photo = logic.read_dicom_and_resize(self.curr_left_file)

            log(f'In [read_img_and_resize_if_needed]: reading the right file')
            right_photo = logic.read_dicom_and_resize(self.curr_right_file)
            return left_photo, right_photo

    def log_current_index(self, called_from):
        log(f"\n\n\n\n{'=' * 150} \nIn [{called_from}]: "
            f"Current index: {self.current_index} - Case number: {self.case_number}", no_time=True)
        if self.show_mode != 'single' and self.data_mode != 'train':
            log(f'In [{called_from}]: There are {len(self.sorted_list)} images in the sorted_list\n', no_time=True)
