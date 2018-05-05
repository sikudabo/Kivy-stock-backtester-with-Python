import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import matplotlib.pyplot as plt
import kivy
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.base import runTouchApp
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
import datetime
import subprocess
import time
import twilio
from twilio.rest import Client
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.core.audio import SoundLoader
import sys
import datetime
from kivy.uix.floatlayout import FloatLayout
from kivy.core.text import LabelBase

from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from time import strftime
import smtplib

import pymysql
import pymysql.cursors
import datetime 
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
import numpy as np
import math
from math import sqrt
import quandl
import statistics
from matplotlib.backends.backend_agg import FigureCanvasAgg
from math import sin
#from kivy.matplotlib import MatplotFigure
from kivy.base import runTouchApp













class Intro(Screen):
    pass






class Select(Screen):
    
    
    def __init__(self, **kwargs):
        super(Select, self).__init__(**kwargs)


    def enterstock(self):
        start = datetime.datetime(2017, 1,1)
        end = datetime.date.today()

        stock = str(self.ids.stock_ticker.text)


        selection = web.DataReader(str(stock), 'yahoo', start, end)
        
        self.ids.stock_price.text += str(selection['Close'].tail(5)) #This += sign allows the stock price to show up in this box once the button is pressed

        selection["20d"] = (selection["Close"].rolling(window = 20, min_periods=0).mean())
        selection["5d"] = (selection["Close"].rolling(window = 5, min_periods=0).mean())
        selection["50d"] = (selection["Close"].rolling(window = 50, min_periods=0).mean())
        standard = statistics.stdev(selection["Close"])

        selection['Z'] = (selection['Close'] - selection['20d']) / standard





        self.ids.stock_z.text += str(selection['Z'].tail(5))

        choice = selection['Z'].tail(1)


        

        

        if choice.item() > 2:
                   self.ids.recommendation.text += "Sell, the Z-Score is " + str(choice[0]) + " standard deviations from the mean."
                   

        elif choice.item() >= 0 and choice.item() < 2:
                    self.ids.recommendation.text += "Hold, the Z-Score is " + str(choice[0]) + " standard deviations from the mean. The stock is trading in a neutral range."


        elif choice.item() < 0:
                     self.ids.recommendation.text += "Buy, the Z-score is " + str(choice[0]) + " standard deviations from the mean. The stock is currently a value buy."
                     
        else:
                    self.ids.recommendation.text += "Your entry was invalid!"


    def clear(self):
        self.ids.stock_ticker.text = ''
        self.ids.stock_price.text = ''
        self.ids.stock_z.text = ''
        self.ids.recommendation.text = ''






