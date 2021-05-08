#!/usr/bin/env python

import requests
import subprocess as sp
from bs4 import BeautifulSoup
from pyqt5bar.widgets_base import SelfUpdatingWidget, TextWidget


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


def sar_thread(wait_time):
    sar_output = sp.check_output(
        f'sar -u {wait_time} 1', text=True, shell=True)
    average = sar_output.splitlines()[-1]
    average = sum(map(float, average.split()[2:5]))
    return '{cpu_usage:0.0f%}'
