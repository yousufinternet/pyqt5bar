#!/usr/bin/env python

import sys
import datetime
import subprocess as sp
from pyqt5bar.main import Bar
from pyqt5bar.builtin_widgets import corona_cases
from PyQt5 import QtWidgets, Qt
from pyqt5bar.widgets_base import SelfUpdatingWidget, TextWidget, GroupWidget


fg_color = 'White'
bg_color = 'Indigo'
altbg_color = 'Chocolate'
border_radius = '9px'

default_args = {
    'color': fg_color, 'border_radius': border_radius,
    'padding_left': border_radius, 'padding_right': border_radius}


def corona_widget():
    corona_icon = TextWidget('🦠', font_family='Noto Color Emoji',
                            background='transparent')
    corona_wdgt = SelfUpdatingWidget(
        '0', None, corona_cases, 3600, None, None, background='transparent',
    )
    return GroupWidget(
        [corona_icon, corona_wdgt],
        {**{'background': altbg_color}, **default_args})


def cpu_usage():
    pass

def main(app):
    bar = Bar(
        [
            TextWidget('Welcome!', background=bg_color, **default_args),
            # TextWidget('\U0001F9A0', font_family='Noto Color Emoji'),
            corona_widget(),
            'Stretch',
            SelfUpdatingWidget(
                'US', 'xkb-switch', None, 600, 'xkb-switch -W',
                lambda x: f'{x.upper()[0:2]}', background=altbg_color,
                click_func=lambda: sp.Popen('xkb-switch -n', shell=True),
                font_weight='bold', **default_args),
            SelfUpdatingWidget(
                '', None,
                lambda: datetime.datetime.now().strftime(
                    '%a, %d-%b-%Y / %I:%M:%S'), 1,
                update_proc=None, post_proc_func=lambda x: x.strip(),
                background=bg_color, **default_args),
        ],
        app=app, widgets_spacing= 10,
        rounded_corner='5px', color='white')
    bar.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(Qt.Qt.AA_UseHighDpiPixmaps)
    main(app)
