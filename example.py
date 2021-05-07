#!/usr/bin/env python

import sys
import datetime
from pyqt5bar.main import Bar
from PyQt5 import QtWidgets, Qt
from pyqt5bar.widgets_base import SelfUpdatingWidget, TextWidget


def main(app):
    bar = Bar(
        [
            TextWidget('Welcome!', background='Indigo', border_radius='9px',
                       border_width='2px', border_color='black', padding='1px',
                       padding_left='15px'),
            TextWidget('💗', font_family='Noto Color Emoji'),
            'Stretch',
            SelfUpdatingWidget(
                'US', 'xkb-switch', None, 600, 'xkb-switch -W',
                lambda x: f'{x.upper()[0:2]}', background='Chocolate',
                border_radius='9px', padding_left='9px', padding_right='9px',
                font_weight='bold'),
            SelfUpdatingWidget(
                'test', None,
                lambda: datetime.datetime.now().strftime(
                    '%a, %d-%b-%Y / %I:%M:%S'), 1,
                update_proc=None, post_proc_func=lambda x: x.strip(),
                background='Indigo', border_radius='9px',
                padding_left='9px', padding_right='9px'),
            # SelfUpdatingWidget(
            #     'test', 'date +"%a, %d-%B-%Y | %I:%M:%S"', None, 1,
            #     update_proc=None, post_proc_func=lambda x: x.strip(),
            #     background='Indigo', border_radius='9px',
            #     padding_left='9px', padding_right='9px'),
        ], app=app, widgets_spacing= 10, rounded_corner='5px', color='white')
    bar.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(Qt.Qt.AA_UseHighDpiPixmaps)
    main(app)
