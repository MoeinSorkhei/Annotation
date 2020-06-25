from logic import *
import logic
import globals


# ========== functions for checking things/resetting
def keystroke_is_valid(window, pressed):
    # ======== only take action if it is a valid number, otherwise will be ignored
    key_stroke_is_valid = \
        (window.show_mode == 'single' and (eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '3')) \
        or \
        (window.show_mode == 'side_by_side' and (
                eval(pressed) == '1' or eval(pressed) == '2' or eval(pressed) == '9'))
    return key_stroke_is_valid


def to_be_checked_for_consistency(window):  # checks with the current indices/indicators of the window
    if window.low_consistency == 'unspecified' and window.high_consistency == 'unspecified':
        return 'low'

    elif window.low_consistency is True and window.high_consistency == 'unspecified':  # low already consistent
        return 'high'

    elif window.low_consistency is True and window.high_consistency is True:  # low and right consistent
        return 'middle'

    else:
        raise NotImplementedError('The configuration is not implemented')


def is_consistent(pressed, with_respect_to):
    if with_respect_to == 'low' and (eval(pressed) == '1' or eval(pressed) == '9'):
        return True
    if with_respect_to == 'high' and (eval(pressed) == '2' or eval(pressed) == '9'):
        return True
    return False


def prev_case_was_aborted(prev_result):
    """
    Previous case has been aborted either in consistency checking for the low image or in the checking with the high image.
    In the first case low_consistency would be False and in the second case high_consistency would be False.
    :param prev_result:
    :return:
    """
    if prev_result['low_consistency'] is False or prev_result['high_consistency'] is False:
        return True
    return False


def index_should_be_changed(window, direction):
    """
    This function checks if the current image index should be change base on the current low and high indices.
    :param window:
    :param direction:
    :return:

    Notes:
        - If the direction is 'next', we only check if low and high refer to the two ends of the list. They are set
          to the two ends of the list if 1) the binary search has completed, or 2) 9 was pressed.

        - If direction is 'previous', we check: 1) if 9 was previously pressed, the index has already been increased
          and should be decreased now. Otherwise if low and high are equal, it means that we were on the last step
          of the binary search, and the index has been increased, so it should be decreased now.
        - In the case of abortion, the index is directly increased without checking this function.
    """
    if direction == 'next':
        if window.data_mode == 'test':
            return window.low == 0 and window.high == len(window.sorted_list) - 1
        else:
            return window.low == 0 and window.high == len(window.bins_list) - 1

    else:  # direction = 'previous' - previously_pressed should be provided
        prev_low, prev_high = window.prev_result['low'], window.prev_result['high']
        previously_pressed = window.prev_result['rate']  # if 9 was pressed previously, index has been already increased

        if 'aborted' in window.prev_result.keys() and window.prev_result['aborted'] is True:  # no remove if we have aborted
            log(f'In [index_should_be_changed]: prev case was aborted ==> index should be decreased')
            return True

        # usual condition
        return prev_low == prev_high or previously_pressed == '9'


def possibly_update_index(window, direction):  # no difference whether search_mode is 'normal' or 'robust'
    if window.show_mode == 'side_by_side':
        if direction == 'next' and index_should_be_changed(window, 'next'):
            window.current_index += 1  # index of the next file
            log('In [possibly_update_index]: Current index increased...')

        elif direction == 'previous' and index_should_be_changed(window, 'previous'):
            window.current_index -= 1
            log('In [possibly_update_index]: Current index decreased...')

        else:
            log('In [possibly_update_index]: No need to increase/decrease index...')

    else:
        # ======== update current index
        if direction == 'next':
            window.current_index += 1  # index of the next file
        else:
            window.current_index -= 1  # index of the previous file


def do_robust_checking(window):
    search_type_match = True if window.search_type == 'robust' else False
    length_match = True if (window.high - window.low) >= 2 else False  # there is at least one item in between

    levels = globals.params['robust_levels']
    level_match = True if (window.high - window.low + 1) / len(window.sorted_list) >= (1 / (2 ** (levels - 1))) else False

    return search_type_match and length_match and level_match


def indicators_exist(window):
    return 'low_consistency' in window.prev_result.keys()


# ========== functions for resetting/reverting
def reset_consistency_indicators(window):
    window.low_consistency = 'unspecified'
    window.high_consistency = 'unspecified'


