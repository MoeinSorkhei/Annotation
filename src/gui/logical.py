from pprint import pformat
from threading import Thread

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


def prev_case_aborted(window):  # 'aborted' attribute exists only when getting rate for m2 is done
    if 'aborted' in window.prev_result.keys() and window.prev_result['aborted'] is True:
    # if 'status' in window.prev_result.keys() and window.prev_result['status'] == 'aborted':
        return True
    return False


def indices_are_reset(window):
    if window.data_mode == 'test':
        return window.low == 0 and window.high == len(window.sorted_list) - 1
    else:
        return window.low == 0 and window.high == len(window.bins_list) - 1


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
        # index should be decreased if we have aborted
        if prev_case_aborted(window):
        # if ternary_m1_m2_rates_exist_in_prev_result(window):
        #    if showing_window_for(window) == 'm1' and prev_case_aborted(window):
                log(f'In [index_should_be_changed]: prev case was aborted ==> index should be decreased')
                return True

        prev_low, prev_high = window.prev_result['low'], window.prev_result['high']
        previously_pressed = window.prev_result['rate']  # if 9 was pressed previously, index has been already increased
        # usual condition
        return prev_low == prev_high or previously_pressed == '9'


def current_index_has_changed(window):
    return window.current_index != window.prev_result['current_index']


def update_current_index_if_needed(window, direction):  # no difference whether search_mode is 'normal' or 'robust'
    """
    Increase in the index is always understood from whether the indices have been reset or not.
    :param window:
    :param direction:
    :return:
    """
    if window.show_mode == 'side_by_side':
        if direction == 'next' and index_should_be_changed(window, 'next'):
            window.current_index += 1  # index of the next file
            log('In [possibly_update_index]: Current index increased...')

        elif direction == 'previous' and index_should_be_changed(window, 'previous'):
            window.current_index -= 1
            log('In [possibly_update_index]: Current index decreased...')

        else:
            log('In [possibly_update_index]: No need to increase/decrease current_index...')

    else:
        # ======== update current index
        if direction == 'next':
            window.current_index += 1  # index of the next file
        else:
            window.current_index -= 1  # index of the previous file


def robust_checking_needed(window, print_details=False):
    levels = globals.params['robust_levels']
    min_length = globals.params['robust_min_length']

    if window.search_type == 'ternary':
        total_length = len(window.sorted_list) if window.data_mode == 'test' else len(window.bins_list)
        current_length = window.high - window.low + 1
        frac = (2 / 3) ** (levels - 1)

        length_match = True if current_length >= min_length else False
        level_match = True if current_length / total_length >= frac else False

    else:
        raise NotImplementedError
        length_match = True if (window.high - window.low) >= min_length else False  # there is at least one item in between
        total_length = len(window.sorted_list) if window.data_mode == 'test' else len(window.bins_list)

        level_match = True if (window.high - window.low + 1) / total_length >= (1 / (2 ** (levels - 1))) else False

    # return search_type_match and length_match and level_match
    if print_details:
        log(f'In [robust_checking_needed]: length_match: {length_match}, level_match: {level_match}\n')
    return length_match and level_match


def indicators_exist(window):
    if window.prev_result is None:  # if discard button pressed
        return False
    return 'low_consistency' in window.prev_result.keys()  # if 'low_consistency' is among the keys


def ternary_m1_m2_rates_exist_in_prev_result(window):
    if window.prev_result is None:
        return False
    return 'm1_rate' in window.prev_result.keys()


def showing_window_for(window):  # could possibly add input_type which says if it is window or m1_rate, m2_rate direclty
    if window.m1_rate is None and window.m2_rate is None:  # getting rate for m1
        return 'm1'

    elif window.m1_rate is not None and window.m2_rate is None:  # m1 already rated, getting rate for m2
        return 'm2'

    else:
        log(f'm1_rate: {window.m1_rate}, '
            f'm2_rate: {window.m2_rate}')
        raise NotImplementedError('Unexpected m1_rate '
                                  'm2_rate condition')


