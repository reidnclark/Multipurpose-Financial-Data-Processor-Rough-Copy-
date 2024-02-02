import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yahoo_fin.stock_info as si

## Set no limit in number of rows / columns displayed for large datasets of stocks:
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

## Format values as $USD
from decimal import Decimal
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

## Currency formatter function
def currency_formatter(value):
    return locale.currency(value, grouping=True)

## Main testing function
def main():
    def all():
        ## Sample Stock Input: Apple / AAPL
        stock1 = yf.Ticker('AAPL')
        extracted_tickername = (str(stock1)[24:28])
        print(f'Ticker Name: {extracted_tickername}')

        ## Set "S&P 500 Index" as the Industry Sector for all Beta Calculations
        market_index = yf.Ticker('^GSPC') # ...so S&P 500 only

        def grapher():
            ## Ask for period to chart, create .history dataframe
            user_period_input = str(input('Enter Time Period to Graph Here: '))
            df_stock1_info_grapher = pd.DataFrame(stock1_info(period=(user_period_input)))

            ## Gather 'x' recent history for stock...
            stock1_cvals_grapher = df_stock1_info_grapher['Close']
            np_stock1_cvals_grapher = np.array(stock1_cvals_grapher)

            ## Count i for elements in x axis
            elements_in_x_axis = len(df_stock1_info_grapher)
            x_axis = np.array(range(0,elements_in_x_axis))

            ## Plot graph
            plt.plot(x_axis, np_stock1_cvals_grapher, label='Close Values', color = "rebeccapurple")
            plt.title(f'{extracted_tickername} Closing Price, Period : {user_period_input}')
            plt.xlabel('Time (Days)')
            plt.ylabel('Price (Close Value)')
            plt.legend()
            plt.show()

        def main_body():
            def wacc_and_related():
                def dcf_model():
                    def enterprise_valuator():
                        
                        ## Find enterprise value
                        ent_val = mkt_cap + total_debt - cash_and_ce
                        print(f'Enterprise Value: {currency_formatter(ent_val)}')

                        ## Calculate equity value of ticker (convert from ent_val)
                        equity_val = ent_val + bal_sheet['Cash Financial'] \
                                        + bal_sheet['Available For Sale Securities'] \
                                        - total_debt
                        
                        ## Print Implied Share Price
                        implied_share_price = equity_val / no_of_shares
                        print(f'Implied Share Price: {currency_formatter(implied_share_price)}')

                    ## Discounted Cash Flow Model Calculator
                    ## 1) Find FCF (Free Cash Flow)
                    fcf = cashflow_st['Free Cash Flow']

                    ## 2) Calculate Market Growth Rate. ('*2' as it is a ...
                    ## ... 6mo period. 'iloc' for more-accurate integer key (less output text desc.)
                    annual_g = (market_returns.iloc[-1] - market_returns.iloc[0])*2
                    
                    ## 3) Calculate Terminal Value using Perpetuity Growth Method
                    perp_growth_terminal_val = (fcf * (1 + annual_g)) / (wCoC - annual_g)

                    ## 4) Calculate Enterprise Value (ent_val)
                    enterprise_valuator()

                ## Calculate WACC (wCoC)
                wCoC = ((erp * beta) + rf) + cost_of_debt
                print(f'Weighted Average Cost of Capital (WACC): {(round(wCoC,2))*100}%')

                ## Call DCF discounted cash flow model calculator
                dcf_model()
            
            ## Find bal sheet, income statement & cashflow stmt for ticker
            bal_sheet_date = '2023-09-30'
            bal_sheet = stock1.balance_sheet[bal_sheet_date]
            inc_st = stock1.income_stmt[bal_sheet_date]
            cashflow_st = stock1.cashflow[bal_sheet_date]
            df_cashflow_st = pd.DataFrame(cashflow_st)

            ## Find market cap & no. of shares for ticker
            mkt_cap = stock1.basic_info['marketCap']
            no_of_shares = bal_sheet['Ordinary Shares Number']
            
            ## Gather 6mo recent close value history for ticker,...
            ## ...arrange close values in pandas dataframe
            stock1_info = stock1.history
            df_stock1_info = pd.DataFrame(stock1_info(period='6mo'))
            stock1_cvals = df_stock1_info['Close']
            ## Gather 6mo recent close value history for market index...
            ## ...performance, ditto above
            ## arrange close values in pandas dataframe again
            market_data = market_index.history(period='6mo')
            df_market_data = pd.DataFrame(market_data)

            ## Calculate stock and market returns (pct change) for ticker
            stock1_returns = stock1_cvals.pct_change().dropna()
            market_returns = df_market_data['Close'].pct_change().dropna()

            ## Calculate covariance & variance of returns (ticker v market)
            covariance = np.cov(stock1_returns, market_returns)[0,1]
            variance_of_market = np.var(market_returns)

            ## Calculate beta of ticker
            beta = covariance / variance_of_market

            ## Designate Equity Risk Premium (erp) for USA (based on S&P), 2024 rate (4.6%)
            erp = 0.046
            ## Designate Rf (Risk-Free Rate). Assume time period 20y. (4.22%)
            ## Treasury Info Link: https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2023
            rf = 0.0422
            ## Designate Rm (Expected Market Return). Assume 8% (based on S&P Historical)
            rm = 0.08

            ## The below is possibly needed in the future
            ## Calculate Cost of Equity (Re)
            #cost_of_equity = rf + beta * (rm - rf)

            ## Find total assets, debt, and liabilities. calc future debt:
            total_assets = bal_sheet['Total Assets']
            total_debt = bal_sheet['Total Debt']
            total_liabilities = bal_sheet['Total Liabilities Net Minority Interest']
            future_debt = (bal_sheet['Long Term Debt']) \
                        + (bal_sheet['Other Non Current Liabilities']) \
                        + (bal_sheet['Tradeand Other Payables Non Current'])

            ## TOTAL EQUITY
            ## APIC Assume as $0 due to missing yfinance SoCI.
            cmn_stock = bal_sheet['Common Stock']
            cmn_stock_equity = bal_sheet['Common Stock Equity']
            treasury_stock = cmn_stock - cmn_stock_equity
            apic = bal_sheet['Capital Stock']
            retained_earnings = bal_sheet['Retained Earnings']
            ## Calc TE
            total_equity = cmn_stock + (apic*0) + retained_earnings + treasury_stock #+ oci 

            ## Calculate Market Value of Debt. Assume interest = rf above
            ## Also, assume 'n' (YTM) = 5, based on S&P typicals.
            ## Recall: CMVoD: pv = fv / (1+r)^n
            mkt_val_ofdebt = future_debt / (1+rf)**5
            ## Calculate Annual Interest Payment
            ## AIP = Total Debt x Interest Rate. Also assume interest = rf above
            ann_int_pmt = total_debt * rf
            ## Calculate Cost of Debt (Rd)
            cost_of_debt = ann_int_pmt / mkt_val_ofdebt

            ## Find weightages
            equity_weightage = (total_equity / mkt_cap) * 100
            debt_weightage = (total_debt / mkt_cap) * 100

            ## Find cash and cash equivalents
            cash_and_ce = bal_sheet['Cash And Cash Equivalents']

            ## Calculate debt ratio
            debt_ratio = total_debt / total_assets

            ## Call WACC_etc to begin technical analysis
            wacc_and_related()

        main_body()

    all()
