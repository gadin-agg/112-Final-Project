'''
Features List:
1. Smooth UI: Using linear interpolation to make the numbers have a 'scrolling' effect.
2. Dynamic Graphing: Each asset has its own graph that is scaled and uses real data from 2016-2026.
3. Graphing Hover Feature: You can hover over the graphs to see price history.
4. Monte Carlo Simulation: You can run a Monte Carlo Simulation of your portfolio (with an animation)
to see future potential portfolio value.
5. Fade Transitions: Nice UI feature for between screens in the game.
6. UI Features: Drop shadows, clean aesthetic, etc.
7. Real Data Extraction: real data from 2016-2026 is being used.

Grading Shortcuts:
"P" to Pause/Unpause
"R" to Restart
"S" to skip one month ahead
"B" to skip to main page and unlock all assets (bypass tutorial/waiting to unlock assets)
"M" to skip to end screen
'''

import os
import pandas as pd
from random import sample, normalvariate
import statistics
from cmu_graphics import *

# The function below was written mostly by AI.
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
    def __init__(self, ticker, priceData, isFractional = False):
        self.ticker = ticker
        self.priceData = priceData
        self.sharesOwned = 0.0
        self.multiplier = 0
        self.isFractional = isFractional
        self.displayedPrice = self.priceData[0]
        self.displayedValue = 0
        self.displayedShares = 0
        
        # monte carlo
        self.returns = self.calculateReturns()
        self.volatility = statistics.stdev(self.returns) if len(self.returns) > 1 else 0.05
        self.meanReturn = statistics.mean(self.returns) if len(self.returns) > 1 else 0

    def __repr__(self):
        return self.ticker
    
    def updateDisplayedValue(self, app):
        targetPrice = self.getCurrentPrice(app.monthIndex)
        priceDiff = targetPrice - self.displayedPrice
        self.displayedPrice += priceDiff * app.scrollingSpeed

        targetValue = self.sharesOwned * targetPrice
        valueDiff = targetValue - self.displayedValue
        self.displayedValue += valueDiff * app.scrollingSpeed

        shareDiff = self.sharesOwned - self.displayedShares
        self.displayedShares += shareDiff * app.scrollingSpeed

    def getCurrentPrice(self, monthIndex):
        if monthIndex < len(self.priceData):
            return self.priceData[monthIndex]
        return self.priceData[-1]

    def getValue(self, monthIndex):
        return self.sharesOwned * self.getCurrentPrice(monthIndex)
    
    def getSmoothValue(self):
        return self.displayedValue

    def calculateReturns(self):
        returns = []
        for i in range(1, len(self.priceData)):
            prev = self.priceData[i-1]
            curr = self.priceData[i]
            returns.append((curr - prev) / prev)
        return returns

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
            size = 16
        else:
            size = 12
        
        drawRect(self.x + 2, self.y + 2, self.width, self.height, fill = rgb(75, 75, 75))
        drawRect(self.x, self.y, self.width, self.height, fill = color, border = 'black', borderWidth = 2)
        drawLabel(self.text, self.x + self.width/2, self.y + self.height/2, fill = 'black', size = size, font = 'serif', bold = True)

    def isClicked(self, mouseX, mouseY):
        return (self.x <= mouseX <= self.x + self.width and self.y <= mouseY <= self.y + self.height)