def revert_indices_and_possibly_consistency_indicators(window):
    window.low, window.high = window.prev_result['low'], window.prev_result['high']
    log(f'In [revert_indices_and_possibly_consistency_indicators]: Reverted indices to: '
        f'low = {window.low}, high = {window.high}')

    if indicators_exist(window):  # revert them if they are available
        window.low_consistency = window.prev_result['low_consistency']
        window.high_consistency = window.prev_result['high_consistency']
        log(f'In [revert_indices_and_possibly_consistency_indicators]: also reverted consistency indicators to: \n'
            f'low_consistency: "{window.low_consistency}" and high_consistency: "{window.high_consistency}"\n')


def reset_indices_and_possibly_consistency_indicators(window):
    if window.data_mode == 'test':
        window.low = 0
        window.high = len(window.sorted_list) - 1

    else:
        raise NotImplementedError
        window.low = 0    # READ THIS PART ONCE BEFORE RUNNING
        window.high = len(window.bins_list) - 1
        log(f'In [binary_search_step]: low and high are reset for the new image: '
            f'low: {window.low}, high: {window.high}\n')

    # also reset low_consistency and high_consistency for the 'robust' checking mode
    if indicators_exist(window):
        reset_consistency_indicators(window)
    log(f'In [reset_indices]: low and high indices '
        f'(and possibly indicators) are reset for the new image.')


# ========== list-related functions
def possibly_remove_item_from_list(window):
    if 'aborted' in window.prev_result.keys() and window.prev_result['aborted'] is True:  # no remove if we have aborted
        log(f'In [possibly_remove_item_from_list]: no remove '
            f'since the previous case had been aborted\n')
        return

    if index_should_be_changed(window, direction='previous'):
        if window.data_mode == 'test':
            insertion_index = window.prev_result['mid_index']  # only in this case we have insertion index, otherwise it is None
            del window.sorted_list[insertion_index]  # delete the wrongly inserted element from the list
            log(f'In [possibly_remove_item_from_list]: index should be decreased ==> '
                f'removed index {insertion_index} from sorted_list - '
                f'Now sorted_list has len: {len(window.sorted_list)}')

            log(f'In [possibly_remove_item_from_list]: saving sorted_list with removed index...')
            write_sorted_list_to_file(window.sorted_list)

            if globals.debug:
                print_list(window.sorted_list)

        else:  # e.g. prev_result: (left_img, right_img, rate, bin, 'last')
            which_bin, insert_pos = window.prev_result['mid_index'], window.prev_result['insert_pos']
            log(
                f'In [possibly_remove_item_from_list]: removing the "{insert_pos}" element from bin {which_bin + 1}')
            del_from_bin_and_save(which_bin, insert_pos)

    else:
        log(f'In [possibly_remove_item_from_list]: index has not changed ==> No need to remove item from list...\n')


