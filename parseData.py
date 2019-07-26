import json
import matplotlib
from matplotlib import pyplot as pl
import numpy as np
import fnmatch
jsonData = json.load(open ( 'allresults.json', 'r' ))
newKey = ''
cats = { 0 : {'ebo':0.0, 'symbol':''}}
numEntries = 0
symbols79 = []
symbols38 = []
bindingE79 = []
bindingE38 = []
for key in (jsonData):
  if key.split('/')[-1] == "Binding Energy":
      partsList = key.split('/')[0 :len(key) -1]
      cats[numEntries] = numEntries 
      ebo = float(jsonData[key]['result'])
      symbol =  "%s%s@%s%s" %(partsList[0], partsList[1], partsList[2], partsList[3])
      cats[numEntries] = {'ebo':ebo,'symbol':symbol}
      numEntries +=1



for item in cats:
  
  if fnmatch.filter(cats[item]['symbol'],"19??@60Ag"):
    symbols79.append(cats[item]['symbol'])
    bindingE79.append(cats[item]['ebo'])
  print fnmatch.fnmatch(cats[item]['symbol'], '*6*@32Ag')
  if fnmatch.fnmatch(cats[item]['symbol'], '*6*@32Ag'):
    symbols38.append(cats[item]['symbol'])
    bindingE38.append(cats[item]['ebo'])



import numpy.numarray as na

from pylab import *

print symbols38, bindingE38

symbols38 = [ symbol[1:3] for symbol in symbols38]

xlocations = na.array(range(len(symbols38)))+0.5
width = 0.5
bar(xlocations, bindingE38, width=width)
yticks(range(0, -5))
xticks(xlocations+ width/2, symbols38)
xlim(0, xlocations[-1]+width*2)
title("Binding Energy")
gca().get_xaxis().tick_bottom()
gca().get_yaxis().tick_left()

show()
 