class Graph:
    def __init__(self, x, y, width, height, asset):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.asset = asset
        self.fillOpacity = 30
        
        # Hover state
        self.isHovering = False
        self.hoverX = 0
        self.hoverY = 0
        self.hoverValue = 0

    def draw(self, app):
        # get the data
        startMonth = max(0, app.monthIndex - 10)
        dataSlice = self.asset.priceData[startMonth:app.monthIndex + 1]
        if len(dataSlice) < 2: return

        # scaling the graph
        minPrice, maxPrice = min(dataSlice), max(dataSlice)
        priceRange = maxPrice - minPrice if maxPrice != minPrice else 1
        stepX = self.width / 10

        # color logic
        if self.asset.priceData[app.monthIndex] >= self.asset.priceData[app.monthIndex - 1]:
            color = 'forestGreen'
        else:
            color = 'fireBrick'

        polygonPoints = []
        linePoints = []

        for i in range(len(dataSlice)):
            currX = self.x + (i * stepX)
            currY = self.y + self.height - ((dataSlice[i] - minPrice) / priceRange * self.height)
            polygonPoints.extend([currX, currY])
            linePoints.append((currX, currY))

        # close the polygon by going to the bottom right and then back to the start
        polygonPoints.extend([self.x + (len(dataSlice)-1) * stepX, self.y + self.height]) # bottom right
        polygonPoints.extend([self.x, self.y + self.height]) # bottom left

        # shaded area of the graph
        drawPolygon(*polygonPoints, fill = color, opacity = self.fillOpacity)

        # draw the line on top
        for i in range(len(linePoints) - 1):
            drawLine(linePoints[i][0], linePoints[i][1], linePoints[i+1][0], linePoints[i+1][1], fill = color, lineWidth = 2)

        if self.isHovering:
            drawCircle(self.hoverX, self.hoverY, 4, fill = 'white', border = 'black', borderWidth = 1)
            drawRect(self.hoverX - 35, self.hoverY - 35, 70, 20, fill = 'black', opacity = 75)
            drawLabel(f"${self.hoverValue:,.2f}", self.hoverX, self.hoverY - 25, fill = 'white', size = 11, bold = True)

    def updateHover(self, mouseX, mouseY, app):
        # check if in box
        if not (self.x <= mouseX <= self.x + self.width and self.y <= mouseY <= self.y + self.height):
            self.isHovering = False
            return False
        
        startMonth = max(0, app.monthIndex - 10)
        dataSlice = self.asset.priceData[startMonth:app.monthIndex + 1]
        stepX = self.width / 10

        idx = int(pythonRound((mouseX - self.x) / stepX))
        idx = max(0, min(idx, len(dataSlice) - 1))

        minP, maxP = min(dataSlice), max(dataSlice)
        priceRange = maxP - minP if maxP != minP else 1
        lineY = (self.y + self.height) - ((dataSlice[idx] - minP) / priceRange * self.height)

        if lineY <= mouseY <= (self.y + self.height):
            self.isHovering = True
            self.hoverValue = dataSlice[idx]
            self.hoverX = self.x + (idx * stepX)
            self.hoverY = lineY
            return True
        else:
            self.isHovering = False
            return False
    
# The function below was written mostly by AI
def loadAssets(folders):
    allStocks = []
    index = []
    allCrops = []
    gold = []

    for folder in folders:
        for file in os.listdir(folder):
            if file.endswith('.csv'):
                path = os.path.join(folder, file)
                ticker = file.replace('.csv', '')
                prices = getCleanData(path)
                if folder == 'stock_data':
                    asset = Asset(ticker, prices)
                    allStocks.append(asset)
                elif folder == 'index_data':
                    asset = Asset(ticker, prices, isFractional = True)
                    index.append(asset)
                elif folder == 'crop_data':
                    asset = Asset(ticker, prices)
                    allCrops.append(asset)
                else:
                    asset = Asset(ticker, prices, isFractional = True)
                    gold.append(asset)

    return allStocks, index, allCrops, gold

def onAppStart(app):
    folders = ['index_data', 'stock_data', 'crop_data', 'gold_data']
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
    app.allS, app.index, app.allC, app.gold = loadAssets(folders)

    app.scrollingSpeed = 0.25

    # timing constants
    app.indexRelease = 6
    app.stockRelease = 12
    app.cropRelease = 18
    app.goldRelease = 24

    app.savingsAPY = 0.01

    app.titleScreenImage = 'opening-screen.png'
    app.tutorialScreenImage = 'tutorial-background.png'
    app.tutorialImages = [None, 'progress-bar.png', 'pocket-cash.png', 'opportunities.png', 'portfolio-simulation.png', None]
    app.totalSlides = 5
    app.simulationEnabled = False

    restartApp(app)

    print(f"Loaded {len(app.stocks)} stocks, {len(app.index)} index, and {len(app.crops)} crop")

