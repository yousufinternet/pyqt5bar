#!/usr/bin/env python

import os
import sys
import requests
import subprocess as sp
from PyQt5 import QtWidgets, QtGui, QtCore
from bs4 import BeautifulSoup
from pyqt5bar.widgets_base import SelfUpdatingWidget, TextWidget, GroupWidget

pathname = os.path.dirname(sys.argv[0])
SCRIPT_PATH = os.path.abspath(pathname)

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

def corona_cases():
    try:
        page = requests.get(
                'https://www.worldometers.info/coronavirus/country/iraq/')
        soup = BeautifulSoup(page.content, features='lxml')
        cases = soup.select("div[class='maincounter-number']")
        deaths_recovered = sum(float(c.span.text.replace(',', ''))
                               for c in cases[1:])
        total_cases = float(cases[0].span.text.replace(',', ''))
        active_cases = total_cases - deaths_recovered
        return f'{active_cases:0,.0f}'
    except Exception:
        return


def pacman_updates():
    aur_packs = sp.check_output(
        'pikaur -Qua | tee /tmp/aurupdates | wc -l',
        shell=True, text=True).strip()
    official = sp.check_output(
        'pacman -Qu | tee /tmp/pacmanupdates | wc -l',
        shell=True, text=True).strip()
    all_packs = int(aur_packs) + int(official)
    return str(all_packs)


class RamUsageWidget(GroupWidget):
    def __init__(self, update_period=5, bar_height=20, **kwargs):
        ram_icon = QtWidgets.QLabel()
        print(f'{SCRIPT_PATH}/Images/ram.png')
        ram_pix = QtGui.QPixmap(f'{SCRIPT_PATH}/Images/ram.png').scaledToHeight(
            bar_height-2, QtCore.Qt.SmoothTransformation)
        ram_icon.setPixmap(ram_pix)
        ram_icon.setMaximumWidth(ram_icon.sizeHint().width())
        ram_icon.setAlignment(QtCore.Qt.AlignCenter)
        ramusage = SelfUpdatingWidget(
            '', func=self.get_usage, update_period=update_period)
        super().__init__([ram_icon, ramusage], **kwargs)

    def get_usage(self):
        ram = sp.check_output('vmstat -s', shell=True, text=True).split('\n')
        used = int(ram[1].strip().split()[0])/(1024**2)
        total = int(ram[0].strip().split()[0])/(1024**2)
        percent = f'{used/total:0>3.0%}'
        return percent


class CpuTempWidget(SelfUpdatingWidget):
    def __init__(self, level_colors=['white', 'orange', 'red'], **kwargs):
        super().__init__('', None, self.get_temp, **kwargs)
        self.icons_dict = {50: '\uf2cb', 60: '\uf2ca', 70: '\uf2c9',
                           80: '\uf2c8', 90: '\uf2c7'}
        self.level_colors = level_colors

    def get_temp(self):
        sensors = sp.check_output('sensors', text=True, shell=True)
        temps = [int(line.split()[2].split('.')[0]) for line in
                 sensors.split('\n') if line.startswith('Core')]
        self.avg_temp = sum(temps)/len(temps)
        self.current_icon = [
            v for k, v in self.icons_dict.items()
            if k >= self.avg_temp or k == 90][0]
        return f'{self.current_icon} {self.avg_temp:0.0f} ℃'

    def update_widget(self, text):
        self.label.setText(text)
        if self.avg_temp > 85:
            self.label.setStyleSheet(f'color: {self.level_colors[-1]}')
        elif self.avg_temp > 70:
            self.label.setStyleSheet(f'color: {self.level_colors[1]}')
        else:
            self.label.setStyleSheet(f'color: {self.level_colors[0]}')


class CpuUsageWidget(SelfUpdatingWidget):
    def __init__(self, update_period=5, warning_level=85, **kwargs):
        self.update_period = update_period
        self.warning_level = warning_level
        super().__init__('', None, self.sar_out, 0.1, None, None, **kwargs)

    def sar_out(self):
        sar_output = sp.check_output(
            f'sar -u {self.update_period} 1', text=True, shell=True)
        average = sar_output.splitlines()[-1]
        average = sum(map(float, average.split()[2:5]))
        return f'{average:0>3.0f}%'

    def update_widget(self, text):
        self.label.setText(text)
        if int(text[:-1]) > 85:
            self.label.setStyleSheet('background: red')
        elif int(text[:-1]) > 70:
            self.label.setStyleSheet('background: orange')
