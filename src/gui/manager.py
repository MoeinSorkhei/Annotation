from .window import *
import logic


# def show_window_with_button_input():
#     root = Tk()  # creates a blank window (or main window)
#     title = Label(root, text='Which image is harder to read? The left one or the right one?', bg='light blue', font='-size 20')
#     title.pack(fill=X)
#
#     # ========= left frame
#     left_frame = Window(master=root,
#                         file="../tmp/imgs/00000001_000.png",
#                         position='left',
#                         mode='button',
#                         resize_to=(512, 512))
#
#     # ========= right frame
#     right_frame = Window(master=root,
#                          file='../tmp/imgs/00000001_001.png',
#                          position='right',
#                          mode='button',
#                          resize_to=(512, 512))
#
#     root.mainloop()  # run the main window continuously


def show_window_with_keyboard_input(mode, imgs, session_name, which_bin):
    if mode == 'single':
        text = 'How hard the image is? 1:  Easy, 2: Medium, 3: Hard'

    else:  # only 'binary_insert'
        text = 'Which image is harder? 1: Left - 2: Right - 9: No difference ' \
               '(Note: Even the slightest difference is important).'

    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text=text, bg='light blue', font='-size 20')
    title.pack(fill=X)

    frame = Window(master=root,
                   cases=imgs,
                   mode=mode,
                   session_name=session_name,
                   which_bin=which_bin)
    root.mainloop()  # run the main window continuously
