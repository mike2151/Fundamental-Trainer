import yfinance as yf

class TickerData():
    def __init__(self, ticker):
        self.ticker = str(ticker)

        stock = yf.Ticker(self.ticker)

        all_hist_data = stock.history(period="max")

        self.historic_data = all_hist_data
    def get_historic_data(self):
        return self.historic_data