main()







## Restart program function
def restart():
            print('Restart?')
            user_input = str(input('(Y/N):')).upper()
            if user_input == 'Y':
                mfdp()
            elif user_input == 'N':
                print('Bonsoir mon Ami.')
                exit()

## Original Merge File
def mfdp():
    def calculator():
        ## 2 - TE - Calculate Total Equity:
        total_equity = cmn_stock + apic + ret_earn + oci + tre_stock
        print(f'Total Equity: {currency_formatter(total_equity)}')

        ## 3 - TD - Print total debt:
        print(f'Total Debt: {currency_formatter(total_debt)}')

        ## Print interest expense:
        print(f'Interest Expense: {currency_formatter(int_exp)}')

        ## Find tax rate (divide income tax expense by pretax income):
        taxrate = income_tax_expense / pretax_inc
        answer = round((taxrate*100),2)
        answer1 = abs(answer)
        print(f'Tax Rate: {answer1}%')
        exit()

    ## Type stock name here:
    ticker_input = str(input('Enter Ticker Here: ')).upper()
    stock = yf.Ticker(ticker_input)
    histdata = stock.history

    ## Type time period here:
    range_input = str(input('Enter Period Here: '))
    histdata = stock.history(period=(range_input))

    ## Data structure for stock info to append into (pandas library):
    df_histdata = pd.DataFrame(histdata)

    ## Arrange open values into a numpy array (numpy library):
    open_values = df_histdata['Open']
    np_open_values = np.array(open_values)
    pps = np_open_values[-1]

    ## Find number of shares:
    bal_sheet_date = '2022-12-31'
    total_shares = stock.balance_sheet[bal_sheet_date]['Ordinary Shares Number']
    ## Find total debt:
    total_debt = stock.balance_sheet[bal_sheet_date]['Total Debt']
    ## Find common stock:
    cmn_stock = stock.balance_sheet[bal_sheet_date]['Common Stock']
    ## Find APIC:
    apic = stock.balance_sheet[bal_sheet_date]['Additional Paid In Capital']
    ## Find RE:
    ret_earn = stock.balance_sheet[bal_sheet_date]['Retained Earnings']
    ## Find OCI (TBD):
    oci = 0
    ## Find Treasury stock (TBD):
    tre_stock = 0
    ## Find Interest expense:
    int_exp = stock.income_stmt[bal_sheet_date]['Interest Expense']
    ## Find income tax expense
    income_tax_expense = stock.income_stmt[bal_sheet_date]['Tax Provision']
    ## Find pretax income
    pretax_inc = stock.income_stmt[bal_sheet_date]['Pretax Income']

    calculator()

#Start MFDP below (unhash)
def newtest():
    ticker_input = 'AAPL'
    #ticker_input = str(input('Enter Ticker Name:'))
    ticker = yf.Ticker(ticker_input)

    bal_sheet = ticker.balance_sheet
    dates_bal_sheet = bal_sheet.iloc[-1]
    df_dates_bal_sheet = pd.DataFrame(dates_bal_sheet)
    most_recent_date_and_time = df_dates_bal_sheet.index[0]
    most_recent_date = str(most_recent_date_and_time)[:10]
    print(most_recent_date)

    #most_recent_bal_sheet = ticker.balance_sheet['2023-09-30']
    #print(most_recent_bal_sheet)

        #def datefinder(financialreport):
        #fin_report = ticker.financialreport
        #dates_fin_report = fin_report.iloc[-1]