# ========== functions for changing window attributes
def reset_consistency_indicators(window):
    window.low_consistency = 'unspecified'
    window.high_consistency = 'unspecified'


def init_or_use_rep(window, mid):
    rep = window.rep
    if rep is None:
        rep = bin_representative(which_bin=mid)
        window.rep = rep
        log(f'In [init_or_use_rep]: rep is None. '
            f'Calculated rep and set attribute to: {window.rep}')
    else:
        log(f'In [init_or_use_rep]: rep is already '
            f'set to: {window.rep}. Using the rep...')
    return rep


def init_or_use_anchor_and_rep(window):
    _curr_anchor = None
    _curr_rep = None  # only initialized and set in train mode

    # specifying the name of the anchor and representative to be used
    window_for = showing_window_for(window)  # 'm1' or 'm2'
    if window_for == 'm1':
        _curr_anchor_name = 'm1_anchor'
        _curr_rep_name = 'm1_rep'
    else:  # m2
        _curr_anchor_name = 'm2_anchor'
        _curr_rep_name = 'm2_rep'

    _curr_anchor = getattr(window, _curr_anchor_name)  # index in sorted list or index of the bin

    # init or use the anchor
    if _curr_anchor is None:
        _curr_anchor = calc_ternary_anchors(window)[window_for]
        setattr(window, _curr_anchor_name, _curr_anchor)
        log(f'In [init_or_use_anchor_and_rep]: {_curr_anchor_name} is None. '
            f'Calculated anchor and set attribute to: {_curr_anchor}')
    else:
        log(f'In [init_or_use_anchor_and_rep]: {_curr_anchor_name} already set to: {_curr_anchor}. '
            f'Using the anchor...')

    # init or use rep
    if window.data_mode == 'train':
        _curr_rep = getattr(window, _curr_rep_name)

        if _curr_rep is None:
            _curr_rep = bin_representative(which_bin=_curr_anchor)
            setattr(window, _curr_rep_name, _curr_rep)
            log(f'In [init_or_use_anchor_and_rep]: {_curr_rep_name} is None. '
                f'Calculated representative and set attribute to: {pure_name(_curr_rep)}')
        else:
            log(f'In [init_or_use_anchor_and_rep]: {_curr_rep_name} already set to: {_curr_rep}. '
                f'Using the representative...')

    return _curr_anchor, _curr_rep


def revert_attributes(window):
    # revert low, high indices
    window.low, window.high = window.prev_result['low'], window.prev_result['high']
    window.current_index = window.prev_result['current_index']

    # for print purposes
    attrs_as_dict = {
        'low': window.low,
        'high': window.high,
        'current_index': window.current_index,

    }

    # revert m1 and m2 rates
    if 'm1_rate' in window.prev_result.keys():
        window.m1_rate = window.prev_result['m1_rate']
        window.m2_rate = window.prev_result['m2_rate']

        attrs_as_dict['m1_rate'] = window.m1_rate
        attrs_as_dict['m2_rate'] = window.m2_rate

    # reset anchors
    if 'm1_anchor' in window.prev_result.keys():
        window.m1_anchor = window.prev_result['m1_anchor']
        window.m2_anchor = window.prev_result['m2_anchor']

        attrs_as_dict['m1_anchor'] = window.m1_anchor
        attrs_as_dict['m2_anchor'] = window.m2_anchor

    # revert bin representatives for train mode
    if 'm1_rep' in window.prev_result.keys():
        window.m1_rep = window.prev_result['m1_rep']
        window.m2_rep = window.prev_result['m2_rep']

        attrs_as_dict['m1_rep'] = window.m1_rep
        attrs_as_dict['m2_rep'] = window.m2_rep

    if 'rep' in window.prev_result.keys():
        window.rep = window.prev_result['rep']
        attrs_as_dict['rep'] = window.rep

    log(f'In [revert_attributes]: Reverted all attributes.')
    # log(f'In [revert_attributes]: Reverted all attributes. Now attributes are: \n{attrs_as_dict}')


