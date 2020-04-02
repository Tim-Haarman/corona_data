import pandas as pd
from get_gemeente_data import get_gemeente_data

def create_data():
    corona_df = pd.read_csv('data/rivm_corona_in_nl.csv', sep=',').rename(columns={'Gemeentecode': 'Gemnr'})
    gemeenten_df = get_gemeente_data('data/gemeente_names.txt')

    combined = corona_df.merge(right=gemeenten_df, how='inner', on='Gemnr')
    combined['per_100k'] = combined['Aantal'] / combined['BevAant'] * 100000
    combined['Datum'] = combined['Datum'] + ' 00:00'

    combined.to_csv('data/corona_aggregated_data.csv', sep=',', index=False)


if __name__ == "__main__":
    create_data()