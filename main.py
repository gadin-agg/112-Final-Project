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


# 04/16/26 - Decided to start coding each individual component in the game, then add features as I go. 




import os
from numpy import size
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

    def __repr__(self):
        return self.ticker

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
    categories = {
        'stock_data' : 'forestGreen',
        'index_data' : 'dodgerBlue',
        'crop_data' : 'coral'}
    
    # Fake names
    app.stockNames = {
    'AAPL':  'Fruit Tech Inc.',
    'AMZN':  'Jungle Prime Delivery',
    'CVX':   'Standard Energy Group',
    'DIS':   'Mouse Kingdom Ent.',
    'GE':    'General Lightning Co.',
    'GOOGL': 'Global Search Corp.',
    'GS':    'Bull & Bear Capital',
    'INTC':  'Micro-Logic Systems',
    'JNJ':   'Band-Aid & Wellness',
    'JPM':   'Heritage Bank & Trust',
    'KO':    'Bubbly Soda Co.',
    'MSFT':  'MicroSystem Software',
    'NFLX':  'Streamline Video',
    'NKE':   'Swift Footwear Group',
    'NVDA':  'Nano-Graphics Processing',
    'SBUX':  'Java Jolt Coffee',
    'TGT':   'Bullseye Retailers',
    'V':     'Swipe-O-Matic Credit',
    'WMT':   'Mega-Mart Supercenters',
    'XOM':   'Titan Oil & Gas'
    }

    # Loading the stock data, picking random things
    app.allS, app.I, app.allC = loadAssets(categories)

    # timing constants
    app.indexRelease = 6
    app.stockRelease = 12
    app.cropRelease = 18
    app.goldRelease = 24

    restartApp(app)

    print(f"Loaded {len(app.stocks)} stocks, {len(app.index)} index, and {len(app.crops)} crop")

def restartApp(app):
    # Basic stuff
    app.cash = 4000
    app.monthIndex = 0
    app.stepsPerSecond = 1
    app.gameOver = False
    app.paused = False

    # released constants
    app.indexReleased = False
    app.stockReleased = False
    app.cropReleased = False
    app.goldReleased = False

    # picking random sample
    app.stocks = sample(app.allS, 5)
    app.index = app.I
    app.crops = sample(app.allC, 1)

    # reseting ownership
    for asset in app.allS + app.I + app.allC:
        asset.sharesOwned = 0

def onStep(app):
    takeStep(app)
    
def takeStep(app):
    if not app.paused:
        app.monthIndex += 1
    if app.monthIndex == app.indexRelease:
        app.indexReleased = True
    if app.monthIndex == app.stockRelease:
        app.stockReleased = True
    if app.monthIndex == app.cropRelease:
        app.cropReleased = True
    if app.monthIndex == app.goldRelease:
        app.goldReleased = True

def onKeyPress(app, key):
    if key == 'r':
        restartApp(app)
    elif key == 'p':
        app.paused = not app.paused
    elif key == 's':
        takeStep(app)

def drawYearBar(app):
    width = 160
    height = 20
    x = 20
    y = 50
    drawRect(x, y, width, height, fill = None, border = 'beige', borderWidth = 1)

    segmentWidth = width / 12
    month = app.monthIndex % 12

    for i in range(month + 1):
        drawRect(x + (i * segmentWidth + 2), y + 2, segmentWidth - 4, height - 4, fill='gold')

def drawTile(app, x, y, width, height, assetName, size):
    color = 'gray' if assetName == 'LOCKED' else 'oldLace'
    drawRect(x + 7, y + 7, width, height, fill = rgb(75, 75, 75))
    drawRect(x, y, width, height, fill = color)
    drawRect(x + 7, y + 7, width - 10, height - 10, fill = None, border = 'black', borderWidth = 3)
    drawLabel(assetName, x + width/2, y + 30, fill = 'black', size = size, font = 'serif', bold = True, align = 'center')

def drawAssetTiles(app):
    stockTileWidth = 216
    stockTileHeight = 240
    otherTileWidth = 570
    otherTileHeight = 240

    drawTile(app, 220, 20, otherTileWidth, otherTileHeight, 'Savings Account', 20)

    title = 'Index Fund' if app.indexReleased else 'LOCKED'
    size = 20 if app.indexReleased else 15
    drawTile(app, 220 + otherTileWidth + 20, 20, otherTileWidth, otherTileHeight, title, size)

    for i in range(5):
        title = app.stockNames[app.stocks[i].ticker] if app.stockReleased else 'LOCKED'
        drawTile(app, 220 + (i * (stockTileWidth + 20)), 280, stockTileWidth, stockTileHeight, title, 15)
    
    title = f'{app.crops[0].ticker}' if app.cropReleased else 'LOCKED'
    size = 20 if app.cropReleased else 15
    drawTile(app, 220, 540, otherTileWidth, otherTileHeight, f'{app.crops[0].ticker}', 20)

    title = 'Gold' if app.goldReleased else 'LOCKED'
    size = 20 if app.goldReleased else 15
    drawTile(app, 220 + otherTileWidth + 20, 540, otherTileWidth, otherTileHeight, title, size)



def drawSideBar(app):
    # Drawing the side bar
    drawRect(0, 0, 200, app.height, fill= rgb(65, 70, 57))

    drawImage('piggy-bank.png', 10, 80, width = 180, height = 180 * 0.54585798816)
    drawLabel(f'YEAR {app.monthIndex // 12} OF 10', 20, 30, fill = 'beige', size = 20, font = 'serif', bold = True, align = 'left')
    drawLabel('POCKET CASH', 20, 400, fill = 'beige', size = 12, font = 'serif', bold = True, align = 'left')
    drawLabel(f'${pythonRound(float(app.cash), 2)}', 20, 420, fill = 'beige', size = 25, font = 'serif', bold = True, align = 'left')
    drawLabel('NET WORTH', 20, 450, fill = 'beige', size = 12, font = 'serif', bold = True, align = 'left')
    drawLabel(f'${getNetWorth(app)}', 20, 470, fill = 'beige', size = 25, font = 'serif', bold = True, align = 'left')

    drawYearBar(app)

def redrawAll(app):
    drawSideBar(app)
    drawAssetTiles(app)

    # drawLabel(f"Loaded {app.stocks} stocks, {app.index} index, and {app.crops} crop", 20, 550, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')


runApp(width=1400, height=800)