def restartApp(app):
    # Basic stuff
    app.barWidth = 0
    app.cash = 4000
    app.displayedCash = 4000
    app.displayedNetWorth = 4000
    app.savingsBalance = 0
    app.displayedSavings = 0
    app.stepCounter = 0
    app.monthIndex = 0
    app.stepsPerSecond = 30
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

    app.fadeOpacity = 0
    app.fadeDirection = 0
    app.nextScreen = None

    app.lastSimMonth = -1
    app.latestSimPaths = []

    app.titleButton = Button(app.width//2 - 100, app.height//2 + 100, 200, 50, 'Start Tutorial', None, 'startTutorial')
    app.tutorialButtons = [Button(app.width//2 - 240, app.height//2, 40, 40, '<', None, 'prevSlide'), 
                           Button(app.width//2 + 200, app.height//2, 40, 40, '>', None, 'nextSlide')]
    app.startButton = Button(app.width//2 - 100, app.height//2 - 200, 200, 50, 'Start Game', None, 'startGame')
    app.simulationButton = Button(5, 730, 190, 50, 'Run Portfolio Simulation', None, 'runSim')

    initializeButtons(app)
    initializeGraphs(app)

    # reseting ownership
    for asset in app.allS + app.index + app.allC:
        asset.sharesOwned = 0

def initializeButtons(app):
    app.buttons = []

    # savings buttons
    createMultiplierRow(app, 'savings', 427.5, 210, [500, 1000, 5000, 'MAX'])
    app.buttons.append(Button(250, 210, 80, 35, 'Deposit', 'savings', 'deposit', 100))
    app.buttons.append(Button(685, 210, 80, 35, 'Withdraw', 'savings', 'withdraw', 100))

    # index buttons
    createMultiplierRow(app, app.index[0], 1022.5, 210, [500, 1000, 5000, 'MAX'])
    app.buttons.append(Button(840, 210, 80, 35, 'Buy', app.index[0], 'buy', 100))
    app.buttons.append(Button(1270, 210, 80, 35, 'Sell', app.index[0], 'sell', 100))

    # stock buttons
    for i in range(len(app.stocks)):
        stock = app.stocks[i]
        x, y = 240 + i * (216 + 20), 480
        x1 = 270.5 + i * (216 + 20)
        createMultiplierRow(app, stock, x1, y - 30, [1, 10, 25, 'MAX'])
        app.buttons.append(Button(x, y, 40, 25, 'Buy', stock, 'buy', 100))
        app.buttons.append(Button(x + 140, y, 40, 25, 'Sell', stock, 'sell', 100))

    # crop buttons
    createMultiplierRow(app, app.crops[0], 432.5, 730, [500, 1000, 5000, 'MAX'])
    app.buttons.append(Button(250, 730, 80, 35, 'Buy', app.crops[0], 'buy', 100))
    app.buttons.append(Button(680, 730, 80, 35, 'Sell', app.crops[0], 'sell', 100))

    # gold buttons
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

def initializeGraphs(app):
    app.graphs = []

    # index
    app.graphs.append(Graph(995, 80, 200, 80, app.index[0]))
    
    # stocks
    for i in range(5):
        x = 240 + (i * (216 + 20)) + 20
        app.graphs.append(Graph(x, 380, 140, 60, app.stocks[i]))
        
    # crops, gold
    app.graphs.append(Graph(405, 600, 200, 80, app.crops[0]))
    app.graphs.append(Graph(995, 600, 200, 80, app.gold[0]))

def isReleased(app, asset):
    if asset == 'savings': return True
    if asset in app.index: return app.indexReleased
    if asset in app.stocks: return app.stockReleased
    if asset in app.crops: return app.cropReleased
    return app.goldReleased

# ---- STEP FUNCTIONS ----

def onStep(app):
    takeStep(app)

def handleEndgameLogic(app):
    if app.monthIndex >= 120 and app.screen == 'main' and app.fadeDirection == 0:
        app.nextScreen = 'gameOver'
        app.fadeDirection = 1
        app.paused = True

def adjustOnStep(app):
    if not app.paused:
        app.stepCounter += 1
        stepsInYear = 720
        maxWidth = 156
        currentYearSteps = app.stepCounter % stepsInYear
        app.barWidth = (currentYearSteps / stepsInYear) * maxWidth
    app.monthIndex = app.stepCounter // 60

def fadeTransition(app):
    if app.fadeDirection == 1:
        app.fadeOpacity += 5
        if app.fadeOpacity >= 100:
            app.fadeOpacity = 100
            app.screen = app.nextScreen
            app.fadeDirection = -1
        
    elif app.fadeDirection == -1:
        app.fadeOpacity -= 5
        if app.fadeOpacity <= 0:
            app.fadeOpacity = 0
            app.fadeDirection = 0

def releaseAssets(app):
    if app.monthIndex == app.indexRelease: app.indexReleased = True
    if app.monthIndex == app.stockRelease: app.stockReleased = True
    if app.monthIndex == app.cropRelease: app.cropReleased = True
    if app.monthIndex == app.goldRelease: app.goldReleased = True

def changeOnMonth(app, oldMonth):
    if app.monthIndex > oldMonth:
        adjustSavingsBalance(app)
        if app.monthIndex > 0 and app.monthIndex % 6 == 0:
            app.cash += 4000

        app.latestSimPaths = runMonteCarloSimulation(app)

def smoothUI(app):
    app.displayedCash = smoothValue(app, app.displayedCash, app.cash)
    app.displayedNetWorth = smoothValue(app, app.displayedNetWorth, getNetWorth(app))
    app.displayedSavings = smoothValue(app, app.displayedSavings, app.savingsBalance)

    for asset in (app.allS + app.index + app.allC + app.gold):
        asset.updateDisplayedValue(app)

def takeStep(app):
    oldMonth = app.monthIndex
    handleEndgameLogic(app)
    adjustOnStep(app)
    fadeTransition(app)
    releaseAssets(app)
    changeOnMonth(app, oldMonth)
    smoothUI(app)
    
# ---- EVENT HANDLERS ----

def onKeyPress(app, key):
    if key == 'r':
        restartApp(app)
    elif key == 'p':
        app.paused = not app.paused
    elif key == 's':
        if app.monthIndex < 120:
            app.stepCounter += 60
            app.barWidth += (156/(60*12)) * 60
    elif key == 'b':
        app.stockReleased = True
        app.indexReleased = True
        app.cropReleased = True
        app.goldReleased = True
        app.screen = 'main'
        app.paused = False
    elif key == 'm':
        app.stepCounter = 60 * 120

def onMouseMove(app, mouseX, mouseY):
    for graph in app.graphs:
        graph.updateHover(mouseX, mouseY, app)
        if graph.updateHover(mouseX, mouseY, app):
            graph.fillOpacity = 60
        else:
            graph.fillOpacity = 30

def onMousePress(app, mouseX, mouseY):
    if app.screen == 'title':
        if app.titleButton.isClicked(mouseX, mouseY):
            app.nextScreen = 'tutorial'
            app.fadeDirection = 1
    
    elif app.screen == 'tutorial':
        for button in app.tutorialButtons:
            if button.isClicked(mouseX, mouseY):
                if button.action == 'prevSlide' and app.tutorialSlide > 0:
                    app.tutorialSlide -= 1
                elif button.action == 'nextSlide' and app.tutorialSlide < app.totalSlides:
                    app.tutorialSlide += 1
        if app.startButton.isClicked(mouseX, mouseY):
            app.nextScreen = 'main'
            app.fadeDirection = 1
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
        if app.simulationButton.isClicked(mouseX, mouseY):
            app.simulationEnabled = not app.simulationEnabled


# --------- SAVINGS ACCOUNT FUNCTIONS ----------

def adjustSavingsBalance(app):
    app.savingsBalance *= (1 + app.savingsAPY / 12)


# --------- OTHER FUNCTIONS ----------

def smoothValue(app, current, target):
    diff = target - current
    return current + (diff * app.scrollingSpeed)

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
            sharesToBuy = (cashToSpend + 0.0001) // price

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
    for asset in (app.stocks + app.crops + app.index + app.gold):
        total += asset.getValue(app.monthIndex)
    total += app.savingsBalance
    return pythonRound(total, 2)

# The function below was written mostly by AI
def runMonteCarloSimulation(app):
    simulations = 100
    projectionMonths = 12
    allSimulationPaths = []
    for i in range(simulations):
        currentPath = [getNetWorth(app)]

        for j in range(projectionMonths):
            simulatedChange = 0
            for asset in (app.stocks + app.index + app.crops + app.gold):
                if asset.sharesOwned > 0:
                    move = normalvariate(asset.meanReturn, asset.volatility)
                    simulatedChange += asset.getValue(app.monthIndex) * move
                
            nextValue = currentPath[-1] + simulatedChange
            currentPath.append(nextValue)

        allSimulationPaths.append(currentPath)

    return allSimulationPaths

# --------- DRAWING FUNCTIONS ----------

def drawYearBar(app):
    width = 160
    height = 20
    x = 20
    y = 50
    monthWidth = width / 12
    drawRect(x, y, width, height, fill = None, border = 'beige', borderWidth = 1)

    for i in range(1, 12):
        lineX = 20 + (i * monthWidth)
        drawLine(lineX, 50, lineX, 70, fill='beige', lineWidth=1, opacity=30)

    if app.barWidth > 0:
        drawRect(x + 2, y + 2, app.barWidth, height - 4, fill = 'gold')

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

def drawSavingsTile(app, otherTileWidth, otherTileHeight):
    # Savings account
    drawTile(app, 220, 20, otherTileWidth, otherTileHeight, 'Savings Account', 20)
    drawImage('savings-account.png', 455, 60, width = 100, height = 100 * 0.95588)
    drawLabel(f'Balance', 250, 170, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
    drawLine(250, 190, 250 + otherTileWidth - 60, 190, fill = 'black', dashes = True)
    drawLabel(f'${app.displayedSavings:,.2f}', 330 + otherTileWidth - 150, 170, fill = 'black', size = 20, font = 'serif', bold = True, align = 'right')

def drawIndexTile(app, otherTileWidth, otherTileHeight):
    # Index fund
    price = app.index[0].displayedPrice
    change = (price / app.index[0].getCurrentPrice(app.monthIndex - 1)) - 1 if app.monthIndex > 0 else 0
    changeColor = 'forestGreen' if change > 0 else 'fireBrick' if change < 0 else 'black'
    title = 'Index Fund' if app.indexReleased else 'LOCKED'
    size = 20 if app.indexReleased else 15
    drawTile(app, 220 + otherTileWidth + 20, 20, otherTileWidth, otherTileHeight, title, size)
    if app.indexReleased:
        drawLabel(f'Balance', 840, 170, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
        drawLine(840, 190, 840 + otherTileWidth - 60, 190, fill = 'black', dashes = True)
        drawLabel(f'${app.index[0].getSmoothValue():,.2f}', 920 + otherTileWidth - 150, 170, fill = 'black', size = 20, font = 'serif', bold = True, align = 'right')
        drawLabel(f'${price:,.2f}', 912.5, 80, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
        drawLabel(f'{(change * 100):.2f}%', 1227.5, 80, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')

def drawStockTiles(app, stockTileWidth, stockTileHeight):
    # Stocks
    for i in range(5):
        price = app.stocks[i].displayedPrice
        change = (price / app.stocks[i].getCurrentPrice(app.monthIndex - 1)) - 1 if app.monthIndex > 0 else 0
        changeColor = 'forestGreen' if change > 0 else 'fireBrick' if change < 0 else 'black'
        title = app.stockNames[app.stocks[i].ticker] if app.stockReleased else 'LOCKED'
        drawTile(app, 220 + (i * (stockTileWidth + 20)), 280, stockTileWidth, stockTileHeight, title, 15)
        if app.stockReleased:
            drawLabel(f'${price:,.2f}', 220 + (i * (stockTileWidth + 20)) + 20, 330, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
            drawLabel(f'{(change * 100):.2f}%', 400 + (i * (stockTileWidth + 20)) + 20, 330, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'right')
            drawLabel(f'Shares: {pythonRound(app.stocks[i].displayedShares)}', 220 + (i * (stockTileWidth + 20)) + 20, 350, fill = 'black', size = 15, font = 'serif', bold = True, align = 'left')
            drawLabel(f'${app.stocks[i].getSmoothValue():,.2f}', 400 + (i * (stockTileWidth + 20)) + 20, 350, fill = 'black', size = 15, font = 'serif', bold = True, align = 'right')

def drawCropTile(app, otherTileWidth, otherTileHeight):
    # Crops
    price = app.crops[0].displayedPrice
    change = (price / app.crops[0].getCurrentPrice(app.monthIndex - 1)) - 1 if app.monthIndex > 0 else 0
    changeColor = 'forestGreen' if change > 0 else 'fireBrick' if change < 0 else 'black'
    title = f'{app.crops[0].ticker}' if app.cropReleased else 'LOCKED'
    size = 20 if app.cropReleased else 15
    drawTile(app, 220, 540, otherTileWidth, otherTileHeight, title, size)
    if app.cropReleased:
        drawLabel(f'Balance', 250, 690, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
        drawLine(250, 710, 250 + otherTileWidth - 60, 710, fill = 'black', dashes = True)
        drawLabel(f'${app.crops[0].getSmoothValue():,.2f}', 330 + otherTileWidth - 150, 690, fill = 'black', size = 20, font = 'serif', bold = True, align = 'right')
        drawLabel(f'${price:,.2f}', 322.5, 600, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
        drawLabel(f'{(change * 100):.2f}%', 637.5, 600, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')

def drawGoldTile(app, otherTileWidth, otherTileHeight):
    # Gold
    price = app.gold[0].displayedPrice
    change = (price / app.gold[0].getCurrentPrice(app.monthIndex - 1)) - 1 if app.monthIndex > 0 else 0
    changeColor = 'forestGreen' if change > 0 else 'fireBrick' if change < 0 else 'black'
    title = 'Gold' if app.goldReleased else 'LOCKED'
    size = 20 if app.goldReleased else 15
    drawTile(app, 220 + otherTileWidth + 20, 540, otherTileWidth, otherTileHeight, title, size)
    if app.goldReleased:
        drawLabel(f'Balance', 840, 690, fill = 'black', size = 20, font = 'serif', bold = True, align = 'left')
        drawLine(840, 710, 840 + otherTileWidth - 60, 710, fill = 'black', dashes = True)
        drawLabel(f'${app.gold[0].getSmoothValue():,.2f}', 920 + otherTileWidth - 150, 690, fill = 'black', size = 20, font = 'serif', bold = True, align = 'right')
        drawLabel(f'${price:,.2f}', 912.5, 600, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')
        drawLabel(f'{(change * 100):.2f}%', 1227.5, 600, fill = changeColor, size = 15, font = 'serif', bold = True, align = 'left')

def drawAssetTiles(app):
    stockTileWidth = 216
    stockTileHeight = 240
    otherTileWidth = 570
    otherTileHeight = 240

    drawSavingsTile(app, otherTileWidth, otherTileHeight)
    drawIndexTile(app, otherTileWidth, otherTileHeight)
    drawStockTiles(app, stockTileWidth, stockTileHeight)
    drawCropTile(app, otherTileWidth, otherTileHeight)
    drawGoldTile(app, otherTileWidth, otherTileHeight)
 

def drawSideBar(app):
    # Drawing the side bar
    drawRect(0, 0, 200, app.height, fill= rgb(65, 70, 57))

    drawImage('piggy-bank.png', 10, 80, width = 180, height = 180 * 0.54585798816)
    drawLabel('POCKET CASH', 20, 400, fill = 'beige', size = 12, font = 'serif', bold = True, align = 'left')
    drawLabel(f'${app.displayedCash:,.2f}', 20, 420, fill = 'beige', size = 25, font = 'serif', bold = True, align = 'left')
    drawLabel('NET WORTH', 20, 450, fill = 'beige', size = 12, font = 'serif', bold = True, align = 'left')
    drawLabel(f'${app.displayedNetWorth:,.2f}', 20, 470, fill = 'beige', size = 25, font = 'serif', bold = True, align = 'left')

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
        app.simulationButton.draw(app)

def drawGraphs(app):
    for graph in app.graphs:
        if isReleased(app, graph.asset):
            graph.draw(app)

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
        drawImage(app.tutorialImages[4], app.width//2 - 150, app.height//2 - 200, width = 300, height = 300 * 0.29591)
        text = ['You have the ability to run a portfolio',
                'simulation at any point in the game.',
                'Simply press the button on the bottom',
                'left to toggle the display. A graph will',
                'appear which will show you the bull/base/bear',
                'scenario values of your portfolio over',
                'the next 12 months.']
        for i in range(len(text)):
            drawLabel(text[i], app.width//2, app.height//2 - 40 + (i * 25), fill = 'beige', size = 20, font = 'serif', align = 'center')

    elif app.tutorialSlide == app.totalSlides:
        text = ["Now that you know the basics, it's time to",
                'start investing! Click the button below to',
                'begin your financial journey. Good luck, and',
                'have fun playing the game!', '\n',
                'Note: at any point, you can press "P" to pause',
                'the game and "R" to restart the game.', '\n',
                'For TAs, you can press "S" to skip a month,',
                '"B" to skip to the main screen, and "M" to',
                'skip to the end screen.']
        for i in range(len(text)):
            drawLabel(text[i], app.width//2, app.height//2 - 130 + (i * 25), fill = 'beige', size = 20, font = 'serif', align = 'center')

    drawTutorialCircles(app)
    drawButtons(app)

# The function below was written by AI
def drawSimulationGraph(app, x, y, width, height):
    # 1. Run the simulation and get starting value
    paths = app.latestSimPaths
    if paths == []: return
    startValue = getNetWorth(app)
    numMonths = 13 # Month 0 to Month 12
    
    # 2. Extract monthly stats to find the "window"
    # We look at the final month to set our Y-axis zoom
    finalValues = sorted([p[-1] for p in paths])
    lowBound = finalValues[5]
    highBound = finalValues[95]
    
    # Set the zoom window with some padding
    minVal = min(lowBound, startValue) * 0.9
    maxVal = max(highBound, startValue) * 1.1
    valRange = maxVal - minVal if maxVal != minVal else 1

    # 3. Build the coordinates
    upperPoints = []
    lowerPoints = []
    medianPoints = []
    stepX = width / (numMonths - 1)

    for m in range(numMonths):
        # Sort values for this specific month across all 100 paths
        monthlyValues = sorted([p[m] for p in paths])
        
        # Calculate percentiles
        lowPrice = monthlyValues[5]
        medPrice = monthlyValues[50]
        highPrice = monthlyValues[95]
        
        currX = x + (m * stepX)
        
        # Convert dollar values to Y-coordinates
        # Formula: yPos = boxBottom - (percentOfRange * boxHeight)
        yLow = (y + height) - ((lowPrice - minVal) / valRange * height)
        yMed = (y + height) - ((medPrice - minVal) / valRange * height)
        yHigh = (y + height) - ((highPrice - minVal) / valRange * height)
        
        upperPoints.append((currX, yHigh))
        lowerPoints.append((currX, yLow))
        medianPoints.append((currX, yMed))

    # 4. Draw the Shaded "Cone"
    # Create one continuous list of points: forward on top, backward on bottom
    conePoints = []
    for p in upperPoints: conePoints.extend([p[0], p[1]])
    for p in reversed(lowerPoints): conePoints.extend([p[0], p[1]])
    
    drawPolygon(*conePoints, fill = 'gold', opacity = 25)
    
    # 5. Draw the Median Path (The "Expected" line)
    for i in range(len(medianPoints) - 1):
        drawLine(medianPoints[i][0], medianPoints[i][1], medianPoints[i+1][0], medianPoints[i+1][1], fill = 'darkGoldenrod', lineWidth = 2, dashes = True)

    # 6. Add GROUNDING LABELS (So the user knows what they are seeing)
    # Use the dollar values from the last indices of our sorted lists
    drawLabel(f"Bull: ${highBound:,.0f}", x + width + 5, upperPoints[-1][1], align = 'left', size = 12, font = 'serif', bold = True, fill = 'forestGreen')
    drawLabel(f"Expected: ${finalValues[50]:,.0f}", x + width + 5, medianPoints[-1][1], align = 'left', size = 12, font = 'serif', bold = True, fill = 'darkGoldenrod')
    drawLabel(f"Bear: ${lowBound:,.0f}", x + width + 5, lowerPoints[-1][1], align = 'left', size = 12, font = 'serif', bold = True, fill = 'fireBrick')

    # 7. Draw Axis and Month Markers
    drawLine(x, y + height, x + width, y + height, fill = 'black', lineWidth = 1)
    for m in [0, 6, 12]:
        labelX = x + (m * stepX)
        drawLabel(f"+{m} months", labelX, y + height + 15, size = 10, font = 'serif')
        
def drawGameOverScreen(app):
    drawImage(app.tutorialScreenImage, 0, 0, width = app.width, height = app.height)
    drawLabel('CONGRATULATIONS!', app.width//2, app.height//2 - 60, size = 45, bold = True, font = 'serif', fill = 'beige')
    drawLabel('In 10 years, you made: ', app.width//2, app.height//2, size = 20, font = 'serif', fill = 'beige')
    drawLabel(f'${getNetWorth(app):,.2f}', app.width//2, app.height//2 + 40, size = 40, bold = True, font = 'serif', fill = 'beige')

def redrawAll(app):
    drawButtons(app)
    if app.screen == 'title':
        drawTitleScreen(app)

    elif app.screen == 'tutorial':
        drawTutorialScreen(app)    
    
    elif app.screen == 'main':
        drawSideBar(app)
        drawAssetTiles(app)
        drawButtons(app)
        drawGraphs(app)
    
    elif app.screen == 'gameOver':
        drawGameOverScreen(app)

    if app.simulationEnabled == True:
        drawTile(app, app.width//2 + 100 - 300, app.height//2 - 200, 600, 400, 'Monte Carlo Simulation', 20)
        drawSimulationGraph(app, app.width//2 - 150, app.height//2 - 150, 400, 300)
    
    if app.fadeOpacity > 0:
        drawRect(0, 0, app.width, app.height, fill='black', opacity=app.fadeOpacity)

runApp(width=1400, height=800)