def update_binary_search_inds_and_possibly_insert(window, pressed):
    """
    This will update the low and high indices for the binary search. In case binary search is completed or 9 is
    pressed by the radiologist, it inserts the image in the right position and resets the low and high indices.
    :param window:
    :param pressed:
    :return:
    """
    mid = (window.low + window.high) // 2  # for train data, this represents bin number
    # ====== update the low and high indexes based ond the rating until suitable position is found
    if window.high != window.low and eval(pressed) != '9':
        if eval(pressed) == '1':  # rated as harder, go to the right half of the list
            window.low = mid if (window.high - window.low) > 1 else window.high
            log(f'In [binary_search_step]: low increased to {window.low}')

        else:  # rated as easier, go to the left half of the list
            window.high = mid
            log(f'In [binary_search_step]: high decreased to {window.high}')

        log(f'In [binary_search_step]: Updated indices: low = {window.low}, high = {window.high}')

        if indicators_exist(window):  # indicators should be reset when changing the indices
            reset_consistency_indicators(window)
            log(f'In [update_binary_search_inds_and_possibly_insert]: also low_consistency and low_consistency are reset \n')
            # \n'f'to: low_consistency: "{window.low_consistency}", high: "{window.high_consistency}"\n')

    # ====== suitable position is found (low = high), insert here
    else:
        # for test data
        if window.data_mode == 'test':
            mid_image = window.sorted_list[mid]

            # if both images are equal
            if eval(pressed) == '9':  # 9 is pressed, so we insert directly
                window.sorted_list.insert(mid, window.curr_left_file)  # insert to the left
                window.prev_result.update({'mid_index': mid, 'mid_image': mid_image})
                log(f'In [binary_search_step]: the two images are equal, inserted into index {mid} of sorted_list - '
                    f'Now sorted_list has len: {len(window.sorted_list)}\n')

            # if ref image is harder (and binary search is completed)
            if eval(pressed) == '1':
                log(f'In [binary_search_step]: low and high are equal. '
                    f'Inserting into list...')
                window.sorted_list.insert(mid + 1, window.curr_left_file)  # insert to the right side if the index
                window.prev_result.update({'mid_index': mid + 1, 'mid_image': mid_image})
                log(f'In [binary_search_step]: inserted into index {mid + 1} of sorted_list - '
                    f'Now sorted_list has len: {len(window.sorted_list)}\n')

            # if ref image is easier (and binary search is completed)
            if eval(pressed) == '2':
                log(f'In [binary_search_step]: low and high are equal. '
                    f'Inserting into list...')
                window.sorted_list.insert(mid, window.curr_left_file)  # insert to the left side if the index
                window.prev_result.update({'mid_index': mid, 'mid_image': mid_image})
                log(f'In [binary_search_step]: inserted into index {mid} of sorted_list - '
                    f'Now sorted_list has len: {len(window.sorted_list)}\n')

            # save the modified list
            log(f'In [binary_search_step]: saving '
                f'sorted_list...')
            write_sorted_list_to_file(window.sorted_list)
            log(f'In [binary_search_step]: also updated prev_result to include the '
                f'insertion index: {window.prev_result["mid_index"]}\n')
            log(f'In [binary_search_step]: also updated prev_result to have '
                f'mid index and img_img.')

            # reset the indices for the next round of binary search
            reset_indices_and_possibly_consistency_indicators(window)

            if globals.debug:
                print_list(window.sorted_list)

        # for train data
        else:
            # if both images are equal
            if eval(pressed) == '9':
                insert_into_bin_and_save(which_bin=mid, pos='before_last', img=window.curr_left_file)
                window.prev_result.update({'mid_index': mid, 'insert_pos': 'before_last'})  # mid represents the bin here
                log(f'In [binary_search_step]: the two images are equal, inserted into pos '
                    f'"before_last" of bin {mid + 1}')
                log(f'In [binary_search_step]: also updated prev_result to have bin number '
                    f'and insertion pos.\n')

            # if ref image is harder (and binary search is completed)
            if eval(pressed) == '1':
                log(f'In [binary_search_step]: low and high are equal. '
                    f'Inserting into bin...')
                insert_into_bin_and_save(which_bin=mid, pos='last', img=window.curr_left_file)
                window.prev_result.update({'mid_index': mid, 'insert_pos': 'last'})  # bin and the insertion position
                log(f'In [binary_search_step]: inserted into pos "last" of '
                    f'bin {mid + 1} and saved bin.')

            # if ref image is easier (and binary search is completed)
            if eval(pressed) == '2':
                log(f'In [binary_search_step]: low and high are equal. '
                    f'Inserting into bin...')
                insert_into_bin_and_save(which_bin=mid, pos='before_last', img=window.curr_left_file)
                window.prev_result.update({'mid_index': mid, 'insert_pos': 'before_last'})  # mid represents the bin here
                log(f'In [binary_search_step]: inserted into pos '
                    f'"before_last" of bin {mid + 1} and saved bin.')

            log(f'In [binary_search_step]: also updated prev_result to have bin number '
                f'and insertion pos.')

            # reset indices
            reset_indices_and_possibly_consistency_indicators(window)


# ========== very generic functions
def read_img_and_resize_if_needed(window):
    if window.show_mode == 'single':
        # return logic.read_dicom_image(self.current_file, self.img_size)
        return logic.read_dicom_and_resize(window.current_file)

    if window.show_mode == 'side_by_side':
        log(f'In [read_img_and_resize_if_needed]: reading the left file')
        left_photo = logic.read_dicom_and_resize(window.curr_left_file)

        log(f'In [read_img_and_resize_if_needed]: reading the right file')
        right_photo = logic.read_dicom_and_resize(window.curr_right_file)
        return left_photo, right_photo


