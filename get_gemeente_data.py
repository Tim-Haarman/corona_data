import requests
import json
import bs4
import pandas as pd
from tqdm import tqdm

_WIKI_API_LINK = 'https://nl.wikipedia.org/api/rest_v1/page/'


def get_lat_lon_for_gemeente(gemeente):
    """
    Find lat-lon pair for gemeente using the Wikipedia API. Fast, but not complete.
    """
    
    json_data = requests.get(_WIKI_API_LINK + 'summary/' + gemeente).json()
    coordinates = json_data.get('coordinates')

    if not coordinates:
        raise ValueError(f'No LatLong found on Wikipedia page for "{gemeente}"')

    lat = coordinates['lat']
    lon = coordinates['lon']

    return lat, lon


def get_lat_lon_for_gemeente_by_geosite(soup):
    """
    Find lat-lon pair for gemeente by using the geohack website. Slower, but has data for all municipalities.
    """

    geo_element = soup.find(id='text_coordinates')
    geo_link = geo_element.select('a')[0]['href']

    if not geo_link:
        raise ValueError('No geohack page found on Wikipedia page')

    geopage_html = requests.get(geo_link).content
    geo_soup = bs4.BeautifulSoup(geopage_html, 'html.parser')

    lat = geo_soup.find('span', {'class': 'latitude'}).text
    lon = geo_soup.find('span', {'class': 'longitude'}).text

    return lat, lon


def get_gemeente_number(gemeente, soup):
    code_element = soup.find('a', {'title': 'Gemeentenummer'}).parent.parent
    gemeente_code = code_element.select('td')[1].text.strip()

    return gemeente_code

def get_rivm_data():
    page = requests.get('https://www.rivm.nl/coronavirus-kaart-van-nederland-per-gemeente')
    soup = bs4.BeautifulSoup(page.content, 'html5lib')

    data_tag = soup.find('div', id='csvData')
    data_list = [row.split(';') for row in data_tag.get_text().strip().split('\n')]
    header = data_list.pop(0)

    return pd.DataFrame(data_list, columns=header).astype({'Gemnr': int, 'BevAant': int})


def get_gemeente_data(gemeenten_filepath):
    with open(gemeenten_filepath, 'r') as gemeenten_file:
        gemeenten = gemeenten_file.read().splitlines()
    
    with open('data/gemeenten_locaties.csv', 'w+') as csv_file:
        all_data = []
        excluded_gemeenten = []

        for gemeente in tqdm(gemeenten):
            html = requests.get('https://nl.wikipedia.org/wiki/' + gemeente).content
            soup = bs4.BeautifulSoup(html, 'html.parser')
            
            try:
                lat, lon = get_lat_lon_for_gemeente(gemeente)
            except ValueError:
                lat, lon = get_lat_lon_for_gemeente_by_geosite(soup)

            try:
                gemeente_number = get_gemeente_number(gemeente, soup)
            except AttributeError:
                excluded_gemeenten.append(gemeente)
                continue

            all_data.append([gemeente, gemeente_number, lat, lon])
    
    if excluded_gemeenten:
        print(f'The following gemeenten were excluded because no gemeentecode could be found: {excluded_gemeenten}')

    data = pd.DataFrame(all_data, columns=['Gemeente (Wikipedia)', 'Gemnr', 'lat', 'lon']).astype({'Gemnr': int})
    rivm_data = get_rivm_data()[['Gemnr', 'BevAant', 'Gemeente']]

    return data.merge(right=rivm_data, how='inner', on='Gemnr')


if __name__ == "__main__":
    df = get_gemeente_data('data/gemeente_names.txt')
    df.to_csv('data/gemeenten_geo_data.csv', sep=',', index=False)
