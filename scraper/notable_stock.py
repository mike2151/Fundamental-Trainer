from ticker_data import TickerData
import requests
import os
from sec_edgar_downloader import Downloader
from yahoofinancials import YahooFinancials
from bs4 import BeautifulSoup

class NotableStock():
    def __init__(self, stock_ticker, num_trading_days_diff, threshold):
        self.ticker = stock_ticker
        ticker_data_obj = TickerData(stock_ticker)
        self.ticker_data_obj = ticker_data_obj
        historic_data = ticker_data_obj.get_historic_data()
        self.historic_data = historic_data
        self.yahoo_financials_obj = YahooFinancials(self.ticker)
        idx_moments = []
        date_moments = []
        percent_moments = []
        moment_results = []
        # have two pointers approach. Each pointer time_horizon_apart
        close_data = historic_data["Close"]
        start = 0
        end = num_trading_days_diff
        while end < len(close_data):
            if abs((close_data[end] - close_data[start])/(close_data[start])) > threshold:
                idx_moments.append(start)
                date_moments.append(str(close_data.index[start]).split(" ")[0])
                percent_moments.append(str(round(((close_data[end] - close_data[start])/(close_data[start])) * 100.00),2) + "%")
                moment_result = 1 if close_data[end] > close_data[start] else 0
                moment_results.append(moment_result)
                start += num_trading_days_diff
                end += num_trading_days_diff
            else:
                start += 1
                end += 1
        self.idx_moments = idx_moments
        self.date_moments = date_moments
        self.moment_results = moment_results
        self.percent_moments = percent_moments
        self._get_trading_view_html()

    # returns index moments and date moments
    def get_notable_moments_idx(self):
        return self.idx_moments
    def get_notable_moments_date(self):
        return self.date_moments
    def get_notable_moments_results(self):
        return self.moment_results
    def get_notable_moments_percent(self):
        return self.percent_moments
    def is_stock_notable(self):
        return len(self.idx_moments) > 0
    def get_past_n_days_historic(self, date_moment, n_days):
        # get idx of date moment
        idx = self.idx_moments[self.date_moments.index(date_moment)]
        return self.historic_data[idx:idx+n_days]
    def get_company_name(self):
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(self.ticker)

        result = requests.get(url).json()

        for x in result['ResultSet']['Result']:
            if x['symbol'] == self.ticker:
                return x['name']

    def get_recent_financial_documents_for_date(self, date, label):
        format_date = date.replace("-", "")
        download_path = os.path.join(os.path.join(os.path.join(os.path.join(os.getcwd(), "stocks/" + label + "/"), self.ticker), date), "statements")
        dl = Downloader(download_path)
        return dl.get_all_available_filings(self.ticker,before_date=format_date, num_filings_to_download=1)

    # Trading View

    def _get_trading_view_html(self):
        url = "https://www.tradingview.com/symbols/{}".format(self.ticker)
        request_obj = requests.get(url)
        html = request_obj.content
        parsed_html = BeautifulSoup(html, "html.parser")
        self.parsed_html = parsed_html

    def _get_tradingview_classes(self, class_name, html_tag):
        val = self.parsed_html.body.find_all(html_tag, {"class": class_name})
        return val

    def _clean_tradingview_html(self, html):
        return html.replace("\n", "").replace("\t", "")


    def get_company_description(self):
        html = self._get_tradingview_classes("tv-widget-description__text", "div")[0].contents[0]
        return self._clean_tradingview_html(html)

    def get_company_industry(self):
        html = self._get_tradingview_classes("tv-widget-description__value", "span")[1].contents[0]
        return self._clean_tradingview_html(html)

    def get_company_sector(self):
        html = self._get_tradingview_classes("tv-widget-description__value", "span")[0].contents[0]
        return self._clean_tradingview_html(html)




