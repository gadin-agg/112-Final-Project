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
    def __init__(self, ticker, priceData, color, isFractional = False):
        self.ticker = ticker
        self.priceData = priceData
        self.color = color
        self.sharesOwned = 0.0
        self.multiplier = 0
        self.isFractional = isFractional

    def __repr__(self):
        return self.ticker

    # makes sure the game isnt over / out of bounds
    def getCurrentPrice(self, monthIndex):
        if monthIndex < len(self.priceData):
            return self.priceData[monthIndex]
        return self.priceData[-1]

    def getValue(self, monthIndex):
        return self.sharesOwned * self.getCurrentPrice(monthIndex)

class Button:
    def __init__(self, x, y, w, h, label, asset, action, value = None):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.text = label
        self.asset = asset
        self.action = action
        self.value = value

    def draw(self, app):

        isHighlighted = False
        if self.action == 'setMultiplier':
            if self.asset == 'savings':
                isHighlighted = (app.savingsMultiplier == self.value)
            else:
                isHighlighted = (self.asset.multiplier == self.value)

        color = 'gold' if isHighlighted else 'oldLace'

        if self.value == 'MAX' and self.asset in app.stocks:
            size = 8
        elif self.value == None:
            size = 20
        else:
            size = 12
        
        drawRect(self.x + 2, self.y + 2, self.width, self.height, fill = rgb(75, 75, 75))
        drawRect(self.x, self.y, self.width, self.height, fill = color, border = 'black', borderWidth = 2)
        drawLabel(self.text, self.x + self.width/2, self.y + self.height/2, fill = 'black', size = size, font = 'serif', bold = True, align = 'center')

    def isClicked(self, mouseX, mouseY):
        return (self.x <= mouseX <= self.x + self.width and self.y <= mouseY <= self.y + self.height)

def loadAssets(categories):
    allStocks = []
    index = []
    allCrops = []
    gold = []

    for folder in categories:
        color = categories[folder]
        for file in os.listdir(folder):
            if file.endswith('.csv'):
                path = os.path.join(folder, file)
                ticker = file.replace('.csv', '')
                prices = getCleanData(path)
                if folder == 'stock_data':
                    asset = Asset(ticker, prices, color)
                    allStocks.append(asset)
                elif folder == 'index_data':
                    asset = Asset(ticker, prices, color, isFractional = True)
                    index.append(asset)
                elif folder == 'crop_data':
                    asset = Asset(ticker, prices, color)
                    allCrops.append(asset)
                else:
                    asset = Asset(ticker, prices, color, isFractional = True)
                    gold.append(asset)

    return allStocks, index, allCrops, gold

