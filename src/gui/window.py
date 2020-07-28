from tkinter import *
import time
from copy import deepcopy

from .logical import *


class Window:
    def __init__(self, master, cases, already_sorted, data_mode, ui_verbosity, n_bins=None):
        """
        :param master:
        :param cases:
        :param already_sorted:
        :param data_mode:
        :param n_bins:

        Notes:
            - Regarding prev_results:
              it is tuple (img, rate) for 'single' show_mode (which will not be used)

              or (low, high, rate, insertion_index, mid_img) for test data where insertion index refers to the index
              we used for inserting an image into the sorted_list and mid_image is the final middle image used for comparison
              before insertion. The last two are available only if insertion has occurred, otherwise the tuple would
              only have (low, high, rate) values.

              or (low, high, rate, bin, pos) for train where bin refers to the bin we inserted and the position for
              insertion ONLY if insertions has occurred. Otherwise the tuple would be (low, high, rate).


        Important notes about the window attributes and prev_result for ternary search:
            - The prev_result also has these attributes of the previous window: low, high, m1_rate, m2_rate
            - Possible situations:
              1) m1_rate = None, m2_rate = None: either getting rate for m1 or doing usual check (will be checked based on the
              robust_checking_needed function)
              2) m1_rate = some number, m2_rate = None: we are getting rate for m2

            - The 'aborted' attribute in prev_result is only to show if the rating that happened in the previous window
              resulted in aborting or not. The window itself does not have this attribute, this attributes is added to
              prev_result a key is pressed on the window.
        """
        self.master = master
        self.cases = cases
        self.data_mode = data_mode  # test or train
        self.ui_verbosity = ui_verbosity
        self.start_time = int(time.time() // 60)  # used for stat panel
        self.case_number = None

        self.prev_result = None

        logic.log(f"{'_' * 150}\nIn Window [__init__]: init with case list of len: {len(cases)}", no_time=True)
        master.bind("<Key>", self.keyboard_press)  # bind keyboard press to function

        self.curr_left_file, self.curr_right_file = None, None
        self.comp_level = 1

        self.m1_rate = None  # default
        self.m2_rate = None
        self.m1_anchor = None
        self.m2_anchor = None

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

            log(f'In Window [__init__]: init sorted_list with len {len(self.sorted_list)}.')

            self.low = 0
            self.high = len(self.sorted_list) - 1

        # train mode
        else:
            self.m1_rep = None  # whenever m1_anchor has a value, m1_rep should also have a value
            self.m2_rep = None  # representatives are actual image names
            self.rep = None  # used only in binary search - m1_rep and m2_rep only used in robust checking

            self.bins_list = list(range(n_bins))  # e.g. [0, ..., 31], only indicates bin indices
            self.current_index = 0
            log(f'In Window [__init__]: init bins_list with len: {len(self.bins_list)}.')  # ony used for comparing indices

            self.low = 0
            self.high = len(self.bins_list) - 1

        self.compute_case_number()
        log_current_index(self, called_from='__init__')
        self.update_files()

        # ======= define attributes and set to None. They will be initialized in different functions.
        self.left_frame, self.right_frame = None, None
        self.left_photo, self.right_photo = None, None
        self.rate_1_indicator, self.rate_2_indicator, self.rate_9_indicator = None, None, None

        self.left_caption_panel, self.right_caption_panel = None, None
        self.photos_panel, self.left_photo_panel, self.right_photo_panel = None, None, None

        self.stat_panel = None
        self.prev_button, self.fin_button = None, None
        self.discard_button = None

        self.init_frames_and_photos(master)  # init and pack
        self.init_stat_panel_and_buttons(master)  # init and pack
        self.update_stat()  # put content

        if self.ui_verbosity > 1:
            self.init_caption_panels()

    # ======================================== UI-level functions  ========================================
    # =====================================================================================================
    def init_frames_and_photos(self, master):
        # ======== frame for putting things into it
        self.photos_panel = Frame(master)
        self.photos_panel.pack(side=TOP)

        self.left_frame = Frame(master=self.photos_panel)
        self.left_frame.pack(side=LEFT)

        self.right_frame = Frame(master=self.photos_panel)
        self.right_frame.pack(side=RIGHT)

        self.rate_9_indicator = Label(master=self.photos_panel, text='9', bg='red', fg='white')
        self.rate_1_indicator = Label(master=self.left_frame, text='1', bg='red', fg='white')
        self.rate_2_indicator = Label(master=self.right_frame, text='2', bg='red', fg='white')
        self.rate_9_indicator.pack(side=TOP)
        self.rate_1_indicator.pack(side=TOP)
        self.rate_2_indicator.pack(side=TOP)

        # ======== show left and right images with caption
        self.left_photo_panel = Label(self.left_frame)
        self.right_photo_panel = Label(self.right_frame)
        self._load_images_into_panels()

    def init_caption_panels(self):
        # caption for showing image names
        self.left_caption_panel = Label(self.photos_panel,
                                        text=shorten_file_name(pure_name(self.curr_left_file)),
                                        font='-size 10')
        self.left_caption_panel.pack(side=LEFT)

        self.right_caption_panel = Label(self.photos_panel,
                                         text=shorten_file_name(pure_name(self.curr_right_file)),
                                         font='-size 10')
        self.right_caption_panel.pack(side=RIGHT)

    def init_stat_panel_and_buttons(self, master):
        # stat panel for showing case number, buttons etc.
        self.stat_panel = Label(master, text='', font='-size 15')
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

    def compute_case_number(self):
        self.case_number = f'{self.start_time}-{self.current_index}-{int(time.time() % 1000)}'

    def create_verbose_stat(self):
        def as_text(item):
            return f'{item}' if item is not None else None

        def _get_compare_index():
            if robust_checking_needed(self):
                if showing_window_for(self) == 'm1':
                    # return f'{self.m1_anchor}' if self.data_mode == 'test' else f'{self.m1_anchor + 1}'
                    return f'{self.m1_anchor}'
                else:
                    # return f'{self.m2_anchor}' if self.data_mode == 'test' else f'{self.m2_anchor + 1}'
                    return f'{self.m2_anchor}'
            else:  # binary
                return f'{(self.low + self.high) // 2}'
                # return f'{(self.low + self.high) // 2}' if self.data_mode == 'test' \
                #     else f'{(self.low + self.high) // 2 + 1}'

        if self.ui_verbosity < 3:
            return ''

        verbose_text = ''
        if self.ui_verbosity >= 3:
            interval_text = f'Search interval: [{self.low} - {self.high}] ' \
                            f'of [{0} - {len(self.sorted_list) - 1 if self.data_mode == "test" else len(self.bins_list) - 1}]'

            index_or_bin = 'index' if self.data_mode == 'test' else 'bin'
            compare_text = f'Comparing with {index_or_bin}: {_get_compare_index()} - ' \
                           f'Level: {self.comp_level} - ' \
                           f'Search: {"ternary" if robust_checking_needed(self) else "binary"}'

            level_2_text = f'{interval_text} - {compare_text}'
            verbose_text += f'\n\n{level_2_text}'

        if self.ui_verbosity == 4:
            anchors_text = f'm1_anchor: {as_text(self.m1_anchor)} \t m2_anchor: {as_text(self.m2_anchor)}'

            rep_text = ''
            if self.data_mode == 'train':
                rep_text = f'm1_rep: {as_text(pure_name(self.m1_rep))} \t m2_rep: {as_text(pure_name(self.m2_rep))} \t' \
                           f'rep: {as_text(pure_name(self.rep))}'

            rate_text = f'm1_rate: {as_text(self.m1_rate)} \t\t m2_rate: {self.m2_rate}'

            level_3_text = f'{anchors_text}\t\t{rep_text}\n\n{rate_text}'
            verbose_text += f'\n{"_" * 100}\n{level_3_text}'

        return verbose_text

    def update_stat(self):
        # final page
        if self.current_index == len(self.cases):
            stat_text = ''
        # other pages
        else:
            stat_text = f'Rating for image {self.current_index + 1} of {len(self.cases)} - ' \
                        f'Case number: {self.case_number}'

            if self.prev_result is not None:
                rate_text = f'Previous rate: ' \
                            f'{self.prev_result["rate"]} ({rate_to_text(self.prev_result["rate"])})'
                stat_text += f'\n{rate_text}'

            stat_text += f'{self.create_verbose_stat()}'

        self.stat_panel.configure(text=stat_text)

    def update_files(self):
        """
        The behavior of this function depends on whether or not we are doing robust check and whether we are
        dealing with test or train data.

        :return:
        """
        # ======== update left and right files
        self.curr_left_file = self.cases[self.current_index]  # left photo unchanged as reference

        if robust_checking_needed(self, print_details=False):
            _curr_anchor, _curr_rep = init_or_use_anchor_and_rep(self)

            # update right file for test mode
            if self.data_mode == 'test':
                self.curr_right_file = self.sorted_list[_curr_anchor]
                log(f'In [update_files]: Updated right photo to '
                    f'show element: {_curr_anchor} of sorted_list \n')

            # update right file for train mode
            else:
                self.curr_right_file = _curr_rep
                log(f'In [update_files]: Updated right photo to '
                    f'show representative: "{pure_name(_curr_rep)}" of bin_{_curr_anchor}.txt\n')

        else:
            mid = (self.low + self.high) // 2
            if self.data_mode == 'test':
                self.curr_right_file = self.sorted_list[mid]  # right photo changed to be compared against
                log(f'In [update_files]: Updated right photo to index middle: '
                    f'{mid} of sorted_list')
            else:
                rep = init_or_use_rep(self, mid)
                self.curr_right_file = rep
                log(f'In [update_files]: Updated right photo to show rep: '
                    f'"{pure_name(rep)}" of bin_{mid}.txt')

        logic.log(f'In [update_files]: Left file: "{pure_name(self.curr_left_file)}"')
        logic.log(f'In [update_files]: Right file: "{pure_name(self.curr_right_file)}"\n\n')

    def _load_images_into_panels(self):
        now = time.time()
        left_image, right_image = read_and_resize_imgs(self, threading=True)
        self.left_photo = ImageTk.PhotoImage(image=left_image)
        self.right_photo = ImageTk.PhotoImage(image=right_image)
        then = time.time()
        log(f'%%%%%%%%%%%%% %%%%%%%%%%% PHOTOS LOADED - Took: {then - now}')

        self.left_photo_panel.configure(image=self.left_photo)
        self.right_photo_panel.configure(image=self.right_photo)
        self.left_photo_panel.pack(side=LEFT, padx=5, pady=5)
        self.right_photo_panel.pack(side=RIGHT, padx=5, pady=5)

    def update_photos(self, frame, files_already_updated):
        """
        :param files_already_updated:
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
            self.left_photo_panel.pack_forget()
            self.right_photo_panel.pack_forget()

            if globals.debug:
                self.left_caption_panel.pack_forget()
                self.right_caption_panel.pack_forget()

        else:
            if not files_already_updated:
                self.update_files()

            # ======== update photos
            self._load_images_into_panels()

            # ======== update captions (image names)
            if self.ui_verbosity > 1:
                self.left_caption_panel.configure(text=shorten_file_name(pure_name(self.curr_left_file)))
                self.right_caption_panel.configure(text=shorten_file_name(pure_name(self.curr_right_file)))
                self.left_caption_panel.pack(side=LEFT)
                self.right_caption_panel.pack(side=RIGHT)

    def _delayed_update_photos(self, frame, files_already_updated):
        self.left_frame.configure(bg="white")
        self.right_frame.configure(bg="white")
        self.update_photos(frame, files_already_updated)

    def update_photos_async(self, rate, frame, files_already_updated):
        if rate == '1':  # draw left border
            self.left_frame.configure(bg='red')
            self.left_frame.after(100, self._delayed_update_photos, frame, files_already_updated)

        elif rate == '2':  # draw right border
            self.right_frame.configure(bg='red')
            self.right_frame.after(100, self._delayed_update_photos, frame, files_already_updated)

        else:  # if 9 is pressed, or showing previous case
            self.update_photos(frame, files_already_updated)

    def update_frame(self, rate=None, files_already_updated=False):
        """
        Important:
            - ALl the logical changes e.g. changing the indexes etc. should be done before calling this function. This
              only changes the stuff related to UI.
        """
        # ======== final page
        if self.current_index == len(self.cases):
            log(f"\n\n\n{'=' * 150}\nON THE FINAL PAGE", no_time=True)
            self.fin_button.pack(side=TOP)  # show finalize button
            self.discard_button.pack_forget()
            self.rate_9_indicator.pack_forget()
            self.rate_1_indicator.pack_forget()
            self.rate_2_indicator.pack_forget()
            self.update_photos_async(rate, 'final', files_already_updated)
            # self.update_photos(frame='final', files_already_updated=files_already_updated)

        # ======== other pages
        if self.current_index != len(self.cases):
            self.compute_case_number()
            log_current_index(self, called_from='update_frame')
            self.rate_9_indicator.pack(side=TOP)
            self.rate_1_indicator.pack(side=TOP)
            self.rate_2_indicator.pack(side=TOP)
            self.update_photos_async(rate, 'others', files_already_updated)
            # self.update_photos(frame='others', files_already_updated=files_already_updated)
            self.fin_button.pack_forget()  # hide finalize button
            self.discard_button.pack(side=BOTTOM)

        # ======== update stat panel
        self.update_prev_button()
        self.update_stat()

    # ======================================== logical functions  ========================================
    # ====================================================================================================
    def finalize_session(self, event):
        log(f'In [finalize_session]: Clicked "finalize_session."')

        if globals.params['email_interval'] is not None:
            logic.email_results()

        log(f'In [finalize_session]: All done')
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
        log(f'In [show_previous_case]: Clicked "show_previous_case".')

        remove_last_rating()
        log(f'In [show_previous_case]: '
            f'removed the last rate')

        # remove if we have inserted
        if 'insert_index' in self.prev_result.keys():
            log(f'In [show_previous_case]: "insert_index" available in prev_result, '
                f'should remove from list...')
            remove_last_inserted(self)

        if 'aborted' in self.prev_result.keys() and self.prev_result['aborted']:
            log(f'In [show_previous_case]: '
                f'removed last aborted item from aborted file.')
            remove_last_aborted()

        # revert the window attributes
        revert_attributes(self)

        self.prev_result = None  # because now we are in the previous window
        log(f'In [show_previous_case]: set prev_result to None. Updating frame to show the previous case...')

        self.update_frame()

    def discard_case(self, event):
        log(f'In [discard_case]: Pushed the Discard button. Discarding the case...')
        save_to_discarded_list(self.curr_left_file)  # save current left file to discarded.txt

        self.current_index += 1
        reset_attributes(self)
        self.prev_result = None

        log('In [discard_case]: current_index increased, indices reset, '
            'and prev_result set to None. Updating the frame...\n')
        self.update_frame()

    def keep_current_state_in_prev_result(self, pressed):
        if self.prev_result is None:  # either for m1 or normal case
            self.prev_result = {}
            log(f'In [keep_current_state_in_prev_result]: prev_result is None ==> initialized prev_result with: '
                f'an empty dictionary')

        # generic attributes
        self.prev_result['current_index'] = self.current_index
        self.prev_result['comp_level'] = self.comp_level
        self.prev_result['low'] = self.low
        self.prev_result['high'] = self.high
        self.prev_result['rate'] = eval(pressed)  # regardless of search mode

        # ternary attributes (will remain None for binary)
        self.prev_result['m1_anchor'] = self.m1_anchor
        self.prev_result['m2_anchor'] = self.m2_anchor

        self.prev_result['m1_rate'] = self.m1_rate
        self.prev_result['m2_rate'] = self.m2_rate

        if robust_checking_needed(self) and showing_window_for(self) == 'm2':
            self.prev_result['aborted'] = False  # set as default, might change to True after consistency check

        # attributes specific for training
        if self.data_mode == 'train':
            self.prev_result['m1_rep'] = self.m1_rep
            self.prev_result['m2_rep'] = self.m2_rep
            self.prev_result['rep'] = self.rep

        log(f'In [keep_current_state_in_prev_result]: now prev_result is: \n{shorten(deepcopy(self.prev_result))}\n')

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
        def _rate_automatically():
            log(f'\n{"*" * 100}', no_time=True)
            log('In [keyboard_press] - automatic rate: Checking if '
                'rate is already available for the next case.\n')
            self.update_files()
            update_file_called = True

            # if the rate exists, perform updates based on available ratings
            rate = get_rate_if_already_exists(self.curr_left_file, self.curr_right_file)

            if rate is None:
                log(f'In [keyboard_press] - automatic rate: rate NOT already available. '
                    f'Updating window to get the rate....')

            while rate is not None:  # rate already exists
                log(f'In [keyboard_press] - automatic rate: rate ALREADY AVAILABLE '
                    f'for the the next case and is: {rate}')
                if matches_binary_insert_rule(self, rate):
                    log(f'In [keyboard_press] - automatic rate: matches with insertion rule. Inserting...')
                    insert_with_binary_inds(self, rate, self.curr_left_file)
                    reset_attributes_and_increase_index(self)
                    update_file_called = False
                    break

                else:
                    update_binary_inds(self, rate)
                    reset_attributes(self, exclude_inds=True, new_comp_level=self.comp_level + 1)
                    self.update_files()
                    rate = get_rate_if_already_exists(self.curr_left_file, self.curr_right_file)
                    log(f'In [keyboard_press] - automatic rate: updated - again checking '
                        f'if already available for the next case...')
                    if rate is None:
                        log(f'In [keyboard_press] - automatic rate: rate NOT already available. '
                            f'Updating window to get the rate....')
            log(f'{"*" * 100}\n', no_time=True)
            return update_file_called

        # ignore keyboard press for the final page
        if self.current_index == len(self.cases):
            logic.log(f'In [keyboard_press]: Ignoring keyboard press for index "{self.current_index}"')
            return

        pressed = repr(event.char)
        logic.log(f'In [keyboard_press]: pressed {pressed}')

        # ======== take action if keystroke is valid (ie, prev_result is confirmed)
        if keystroke_is_valid(pressed):
            save_rating(self.curr_left_file, self.curr_right_file, eval(pressed))
            log(f'In [keyboard_press]: saved the rating\n')
            files_already_updated = False
            insert_happened = False
            abort_happened = False

            if robust_checking_needed(self):
                # showing for m1
                if showing_window_for(self) == 'm1':
                    log(f'In [keyboard_press]: showing '
                        f'window for: m1')
                    self.prev_result = None  # init prev result from scratch
                    self.keep_current_state_in_prev_result(pressed)
                    self.m1_rate = eval(pressed)  # to be used in the next page

                # showing for m2
                else:
                    log(f'In [keyboard_press]: showing '
                        f'window for: m2')
                    self.keep_current_state_in_prev_result(pressed)
                    rule = calc_rule(self.m1_rate, eval(pressed))

                    if 'update' in rule:
                        update_ternary_indices(self, update_type=rule)
                        reset_attributes(self, exclude_inds=True, new_comp_level=self.comp_level + 1)
                        log(f'In [keyboard_press]: Updated ternary indices according to "{rule}". '
                            f'Now low = {self.low}, high = {self.high}.\n')

                    elif rule == 'insert_m1':
                        insert_with_ternary_inds(self, anchor=self.m1_anchor, item=self.curr_left_file)
                        reset_attributes_and_increase_index(self)
                        insert_happened = True
                        log(f'In [keyboard_press]: inserted directly to "m1_anchor" and reset attributes - '
                            f'current_index increased to {self.current_index}')

                    elif rule == 'insert_m2':
                        insert_with_ternary_inds(self, anchor=self.m2_anchor, item=self.curr_left_file)
                        reset_attributes_and_increase_index(self)
                        insert_happened = True
                        log(f'In [keyboard_press]: inserted directly to "m2_anchor" and reset attributes - '
                            f'current_index increased to {self.current_index}')

                    else:  # abort
                        self.prev_result['aborted'] = True
                        reset_attributes_and_increase_index(self)
                        abort_happened = True
                        save_to_aborted_list(self.curr_left_file)
                        log(f'In [keyboard_press]: rates are INCONSISTENT. Case aborted and reset attributes - '
                            f'current_index increased to: {self.current_index}')

            # normal binary mode
            else:
                self.keep_current_state_in_prev_result(pressed)

                # insert
                if matches_binary_insert_rule(self, eval(pressed)):
                    insert_with_binary_inds(self, eval(pressed), self.curr_left_file)
                    reset_attributes_and_increase_index(self)
                    insert_happened = True
                    log(f'In [keyboard_press]: reset attributes after binary insert - '
                        f'current_index increased to: {self.current_index}\n')

                # update indices
                else:
                    update_binary_inds(self, eval(pressed))
                    reset_attributes(self, exclude_inds=True, new_comp_level=self.comp_level + 1)

            upload_results_regularly(self)
            # check automatically if the rate is available for the next page(s)
            if not insert_happened and not abort_happened and not robust_checking_needed(self):
                files_already_updated = _rate_automatically()

            self.update_frame(eval(pressed), files_already_updated)
