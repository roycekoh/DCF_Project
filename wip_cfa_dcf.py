# -*- coding: utf-8 -*-
"""WIP_CFA_DCF.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EhBvcwiWPYqox09ZYbQhL9yQ3KUFBImm
"""

!pip install yfinance
!pip install requests

#Imports
import pandas as pd
import yfinance as yf
import datetime as dt
import requests as r
import argparse
import os

from modeling.data import *
from modeling.dcf import *
from visualization.plot import *
from visualization.printouts import *

aapl = yf.Ticker("AAPL")
market = yf.Ticker("VOO")
currentDate = dt.datetime.now()
startDate = dt.datetime(int(currentDate.strftime("%G"))-5, int(currentDate.strftime("%u")), int(currentDate.strftime("%V")))
marketHistory = market.history(start=startDate, end=currentDate, interval='1mo', actions=False)
companyHistory = aapl.history(start=startDate, end=currentDate, interval='1mo', actions=False)
companyBeta = aapl.info['beta']
print(companyBeta)
MarketRiskPremium = 4.6
RiskFreeRate = 0.95
CAPM = RiskFreeRate + (companyBeta * MarketRiskPremium)
companyCap = aapl.info['marketCap']
financials = r.get('https://financialmodelingprep.com/api/v3/financial-statement-full-as-reported/AAPL?apikey=demo')

def main(args):
    if args.s > 0:
        if args.v is not None:
            if args.v == 'eg' or 'earnings_growth_rate':
                cond, dcfs = run_setup(args, variable = 'eg')
            elif args.v == 'cg' or 'cap_ex_growth_rate':
                cond, dcfs = run_setup(args, variable = 'cg')
            elif args.v == 'pg' or 'perpetual_growth_rate':
                cond, dcfs = run_setup(args, variable = 'pg')
            elif args.v == 'discount_rate' or 'discount':
                cond, dcfs = run_setup(args, variable = 'discount')
            else:
                raise ValueError('args.variable is invalid, must choose either earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, or discount')
        else:
            raise ValueError
    else:
        cond, dcfs = {'Ticker': [args.t]}, {}
        dcfs[args.t] = historical_DCF(args.t, args.y, args.p, args.d, args.eg, args.cg, args.pg, args.i, args.apikey)

    if args.y > 1: 
        visualize_bulk_historicals(dcfs, args.t, cond, args.apikey)
    else:
        prettyprint(dcfs, args.y)

def run_setup(args, variable):
    dcfs, cond = {}, {args.v: []}
    
    for increment in range(1, int(args.steps) + 1):
        var = vars(args)[variable] * (1 + (args.s * increment))
        step = '{}: {}'.format(args.v, str(var)[0:4])
        cond[args.v].append(step)
        vars(args)[variable] = var
        dcfs[step] = historical_DCF(args.t, args.y, args.p, args.d, args.eg, args.cg, args.pg, args.i, args.apikey)
    return cond, dcfs


def multiple_tickers():
    return NotImplementedError

def DCF(ticker, ev_statement, income_statement, balance_statement, cashflow_statement, discount_rate, forecast, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate):
    enterprise_val = enterprise_value(income_statement, cashflow_statement, balance_statement, forecast, discount_rate, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate)

    equity_val, share_price = equity_value(enterprise_val, ev_statement)
    print('\nEnterprise Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(enterprise_val))), 
              '\nEquity Value for {}: ${}.'.format(ticker, '%.2E' % Decimal(str(equity_val))),
           '\nPer share value for {}: ${}.\n'.format(ticker, '%.2E' % Decimal(str(share_price))),
            '-'*60)
    return {
        'date': income_statement[0]['date'],       # statement date used
        'enterprise_value': enterprise_val,
        'equity_value': equity_val,
        'share_price': share_price
    }