def reset_attributes(window, exclude_inds=False):
    """
    The behavior of this function depends on whether we are dealing with test or train data.

    :param exclude_inds:
    :param window:
    :return:
    """
    if not exclude_inds:
        if window.data_mode == 'test':
            window.low = 0
            window.high = len(window.sorted_list) - 1

        else:
            window.low = 0
            window.high = len(window.bins_list) - 1
            # log(f'In [binary_search_step]: low and high are reset for the new image: '
            #     f'low: {window.low}, high: {window.high}\n')

    # also reset low_consistency and high_consistency for the 'robust' checking mode
    # if indicators_exist(window):   # NOT SURE IF IT IS RIGHT: it checks based on prev_result, change code like below
    #     reset_consistency_indicators(window)

    # rest m1 and m2 rates
    if hasattr(window, 'm1_rate'):
        window.m1_rate = None

    if hasattr(window, 'm2_rate'):
        window.m2_rate = None

    if hasattr(window, 'm1_anchor'):
        window.m1_anchor = None

    if hasattr(window, 'm2_anchor'):
        window.m2_anchor = None

    if hasattr(window, 'm1_rep'):
        window.m1_rep = None

    if hasattr(window, 'm2_rep'):
        window.m2_rep = None

    if hasattr(window, 'rep'):
        window.rep = None

    log(f'In [reset_attributes]: attributes are reset for the new image.')


# def update_m1_m2_rates(window, pressed):
#     if showing_window_for(window) == 'm1':
#         window.m1_rate = eval(pressed)
#     else:  # for m2
#         window.m2_rate = eval(pressed)


def calc_ternary_anchors(window):
    low, high = window.low, window.high
    length = high - low

    m1 = low + int(length * (1/3))
    m2 = low + int(length * (2/3))

    anchors = {'m1': m1, 'm2': m2}
    # log(f'In [calc_ternary_anchors]: '
    #     f'computed anchors for low: {low}, high: {high} are: {anchors}\n')
    return anchors


def update_ternary_indices(window, pressed):
    m1_anchor = window.m1_anchor
    m2_anchor = window.m2_anchor
    m1_rate = window.m1_rate
    m2_rate = eval(pressed)

    if m1_rate == '1' and m2_rate == '1':
        window.low = m1_anchor
        log(f'In [update_ternary_indices]: '
            f'low increased to m1_anchor: {m1_anchor}')

    elif m1_rate == '1' and m2_rate == '2':
        window.low = m1_anchor
        window.high = m2_anchor
        log(f'In [update_ternary_indices]: '
            f'low increased to m1_anchor: {m1_anchor}, high decreased to m2_anchor: {m2_anchor}')

    elif m1_rate == '2' and m2_rate == '2':
        window.high = m2_anchor
        log(f'In [update_ternary_indices]: '
            f'high decreased to m2_anchor: {m2_anchor}')

    else:
        log(f'In [update_ternary_indices]: m1 and m2 rates are m1 = {m1_rate}, m2 = {m2_rate}')
        raise NotImplementedError('Unexpected m1 and m2 rates')

    log(f'In [update_ternary_indices]: Updated indices are low: {window.low}, high: {window.high} \n')


def update_binary_inds(window, pressed):
    """
    This will update the low and high indices for the binary search. In case binary search is completed or 9 is
    pressed by the radiologist, it inserts the image in the right position and resets the low and high indices.
    The behavior of this function depends on whether we are dealing with test or train data.

    :param window:
    :param pressed:
    :return:
    """
    mid = (window.low + window.high) // 2  # for train data, this represents bin number
    # ====== update the low and high indexes based ond the rating until suitable position is found
    # if window.high != window.low and eval(pressed) != '9':
    if eval(pressed) == '1':  # rated as harder, go to the right half of the list
        window.low = mid if (window.high - window.low) > 1 else window.high
        log(f'In [binary_search_step]: low increased to {window.low}')

    else:  # rated as easier, go to the left half of the list
        window.high = mid
        log(f'In [binary_search_step]: high decreased to {window.high}')

    log(f'In [binary_search_step]: Updated indices: low = {window.low}, high = {window.high}')

        # if indicators_exist(window):  # indicators should be reset when changing the indices
        #     reset_consistency_indicators(window)
        #     log(f'In [update_binary_search_inds_and_possibly_insert]: also low_consistency and low_consistency are reset \n')
            # \n'f'to: low_consistency: "{window.low_consistency}", high: "{window.high_consistency}"\n')

    # ====== suitable position is found (low = high), insert here
    # else:


