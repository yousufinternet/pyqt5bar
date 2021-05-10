#!/usr/bin/env python

import os
import sys
import requests
import subprocess as sp
from functools import partial
from PyQt5 import QtWidgets, QtGui, QtCore, Qt
from bs4 import BeautifulSoup
from pyqt5bar.widgets_base import SelfUpdatingWidget, SelfUpdatingWidgets, TextWidget, GroupWidget, LabelWithSignals

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


def cmd_output(cmd, **kwargs):
    try:
        return sp.check_output(cmd, text=True, shell=True).strip()
    except sp.CalledProcessError:
        return ''

class HerbstluftwmTagsWidget(SelfUpdatingWidgets):
    '''
    urgent_style  : tags with urgent windows stylesheet
    focused_style : focused tag stylesheet
    empty_style   : tags with no windows stylesheet
    used_style    : tags with windows stylesheet
    animate_urgent: if tags with urgent windows are animated
    '''
    def __init__(
            self,
            urgent_style={'background': 'Red'},
            focused_style={
                'background': 'White', 'color': 'Indigo',
                'font-weight': 'bold'},
            empty_style={
                'background': 'Gray', 'color': 'rgba(255, 255, 255, 50%)'},
            used_style={'background': 'transparent'},
            animate_urgent=True,
            **kwargs):
        super().__init__(
            [], None, self.tags_state, update_period=5, **kwargs,
            update_proc="herbstclient --idle 'focus_changed|tag_changed'")
        self.urgent_style = urgent_style
        self.focused_style = focused_style
        self.empty_style = empty_style
        self.used_style = used_style
        self.animate_urgent = animate_urgent
        self.org_tags_count = int(cmd_output('herbstclient attr tags.count'))
        self.populate_group()

    def populate_group(self):
        if hasattr(self, 'widgets'):
            for wdgt in self.widgets:
                self.hlayout.removeWidget(wdgt)
        tags_count = int(cmd_output('herbstclient attr tags.count'))
        tags_names = [cmd_output(f'herbstclient attr tags.{i}.name')
                      for i in range(tags_count)]
        self.widgets = [LabelWithSignals(n) for n in tags_names]
        for wdgt in self.widgets:
            wdgt.setMinimumWidth(20)
            wdgt.setAlignment(Qt.Qt.AlignCenter)
            self.hlayout.addWidget(wdgt)
            wdgt.clicked.connect(partial(self.command, wdgt.text()))

    def command(self, txt):
        print(txt)
        if txt.endswith('__hov__'):
            tag = txt.rstrip('__hov__')

            # hover logic goes here
            return
        # click logic goes here
        sp.Popen(f'herbstclient use {txt}', shell=True)

    def animate_urgent_wdgt(self, wdgt):
        pass

    def update_widget(self, state):
        focused, empty_tags, urgent_tags = state
        for wdgt in self.widgets:
            if wdgt.text() == focused:
                wdgt.setStyleSheet('; '.join(
                    f'{k}: {v}' for k, v in self.focused_style.items()))
            elif wdgt.text() in urgent_tags:
                wdgt.setStyleSheet('; '.join(
                    f'{k}: {v}' for k, v in self.urgent_style.items()))
                if self.animate_urgent:
                    self.animate_urgent_wdgt(wdgt)
            elif wdgt.text() in empty_tags:
                wdgt.setStyleSheet('; '.join(
                    f'{k}: {v}' for k, v in self.empty_style.items()))
            else:
                wdgt.setStyleSheet('; '.join(
                    f'{k}: {v}' for k, v in self.used_style.items()))
 
    def tags_state(self):
        tags_count = int(cmd_output('herbstclient attr tags.count'))
        tags_names = [cmd_output(f'herbstclient attr tags.{i}.name')
                      for i in range(tags_count)]
        if tags_count != self.org_tags_count:
            self.org_tags_count = tags_count
            self.populate_group()

        focused = cmd_output('herbstclient attr tags.focus.name')

        empty_tags, urgent_tags = [], []
        for desk in tags_names:
            wins_count = cmd_output(
                f"herbstclient attr tags.by-name.{desk}.client_count")
            urgent_count = cmd_output(
                f'herbstclient attr tags.by-name.{desk}.urgent_count')
            urgent_count = 0 if urgent_count == '' else urgent_count
            if int(wins_count) == 0:
                empty_tags.append(desk)
            if int(urgent_count) != 0:
                urgent_tags.append(desk)
        return focused, empty_tags, urgent_tags


