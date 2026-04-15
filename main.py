# Download 20 stock CSV files and put them in a folder named data. !!------ DONE ------!!

# Use the csv or pandas module in onAppStart to load all price data into a dictionary.

# Set up app variables for cash, sharesOwned, and currentDayIndex.

# Use random.sample to pick 5 stocks from your list of 20 at the start of each game.

# Create an onStep function that increments currentDayIndex every 1 or 2 seconds.

# Update the list of "visible" prices in onStep so the graph has new data to display.

# Draw 5 beige rectangles to serve as the "cards" for your stocks.

# Place your drawScrollingGraph function inside each card to show the price movement.

# Use onMousePress to detect if a user clicks a "Buy" or "Sell" area on a card.

# Update app.cash and app.sharesOwned based on those clicks and the current price.

# Create a list of "Life Events" (e.g., "Car Break Down", "Tax Refund").

# Add a small random chance in onStep to trigger a popup for these events.

# Add a "Savings Account" card that applies a fixed interest rate to a specific cash balance.

# Draw a "Total Net Worth" label at the top that calculates the value of all cash and stocks combined.

# Apply the olive green and beige color scheme to all shapes and labels.


import os
import pandas as pd
from cmu_graphics import *

def getCleanData(filePath):
    assetData = pd.read_csv(filePath)
    
    assetData['Close/Last'] = assetData['Close/Last'].astype(str).str.replace('$', '').str.replace(',', '')
    assetData['Close/Last'] = pd.to_numeric(assetData['Close/Last'])

    assetData['Date'] = pd.to_datetime(assetData['Date'])
    assetData = assetData.set_index('Date')

    monthlyStockData = assetData.resample('ME').last()

    return monthlyStockData['Close/Last'].tolist()



class Asset:
    def __init__(self, ticker, priceData, color):
        self.ticker = ticker
        self.priceData = priceData
        self.color = color
        self.sharesOwned = 0

    def getCurrentPrice(self, monthIndex):
        if monthIndex < len(self.priceData):
            return self.priceData[monthIndex]
        return self.priceData[-1]

    def getValue(self, monthIndex):
        return self.sharesOwned * self.getCurrentPrice(monthIndex)
    

def loadAssets(categories):
    allStocks = []
    index = []
    allCrops = []

    for folder in categories:
        color = categories[folder]
        for file in os.listdir(folder):
            if file.endswith('.csv'):
                path = os.path.join(folder, file)
                ticker = file.replace('.csv', '')
                prices = getCleanData(path)
                asset = Asset(ticker, prices, color)
                if folder == 'stock_data':
                    allStocks.append(asset)
                elif folder == 'index_data':
                    index.append(asset)
                else:
                    allCrops.append(asset)

    return allStocks, index, allCrops


def onAppStart(app):
    app.cash = 4000
    app.monthIndex = 0

    categories = {
        'stock_data' : 'forestGreen',
        'index_data' : 'dodgerBlue',
        'crop_data' : 'coral'}

    app.allStocks, app.index, app.allCrops = loadAssets(categories)

    print(f"Loaded {len(app.allStocks)} stocks, {len(app.index)} indices, and {len(app.allCrops)} crops.")

runApp(width=800, height=600)