#!/usr/bin/python3

import requests
import argparse
import sys
import npyscreen
from bs4 import BeautifulSoup

BASE_URL = 'https://www.klart.se/se/pollenprognoser/stationer/'

parser = argparse.ArgumentParser()
parser.add_argument('city')
args = parser.parse_args()

def get_information(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    pollen_table = soup.find('table', {'class': 'pollen-table'}).find('tbody')
    reports = pollen_table.findAll('tr', {'class': 'row'})
    pollen_information = {}
    for report in reports:
        type = str(report.find('td', {'class': 'type'}).text).strip()
        day = report.find('td', {'class': 'day'})
        if day:
            level = str(day.find('i', {'class': 'level'})['class'][1]).replace('-', '')
        else:
            text = str(report.find('td', {'colspan': '5'}).text).strip().split()
            level = text[0] + ' ' + text[1]

        pollen_information[type] = level
    return pollen_information


def display_information(city, pollen_information):
    F = npyscreen.Form(name='Pollenkoll: ' + city)
    gd = F.add(MyGrid, col_titles=['Ort', 'Pollenhalt'], editable=False)
    gd.values = []
    if bool(pollen_information):
        for type in sorted(pollen_information.keys()):
            row = []
            row.append(type)
            row.append(pollen_information[type])
            gd.values.append(row)
    else:
        gd.values.append(['No information'])
    F.edit()
    print(F)


class MyGrid(npyscreen.GridColTitles):
    def custom_print_cell(self, actual_cell, cell_display_value):
        if cell_display_value =='none':
            actual_cell.color = 'DEFAULT'
        elif cell_display_value == 'low':
            actual_cell.color = 'SAFE'
        elif cell_display_value == 'medium':
            actual_cell.color = 'WARNING'
        elif cell_display_value == 'high':
            actual_cell.color = 'DANGER'
        else:
            actual_cell.color = 'DEFAULT'

class Pollenkoll(npyscreen.NPSApp):
    def main(self):
        pollen_information = get_information(BASE_URL + args.city)
        display_information(args.city, pollen_information)


if __name__ == '__main__':
    if args.city:
        App = Pollenkoll()
        App.run()
    else:
        sys.exit(0)