def insert_with_ternary_inds(window, anchor, item):
    """
    Note: insert_with_ternary_inds only happens if 9 is pressed, it is assumed that ternary indices are never equal.
    :param anchor:
    :param window:
    :param anchor_name:
    :param item:
    :return:
    """
    # anchor = getattr(window, anchor_name)  # get the anchor using its name
    if window.data_mode == 'test':
        insert_to_list(window.sorted_list, anchor, item)
        window.prev_result['insert_index'] = anchor

    else:
        pos = 'last' if globals.params['bin_rep_type'] == 'random' else 'before_last'
        insert_into_bin_and_save(which_bin=anchor, pos=pos, img=item)
        window.prev_result['insert_index'] = anchor
        window.prev_result['insert_pos'] = pos


def insert_with_binary_inds(window, pressed, item):
    # for test data
    mid = (window.low + window.high) // 2  # for train data, this represents bin number
    if window.data_mode == 'test':
        # if both images are equal
        if eval(pressed) == '9' or eval(pressed) == '2':  # 9 is pressed, so we insert directly
            insert_index = mid
            # window.sorted_list.insert(mid, window.curr_left_file)  # insert to the left
            # window.prev_result.update({'mid_index': mid, 'mid_image': mid_image})
            # window.prev_result.update({'insert_index': mid})
            if eval(pressed) == '9':
                log(f'In [insert_with_binary_inds]: the two images are equal')
            if eval(pressed) == '2':
                log(f'In [insert_with_binary_inds]: low and high are equal')

        # if ref image is harder (and binary search is completed)
        # elif eval(pressed) == '1':
        else:  # eval(pressed) == '1'
            # log(f'In [binary_search_step]: low and high are equal. '
            #     f'Inserting into list...')
            # window.prev_result.update({'mid_index': mid + 1, 'mid_image': mid_image})
            insert_index = mid + 1
            log(f'In [insert_with_binary_inds]: low and high are equal')
            # window.sorted_list.insert(mid + 1, window.curr_left_file)  # insert to the right side if the index
            # window.prev_result.update({'insert_index': mid + 1})
            # log(f'In [binary_search_step]: low and high are equal. Inserted into index {mid + 1} of sorted_list - '
            #     f'Now sorted_list has len: {len(window.sorted_list)}\n')

        # if ref image is easier (and binary search is completed)
        # else:  # eval(pressed) == '2':
        #     # log(f'In [binary_search_step]: low and high are equal. '
        #     #     f'Inserting into list...')
        #     # window.prev_result.update({'mid_index': mid, 'mid_image': mid_image})
        #     insert_index = mid
        #     # window.sorted_list.insert(mid, window.curr_left_file)  # insert to the left side if the index
        #     # window.prev_result.update({'insert_index': mid})
        #     log(f'In [binary_search_step]: low and high are equal. Inserted into index {mid} of sorted_list - '
        #         f'Now sorted_list has len: {len(window.sorted_list)}\n')

        # window.sorted_list.insert(insert_index, window.curr_left_file)
        # insert_to_list(window.sorted_list, insert_index, window.curr_left_file)
        insert_to_list(window.sorted_list, insert_index, item)
        window.prev_result.update({'insert_index': insert_index})
        # log(f'In [binary_search_step]: also updated prev_result to include '
        #     f'insert_index: {window.prev_result["insert_index"]}\n')
        # save the modified list
        # log(f'In [binary_search_step]: saving '
        #     f'sorted_list...')
        # write_sorted_list_to_file(window.sorted_list)
        # log(f'In [binary_search_step]: also updated prev_result to have '
        #     f'mid index and img_img.')

        # reset the indices for the next round of binary search
        # reset_attributes(window)
        # window.current_index += 1
        log(f'In [insert_with_binary_inds]: inserted into index {insert_index} of sorted_list')

        # if globals.debug:
        #     print_list(window.sorted_list)

    # for train data
    else:
        which_bin = mid  # bin number to insert to
        bin_rep_type = globals.params['bin_rep_type']

        if bin_rep_type == 'random':
            pos = 'last'
        else:
            if eval(pressed) == '9' or eval(pressed) == '2':
                pos = 'before_last'
            else:
                pos = 'last'

        string = 'the two images are equal' if eval(pressed) == '9' else 'low and high are equal'
        log(f'In [insert_with_binary_inds]: {string} and bin_rep_type is "{bin_rep_type}", '
            f'inserting into position "{pos}" of bin {which_bin + 1}')

        # insert_into_bin_and_save(which_bin, pos, window.curr_left_file)
        insert_into_bin_and_save(which_bin, pos, item)
        window.prev_result.update({'insert_index': which_bin, 'insert_pos': pos})

        # # if both images are equal
        # if eval(pressed) == '9':
        #     insert_into_bin_and_save(which_bin=mid, pos='before_last', img=window.curr_left_file)
        #     window.prev_result.update({'mid_index': mid, 'insert_pos': 'before_last'})  # mid represents the bin here
        #     log(f'In [binary_search_step]: the two images are equal, inserted into pos '
        #         f'"before_last" of bin {mid + 1}')
        #     log(f'In [binary_search_step]: also updated prev_result to have bin number '
        #         f'and insertion pos.\n')
        #
        # # if ref image is harder (and binary search is completed)
        # if eval(pressed) == '1':
        #     log(f'In [binary_search_step]: low and high are equal. '
        #         f'Inserting into bin...')
        #     insert_into_bin_and_save(which_bin=mid, pos='last', img=window.curr_left_file)
        #     window.prev_result.update({'mid_index': mid, 'insert_pos': 'last'})  # bin and the insertion position
        #     log(f'In [binary_search_step]: inserted into pos "last" of '
        #         f'bin {mid + 1} and saved bin.')
        #
        # # if ref image is easier (and binary search is completed)
        # if eval(pressed) == '2':
        #     log(f'In [binary_search_step]: low and high are equal. '
        #         f'Inserting into bin...')
        #     insert_into_bin_and_save(which_bin=mid, pos='before_last', img=window.curr_left_file)
        #     window.prev_result.update({'mid_index': mid, 'insert_pos': 'before_last'})  # mid represents the bin here
        #     log(f'In [binary_search_step]: inserted into pos '
        #         f'"before_last" of bin {mid + 1} and saved bin.')
        #
        # log(f'In [binary_search_step]: also updated prev_result to have bin number '
        #     f'and insertion pos.')

        # reset indices
        # reset_attributes(window)
        # window.current_index += 1


