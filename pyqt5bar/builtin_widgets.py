#!/usr/bin/env python

from pyqt5bar.widgets_base import SelfUpdatingWidget, TextWidget


def process_xkb(txt):
    return txt.upper()[0:2]

keyboardLayout = SelfUpdatingWidget(
    'US', 'xkb-switch', None, 600, 'xkb-switch -W', lambda x: f'{x.upper()[0:2]}')