class backtest(Screen):
    """This class will allow us to back test a stock that has been entered"""
    def __init__(self, **kwargs):
        super(backtest, self).__init__(**kwargs)


    def test_stock(self):





        start = datetime.datetime(2017, 1,1)
        end = datetime.date.today()

        stock = str(self.ids.test_ticker.text)


        selection = web.DataReader(str(stock), 'yahoo', start, end)

        selection["20d"] = (selection["Close"].rolling(window = 20, min_periods=0).mean())
        selection["5d"] = (selection["Close"].rolling(window = 5, min_periods=0).mean())
        selection["50d"] = (selection["Close"].rolling(window = 50, min_periods=0).mean())
        standard = statistics.stdev(selection["Close"])

        selection['Z'] = (selection['Close'] - selection['20d']) / standard



        X = .05


        selection['Regime'] = np.where(selection['Z'] > X, -1 , 0)
        selection['Regime'] = np.where(selection['Z'] < X, 1, selection['Regime'])

       

        ##selection['Regime'].plot(lw=1.5,ylim=[-1,2])
        ##selection.loc['2016-11-15':'2017-11-15',"Regime"].plot(ylim = (-2,2)).axhline(y = 0, color = "black", lw = 2)
        #plt.show()
        #print(selection.describe())

        regime_orig = selection.ix[-1, 'Regime']
        selection.ix[-1, 'Regime'] = 0
        selection['Signal'] = np.sign(selection["Regime"] - selection["Regime"].shift(1))
        # Restore original regime data
        selection.ix[-1, 'Regime'] = regime_orig
        ##
        ##selection["Signal"].plot(ylim = (-2, 2))
        ##plt.show()
        #print(selection.tail())

        #print(selection.loc[selection["Signal"] == 1, "Close"])
        #print(selection.loc[selection["Signal"] == -1, "Close"])



        selection_signals = pd.concat([
                pd.DataFrame({"Price": selection.loc[selection["Signal"] == 1, "Close"],
                             "Regime": selection.loc[selection["Signal"] == 1, "Regime"],
                             "Signal": "Buy"}),
                pd.DataFrame({"Price": selection.loc[selection["Signal"] == -1, "Close"],
                             "Regime": selection.loc[selection["Signal"] == -1, "Regime"],
                             "Signal": "Sell"}),
            ])
        selection_signals.sort_index(inplace = True)


        self.ids.test_signals.text += str(selection_signals)





        selection_long_profits = pd.DataFrame({
                "Price": selection_signals.loc[(selection_signals["Signal"].shift(1) == "Buy") &
                                          selection_signals["Regime"].shift(1) == 1, "Price"],
                "Profit": pd.Series(selection_signals["Price"] - selection_signals["Price"].shift(1)).loc[
                    selection_signals.loc[(selection_signals["Signal"].shift(1) == "Buy") & (selection_signals["Regime"].shift(1) == 1)].index
                ].tolist(),
                "End Date": selection_signals["Price"].loc[
                    selection_signals.loc[(selection_signals["Signal"].shift(1) == "Buy") & (selection_signals["Regime"].shift(1) == 1)].index
                ].index
            })
        selection_long_profits.sort_index(inplace = True)



            

        self.ids.test_profits.text += str(selection_long_profits)




        cash = 100000
        selection_backtest = pd.DataFrame({"Start Port. Value": [],
                                 "End Port. Value": [],
                                 "End Date": [],
                                 "Shares": [],
                                 "Share Price": [],
                                 "Trade Value": [],
                                 "Profit per Share": [],
                                 "Total Profit": [],
                                 "Stop-Loss Triggered": []})
        port_value = 1  # Max proportion of portfolio bet on any trade
        batch = 400      # Number of shares bought per batch
        stoploss = .70     # % of trade loss that would trigger a stoploss
        for index, row in selection_long_profits.iterrows():
            batches = np.floor(cash * port_value) // np.ceil(batch * row["Price"]) # Maximum number of batches of stocks invested in
            trade_val = batches * batch * row["Price"] # How much money is put on the line with each trade
            if row["Price"] < (1 - stoploss) * row["Price"]:   # Account for the stop-loss
                share_profit = np.round((1 - stoploss) * row["Price"], 2)
                stop_trig = True
            else:
               share_profit = row["Profit"]
               stop_trig = False
            profit = share_profit * batches * batch # Compute profits
            # Add a row to the backtest data frame containing the results of the trade
            selection_backtest = selection_backtest.append(pd.DataFrame({
                        "Start Port. Value": cash,
                        "End Port. Value": cash + profit,
                        "End Date": row["End Date"],
                        "Shares": batch * batches,
                        "Share Price": row["Price"],
                        "Trade Value": trade_val,
                        "Profit per Share": share_profit,
                        "Total Profit": profit,
                        "Stop-Loss Triggered": stop_trig
                    }, index = [index]))
            cash = max(0, cash + profit)

        self.ids.port_test.text += str(selection_backtest)
        


    def clear2(self):
        self.ids.port_test.text = ''
        self.ids.test_signals.text = ''
        self.ids.test_profits.text = ''
        

    
        
        

    
        
        

        

    
        
        











class ScreenManagement(ScreenManager):
    pass





profile = Builder.load_file("stocksapp.kv")

class StocksApp(App):
    def build(self):
        return profile
    
if __name__=='__main__':
    StocksApp().run()