# with the change of indices, we set curr_bin_representative to None sine the bin will be changed
# if window.data_mode == 'train':
#     window.curr_bin_representative = None
#     log(f'In [binary_search_step]: Updated indices: also set curr_bin_representative to None. \n')


# ========== list-related functions
def remove_last_inserted(window):
    if window.data_mode == 'test':
        # insertion_index = window.prev_result['mid_index']  # only in this case we have insertion index, otherwise it is None
        insertion_index = window.prev_result['insert_index']  # only in this case we have insertion index, otherwise it is None
        del window.sorted_list[insertion_index]  # delete the wrongly inserted element from the list
        log(f'In [remove_last_inserted]: index should be decreased ==> '
            f'removed index {insertion_index} from sorted_list - '
            f'Now sorted_list has len: {len(window.sorted_list)}')

        log(f'In [remove_last_inserted]: saving sorted_list with removed index...')
        write_sorted_list_to_file(window.sorted_list)

        # if globals.debug:
        #     print_list(window.sorted_list)

    else:  # e.g. prev_result: (left_img, right_img, rate, bin, 'last')
        which_bin, insert_pos = window.prev_result['insert_index'], window.prev_result['insert_pos']
        log(f'In [remove_last_inserted]: removing the "{insert_pos}" element from bin_{which_bin + 1}.txt')
        del_from_bin_and_save(which_bin, insert_pos)


