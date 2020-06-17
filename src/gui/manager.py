from .window import *


def show_window_with_keyboard_input(mode, not_already_sorted, already_sorted, already_comparisons, session_name):
    if mode == 'single':
        text = 'How hard the image is? 1:  Easy, 2: Medium, 3: Hard'

    else:  # only 'binary_insert'
        text = 'Which image is harder? 1: Left - 2: Right - 9: No difference ' \
               '(Note: Even the slightest difference is important).'

    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text=text, bg='light blue', font='-size 20')
    title.pack(fill=X)

    frame = Window(master=root,
                   cases=not_already_sorted,
                   already_sorted=already_sorted,
                   already_comparisons=already_comparisons,
                   mode=mode,
                   session_name=session_name)
    root.mainloop()  # run the main window continuously
