from tkinter import *
from threading import Thread
import time

from .logical import *


class Window:
    def __init__(self, master, cases, already_sorted, already_comparisons, show_mode, data_mode, search_type, train_bins=None):
        """
        :param master:
        :param cases:
        :param already_sorted:
        :param already_comparisons:
        :param show_mode:
        :param data_mode:
        :param search_type: could be 'normal' or 'robust'. If 'normal', the binary search is done as usual, and if
        'robust', 3-way comparison will be done.
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
        self.cases = cases
        self.show_mode = show_mode  # single or side_by_side
        self.data_mode = data_mode  # test or train
        self.search_type = search_type   # 'normal' or 'robust'
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
            log_current_index(self, called_from='__init__')

            self.current_file = cases[self.current_index]  # this first file
            multi_log([f'Image: "{pure_name(self.current_file)}"', f'Full path: "{self.current_file}" \n'])

            # ======== frame for putting things into it
            self.frame = Frame(master=master)
            self.frame.pack(side=TOP)

            # ======== show image with caption, if caption enabled
            self.photo = read_img_and_resize_if_needed(self)

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
            self.curr_left_file, self.curr_right_file = None, None

            if search_type == 'robust':
                self.low_consistency = 'unspecified'
                self.high_consistency = 'unspecified'

            if self.data_mode == 'test':
                if len(already_sorted) > 0:  # the file sorted.txt already exists, so create the list based on them
                    self.sorted_list = already_sorted
                    log(f'In Window [__init__]: there ARE already_sorted images ==> init sorted_list with already_sorted '
                        f'images of len {len(self.sorted_list)}.')
                    self.current_index = 0

                else:  # no sorted.txt exists, construct the list from scratch
                    self.sorted_list = [self.cases[0]]
                    log(f'In Window [__init__]: there are NO already_sorted images ==> init sorted_list with the first image '
                        f'in the cases. sorted_list has len: {len(self.sorted_list)}.')
                    self.current_index = 1  # because the first image is used to create the sorted_list

                self.comparisons.update({self.cases[0]: [[], [], []]})  # add the first ref image (which has no comparisons so far)
                log(f'In Window [__init__]: init sorted_list with len {len(self.sorted_list)}.')

                self.low = 0
                self.high = len(self.sorted_list) - 1

                # if search_type == 'robust':
                #     self.low_consistency = 'unspecified'
                #     self.high_consistency = 'unspecified'

                self.init_or_update_case_number()
                log_current_index(self, called_from='__init__')
                self.update_files()  # left and right files to be shown

            else:  # for train bins
                self.bins_list = list(range(train_bins))  # e.g. [0, ..., 31], only indicates bin indices
                self.current_index = 0
                log(f'In Window [__init__]: init bins_list with len: {len(self.bins_list)}.')  # ony used for comparing indices

                self.low = 0
                self.high = len(self.bins_list) - 1

                # if search_type == 'robust':
                #     self.low_consistency = 'unspecified'
                #     self.high_consistency = 'unspecified'

                self.init_or_update_case_number()
                log_current_index(self, called_from='__init__')
                self.update_files()

                # self.curr_left_file = self.cases[self.current_index]  # image with current index (reference image)
                # which_bin = self.bins_list[(self.low + self.high) // 2]  # get the bin number to show its last img
                # # read the last image (most difficult one) in the bin
                # self.curr_right_file = last_img_in_bin(which_bin)  # which_bin = 0 ==> read from bin_1 file

                # if data_mode == 'train':
                # log(f'In Window [__init__]: Starting comparison with the last image in bin: {which_bin + 1}')

            # ======= define attributes and set to None. They will be initialized in different functions.
            self.left_frame, self.right_frame = None, None
            self.left_photo, self.right_photo = None, None

            self.left_caption_panel, self.right_caption_panel = None, None
            self.photos_panel, self.left_photo_panel, self.right_photo_panel = None, None, None

            self.stat_panel = None
            self.prev_button, self.fin_button = None, None
            self.discard_button = None

            self.init_frames_and_photos(master)

            if globals.debug:
                self.init_caption_panels()

        self.init_stat_panel_and_buttons(master)

    # ======================================== UI-level functions  ========================================
    # =====================================================================================================
    def init_frames_and_photos(self, master):
        # ======== frame for putting things into it
        self.photos_panel = Frame(master)
        self.photos_panel.pack(side=TOP)

        self.left_frame = Frame(master=self.photos_panel, background="red")
        self.left_frame.pack(side=LEFT, padx=10, pady=10)

        self.right_frame = Frame(master=self.photos_panel)
        self.right_frame.pack(side=RIGHT, padx=10, pady=10)

        # ======== show left and right images with caption, if caption enabled
        # self.left_photo, self.right_photo = self.read_img_and_resize_if_needed()
        self.left_photo, self.right_photo = read_img_and_resize_if_needed(self)

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
        stat_text = f'Rating for image {self.current_index + 1} (with border around it) of {len(self.cases)} - ' \
                    f'Case number: {self.case_number}' + \
                    (f'\nPrevious rating: {self.prev_result["rate"]}' if self.prev_result is not None else '')
        self.stat_panel = Label(master, text=stat_text, font='-size 15')
        self.stat_panel.pack(side=TOP)

        # ======== prev_button
        self.prev_button = Button(master, text="Show previous case")
        self.prev_button.bind('<Button-1>', self.show_previous_case)

        # ======== discard button
        self.discard_button = Button(master, text='Discard this case')
        self.discard_button.bind('<Button-1>', self.discard_case)
        self.discard_button.pack(side=BOTTOM)  # show it in the first page

        # ======== finalize button
        self.fin_button = Button(master, text="Finalize this session \n(Takes a few seconds once clicked)")
        self.fin_button.bind('<Button-1>', self.finalize_session)

    def update_prev_button(self):
        if self.prev_result is not None:  # direction = 'next: show if we are in the next new frame
            self.prev_button.pack(side=BOTTOM)

        else:  # direction = 'previous: hide the prev_button again if we are in the previous window
            self.prev_button.pack_forget()

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
                            (f'\nPrevious rating: {self.prev_result["rate"]}' if self.prev_result is not None else '')

        else:  # do not show case on the final page
            if self.show_mode == 'single':
                stat_text = f'\nPrevious rating: {self.prev_result["rate"]}'

            if self.show_mode == 'side_by_side':
                # if prev_result is None: previous case was discarded
                stat_text = f'\nPrevious rating: {self.prev_result["rate"]}' if self.prev_result is not None else ''

        self.stat_panel.configure(text=stat_text)

    def update_files(self):
        """
        The behavior of this function depends on whether or not we are doing robust check and whether we are
        dealing with test or train data.

        :return:
        """
        # ======== update left and right files
        mid = (self.low + self.high) // 2
        self.curr_left_file = self.cases[self.current_index]  # left photo unchanged as reference

        if self.data_mode == 'test':
            if do_robust_checking(self):
                log(f'In [update_files]: SHOULD DO ROBUST CHECKING...')

                if to_be_checked_for_consistency(self) == 'low':
                    self.curr_right_file = self.sorted_list[self.low]
                    log(f'In [update_files]: Checking with "low" ==> Updated right photo to index '
                        f'low: {self.low} of sorted_list\n')

                elif to_be_checked_for_consistency(self) == 'high':
                    self.curr_right_file = self.sorted_list[self.high]
                    log(f'In [update_files]: Checking with "high" ==> Updated right photo to index '
                        f'high: {self.high} of sorted_list\n')

                elif to_be_checked_for_consistency(self) == 'middle':
                    self.curr_right_file = self.sorted_list[mid]  # right photo changed to be compared against
                    log(f'In [update_files]: Checking with "middle" ==> Updated right photo to index '
                        f'mid: {mid} of sorted_list\n')

            # normal mode
            else:
                log(f'In [update_files]: NO ROBUST CHECKING NEEDED... \n')
                self.curr_right_file = self.sorted_list[mid]  # right photo changed to be compared against
                log(f'In [update_files]: Updated right photo to index middle: {mid} of sorted_list')

        # train data
        else:
            if do_robust_checking(self):
                log(f'In [update_files]: SHOULD DO ROBUST CHECKING...')

                if to_be_checked_for_consistency(self) == 'low':
                    self.curr_right_file = last_img_in_bin(which_bin=self.low)
                    log(f'In [update_files]: Checking with "low" ==> Updated right photo to last image of bin '
                        f'low: {self.low + 1}\n')

                elif to_be_checked_for_consistency(self) == 'high':
                    self.curr_right_file = last_img_in_bin(which_bin=self.high)
                    log(f'In [update_files]: Checking with "high" ==> Updated right photo to last image of bin '
                        f'high: {self.high + 1}\n')

                elif to_be_checked_for_consistency(self) == 'middle':
                    self.curr_right_file = last_img_in_bin(which_bin=mid)
                    log(f'In [update_files]: Checking with "middle" ==> Updated right photo to last image of bin '
                        f'middle: {mid + 1}\n')

            else:
                log(f'In [update_files]: NO ROBUST CHECKING NEEDED... \n')
                self.curr_right_file = last_img_in_bin(which_bin=mid)
                log(f'In [update_files]: Updated right photo to '
                    f'last image of bin middle: {mid + 1}.\n')  # +1 is for printing bin 0 as bin 1

        logic.log(f'In [update_files]: Left file: "{pure_name(self.curr_left_file)}"')
        logic.log(f'In [update_files]: Left Full path: "{self.curr_left_file}" \n')
        logic.log(f'In [update_files]: Right file: "{pure_name(self.curr_right_file)}"')
        logic.log(f'In [update_files]: Right Full path: "{self.curr_right_file}" \n')

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


        Possible configurations in a window for the robust search:
            - self.low_consistency == 'unspecified' and self.high_consistency == 'unspecified', in which case we show
              the left image and update low_consistency based on the rate
            - self.low_consistency is True and self.high_consistency == 'unspecified', in which case the right image is shown
            - low_consistency and high_consistency are both True, in which case the middle image is show. We had already
              aborted the case if one of them have been False.
        """
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

        else:
            if self.show_mode == 'single':
                # ======== update current file
                self.current_file = self.cases[self.current_index]  # next file path
                logic.log(f'Image: "{pure_name(self.current_file)}"')
                logic.log(f'Full path: "{self.current_file}" \n')

                # ======== update the image
                self.photo = read_img_and_resize_if_needed(self)  # resize next file
                self.photo_panel.configure(image=self.photo)  # update the image
                self.photo_panel.image = self.photo
                self.photo_panel.pack(side=TOP)

                # ======== update caption
                if globals.debug:
                    self.caption_panel.configure(text=pure_name(self.current_file))  # update the caption
                    self.caption_panel.pack(side=TOP)

            if self.show_mode == 'side_by_side':
                self.update_files()

                # ======== make background appear on pages other than the final
                self.left_frame.configure(background="red")
                # ======== update photos
                self.left_photo, self.right_photo = read_img_and_resize_if_needed(self)
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

    def update_frame(self):
        """
        Important:
            - ALl the logical changes e.g. changing the indexes etc. should be done before calling this function. This
              only changes the stuff related to UI.
        """
        # ======== print the current index (except for the final page)
        if self.current_index < len(self.cases):
            self.init_or_update_case_number()
            log_current_index(self, called_from='update_frame')

        # ======== update the prev_button
        self.update_prev_button()

        # ======== update the image and caption for finalize page - hide image(s)
        if self.current_index == len(self.cases):
            log(f"\n\n\n{'=' * 150}\nON THE FINAL PAGE", no_time=True)
            self.update_photos(frame='final')
            self.fin_button.pack(side=TOP)  # show finalize button
            self.discard_button.pack_forget()

        # ======== update the image and caption for other pages - show image(s)
        if self.current_index != len(self.cases):
            self.update_photos(frame='others')
            self.fin_button.pack_forget()  # hide finalize button
            self.discard_button.pack(side=BOTTOM)

        # ======== update stat panel
        self.update_stat()

    # ======================================== logical functions  ========================================
    # ====================================================================================================
    def finalize_session(self, event):
        log(f'In [finalize_session]: Clicked "finalize_session."\n')
        # log(f'In [finalize_session]: saving previous result...')
        # save_prev_rating(self)
        log(f'In [finalize_session]: saving aborted cases...')
        save_aborted_cases(self)

        log(f'In [finalize_session]: Session is finalized. Uploading the result and terminating...')

        logic.email_results()
        exit(0)

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
            # undo the las index update by binary search
            log(f'In [show_previous_case]: Clicked "show_previous_case". Checking if item should be removed from list...')
            possibly_remove_item_from_list(self)
            revert_indices_and_possibly_consistency_indicators(self)

            log(f'In [show_previous_case]: checking if index should be decreased...')
            possibly_update_index(self, direction='previous')  # uses prev_result to decide if index should be changed

            self.prev_result = None  # because now we are in the previous window
            log(f'In [show_previous_case]: set prev_result to None. Updating frame to show the previous case...')

        else:
            # previously_pressed = None
            self.prev_result = None  # because now we are in the previous window
            log(f'In [show_previous_case]: Clicked "show_previous_case" ==> prev_result set to None. '
                f'Updating frame to show the previous case...')

        self.update_frame()

    def discard_case(self, event):
        self.current_index += 1
        reset_indices_and_possibly_consistency_indicators(self)
        self.prev_result = None
        self.update_frame()
        log('In [discard_case]: current_index increased, indices reset, and prev_result set to None. Frame updated...\n')

    def abort_if_not_consistent(self):  # no difference whether to be used for test or train data
        if self.low_consistency is False or self.high_consistency is False:
            log(f'In [abort_current_case]: increasing current index, '
                f'resetting indices/indicators, setting prev_result["aborted"] to True...')

            self.current_index += 1
            self.prev_result['aborted'] = True
            reset_indices_and_possibly_consistency_indicators(self)

            log(f'In [abort_current_case]: aborting: done.\n')

    def check_for_consistency(self, pressed, with_respect_to):  # no difference whether to be used for test or train data
        if with_respect_to == 'low':
            if is_consistent(pressed, with_respect_to='low'):
                self.low_consistency = True
                log(f'In [check_consistency_and_abort_if_not_consistent]: case IS consistent '
                    f'with respect to "low" \n')

            else:
                self.low_consistency = False
                log(f'In [check_consistency_and_abort_if_not_consistent]: case IS NOT consistent '
                    f'with respect to "low" \n')

        if with_respect_to == 'high':
            if is_consistent(pressed, with_respect_to='high'):
                self.high_consistency = True
                log(f'In [check_consistency_and_abort_if_not_consistent]: case IS consistent '
                    f'with respect to "high" \n')

            else:
                self.high_consistency = False
                log(f'In [check_consistency_and_abort_if_not_consistent]: case IS NOT consistent '
                    f'with respect to "high" \n')

            log(f'In [check_for_consistency]: low and high indicators changed to: '
                f'"low_consistency": {self.low_consistency}, "high_consistency": {self.high_consistency} \n')

    def init_or_update_prev_result(self, pressed):
        if do_robust_checking(self):
            if self.prev_result is None:
                self.prev_result = {}
                log(f'In [init_or_update_prev_result]: prev_result is None ==> initialized prev_result with: '
                    f'an empty dictionary')

            self.prev_result['low'] = self.low
            self.prev_result['high'] = self.high
            self.prev_result['low_consistency'] = self.low_consistency
            self.prev_result['high_consistency'] = self.high_consistency
            self.prev_result['rate'] = eval(pressed)
            self.prev_result['aborted'] = False  # default, will set to True in the abort function

            log(f'In [init_or_update_prev_result]: updated prev_result to have indices/indicators and rate - now prev_result is: \n'
                f'{self.prev_result} \n')
            # log(f'In [init_or_update_prev_result]: now prev_result is: \n'
            #     f'{self.prev_result} \n')

        # normal mode
        else:
            self.prev_result = {'low': self.low, 'high': self.high, 'rate': eval(pressed)}  # updating to current choice
            log(f'In [init_or_update_prev_result]: set prev_result to: {self.prev_result}\n')

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
        logic.log(f'In [keyboard_press]: pressed {pressed}\n')

        # ======== take action if keystroke is valid (ie, prev_result is confirmed)
        if keystroke_is_valid(self, pressed):
            # ======== save the prev_result once confirmed (ie when keyboard is pressed on current window)
            # if self.prev_result is not None:  # that is we are not in the prev window
            #     log(f'In [keyboard_press]: Saving previous result...')
            #     save_prev_rating(self)

            # ======== update the prev_result to current decision
            if self.show_mode == 'single':
                # self.prev_result = (pure_name(self.current_file), eval(pressed))
                self.prev_result = (self.current_file, eval(pressed))

            if self.show_mode == 'side_by_side':
                if do_robust_checking(self):
                    # log(f'In [keyboard_press]: '
                    #     f'SHOULD DO ROBUST CHECKING... \n')

                    # first store current attributes in prev_result before changing them for the next window
                    self.init_or_update_prev_result(pressed)

                    if to_be_checked_for_consistency(self) == 'low':
                        self.check_for_consistency(pressed, with_respect_to='low')  # updates the consistency indicators
                        self.abort_if_not_consistent()

                    elif to_be_checked_for_consistency(self) == 'high':
                        self.check_for_consistency(pressed, with_respect_to='high')  # updates the consistency indicators
                        self.abort_if_not_consistent()

                    elif to_be_checked_for_consistency(self) == 'middle':
                        update_binary_search_inds_and_possibly_insert(self, pressed)
                        possibly_update_index(self, direction='next')  # uses current low and high to decide if index should change

                # normal mode
                else:
                    # log(f'In [keyboard_press]: NO ROBUST '
                    #     f'CHECKING NEEDED...')

                    # first store current attributes in prev_result before changing them for the next window
                    self.init_or_update_prev_result(pressed)
                    # now that we keep indices in prev_result, we can update them
                    update_binary_search_inds_and_possibly_insert(self, pressed)
                    possibly_update_index(self, direction='next')  # uses current low and high to decide if index should change

            # ======== upload results regularly
            if self.current_index <= 1 or self.current_index % globals.params['email_interval'] == 0:
                thread = Thread(target=logic.email_results)  # make it non-blocking as emailing takes time
                thread.start()

            # possibly_update_index(self, direction='next')  # uses current low and high to decide if index should change
            self.update_frame()  # update the frame and photos based in the new low and high indices