def historical_DCF(ticker, years, forecast, discount_rate, earnings_growth_rate, cap_ex_growth_rate, perpetual_growth_rate, interval = 'annual', apikey = ''):
    dcfs = {}

    income_statement = get_income_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    balance_statement = get_balance_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    cashflow_statement = get_cashflow_statement(ticker = ticker, period = interval, apikey = apikey)['financials']
    enterprise_value_statement = get_EV_statement(ticker = ticker, period = interval, apikey = apikey)['enterpriseValues']

    if interval == 'quarter':
        intervals = years * 4
    else:
        intervals = years

    for interval in range(0, intervals):
        try:
            dcf = DCF(ticker, 
                    enterprise_value_statement[interval],
                    income_statement[interval:interval+2],        # pass year + 1 bc we need change in working capital
                    balance_statement[interval:interval+2],
                    cashflow_statement[interval:interval+2],
                    discount_rate,
                    forecast, 
                    earnings_growth_rate,  
                    cap_ex_growth_rate, 
                    perpetual_growth_rate)
        except IndexError:
            print('Interval {} unavailable, no historical statement.'.format(interval)) # catch
        dcfs[dcf['date']] = dcf 
    
    return dcfs

def ulFCF(ebit, tax_rate, non_cash_charges, cwc, cap_ex):
    return ebit * (1-tax_rate) + non_cash_charges + cwc + cap_ex

def equity_value(enterprise_value, enterprise_value_statement):
    return equity_val,  share_price

data_source = 'kaggle' # alphavantage or kaggle

if data_source == 'alphavantage':

    api_key = '<your API key>'

    # American Airlines stock market prices
    ticker = "AAL"

    # JSON file with all the stock market data for AAL from the last 20 years
    url_string = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s"%(ticker,api_key)

    # Save data to this file
    file_to_save = 'stock_market_data-%s.csv'%ticker
    if not os.path.exists(file_to_save):
        with urllib.request.urlopen(url_string) as url:
            data = json.loads(url.read().decode())
            # extract stock market data
            data = data['Time Series (Daily)']
            df = pd.DataFrame(columns=['Date','Low','High','Close','Open'])
            for k,v in data.items():
                date = dt.datetime.strptime(k, '%Y-%m-%d')
                data_row = [date.date(),float(v['3. low']),float(v['2. high']),
                            float(v['4. close']),float(v['1. open'])]
                df.loc[-1,:] = data_row
                df.index = df.index + 1
        print('Data saved to : %s'%file_to_save)        
        df.to_csv(file_to_save)

    # If the data is already there, just load it from the CSV
    else:
        print('File already exists. Loading data from CSV')
        df = pd.read_csv(file_to_save)

else:
    df = pd.read_csv(os.path.join('Stocks','hpq.us.txt'),delimiter=',',usecols=['Date','Open','High','Low','Close'])
    print('Loaded data from the Kaggle repository')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--p', '--period', help = 'years to forecast', type = int, default =  3)
    parser.add_argument('--t', '--ticker', help = 'pass a single ticker to do historical DCF', type = str, default = 'AAPL')
    parser.add_argument('--y', '--years', help = 'number of years to compute DCF analysis for', type = int, default = 1)
    parser.add_argument('--i', '--interval', help = 'interval period for each calc, either "annual" or "quarter"', default = 'annual')
    parser.add_argument('--s', '--step_increase', help = 'specify step increase for EG, CG, PG to enable comparisons.', type = float, default = 0)
    parser.add_argument('--steps', help = 'steps to take if --s is > 0', default = 5)
    parser.add_argument('--v', '--variable', help = 'if --step_increase is specified, must specifiy variable to increase from: [earnings_growth_rate, discount_rate]', default = None)
    parser.add_argument('--d', '--discount_rate', help = 'discount rate for future cash flow to firm', default = 0.1)
    parser.add_argument('--eg', '--earnings_growth_rate', help = 'growth in revenue, YoY',  type = float, default = .05)
    parser.add_argument('--cg', '--cap_ex_growth_rate', help = 'growth in cap_ex, YoY', type = float, default = 0.045)
    parser.add_argument('--pg', '--perpetual_growth_rate', help = 'for perpetuity growth terminal value', type = float, default = 0.05)
    parser.add_argument('--apikey', help='API key for financialmodelingprep.com', default=os.environ.get('APIKEY'))

    args = parser.parse_args()
    main(args)




