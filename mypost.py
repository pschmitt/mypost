#!/usr/bin/python
# coding: utf-8

from __future__ import print_function
import argparse
import base64
import requests
from colorama import init
from termcolor import colored


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    return parser.parse_args()


def get_consumption(username, password):
    headers = {
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0',
    }
    with requests.session() as s:
        # login
        s.post(
            url='https://www.mypost.lu/auth/mypostid-eai-api/v0.1/login',
            headers=headers,
            json={'username': username, 'password': base64.b64encode(password)}
        )
        # Get consumption data
        consumption = s.get(
            url='https://www.mypost.lu/api/private/v0.1/client/infoconso',
            headers=headers
        )
        if consumption.ok:
            return consumption.json()
        else:
            consumption.raise_for_status()

def get_color(consumed, available):
    ratio = consumed * 100 / available
    if ratio > 80:
        return 'red'
    elif ratio > 50:
        return 'yellow'
    else:
        return 'green'


if __name__ == '__main__':
    args = parse_args()
    c = get_consumption(args.username, args.password)
    # Get consumption data and convert to MB
    consumed = c['client']['subscription']['balances'][0]['currentValue'] / 1024 / 1024
    available = c['client']['subscription']['balances'][0]['maxValue'] / 1024 / 1024
    # Init colorama
    # Get the consumption color
    init()
    color = get_color(consumed, available)
    print(
        colored('{0:.1f}'.format(consumed), color),
        '/{1:.1f} MB'.format(consumed, available),
        sep=''
    )