class VolumeWidget(GroupWidget):
    '''
    Battery percentage with papirus icons for panel
    '''
    def __init__(self, bar_height=20, **kwargs):
        self.volume_levels = {'none': 0, 'low': 25, 'medium': 50, 'high': 75}
        self.volume_icon = QtWidgets.QLabel()
        self.volume_icon.setStyleSheet('padding: 0px; background: transparent')

        self.volume = SelfUpdatingWidget(
            '100%', None, self.get_volume, 1, None, None,
            click_func=partial(self.set_volume, '100%'),
            doubleclick_func=partial(self.set_volume, '0'),
            scrollup_func=partial(self.set_volume, '+2%'),
            scrolldown_func=partial(self.set_volume, '-2%'))

        self.bar_height = bar_height
        super().__init__([self.volume_icon, self.volume], **kwargs)

    def set_volume(self, vol):
        sp.Popen(f'pactl set-sink-volume @DEFAULT_SINK@ {vol}',
                 shell=True, text=True)

    def get_volume(self):
        volume = cmd_output('pamixer --get-volume')
        volume = volume if volume else '0'
        icon = [k for k, v in self.volume_levels.items()
                if v >= int(volume)][0]
        icon = f'volume-level-{icon}-panel.svg'
        if hasattr(self, 'prev_icon') and icon == self.prev_icon:
            return f'{int(volume):0>3.0f}%'
        self.prev_icon = icon
        icon = os.path.join(SCRIPT_PATH, 'Images', 'volume', icon)
        vol_pix = QtGui.QPixmap(icon).scaledToHeight(
            self.bar_height-4, QtCore.Qt.SmoothTransformation)
        self.volume_icon.setPixmap(vol_pix)
        return f'{int(volume):0>3.0f}%'
        

class BatteryWidget(GroupWidget):
    '''
    Battery percentage with papirus icons for panel
    '''
    def __init__(self, bar_height=20, **kwargs):
        self.icons = os.listdir(f'{SCRIPT_PATH}/Images/battery')
        print(self.icons)
        self.battery_icon = QtWidgets.QLabel()
        self.battery_icon.setStyleSheet('padding: 0px; background: transparent')
        self.battery = SelfUpdatingWidget(
            '100%', func=self.output, update_period=120)
        self.bar_height = bar_height
        super().__init__([self.battery_icon, self.battery], **kwargs)

    def output(self):
        battery = sp.check_output('acpi --battery', text=True, shell=True).strip()
        if battery != '':
            charging = 'Charging' in battery
            status = battery.split(': ')[1].split(', ')[0]
            battery = battery.split(': ')[1].split(', ')[1]
            bat_vlu = int(battery.rstrip('%'))
            icon_name = f'battery-{round(bat_vlu, -1):0>3.0f}'
            icon_name += '-charging' if charging else ''
            icon_name += '.svg'
            print(icon_name)
            bat_pix = QtGui.QPixmap(
                f'{SCRIPT_PATH}/Images/battery/{icon_name}').scaledToHeight(
                    self.bar_height-4, QtCore.Qt.SmoothTransformation)
            self.battery_icon.setPixmap(bat_pix)
        return battery


class RamUsageWidget(GroupWidget):
    def __init__(self, update_period=5, bar_height=20, **kwargs):
        self.ram_icon = QtWidgets.QLabel()
        self.ram_pix = QtGui.QPixmap(
            f'{SCRIPT_PATH}/Images/ram_tiny.png').scaledToHeight(
                bar_height-4, QtCore.Qt.SmoothTransformation)
        self.ram_icon.setPixmap(self.ram_pix)
        self.ram_icon.setMaximumWidth(self.ram_pix.width())
        self.ram_icon.setAlignment(QtCore.Qt.AlignCenter)
        self.ram_icon.setStyleSheet('padding: 0px; background: transparent')

        ramusage = SelfUpdatingWidget(
            '', func=self.get_usage, update_period=update_period)

        super().__init__([self.ram_icon, ramusage], **kwargs)

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
        return f'{self.current_icon} {self.avg_temp:0.0f}℃'

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
