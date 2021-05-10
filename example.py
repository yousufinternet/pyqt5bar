#!/usr/bin/env python

import sys
import datetime
import subprocess as sp
from pyqt5bar.main import Bar
from pyqt5bar.builtin_widgets import corona_cases, CpuUsageWidget, CpuTempWidget, RamUsageWidget, BatteryWidget, HerbstluftwmTagsWidget, VolumeWidget
from PyQt5 import QtWidgets, Qt
from pyqt5bar.widgets_base import SelfUpdatingWidget, TextWidget, GroupWidget


fg_color = '#f8f8f2'
altfg_color = '#e0e0e0'
bg_color = '#282a36'
altbg_color = '#181920'
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
        background=altbg_color, **default_args)


def main(app):
    tags_def_style = {'padding': '2px', 'border-radius': '2px'}
    soft_white = 'rgba(248, 248, 242, 20%)'
    dark_black = 'rgba(40, 42, 54, 80%)'
    bar = Bar(
        [
            HerbstluftwmTagsWidget(
                urgent_style={'background': '#ff5555', **tags_def_style},
                focused_style={'background': '#ff79c6', **tags_def_style, 'font-weight': '900'},
                empty_style={'background': 'transparent',
                             'color': 'rgba(255, 255, 255, 50%)',
                             'font-weight': '100', **tags_def_style},
                used_style={'font-weight': 'bold', **tags_def_style},
                background=bg_color,
                **default_args, border_bottom_left_radius='0px'),
            corona_widget(),
            SelfUpdatingWidget(
                'US', 'xkb-switch', None, 600, 'xkb-switch -W',
                lambda x: f'{x.upper()[0:2]}', background=bg_color,
                click_func=lambda: sp.Popen('xkb-switch -n', shell=True),
                font_weight='bold', **default_args),
            VolumeWidget(background=altbg_color, **default_args),

            'Stretch',

            GroupWidget([
                TextWidget('SysStats:', background='transparent',
                           padding_left='5px', padding_right='0px',
                           font_weight='bold'),
                RamUsageWidget(background=soft_white, padding_left='2px',
                               padding_right='2px', border_radius='2px'),
                CpuTempWidget(update_period=5, background=soft_white,
                              padding_left='2px', padding_right='2px',
                              border_radius='2px'),
                GroupWidget(
                    [TextWidget('\U0001F4BB', font_family='Noto Color Emoji'),
                     CpuUsageWidget()], background=soft_white,
                    padding_left='2px', padding_right='2px',
                    border_radius='2px'),
                BatteryWidget(background=soft_white, padding_left='2px',
                              padding_right='2px', border_radius='2px'),
            ], background='Black', **default_args),
            SelfUpdatingWidget(
                '', None,
                lambda: datetime.datetime.now().strftime(
                    '%a, %d-%b-%Y / %I:%M:%S'), 1,
                update_proc=None, post_proc_func=lambda x: x.strip(),
                background=bg_color, **default_args),
        ],
        app=app, widgets_spacing= 10,
        rounded_corner='5px', color='white', font_family='Fira Code',
        background=dark_black)
    bar.show()
    bar.setMaximumHeight(20)
    if bar.isVisible():
        sp.Popen('xdo raise -a xfce4-panel', shell=True)
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(Qt.Qt.AA_UseHighDpiPixmaps)
    main(app)