def log_current_index(window, called_from):
    log(f"\n\n\n\n{'=' * 150} \nIn [{called_from}]: "
        f"Current index: {window.current_index} - Case number: {window.case_number}", no_time=True)
    if window.show_mode != 'single' and window.data_mode != 'train':
        log(f'In [{called_from}]: There are {len(window.sorted_list)} images in the sorted_list\n', no_time=True)


def get_prev_imgs_from_prev_result(window):
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
    if window.data_mode == 'test':
        if index_should_be_changed(window, direction='previous'):
            right_img = window.prev_result["mid_image"]  # mid_image, the last image compared to before inserting to the sorted list
            left_img = window.cases[window.current_index - 1]  # the image that was newly inserted

        else:
            prev_mid = (window.prev_result["low"] + window.prev_result["high"]) // 2
            right_img = window.sorted_list[prev_mid]  # finding mid_img index, sorted_list has not changed
            left_img = window.cases[window.current_index]

    else:
        # prev_bin could always be specified by the mid index, no matter an image has been inserted or not
        prev_bin = (window.prev_result['low'] + window.prev_result['high']) // 2

        if index_should_be_changed(window, direction='previous'):
            left_img = window.cases[window.current_index - 1]
            prev_bin_imgs, insert_pos = read_imgs_from_bin(prev_bin), window.prev_result['insert_pos']
            # in case item has been inserted: get the correct last item if a new item has been inserted into the bin
            right_img = prev_bin_imgs[-1] if insert_pos == 'before_last' else prev_bin_imgs[-2]

        else:  # index has not changed
            left_img = window.cases[window.current_index]
            right_img = last_img_in_bin(prev_bin)

    return left_img, right_img


def save_prev_rating(window):
    if window.show_mode == 'single':
        imgs = [window.prev_result[0]]
        rate = window.prev_result[1]
        # save_rating(self.session_name, imgs, rate)
        save_rating(imgs, rate)

    if window.show_mode == 'side_by_side':
        left_img, right_img = get_prev_imgs_from_prev_result(window)
        imgs = [left_img, right_img]
        rate = window.prev_result["rate"]
        save_rating(imgs, rate)
        update_and_save_comparisons_list(window, left_img, right_img, rate)


def update_and_save_comparisons_list(window, left_img, right_img, rate):
    """
    NOTES: Comparisons are only with respect to the reference image, ie if left image: 4.dcm is harder than right
    image: 2.dcm, since the left image is reference, only 2.dcm is added to the easier_list for 4.dcm and 4.dcm is
    not added to the harder_list for 2.dcm. This is because we only want to keep track of the images that were rated
    against the reference image (the image that is to be inserted into the list).

    ASSUMPTION: we pay attention to the latest choice by the radiologist if two choices are not compatible.
    :param window:
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
    if left_img not in window.comparisons.keys():
        window.comparisons.update({left_img: [[], [], []]})
    if right_img not in window.comparisons.keys():
        window.comparisons.update({right_img: [[], [], []]})

    if rate == '1':  # ref image is harder, should add right image to easier_list
        # add right_img to easier_list for left img
        window.comparisons = add_to_ref_img_easier_list_and_save(ref_img=left_img,
                                                                 compared_to=right_img,
                                                                 comparisons=window.comparisons)
        # add left_img to harder_list for right img
        window.comparisons = add_to_ref_img_harder_list_and_save(ref_img=right_img,
                                                                 compared_to=left_img,
                                                                 comparisons=window.comparisons)

    elif rate == '9':
        window.comparisons = add_to_ref_img_equal_and_save(ref_img=left_img,
                                                           compared_to=right_img,
                                                           comparisons=window.comparisons)
        window.comparisons = add_to_ref_img_equal_and_save(ref_img=right_img,
                                                           compared_to=left_img,
                                                           comparisons=window.comparisons)

    else:  # ref image is easier, should add right image to harder_list
        window.comparisons = add_to_ref_img_harder_list_and_save(ref_img=left_img,
                                                                 compared_to=right_img,
                                                                 comparisons=window.comparisons)
        window.comparisons = add_to_ref_img_easier_list_and_save(ref_img=right_img,
                                                                 compared_to=left_img,
                                                                 comparisons=window.comparisons)

    if globals.debug:
        print_comparisons_lists(window.comparisons)

    save_comparisons_list(window.comparisons)
    log(f'In [update_comparison_sets]: saved comparison_sets to file.\n')
