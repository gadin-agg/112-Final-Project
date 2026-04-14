from cmu_graphics import *
import pandas as pd
from PIL import Image

def redrawAll(app):
    drawCircle(app.width/2, app.height/2, 100, fill='red')

runApp(width=400, height=400)