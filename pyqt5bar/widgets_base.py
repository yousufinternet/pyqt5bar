#!/usr/bin/env python

import time
import select
import subprocess
from PyQt5 import QtCore, QtWidgets, Qt


default_style = {'background': 'transparent', 'padding': '0px', 'margin': '0px'}


class LabelWithSignals(QtWidgets.QLabel):
    '''
    QLabel with signals for hover, click and double click event
    '''
    clicked = QtCore.pyqtSignal()
    hovered = QtCore.pyqtSignal()
    doubleClicked = QtCore.pyqtSignal()
    scrollUp = QtCore.pyqtSignal()
    scrollDown = QtCore.pyqtSignal()

    def wheelEvent(self, ev):
        print(ev.angleDelta().y())
        if ev.angleDelta().y() < 0:
            print('Down')
            self.scrollDown.emit()
        else:
            print('Up')
            self.scrollUp.emit()

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()

    def enterEvent(self, ev):
        self.hovered.emit()

    def mouseDoubleClickEvent(self, ev):
        self.doubleClicked.emit()


class GroupWidget(QtWidgets.QFrame):
    def __init__(self, wdgts, **kwargs):
        super().__init__()
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        for wdgt in wdgts:
            self.hlayout.addWidget(wdgt)
        self.setLayout(self.hlayout)

        self.props = default_style.copy()
        for k, v in kwargs.items():
            self.props[k] = v
        self.stylize()

    def stylize(self):
        stylesheet = " ".join(
            f'{k.replace("_", "-")}: {v};'
            for k, v in self.props.items())
        self.setStyleSheet(stylesheet)
        # self.setProperty('group_frame', True)


class BaseWidget(QtWidgets.QWidget):
    '''
    Bar widget that is the base for all widgets
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.props = default_style.copy()
        for k, v in kwargs.items():
            self.props[k] = v
        self.stylize()

    def stylize(self):
        '''
        Apply user settings
        '''
        stylesheet = " ".join(f'{k.replace("_", "-")}: {v};'
                              for k, v in self.props.items())
        self.setStyleSheet(stylesheet)


class TextWidget(BaseWidget):
    def __init__(self, text, click_func=None, hover_func=None,
                 doubleclick_func=None, scrollup_func=None,
                 scrolldown_func=None, **kwargs):
        super().__init__(**kwargs)
        self.click_func = click_func
        self.hover_func = hover_func
        self.doubleclick_func = doubleclick_func
        self.scrollup_func = scrollup_func
        self.scrolldown_func = scrolldown_func
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.label = LabelWithSignals(text)
        self.setLayout(self.hbox)
        self.hbox.addWidget(self.label)
        self.connect_signals()

    def connect_signals(self):
        if self.click_func is not None:
            self.label.clicked.connect(self.click_func)
        if self.hover_func is not None:
            self.label.hovered.connect(self.hover_func)
        if self.doubleclick_func is not None:
            self.label.doubleClicked.connect(self.doubleclick_func)
        if self.scrollup_func is not None:
            self.label.scrollUp.connect(self.scrollup_func)
        if self.scrolldown_func is not None:
            self.label.scrollDown.connect(self.scrolldown_func)


class SubProcessObject(QtCore.QObject):
    '''
    Object for running subprocess and waiting for results
    to be moved into a thread object
    '''
    update_signal = QtCore.pyqtSignal(object)

    def __init__(self, cmd, func, update_period, update_proc, post_proc_func):
        super().__init__()
        if cmd is None and func is None:
            raise ValueError('You have to either pass a function or a command')
        if cmd is not None and func is not None:
            raise ValueError(
                'You cannot pass a function and a command at the same time')
        self.cmd = cmd
        self.func = func
        self.update_period = update_period
        self.post_proc_func = post_proc_func
        self.update_proc = update_proc
        self.start_updater_proc()

    def start_updater_proc(self):
        if self.update_proc is None:
            return
        self.update_p = subprocess.Popen(
            self.update_proc, text=True, shell=True,
            stdout=subprocess.PIPE)
    
    def wait_updater(self):
        '''
        return early if updater produced something
        '''
        ready, _, _ = select.select(
            [self.update_p.stdout], [], [], self.update_period)
        if ready:
            _ = ready[0].readline()
            return True
        return False

    def start_process(self):
        while True:
            if self.cmd is not None:
                try:
                    P = subprocess.Popen(
                        self.cmd, text=True, shell=True,
                        stdout=subprocess.PIPE)
                    P.wait()
                    out = P.stdout.read()
                except subprocess.CalledProcessError:
                    out = ''
            if self.func is not None:
                out = self.func()
            if self.post_proc_func is not None:
                out = self.post_proc_func(out)
            self.update_signal.emit(out)
            if self.update_period == 0:
                break
            if self.update_proc is not None:
                self.wait_updater()
            else:
                time.sleep(self.update_period)


class CommandInThread(QtCore.QThread):
    '''
    A QThread for running subprocesses and waiting for results
    override start method for running your own functions
    '''
    def __init__(self, func_obj):
        super().__init__()
        self.func_obj = func_obj

    def start(self):
        self.func_obj.moveToThread(self)
        self.started.connect(self.func_obj.start)
        super().start()


class SelfUpdatingWidget(TextWidget):
    def __init__(
            self, inittext='', cmd=None, func=None, update_period=0,
            update_proc=None, post_proc_func=None, **kwargs):
        super().__init__(inittext, **kwargs)
        self.current_text = inittext

        self.func_obj = SubProcessObject(
            cmd, func, update_period, update_proc, post_proc_func)

        self.thread = QtCore.QThread()
        self.func_obj.moveToThread(self.thread)
        self.func_obj.update_signal.connect(self.update_widget)
        self.thread.started.connect(self.func_obj.start_process)
        self.thread.start()

    def update_widget(self, text):
        if self.label.text() == text:
            return
        self.label.setText(text)


class SelfUpdatingWidgets(GroupWidget):
    def __init__(
            self, wdgts, cmd=None, func=None, update_period=0,
            update_proc=None, post_proc_func=None, **kwargs):
        super().__init__(wdgts, **kwargs)

        self.func_obj = SubProcessObject(
            cmd, func, update_period, update_proc, post_proc_func)

        self.thread = QtCore.QThread()
        self.func_obj.moveToThread(self.thread)
        self.func_obj.update_signal.connect(self.update_widget)
        self.thread.started.connect(self.func_obj.start_process)
        self.thread.start()
        self.widgets = wdgts

    def update_widgets(self, output:list):
        '''
        Override with your logic
        '''
        pass
