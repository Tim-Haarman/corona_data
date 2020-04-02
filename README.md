# corona_data
Code to scrape and combine data about the Corona disease in the Netherlands. Data from the RIVM is combined with Lat-Lon values from gemeenten as scraped from Wikipedia. 

Visualisation of the data using Kepler.GL can be found here: https://kepler.gl/demo/map?mapUrl=https://dl.dropboxusercontent.com/s/a3vzyqen7yv3jy3/keplergl_0apy9k.json


## Instructions
The complete aggregated data file can be found at `/data/corona_aggregated_data.csv`. Running `create_data.py` collects the same data and regenerates this file, to show how the data was collected. To do this requires the `rivm_corona_in_nl.csv` file from https://github.com/J535D165/CoronaWatchNL/blob/master/data/rivm_corona_in_nl.csv to be put in the `/data` folder, as the RIVM does not seem to provide historical data about the corona virus.
The latest data from the RIVM will be used to get the population of each 'gemeente' (municipality), and the lat-lon for all gemeenten are scraped from wikipedia.
