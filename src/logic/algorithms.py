from .helper import *


# Returns index of x in arr if present, else -1
def binary_search2(sorted_list, low, high, x):
    """
    Code adapted from: https://www.geeksforgeeks.org/python-program-for-binary-search/
    :param sorted_list:
    :param low:
    :param high:
    :param x:
    :return:
    """
    # Check base case
    if high >= low:
        mid = (high + low) // 2

        # If element is present at the middle itself
        if sorted_list[mid] == x:
            return mid

        # If element is smaller than mid, then it can only
        # be present in left subarray
        elif sorted_list[mid] > x:
            return binary_search(sorted_list, low, mid - 1, x)

        # Else the element can only be present in right subarray
        else:
            return binary_search(sorted_list, mid + 1, high, x)

    else:
        # Element is not present in the array
        return -1


def binary_search_step(sorted_list, low, high, new_img):
    log(f'In [binary_search]: starting with low = {low}, high = {high}')
    mid = (low + high) // 2

    log(f'In [binary_search]: mid = {mid} ==> sorted_list[{mid}]: {sorted_list[mid]}')
    inp = input()
    new_img_harder = inp == '2'

    if new_img_harder:  # rated as harder, go to the right half of the list
        low = mid if (high - low) > 1 else high  # low will be equal to high if high is only once index higher
        multi_log([f'In [binary_search]: new image rated as HARDER',
                   f'In [binary_search]: now low set to: {low} ==> low = {low}, high = {high}'])
    else:  # rated as easier, go to the left half of the list
        high = mid
        multi_log([f'In [binary_search]: new image rated as EASIER',
                   f'In [binary_search]: now high set to: {high} ==> low = {low}, high = {high}'])

    log(f'In [binary_search]: now low and high are equal: {low} = {high}')

    # compare with the current index
    current_index = low  # current_index = low = high
    log(
        f'In [binary_search]: comparing {new_img} with image at current index {current_index}: {sorted_list[current_index]}')
    inp = input()
    harder_than_current = inp == '2'

    if harder_than_current:
        sorted_list.insert(current_index + 1, new_img)  # insert to the right side if the index
        multi_log([f'In [binary_search]: new image rated as HARDER',
                   f'In [binary_search]: inserted {new_img} after current index'])

    else:
        sorted_list.insert(current_index, new_img)  # insert to the left side if the index
        multi_log([f'In [binary_search]: new image rated as EASIER',
                   f'In [binary_search]: inserted {new_img} before current index'])

    multi_log([f'In [binary_search]: sorted_list[{current_index}]: {sorted_list[current_index]}',
               f'In [binary_search]: sorted_list[{current_index + 1}]: {sorted_list[current_index + 1]}'])
    print(f'final sorted list: {sorted_list}')


def binary_search(sorted_list, low, high, new_img):
    log(f'In [binary_search]: starting with low = {low}, high = {high}')
    # ======== compare util we get to the suitable index
    while low != high:
        mid = (low + high) // 2

        log(f'In [binary_search]: mid = {mid} ==> sorted_list[{mid}]: {sorted_list[mid]}')
        inp = input()
        new_img_harder = inp == '2'

        if new_img_harder:  # rated as harder, go to the right half of the list
            low = mid if (high - low) > 1 else high  # low will be equal to high if high is only once index higher
            multi_log([f'In [binary_search]: new image rated as HARDER',
                       f'In [binary_search]: now low set to: {low} ==> low = {low}, high = {high}'])
        else:  # rated as easier, go to the left half of the list
            high = mid
            multi_log([f'In [binary_search]: new image rated as EASIER',
                       f'In [binary_search]: now high set to: {high} ==> low = {low}, high = {high}'])

    log(f'In [binary_search]: now low and high are equal: {low} = {high}')

    # compare with the current index
    current_index = low  # current_index = low = high
    log(f'In [binary_search]: comparing {new_img} with image at current index {current_index}: {sorted_list[current_index]}')
    inp = input()
    harder_than_current = inp == '2'

    if harder_than_current:
        sorted_list.insert(current_index + 1, new_img)  # insert to the right side if the index
        multi_log([f'In [binary_search]: new image rated as HARDER',
                   f'In [binary_search]: inserted {new_img} after current index'])

    else:
        sorted_list.insert(current_index, new_img)  # insert to the left side if the index
        multi_log([f'In [binary_search]: new image rated as EASIER',
                   f'In [binary_search]: inserted {new_img} before current index'])

    multi_log([f'In [binary_search]: sorted_list[{current_index}]: {sorted_list[current_index]}',
               f'In [binary_search]: sorted_list[{current_index + 1}]: {sorted_list[current_index + 1]}'])
    print(f'final sorted list: {sorted_list}')
