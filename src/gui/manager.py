from tkinter import *

from .window import *
import logic


def show_window_with_button_input():
    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text='Which image is harder to read? The left one or the right one?', bg='light blue', font='-size 20')
    title.pack(fill=X)

    # ========= left frame
    left_frame = Window(master=root,
                        file="../tmp/imgs/00000001_000.png",
                        position='left',
                        input_type='button',
                        resize_to=(512, 512))

    # ========= right frame
    right_frame = Window(master=root,
                         file='../tmp/imgs/00000001_001.png',
                         position='right',
                         input_type='button',
                         resize_to=(512, 512))

    root.mainloop()  # run the main window continuously


def show_window_with_keyboard_input():
    # IMPORTANT: the image directory has only images and not any other file, otherwise code must be refactored
    single_cases = logic.get_files_paths(imgs_dir=globals.params['imgs_dir'])
    comparison_cases = [
        ('../tmp/dicoms_limited/2F672B32523239764556705333486D7930764A674F513D3D_537153536F422F464D673533317446556E456D3763774455364A6367436A4C48_20140424_1.dcm',
         '../tmp/dicoms_limited/2F672B32523239764556705333486D7930764A674F513D3D_537153536F422F464D673533317446556E456D3763774455364A6367436A4C48_20140424_2.dcm'),

        ('../tmp/dicoms_limited/2F672B32523239764556705333486D7930764A674F513D3D_537153536F422F464D673533317446556E456D3763774455364A6367436A4C48_20140424_3.dcm',
         '../tmp/dicoms_limited/2F672B32523239764556705333486D7930764A674F513D3D_537153536F422F464D673533317446556E456D3763774455364A6367436A4C48_20140424_4.dcm'),

        ('../tmp/dicoms_limited/2F672B32523239764556705333486D7930764A674F513D3D_537153536F422F464D673533317446556E456D3763774455364A6367436A4C48_20140424_1.dcm',
         '../tmp/dicoms_limited/2F672B32523239764556705333486D7930764A674F513D3D_537153536F422F464D673533317446556E456D3763774455364A6367436A4C48_20140424_3.dcm'),

        ('../tmp/dicoms_limited/2F672B32523239764556705333486D7930764A674F513D3D_537153536F422F464D673533317446556E456D3763774455364A6367436A4C48_20140424_2.dcm',
         '../tmp/dicoms_limited/2F672B32523239764556705333486D7930764A674F513D3D_537153536F422F464D673533317446556E456D3763774455364A6367436A4C48_20140424_4.dcm')

    ]
    # mode = 'comparison'
    # mode = 'single'
    mode = 'binary_insert'
    '''if mode == 'single':
        text = 'Which image is harder? (press the keyboard) \n Left: 1 - Right: 2'
        title = Label(root, text=text, bg='light blue', font='-size 20')
        title.pack(fill=X)

        frame = Window(master=root, mode=mode,
                       cases=single_cases,
                       # position='top',
                       input_type='single',
                       resize_to=globals.params['img_size'])

    elif mode == 'side_by_side':
        frame = Window(master=root, mode=mode,
                       cases=comparison_cases,
                       # position='top',
                       input_type='side_by_side',
                       resize_to=globals.params['img_size'])

    else:
        frame = Window(master=root, mode=mode,
                       cases=single_cases,
                       # position='top',
                       input_type='side_by_side',
                       resize_to=globals.params['img_size'])'''

    if mode == 'single':
        input_type = 'single'
        text = 'How hard the image is? 1:  Easy, 2: Medium, 3: Hard'
        cases = single_cases

    else:  # only 'binary_insert'
        input_type = 'side_by_side'
        text = 'Which image is harder? 1: Left - 2: Right'
        cases = single_cases

    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text=text, bg='light blue', font='-size 20')
    title.pack(fill=X)

    frame = Window(master=root, mode=mode,
                   cases=cases,
                   # position='top',
                   # input_type='side_by_side',
                   input_type=input_type)
                   # resize_to=globals.params['img_size'])

    root.mainloop()  # run the main window continuously