def onAppStart(app):
    categories = {
        'stock_data' : 'forestGreen',
        'index_data' : 'dodgerBlue',
        'crop_data' : 'coral',
        'gold_data' : 'gold'}
    
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
    app.allS, app.index, app.allC, app.gold = loadAssets(categories)
    print(app.gold)

    # timing constants
    app.indexRelease = 6
    app.stockRelease = 12
    app.cropRelease = 18
    app.goldRelease = 24

    app.savingsAPY = 0.01
    
    app.titleScreenImage = 'opening-screen.png'
    app.tutorialScreenImage = 'tutorial-background.png'
    app.tutorialImages = [None, 'progress-bar.png', 'pocket-cash.png', 'opportunities.png', 'lesson.png', None]
    app.totalSlides = 5
    app.titleButton = Button(app.width//2 - 100, app.height//2 + 100, 200, 50, 'Start Tutorial', None, 'startTutorial')
    app.tutorialButtons = [Button(app.width//2 - 240, app.height//2, 40, 40, '<', None, 'prevSlide'), 
                           Button(app.width//2 + 200, app.height//2, 40, 40, '>', None, 'nextSlide')]
    app.startButton = Button(app.width//2 - 100, app.height//2 - 200, 200, 50, 'Start Game', None, 'startGame')
    

    restartApp(app)

    print(f"Loaded {len(app.stocks)} stocks, {len(app.index)} index, and {len(app.crops)} crop")

def restartApp(app):
    # Basic stuff
    app.cash = 4000
    app.savingsBalance = 0
    app.stepCounter = 0
    app.monthIndex = 0
    app.stepsPerSecond = 1
    app.gameOver = False
    app.paused = True
    app.screen = 'title'

    # released constants
    app.indexReleased = False
    app.stockReleased = False
    app.cropReleased = False
    app.goldReleased = False

    # picking random sample (gold and index only have 1, so we dont need to sample)
    app.stocks = sample(app.allS, 5)
    app.crops = sample(app.allC, 1)
    app.savingsMultiplier = 0

    app.tutorialSlide = 0

    initializeButtons(app)

    # reseting ownership
    for asset in app.allS + app.index + app.allC:
        asset.sharesOwned = 0

def initializeButtons(app):
    app.buttons = []

    # --- Savings Buttons --- 
    createMultiplierRow(app, 'savings', 427.5, 210, [500, 1000, 5000, 'MAX'])
    app.buttons.append(Button(250, 210, 80, 35, 'Deposit', 'savings', 'deposit', 100))
    app.buttons.append(Button(685, 210, 80, 35, 'Withdraw', 'savings', 'withdraw', 100))

    # --- Index Buttons ---
    createMultiplierRow(app, app.index[0], 1022.5, 210, [500, 1000, 5000, 'MAX'])
    app.buttons.append(Button(840, 210, 80, 35, 'Buy', app.index[0], 'buy', 100))
    app.buttons.append(Button(1270, 210, 80, 35, 'Sell', app.index[0], 'sell', 100))

    # --- Stock Buttons ---
    for i in range(len(app.stocks)):
        stock = app.stocks[i]
        x, y = 240 + i * (216 + 20), 480
        x1 = 270.5 + i * (216 + 20)
        createMultiplierRow(app, stock, x1, y - 30, [1, 10, 25, 'MAX'])
        app.buttons.append(Button(x, y, 40, 25, 'Buy', stock, 'buy', 100))
        app.buttons.append(Button(x + 140, y, 40, 25, 'Sell', stock, 'sell', 100))

    # --- Crop Buttons ---
    createMultiplierRow(app, app.crops[0], 432.5, 730, [500, 1000, 5000, 'MAX'])
    app.buttons.append(Button(250, 730, 80, 35, 'Buy', app.crops[0], 'buy', 100))
    app.buttons.append(Button(680, 730, 80, 35, 'Sell', app.crops[0], 'sell', 100))

    # --- Gold Buttons ---
    createMultiplierRow(app, app.gold[0], 1022.5, 730, [500, 1000, 5000, 'MAX'])
    app.buttons.append(Button(840, 730, 80, 35, 'Buy', app.gold[0], 'buy', 100))
    app.buttons.append(Button(1270, 730, 80, 35, 'Sell', app.gold[0], 'sell', 100))

def createMultiplierRow(app, asset, x, y, multipliers):
    width = 35 if asset not in app.stocks else 25
    height = 35 if asset not in app.stocks else 25
    gap = 5
    for i in range(len(multipliers)):
        multiplier = multipliers[i]
        label = str(multiplier)
        button = Button(x + i * (width + gap), y, width, height, label, asset, 'setMultiplier', multiplier)
        app.buttons.append(button)

def isReleased(app,asset):
    if asset == 'savings':
        return True
    elif asset in app.index:
        return app.indexReleased
    elif asset in app.stocks:
        return app.stockReleased
    elif asset in app.crops:
        return app.cropReleased
    else:
        return app.goldReleased

def onStep(app):
    takeStep(app)

def takeStep(app):
    oldMonth = app.monthIndex
    if not app.paused:
        app.stepCounter += 1
    app.monthIndex = app.stepCounter // 3
    if app.monthIndex == app.indexRelease:
        app.indexReleased = True
    if app.monthIndex == app.stockRelease:
        app.stockReleased = True
    if app.monthIndex == app.cropRelease:
        app.cropReleased = True
    if app.monthIndex == app.goldRelease:
        app.goldReleased = True

    if app.monthIndex > oldMonth:
        adjustSavingsBalance(app)
        if app.monthIndex > 0 and app.monthIndex % 6 == 0:
            app.cash += 4000
    
    if app.monthIndex >= 120:
        app.gameOver = True
        app.paused = True
        app.screen = 'gameOver'

def onKeyPress(app, key):
    if key == 'r':
        restartApp(app)
    elif key == 'p':
        app.paused = not app.paused
    elif key == 's':
        takeStep(app)
    elif key == 'b':
        app.stockReleased = True
        app.indexReleased = True
        app.cropReleased = True
        app.goldReleased = True

def onMousePress(app, mouseX, mouseY):
    if app.screen == 'title':
        if app.titleButton.isClicked(mouseX, mouseY):
            app.screen = 'tutorial'
    
    elif app.screen == 'tutorial':
        for button in app.tutorialButtons:
            if button.isClicked(mouseX, mouseY):
                if button.action == 'prevSlide' and app.tutorialSlide > 0:
                    app.tutorialSlide -= 1
                elif button.action == 'nextSlide' and app.tutorialSlide < app.totalSlides:
                    app.tutorialSlide += 1
        if app.startButton.isClicked(mouseX, mouseY):
            app.screen = 'main'
            app.paused = False

    elif app.screen == 'main':
        for button in app.buttons:
            if button.isClicked(mouseX, mouseY):
                if button.action == 'setMultiplier':
                    if button.asset == 'savings':
                        app.savingsMultiplier = button.value
                    else:
                        button.asset.multiplier = button.value
                elif button.action in ['buy', 'sell']:
                    executeTrade(app, button.action, button.asset)
                elif button.action in ['deposit','withdraw']:
                    handleSavings(app, button.action)


# --------- SAVINGS ACCOUNT FUNCTIONS ----------

def adjustSavingsBalance(app):
    app.savingsBalance *= (1 + app.savingsAPY / 12)


# --------- OTHER FUNCTIONS ----------

def executeTrade(app, action, asset):
    price = asset.getCurrentPrice(app.monthIndex)
    if action == 'buy':
        if asset.multiplier == 'MAX':
            cashToSpend = app.cash
        else:
            cashToSpend = asset.multiplier if asset.isFractional else asset.multiplier * price
        
        if asset.isFractional:
            sharesToBuy = cashToSpend / price
        else:
            sharesToBuy = cashToSpend // price

        if app.cash >= sharesToBuy * price and sharesToBuy > 0:
            app.cash -= sharesToBuy * price
            asset.sharesOwned += sharesToBuy
    
    elif action == 'sell':
        if asset.multiplier == 'MAX':
            sharesToSell = asset.sharesOwned
        else:
            if asset.isFractional:
                sharesToSell = min(asset.multiplier / price, asset.sharesOwned)
            else:
                sharesToSell = asset.multiplier
        
        if asset.sharesOwned >= sharesToSell and sharesToSell > 0:
            app.cash += sharesToSell * price
            asset.sharesOwned -= sharesToSell

def handleSavings(app, action):
    if app.savingsMultiplier == 'MAX':
        amount = app.cash if action == 'deposit' else app.savingsBalance
    else:
        amount = app.savingsMultiplier
    
    if action == 'deposit' and app.cash >= amount:
        app.cash -= amount
        app.savingsBalance += amount
    elif action == 'withdraw' and app.savingsBalance >= amount:
        app.cash += amount
        app.savingsBalance -= amount

def getNetWorth(app):
    total = app.cash
    for stock in app.stocks:
        total += stock.getValue(app.monthIndex)
    for crop in app.crops:
        total += crop.getValue(app.monthIndex)
    for index in app.index:
        total += index.getValue(app.monthIndex)
    for gold in app.gold:
        total += gold.getValue(app.monthIndex)
    total += app.savingsBalance
    return pythonRound(total, 2)


# --------- DRAWING FUNCTIONS ----------

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

    if not app.paused:
        drawLabel(f'YEAR {app.monthIndex // 12} OF 10', 20, 30, fill = 'beige', size = 20, font = 'serif', bold = True, align = 'left')
    else:
        drawLabel('PAUSED', 20, 30, fill = 'beige', size = 20, font = 'serif', bold = True, align = 'left')

def drawTile(app, x, y, width, height, assetName, size):
    color = 'gray' if assetName == 'LOCKED' else 'oldLace'
    shift = 25 if assetName in app.stockNames.values() else 30
    drawRect(x + 7, y + 7, width, height, fill = rgb(75, 75, 75))
    drawRect(x, y, width, height, fill = color)
    drawRect(x + 7, y + 7, width - 10, height - 10, fill = None, border = 'black', borderWidth = 3)
    drawLabel(assetName, x + width/2, y + shift, fill = 'black', size = size, font = 'serif', bold = True, align = 'center')

def drawAssetTiles(app):
    stockTileWidth = 216
    stockTileHeight = 240
    otherTileWidth = 570
    otherTileHeight = 240

    # Savings account
    drawTile(app, 220, 20, otherTileWidth, otherTileHeight, 'Savings Account', 20)
    drawImage('savings-account.png', 455, 60, width = 100, height = 100 * 0.95588)
    drawLabel(f'Balance', 250, 170, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
    drawLine(250, 190, 250 + otherTileWidth - 60, 190, fill = 'black', dashes = True)
    drawLabel(f'${app.savingsBalance:,.2f}', 250 + otherTileWidth - 150, 170, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')

    # Index fund
    price = app.index[0].getCurrentPrice(app.monthIndex)
    change = (price / app.index[0].getCurrentPrice(app.monthIndex - 1)) - 1 if app.monthIndex > 0 else 0
    changeColor = 'forestGreen' if change > 0 else 'fireBrick' if change < 0 else 'black'
    title = 'Index Fund' if app.indexReleased else 'LOCKED'
    size = 20 if app.indexReleased else 15
    drawTile(app, 220 + otherTileWidth + 20, 20, otherTileWidth, otherTileHeight, title, size)
    if app.indexReleased:
        drawLabel(f'Balance', 840, 170, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
        drawLine(840, 190, 840 + otherTileWidth - 60, 190, fill = 'black', dashes = True)
        drawLabel(f'${app.index[0].getValue(app.monthIndex):,.2f}', 840 + otherTileWidth - 150, 170, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
        drawLabel(f'${price:,.2f}', 912.5, 80, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
        drawLabel(f'{(change * 100):.2f}%', 1227.5, 80, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
        drawGraph(app, 995, 80, 200, 80, app.index[0])

    # Stocks
    for i in range(5):
        price = app.stocks[i].getCurrentPrice(app.monthIndex)
        change = (price / app.stocks[i].getCurrentPrice(app.monthIndex - 1)) - 1 if app.monthIndex > 0 else 0
        changeColor = 'forestGreen' if change > 0 else 'fireBrick' if change < 0 else 'black'
        title = app.stockNames[app.stocks[i].ticker] if app.stockReleased else 'LOCKED'
        drawTile(app, 220 + (i * (stockTileWidth + 20)), 280, stockTileWidth, stockTileHeight, title, 15)
        if app.stockReleased:
            drawLabel(f'${price:,.2f}', 240 + (i * (stockTileWidth + 20)) + 20, 330, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
            drawLabel(f'{(change * 100):.2f}%', 345 + (i * (stockTileWidth + 20)) + 20, 330, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
            drawGraph(app, 240 + (i * (stockTileWidth + 20)) + 20, 370, 140, 60, app.stocks[i])
    # Crops
    price = app.crops[0].getCurrentPrice(app.monthIndex)
    change = (price / app.crops[0].getCurrentPrice(app.monthIndex - 1)) - 1 if app.monthIndex > 0 else 0
    changeColor = 'forestGreen' if change > 0 else 'fireBrick' if change < 0 else 'black'
    title = f'{app.crops[0].ticker}' if app.cropReleased else 'LOCKED'
    size = 20 if app.cropReleased else 15
    drawTile(app, 220, 540, otherTileWidth, otherTileHeight, title, size)
    if app.cropReleased:
        drawLabel(f'Balance', 250, 690, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
        drawLine(250, 710, 250 + otherTileWidth - 60, 710, fill = 'black', dashes = True)
        drawLabel(f'${app.crops[0].getValue(app.monthIndex):,.2f}', 250 + otherTileWidth - 150, 690, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
        drawLabel(f'${price:,.2f}', 322.5, 600, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
        drawLabel(f'{(change * 100):.2f}%', 637.5, 600, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
        drawGraph(app, 405, 600, 200, 80, app.crops[0])

    # Gold
    price = app.gold[0].getCurrentPrice(app.monthIndex)
    change = (price / app.gold[0].getCurrentPrice(app.monthIndex - 1)) - 1 if app.monthIndex > 0 else 0
    changeColor = 'forestGreen' if change > 0 else 'fireBrick' if change < 0 else 'black'
    title = 'Gold' if app.goldReleased else 'LOCKED'
    size = 20 if app.goldReleased else 15
    drawTile(app, 220 + otherTileWidth + 20, 540, otherTileWidth, otherTileHeight, title, size)
    if app.goldReleased:
        drawLabel(f'Balance', 840, 690, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
        drawLine(840, 710, 840 + otherTileWidth - 60, 710, fill = 'black', dashes = True)
        drawLabel(f'${app.gold[0].getValue(app.monthIndex):,.2f}', 840 + otherTileWidth - 150, 690, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
        drawLabel(f'${price:,.2f}', 912.5, 600, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
        drawLabel(f'{(change * 100):.2f}%', 1227.5, 600, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
        drawGraph(app, 995, 600, 200, 80, app.gold[0])

def drawSideBar(app):
    # Drawing the side bar
    drawRect(0, 0, 200, app.height, fill= rgb(65, 70, 57))

    drawImage('piggy-bank.png', 10, 80, width = 180, height = 180 * 0.54585798816)
    drawLabel('POCKET CASH', 20, 400, fill = 'beige', size = 12, font = 'serif', bold = True, align = 'left')
    drawLabel(f'${app.cash:,.2f}', 20, 420, fill = 'beige', size = 25, font = 'serif', bold = True, align = 'left')
    drawLabel('NET WORTH', 20, 450, fill = 'beige', size = 12, font = 'serif', bold = True, align = 'left')
    drawLabel(f'${getNetWorth(app):,.2f}', 20, 470, fill = 'beige', size = 25, font = 'serif', bold = True, align = 'left')

    drawYearBar(app)

def drawButtons(app):
    if app.screen == 'title':
        app.titleButton.draw(app)
    elif app.screen == 'tutorial':
        if 0 < app.tutorialSlide < app.totalSlides:
            app.tutorialButtons[0].draw(app)
            app.tutorialButtons[1].draw(app)
        elif app.tutorialSlide == 0:
            app.tutorialButtons[1].draw(app)
        elif app.tutorialSlide == app.totalSlides: 
            app.tutorialButtons[0].draw(app)
            app.startButton.draw(app)
    else:
        for button in app.buttons:
            if isReleased(app, button.asset):
                button.draw(app)

def drawGraph(app, x, y, width, height, asset):
    # get the data
    startMonth = max(0, app.monthIndex - 10)
    dataSlice = asset.priceData[startMonth:app.monthIndex + 1]
    if len(dataSlice) < 2: return

    # scaling the graph
    minPrice, maxPrice = min(dataSlice), max(dataSlice)
    priceRange = maxPrice - minPrice if maxPrice != minPrice else 1
    stepX = width / 10

    # color logic
    if asset.priceData[app.monthIndex] >= asset.priceData[app.monthIndex - 1]:
        color = 'forestGreen'
    else:
        color = 'fireBrick'

    points = []

    for i in range(len(dataSlice)):
        currX = x + (i * stepX)
        currY = y + height - ((dataSlice[i] - minPrice) / priceRange * height)
        points.extend([currX, currY])

    # close the polygon by going to the bottom right and then back to the start
    points.extend([x + (len(dataSlice)-1) * stepX, y + height])
    points.extend([x, y + height])

    # shaded area of the graph
    drawPolygon(*points, fill=color, opacity=20)

def drawTutorialCircles(app):
    circleSize = 20
    gap = 10
    totalWidth = (circleSize * app.totalSlides + 1) + (gap * (app.totalSlides))
    startX = (app.width - totalWidth) // 2

    for i in range(app.totalSlides + 1):
        fillColor = 'gold' if i == app.tutorialSlide else None
        drawCircle(startX + i * (circleSize + gap) + circleSize/2, app.height//2 + 150, circleSize/2, fill = fillColor, border = 'beige')

def drawTitleScreen(app):
    drawImage(app.titleScreenImage, 0, 0, width = app.width, height = app.height)
    drawLabel('By Gadin Aggarwal', app.width//2, app.height//2, fill = 'beige', size = 15, font = 'serif', bold = True, align = 'center')
    drawButtons(app)

def drawTutorialScreen(app):
    drawImage(app.tutorialScreenImage, 0, 0, width = app.width, height = app.height)

    if app.tutorialSlide == 0:
        text = ['Welcome to the', 'Financial Literacy Game!', 'In this game, you will learn how to manage your',
                'money and make smart investments over a simulated', '10-year period. Use the buttons to buy and sell',
                'assets, and try to grow your net worth as much as possible!']
        for i in range(2):
            drawLabel(text[i], app.width//2, app.height//2 - 200 + (i * 35), fill = 'beige', size = 25, font = 'serif', bold = True, align = 'center')
        for i in range(2, len(text)):
            drawLabel(text[i], app.width//2, app.height//2 - 120 + ((i-2) * 25), fill = 'beige', size = 20, font = 'serif', align = 'center')

    elif app.tutorialSlide == 1:
        drawImage(app.tutorialImages[1], app.width//2 - 150, app.height//2 - 200, width = 300, height = 300 * 0.36666)
        text = ['The yellow bar at the top shows the current', 
                ' month and year. Each segment represents one',
                'month, and when a new segment is filled in, a', 
                'new month has started. The game lasts for 10',
                'years, or 120 months.']
        for i in range(len(text)):
            drawLabel(text[i], app.width//2, app.height//2 - 20 + (i * 25), fill = 'beige', size = 20, font = 'serif', align = 'center')

    elif app.tutorialSlide == 2:
        drawImage(app.tutorialImages[2], app.width//2 - 150, app.height//2 - 200, width = 300, height = 300 * 0.41525)
        text = ['This is your pocket cash. This is the money',
                'you have on hand to make purchases and cover',
                'expenses. Your net worth is the total value of',
                'all your assets (stocks, index fund, crops, gold,',
                'and savings) plus your pocket cash. Try to maximize',
                'your net worth by the end of the game!']
        for i in range(len(text)):
            drawLabel(text[i], app.width//2, app.height//2 - 40 + (i * 25), fill = 'beige', size = 20, font = 'serif', align = 'center')

    elif app.tutorialSlide == 3:
        drawImage(app.tutorialImages[3], app.width//2 - 150, app.height//2 - 200, width = 300, height = 300 * 0.65961)
        text = ['As the game progresses, you will unlock',
                'different assets to invest in. Each asset',
                'has its own price that changes every month.',
                'The graph shows the recent price history',
                'of the asset, and the current price and monthly',
                'change are shown above it.']
        for i in range(len(text)):
            drawLabel(text[i], app.width//2, app.height//2 + 20 + (i * 20), fill = 'beige', size = 18, font = 'serif', align = 'center')
    
    elif app.tutorialSlide == 4:
        drawImage(app.tutorialImages[4], app.width//2 - 150, app.height//2 - 200, width = 300, height = 300 * 0.64625)
        text = ['As you unlock new assets, a lesson will',
                'pop up to teach you about that asset and',
                'how to invest in it wisely. Pay attention',
                'to these lessons, as they will give you',
                'tips on how to maximize your net worth',
                'by the end of the game!']
        for i in range(len(text)):
            drawLabel(text[i], app.width//2, app.height//2 + 15 + (i * 20), fill = 'beige', size = 18, font = 'serif', align = 'center')

    elif app.tutorialSlide == app.totalSlides:
        text = ["'Now that you know the basics, it's time to'",
                'start investing! Click the button below to',
                'begin your financial journey. Good luck, and',
                'have fun playing the game!', '\n',
                'Note: at any point, you can press "P" to pause',
                'the game and "R" to restart the game.']
        for i in range(len(text)):
            drawLabel(text[i], app.width//2, app.height//2 - 75 + (i * 25), fill = 'beige', size = 20, font = 'serif', align = 'center')

    drawTutorialCircles(app)
    drawButtons(app)

def redrawAll(app):
    drawButtons(app)
    if app.screen == 'title':
        drawTitleScreen(app)
    elif app.screen == 'tutorial':
        drawTutorialScreen(app)
        
    else:
        drawSideBar(app)
        drawAssetTiles(app)
        drawButtons(app)

runApp(width=1400, height=800)