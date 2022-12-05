# Importing Libraries
import time
start_time = time.time()

import pandas_datareader.data as web
from pandas_datareader import data
import datetime
from datetime import date
import pandas as pd
import numpy as np
import os
import fnmatch
from tabulate import tabulate
import requests
import csv
import matplotlib.pyplot as plt

#Downloading Data For US Companies with Market Cap >= 10 Billion USD
headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
}

#Companies with Market cap>=10B USD requested from NASDAQ API
url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&marketcap=large&download=true"
r = requests.get(url, headers=headers)
j = r.json()
print(r)

table = j['data']
table_headers = table['headers']

#Storing the File as 'Stocks.csv'
with open('Stocks.csv', 'w', newline='') as f_output:
    csv_output = csv.DictWriter(f_output, fieldnames=table_headers.values(), extrasaction='ignore')
    csv_output.writeheader()

    for table_row in table['rows']:
        csv_row = {table_headers.get(key, None) : value for key, value in table_row.items()}
        csv_output.writerow(csv_row)

### Reading the pulled filed out of NASDAQ API

## DATA for all companies present at the link ===> https://www.nasdaq.com/market-activity/stocks/screener
files = [f for f in os.listdir('.') if os.path.isfile(f)]
file_name = fnmatch.filter(files, '*.csv')
## Reading the excel file
df = pd.read_csv (file_name[0])

#Dates
today = date.today()
year = today.year
month = today.month
day = today.day

## Picking companies not less than 10 years of age 
# Extracting companies not older than 10 years
final_set = df[df["IPO Year"] >= (year-10)]

# retrieving ticker trading symbols
tickers = final_set.Symbol.values.tolist()
print("Shortlisted companies: " + str(len(tickers)))
print(tickers)
print("\n\n")

### Making a new dataframe

## Assign data of lists.  
market_dict = {'Symbol': [], 'Company Name': [], 'IPO Year': [], 'Market Cap': [], 'Market': [], 'First IPO Price': [], 'Today\'s Price': []}

## identifying starts and ends
start = datetime.datetime(year-12, month,1)
end = datetime.datetime(year, month, day) 
####YFINANCE HERE
## Requesting through yahoo finance  API(historic and current prices)
for i in range(len(tickers)):
    test = web.DataReader(tickers[i], "yahoo", start, end)
    first_price = test.iloc[0,3]
    todays_price = test.iloc[-1,3]
    print(final_set.iloc[i,1])
    print("IPO'ed at: $"+str(first_price))
    print("Today's Price: $"+str(todays_price))
    print("--------------------------------------------\n")
    if ( (todays_price < (first_price + (first_price*0.03) ) ) and (todays_price > (first_price - (first_price*0.03) ) ) ):
        market_dict['Symbol'].append(tickers[i])
        market_dict['Company Name'].append(final_set.iloc[i,1])
        market_dict['IPO Year'].append(final_set.iloc[i,7])
        market_dict['Market Cap'].append(final_set.iloc[i,5])
        market_dict['Market'].append("US")
        market_dict['First IPO Price'].append("$"+str(first_price))
        market_dict['Today\'s Price'].append("$"+str(todays_price))
        

        plot_name = "Shortlisted_Graphs/"+str(final_set.iloc[i,1])+".png"
        plt.plot(test.index, test.iloc[:,3])

        plt.xlabel("Time-series")
        plt.ylabel("Closing Index")
        plt.xticks(rotation = 45)
        plt.title(final_set.iloc[i,1])

        plt.savefig(plot_name, dpi = 720)
        plt.close()
      
df = pd.DataFrame(market_dict)  


print("\n\nFINAL SHORT-LISTED COMPANIES WITH PLUS MINUS 3% VALUE CONDITION")
print(tabulate(df, headers = 'keys', tablefmt = 'psql'))

print("Elapsed Time")
print("--- %s seconds ---" % (time.time() - start_time)) 