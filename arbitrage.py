import os
from binance.client import Client
import pandas as pd
from datetime import datetime
import json
import logging
import time as t

class BinanceDS():  
    FILENAME = ''
    API = ''
    API_SECRET = ''
    COIN_CONTEXT = ''

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        with open('../metadata/binance_keys.txt') as f:
            keys = f.read()
            keys = keys.split(',')
            BinanceDS.API, BinanceDS.API_SECRET = keys[0], keys[1]
        self.client = Client(BinanceDS.API, BinanceDS.API_SECRET)
        self.pair_list = self.get_pairs()
        self.get_triangular_pairs()
        # self.get_triangular_pairs(pair='ADX')
        # self.get_real_prices(pair='QSPBNB')
        # self.get_best_prices(pair='QSPBNB')

    def get_pairs(self):
        key_pairs, pair_list = ['BNB', 'BTC', 'ETH' , 'TRX', 'XRP', 'USDT', 'PAX', 'TUSD', 'USDC', 'BUSD', 'USDS'], []
        prices = self.client.get_exchange_info()
        pairs = [item['symbol'] for item in prices['symbols'] if item['status'] == 'TRADING']
        for key_pair in key_pairs:
            pair_dict = {'symbol': key_pair, 'sec_pair': []}
            for pair in pairs:
                if pair[-3:] == key_pair:
                    pair_dict['sec_pair'].append(pair[:-3])
                elif pair[-4:] == key_pair:
                    pair_dict['sec_pair'].append(pair[:-4])
            pair_list.append(pair_dict)
        return pair_list


    def get_triangular_pairs(self, pair=''):
        name_coin_0, name_coin_1 = 'BNB', 'BTC'
        common_list = list(set(self.pair_list[0]['sec_pair']) & set(self.pair_list[1]['sec_pair']))
        bnb_bal = 2
        highest = -99
        estimated_fee = (bnb_bal*0.00075*bnb_bal)*3
        if pair == '':
            print(f"Finding a trade pair. The amount of BNB trading with is {bnb_bal}")
            for i in common_list:
                print("Working...")
                buy_price = float(self.get_real_prices(pair= i+"BNB", type='Buy'))
                exchange_price = float(self.get_real_prices(pair=i+"BTC", type='Sell'))
                sell_price = float(self.get_real_prices(pair="BNB"+"BTC", type='Sell'))
                net_profit = ((bnb_bal/(buy_price))*exchange_price)/sell_price
                profit = net_profit-estimated_fee
                if profit > bnb_bal:
                    print(f'Buy {bnb_bal/(buy_price):.2f} @ {i+"BNB"} for {buy_price} --> Exchange for {((bnb_bal/(buy_price))*exchange_price):.5f} @ {i+"BTC"} for {exchange_price} --> Sell {profit:.3f} @ {"BTC"+"BNB"} for {sell_price}' )
                    if profit > highest:
                        pair = i
                        highest = profit
                else:
                    print(f'No profit would be made. A loss of {bnb_bal-profit} would occur.')
        else:
            print(f"The amount of BNB trading with is {bnb_bal}, the trading pair is {pair}")
            buy_price = float(self.get_real_prices(pair= pair+"BNB", type='Buy'))
            exchange_price = float(self.get_real_prices(pair=pair+"BTC", type='Sell'))
            sell_price = float(self.get_real_prices(pair="BNB"+"BTC", type='Sell'))

            profit = ((bnb_bal/(buy_price))*exchange_price)/sell_price
            profit = net_profit-estimated_fee

            if profit > bnb_bal:
                print(f'Buy {bnb_bal/(buy_price):.2f} @ {pair+"BNB"} for {buy_price} --> Exchange for {((bnb_bal/(buy_price))*exchange_price):.5f} @ {pair+"BTC"} for {exchange_price} --> Sell {profit:.3f} @ {"BTC"+"BNB"} for {sell_price}' )
                if profit > highest:
                    highest = profit
        if highest == -99:
            print("No profitable oppurtnitys were found.")
        else:
            print(f'The highest profit found on this run was {highest:.2f} with pair {pair}')

    def get_real_prices(self, pair, type = ''):
        depth = self.client.get_order_book(symbol=pair)
        if type == 'Buy':
            return depth['asks'][0][0]
        elif type == 'Sell':
            return depth['bids'][0][0]
        else:
            print('Please specify market type (Buy/Sell)')
            return


BinanceDS()
        