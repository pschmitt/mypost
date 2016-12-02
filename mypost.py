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
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
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
            url='https://www.mypost.lu/api/private/v0.3/client/infoconso',
            headers=headers
        )
        if consumption.ok:
            return consumption.json()
        else:
            consumption.raise_for_status()


def extract_consumption_data(consumption, data_type):
    d = [x for x in c['components'] if x['type'] == data_type]
    assert d, 'Failed to extract {} consumption'.format(data_type)
    data_consumption = d[0]
    current = data_consumption['balance']['current']
    available = data_consumption['balance']['maxValue']
    unit = data_consumption['units']
    return current, available, unit


def extract_data_consumption(consumption):
    return extract_consumption_data(consumption, 'DATA')


def extract_sms_consumption(consumption):
    return extract_consumption_data(consumption, 'SMS')


def extract_mms_consumption(consumption):
    return extract_consumption_data(consumption, 'MMS')


def available_components(consumption):
    return sorted([x['type'] for x in consumption['components']])


def extract_out_of_bundle(consumption):
    return consumption['outOfBundle']


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
    # Init colorama
    init()
    for component in available_components(c):
        # Get consumption data and convert to MB
        consumed, available, unit = extract_consumption_data(c, component)
        if unit == 'GB':
            consumed = float(consumed) / (1024 * 1024)
            available = float(available) / (1024 * 1024)
        elif unit == 'MB':
            consumed = float(consumed) / 1024
            available = float(available) / 1024
        # Get the consumption color
        color = get_color(consumed, available)
        # Debug
        # print(color, component, consumed, available)
        col = colored('{0:.1f}'.format(consumed), color)
        print('{}: {} / {:.1f}'.format(component, col, available))
    print('Out of bundle: -{}€'.format(extract_out_of_bundle(c)))
