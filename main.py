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
from random import sample
from cmu_graphics import *

# Cleaning the CSV file
def getCleanData(filePath):
    assetData = pd.read_csv(filePath)
    
    assetData['Close/Last'] = assetData['Close/Last'].astype(str).str.replace('$', '').str.replace(',', '')
    assetData['Close/Last'] = pd.to_numeric(assetData['Close/Last'])

    assetData['Date'] = pd.to_datetime(assetData['Date'])
    assetData = assetData.set_index('Date')

    monthlyStockData = assetData.resample('ME').last()

    return monthlyStockData['Close/Last'].tolist()

# General class for each of the assets
class Asset:
    def __init__(self, ticker, priceData, color):
        self.ticker = ticker
        self.priceData = priceData
        self.color = color
        self.sharesOwned = 0

    # makes sure the game isnt over / out of bounds
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

def getNetWorth(app):
    total = app.cash
    for stock in app.stocks:
        total += stock.getValue(app.monthIndex)
    for crop in app.crops:
        total += crop.getValue(app.monthIndex)
    for index in app.index:
        total += index.getValue(app.monthIndex)
    return pythonRound(total, 2)

def onAppStart(app):
    # Basic stuff
    app.cash = 4000
    app.monthIndex = 0

    categories = {
        'stock_data' : 'forestGreen',
        'index_data' : 'dodgerBlue',
        'crop_data' : 'coral'}

    # Loading the stock data, picking random things
    allS, I, allC = loadAssets(categories)

    app.stocks = sample(allS, 5)
    app.index = I
    app.crops = sample(allC, 1)

    # timing constants
    app.indexRelease = 6
    app.stockRelease = 12
    app.cropRelease = 18
    app.goldRelease = 24

    print(f"Loaded {len(app.stocks)} stocks, {len(app.index)} index, and {len(app.crops)} crop")

def redrawAll(app):

    # Drawing the side bar
    drawRect(0, 0, 200, app.height, fill= rgb(65, 70, 57))

    drawLabel(f'YEAR {app.monthIndex // 12} OF 10', 20, 30, fill = 'white', size = 20, font = 'serif', bold = True, align = 'left')
    drawLabel('POCKET CASH', 20, 400, fill = 'white', size = 20, font = 'serif', bold = True, align = 'left')
    drawLabel(f'${pythonRound(app.cash, 2)}', 20, 430, fill = 'white', size = 25, font = 'serif', bold = True, align = 'left')
    drawLabel('NET WORTH', 20, 470, fill = 'white', size = 20, font = 'serif', bold = True, align = 'left')
    drawLabel(f'${getNetWorth(app)}', 20, 500, fill = 'white', size = 25, font = 'serif', bold = True, align = 'left')



runApp(width=1000, height=800)