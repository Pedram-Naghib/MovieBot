import sqlite3


# def exists(_id):
#     with sqlite3.connect('./database.db') as conn:
#         cursor = conn.cursor()
#         update_query = f'''
#         SELECT Title FROM media WHERE imdbID == ?;
#         '''

#         data = cursor.execute(update_query, (_id,))
#         print(data)
#         conn.commit()


AWARDS = {'SFF': 'Sundance Film Festival', 'TIFF': 'Toronto International Film Festival', 'Cannes': 'Cannes Film Festival',
          'Berlinale': 'Berlin International Film Festival', 'SanSebastián': 'San Sebastián International Film Festival',
          'MoscowIFF': 'Moscow International Film Festival', 'MIFF': 'Melbourne International Film Festival',
          'IFFR': 'International Film Festival Rotterdam', 'Venice': 'Venice Film Festival', 'PÖFF': 'Tallinn Black Nights Film Festival',
          'IDFA': 'International Documentary FilmFestival Amsterdam', 'SFIFF': 'San Francisco International Film Festival',
          'NYFF': 'New York Film Festival', 'IndieMemphis': 'Indie Memphis Film Festival', 'Locarno': 'Locarno International Film Festival',
          'TFF': 'Thessaloniki Film Festival', 'TDF': 'Thessaloniki Documentary Festival', 'KVIFF': 'Karlovy Vary International Film Festival',
          'RIFF': 'Riga International Film Festival', 'Viennale': 'Vienna International Film Festival', 'ZFF': 'Zurich Film Festival',
          'MdPIFF': 'Mar del Plata International Film Festival', 'DaviddiDonatello': 'David di Donatello Awards',
          'VIFF': 'Vancouver International Film Festival', 'CIFF': 'Cairo International Film Festival', 'FIFF': 'Faro Island Film Festival',
          'SIFF': 'Shanghai International Film Festival'}


import requests
from bs4 import BeautifulSoup
import html.parser


def award_data(title):
    title = title.replace(' ', '-')
    read = requests.get(f"https://mubi.com/en/tr/films/{title}/awards")
    soup = BeautifulSoup(read.content, "html.parser")
    # returns an iterable containing all the HTML for all the listings displayed on that page
    awards = soup.find_all("div", class_="css-wffprx e1at15620")
    aws = set()

    for award in awards:
        name = award.find("a", class_='css-15hqn5v e1at15624').text
        if name in AWARDS.values():
            year = award.find("div", class_='css-16kkjs e1at15626').text.split(' ')[0]
            aws.add((name, year))

    return aws


# print(award_data('Annette'))

from src import constants


def award_data(_id, title):
    title = title.replace(' ', '-')
    read = requests.get(f"https://mubi.com/en/tr/films/{title}/awards")
    soup = BeautifulSoup(read.content, "html.parser")
    # returns an iterable containing all the HTML for all the listings displayed on that page
    awards = soup.find_all("div", class_="css-wffprx e1at15620")
    aws = {}

    for award in awards:
        name = award.find("a", class_='css-15hqn5v e1at15624').text
        if name in constants.AWARDS.keys():
            year = award.find("div", class_='css-16kkjs e1at15626').text.split(' ')[0]
            if aws.get(name, None):
                aws[name].add(year)
            else:
                aws[name] = {year}

    # sqldb.add_awards(_id, aws)
    return aws


print(award_data('tt6217926', 'Annette'))