def _remove_if_index_has_changed(window):
    # if index_should_be_changed(window, direction='previous'):
    if current_index_has_changed(window):  # index has been increased
        if window.data_mode == 'test':
            # insertion_index = window.prev_result['mid_index']  # only in this case we have insertion index, otherwise it is None
            insertion_index = window.prev_result['insert_index']  # only in this case we have insertion index, otherwise it is None
            del window.sorted_list[insertion_index]  # delete the wrongly inserted element from the list
            log(f'In [_remove_if_index_has_changed]: index should be decreased ==> '
                f'removed index {insertion_index} from sorted_list - '
                f'Now sorted_list has len: {len(window.sorted_list)}')

            log(f'In [_remove_if_index_has_changed]: saving sorted_list with removed index...')
            write_sorted_list_to_file(window.sorted_list)

            if globals.debug:
                print_list(window.sorted_list)

        else:  # e.g. prev_result: (left_img, right_img, rate, bin, 'last')
            which_bin, insert_pos = window.prev_result['mid_index'], window.prev_result['insert_pos']
            log(f'In [_remove_if_index_has_changed]: removing the "{insert_pos}" element from bin {which_bin + 1}')
            del_from_bin_and_save(which_bin, insert_pos)

    else:
        log(f'In [_remove_if_index_has_changed]: index has not changed ==> No need to remove item from list...\n')


def remove_item_from_list_if_needed(window):
    """
    The behavior of this function depends on whether we are dealing with test or train data.
    :param window:
    :return:
    """

    # no remove if we are getting m2_rate
    if showing_window_for(window) == 'm2':
        log(f'In [remove_item_from_list_if_needed]: no remove '
            f'since since we are getting rate for m2\n')
        return

    # no remove if increase in index was due to abortion
    # if prev_case_aborted(window):
    if window.prev_result['aborted'] is True:
        log(f'In [remove_item_from_list_if_needed]: no remove '
            f'since the previous case had been aborted\n')
        return

    # now if index has changed, insertion has taken place
    _remove_if_index_has_changed(window)


# ========== very generic functions
def window_attributes(window):
    as_dict = {
        'current_index': window.current_index,
        'low': window.low,
        'high': window.high
    }

    if hasattr(window, 'm1_anchor'):
        as_dict['m1_anchor'] = window.m1_anchor

    if hasattr(window, 'm2_anchor'):
        as_dict['m2_anchor'] = window.m2_anchor

    if hasattr(window, 'm1_rate'):
        as_dict['m1_rate'] = window.m1_rate

    if hasattr(window, 'm2_rate'):
        as_dict['m2_rate'] = window.m2_rate

    if hasattr(window, 'm1_rep'):
        as_dict['m1_rep'] = pure_name(window.m1_rep)

    if hasattr(window, 'm2_rep'):
        as_dict['m2_rep'] = pure_name(window.m2_rep)

    if hasattr(window, 'rep'):
        as_dict['rep'] = pure_name(window.rep)
    return as_dict


def shorten(dictionary):
    keys = ['m1_rep', 'm2_rep', 'rep']
    for key in keys:
        if key in dictionary.keys():
            dictionary[key] = pure_name(dictionary[key])
    return dictionary


def read_img_and_resize_if_needed(window):
    if window.show_mode == 'single':
        # return logic.read_dicom_image(self.current_file, self.img_size)
        return logic.read_dicom_and_resize(window.current_file)

    if window.show_mode == 'side_by_side':
        # log(f'In [read_img_and_resize_if_needed]: reading the left file')
        left_photo = logic.read_dicom_and_resize(window.curr_left_file)

        # log(f'In [read_img_and_resize_if_needed]: reading the right file')
        right_photo = logic.read_dicom_and_resize(window.curr_right_file)

        # log(f'In [read_img_and_resize_if_needed]: reading left and right files: done.\n')
        return left_photo, right_photo


