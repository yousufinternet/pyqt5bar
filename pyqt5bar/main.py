#!/usr/bin/env python

import sys
from PyQt5 import QtWidgets, QtCore, QtGui, Qt

from pyqt5bar.widgets_base import TextWidget, SelfUpdatingWidget

class BarProps:
    '''
    Stores the bar properties, with defaults
    '''
    def __init__(self, app, **kwargs):
        self.x, self.y, self.widgets_spacing = 0, 0, 0
        self.width = app.primaryScreen().size().width()
        self.height, self.rounded_corner = 20, '0px'
        self.background = 'transparent'
        self.font_family = '"Fira Code"'
        self.font_weight = 'normal'
        self.font_size = 10

        # update with user set values
        for k, v in kwargs.items():
            setattr(self, k, v)


class Bar(QtWidgets.QWidget):
    def __init__(self, wdgts, app, **kwargs):
        super().__init__()
        self.app = app
        self.props = BarProps(app, **kwargs)
        self.wdgts = wdgts
        self.initProps()

    def initProps(self):
        bypass = Qt.Qt.BypassWindowManagerHint
        for flag in (
                Qt.Qt.WindowStaysOnBottomHint, Qt.Qt.FramelessWindowHint,
                Qt.Qt.NoDropShadowWindowHint, Qt.Qt.WindowDoesNotAcceptFocus,):
            self.setWindowFlag(flag, True)
        self.setAttribute(Qt.Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.Qt.WA_X11NetWmWindowTypeDock)

        self.main_layout = QtWidgets.QHBoxLayout()

        holder_layout = QtWidgets.QHBoxLayout()
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setLayout(self.main_layout)
        holder_layout.addWidget(self.main_frame)

        # Fixed Settings
        holder_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        holder_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(holder_layout)

        # Apply settings
        self.inforce_bar_height()
        self.stylize()
        self.populate_widgets()

    def stylize(self):
        self.main_layout.setSpacing(self.props.widgets_spacing)
        self.setStyleSheet('margin: 0px; padding: 0px; border: 0px none transparent')
        self.main_frame.setStyleSheet(
            f'background-color: {self.props.background}; margin: 0px;'
            ' padding: 0px; border: 0px none transparent;'
            f'border-radius: {self.props.rounded_corner};'
            f'font-family: {self.props.font_family};'
            f'font-size: {self.props.font_size};'
            f'font-weight: {self.props.font_weight};'
        )

    def inforce_bar_height(self):
        self.setGeometry(
            self.props.x, self.props.y, self.props.width, self.props.height)
        self.setMaximumHeight(self.props.height)
        for child in self.children():
            for c in child.children():
                if not (isinstance(c, QtWidgets.QHBoxLayout) or c is None):
                    c.setMaximumHeight(self.props.height)

        children = (self.main_layout.itemAt(i) for i in range(self.main_layout.count()))
        for child in children:
            if child.widget() is not None:
                child.widget().setMaximumHeight(self.props.height)

    def populate_widgets(self):
        # Close button for debugging
        close = QtWidgets.QPushButton('close')
        close.clicked.connect(self.app.quit)
        close.setFlat(True)
        close.setMaximumHeight(self.props.height)
        close.setStyleSheet('border: 0px none transparent')

        for wdgt in self.wdgts:
            if not isinstance(wdgt, str):
                self.main_layout.addWidget(wdgt)
            else:
                if wdgt == 'Stretch':
                    self.main_layout.addStretch()
                elif wdgt.startswith('Spacing'):
                    spacing = int(wdgt.split(maxsplit=1)[1])
                    self.main_layout.addSpacing(spacing)
        self.main_layout.addWidget(close)
        self.inforce_bar_height()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(Qt.Qt.AA_UseHighDpiPixmaps)
    bar = Bar(
        [
            TextWidget('Welcome!', background='Indigo', border_radius='9px',
                       border_width='2px', border_color='black', padding='1px',
                       padding_left='15px'),
            TextWidget('💗', font_family='Noto Color Emoji'),
            'Stretch',
            SelfUpdatingWidget(
                'test', 'date +"%a, %d-%B-%Y | %I:%M:%S"', None, 1, update_proc=None,
                post_proc_func=lambda x: x.strip(), background='Indigo', border_radius='9px', padding_left='9px', padding_right='9px'),
        ],
        rounded_corner='5px')
    bar.show()
    sys.exit(app.exec_())
    
