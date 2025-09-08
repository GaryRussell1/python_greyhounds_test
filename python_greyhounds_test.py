import clr
clr.AddReference("c:/Program Files (x86)/Betting Assistant/BettingAssistantCom.dll")
from BettingAssistantCom.Application import ComClass
from dataclasses import dataclass, field
from typing import Dict
from datetime import date
import time

@dataclass
class BAPrice:
    backOdds:float
    layOdds:float

@dataclass
class BAMarket:
    marketName: str
    marketId: int
    winPrices: Dict[str, BAPrice] = field(default_factory=dict)

def findMarkets(ba):
    winMarkets = {}
    sports = ba.getSports()
    for sport in sports:
        if sport.sport != "Greyhound - Today's Card":
            continue
        for market in ba.getEvents(sport.sportId):
            baMarket = BAMarket(market.eventName, market.eventId)
            startTime = market.startTime.ToString("ddMMyy_HH:mm")
            winMarkets[f"{baMarket.marketName}_{startTime}"] = baMarket
    return winMarkets

def getBAPrices(ba, baMarket):
    while True:
        time.sleep(0.1)
        baPrices = ba.getPrices()
        marketId = ''
        for bfOdds in baPrices:
            marketId = int(bfOdds.marketId)
            bfPrice = BAPrice(float(bfOdds.backOdds1), float(bfOdds.layOdds1))
            baMarket.winPrices[bfOdds.selection] = bfPrice
        if marketId == baMarket.marketId:
            break
        else:
            baMarket.winPrices.clear()

def cycleWinMarkets(ba, winMarkets):
    global currentMarket
    for baMarket in winMarkets.values():
        print(f"Opening market {baMarket.marketName}")
        ba.openMarket(baMarket.marketId, 1)
        getBAPrices(ba, baMarket)
        print (f"Market {baMarket.marketName} prices:")
        for selec, price in baMarket.winPrices.items():
            print(f"  {selec}: Back {price.backOdds}, Lay {price.layOdds}")

# connect to BA
ba = ComClass()
# find markets
winMarkets = findMarkets(ba)
# cycle through markets
cycleWinMarkets(ba, winMarkets)
# clean up
ba = None
print("Application exit.")