def log_current_index(window, called_from):
    log(f"\n\n\n\n{'=' * 150} \nIn [{called_from}]: "
        f"Current index: {window.current_index} - Case number: {window.case_number}\n", no_time=True)
    if window.show_mode != 'single' and window.data_mode != 'train':
        log(f'In [{called_from}]: There are {len(window.sorted_list)} images in the sorted_list\n', no_time=True)
    log(f'Showing window with attributes: \n{window_attributes(window)}\n', no_time=True)
    # log(f'Showing window with attributes: \n{window_attributes(window)}\n'
    #     f'Prev_result is: {window.prev_result}\n', no_time=True)


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
            # right_img = last_img_in_bin(prev_bin)
            right_img = bin_representative(prev_bin)   # ABOSLUTELY WRONG; SHOULD READ IT FROM PREV_RESULT

    return left_img, right_img


# def save_prev_rating(window):
#     if window.show_mode == 'single':
#         imgs = [window.prev_result[0]]
#         rate = window.prev_result[1]
#         # save_rating(self.session_name, imgs, rate)
#         save_rating(imgs, rate)
#
#     if window.show_mode == 'side_by_side':
#         prev_stat = window.prev_result['status']
#         prev_left_index = window.prev_result['left_index']  # index of the left image (previous current_index)
#         prev_right_index = window.prev_result['right_index']  # could be index of image or bin
#
#         prev_left_img = window.cases[prev_left_index]
#         prev_right_img = None
#
#         if prev_stat == 'OK':
#             pass
#
#         elif prev_stat == 'aborted':
#             pass
#         elif prev_stat == 'discarded':
#             pass
#         else:
#             raise NotImplementedError
#
#         left_img, right_img = get_prev_imgs_from_prev_result(window)
#         imgs = [left_img, right_img]
#         rate = window.prev_result["rate"]
#         save_rating(imgs, rate)
#         # update_and_save_comparisons_list(window, left_img, right_img, rate)
#
#         # keep track of the aborted cases
#         if prev_case_aborted(window):
#             save_to_aborted_list(left_img)


def read_discarded_cases():
    discarded_file = globals.params['discarded']
    discarded_list = read_file_to_list_if_exists(discarded_file)
    return discarded_list


def read_aborted_cases():
    aborted_file = globals.params['aborted']
    aborted_list = read_file_to_list_if_exists(aborted_file)
    return aborted_list


def save_aborted_cases(window):
    if window.data_mode == 'test':
        successful_cases = read_sorted_imgs()
    else:
        _, successful_cases = all_imgs_in_all_bins()

    discarded_cases = read_discarded_cases()
    aborted_cases = [case for case in window.cases if (case not in successful_cases and case not in discarded_cases)]

    for aborted in aborted_cases:
        save_to_aborted_list(aborted)
    log(f'In [save_aborted_cases]: saved {len(aborted_cases)} aborted cases...\n')


def save_to_discarded_list(case):
    filename = globals.params['discarded']
    append_to_file(filename, case)
    log(f'In [save_to_discarded_list]: saved case "{case}" to discarded list.')


def save_to_aborted_list(case):
    filename = globals.params['aborted']
    with open(filename, 'a') as file:
        file.write(f'{case}\n')
    log(f'In [save_to_aborted_list]: saved case "{case}" to aborted list.')


def remove_last_record(from_file):
    if from_file == 'comparisons':
        file = globals.params['comparisons']
    elif from_file == 'aborted':
        file = globals.params['aborted']
    else:
        raise NotImplementedError

    records = read_file_to_list_if_exists(file)
    records = records[:-1]
    write_list_to_file(records, file)
    log(f'In [remove_last_record]: removed the last record from "{from_file}" and saved it. \n')


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


def upload_results_regularly(window):
    if globals.params['email_interval'] is None:
        return

    if window.current_index <= 1 or window.current_index % globals.params['email_interval'] == 0:
        thread = Thread(target=logic.email_results)  # make it non-blocking as emailing takes time
        thread.start()
