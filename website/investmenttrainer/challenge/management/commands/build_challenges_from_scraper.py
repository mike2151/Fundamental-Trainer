from django.core.management.base import BaseCommand
from challenge.models import Challenge
import os
import json
from django.core.files import File
from os import listdir

class Command(BaseCommand):

    help = "Builds models from scraper results"

    def handle(self, *args, **kwargs):
        stocks_dir = os.path.join(os.path.abspath(os.path.join(__file__ ,"../../../../../..")),"scraper/stocks")
        stock_recorded = {}
        all_challenges = Challenge.objects.all()
        for challenge in all_challenges:
            ticker = challenge.ticker
            if ticker not in stock_recorded:
                stock_recorded[ticker] = True
        # iterate through all folders and get tickers not yet processed
        all_tickers  = [str(o) for o in os.listdir(stocks_dir) if os.path.isdir(os.path.join(stocks_dir,o))]
        tickers_not_processed = []
        for ticker in all_tickers:
            if ticker not in stock_recorded:
                tickers_not_processed.append(ticker)

        # now make challenge objects for all of the unprocessed tickers
        for ticker in tickers_not_processed:
            stock_dir = os.path.join(stocks_dir, str(ticker))
            for moment in [str(o) for o in os.listdir(stock_dir) if os.path.isdir(os.path.join(stock_dir,o))]:
                # source files
                moment_dir = os.path.join(stock_dir, moment)
                info_file = os.path.join(moment_dir, "info/info.json")
                historic_data_file = os.path.join(moment_dir, "historic_data/historic_data.csv")
                financial_statements_folder = os.path.join(moment_dir, "statements/sec_edgar_filings/" + ticker)

                # fields
                with open(info_file, "r") as info:
                    info_json = json.loads(info.read())
                    stock_name = info_json["name"]
                    stock_description = info_json["description"]
                    stock_result = info_json["result"]
                    info.close()

                with open(historic_data_file, "r") as historic_file:
                    historic_content = historic_file.read()
                    historic_file.close()


                # model creation
                challenge_obj = Challenge(stock_name=stock_name,
                                          stock_ticker = ticker,
                                          stock_description = stock_description,
                                          window_date=moment,
                                          result = stock_result,
                                          historic_data = historic_content)

                # financial statements
                for statement in [str(o) for o in os.listdir(financial_statements_folder) if os.path.isdir(os.path.join(financial_statements_folder,o))]:
                    if statement == "8-K":
                        d = (os.path.join(financial_statements_folder, statement))
                        file_name = [f for f in listdir(d) if os.path.isfile(os.path.join(d,f))][0]
                        local_file = open(os.path.join(d, file_name))
                        djangofile = File(local_file)
                        challenge_obj.statement_8k.save('8k.html', djangofile)
                        local_file.close()
                    elif statement == "10-K":
                        d = (os.path.join(financial_statements_folder, statement))
                        file_name = [f for f in listdir(d) if os.path.isfile(os.path.join(d,f))][0]
                        local_file = open(os.path.join(d, file_name))
                        djangofile = File(local_file)
                        challenge_obj.statement_10k.save('10k.html', djangofile)
                        local_file.close()
                    elif statement == "10-Q":
                        d = (os.path.join(financial_statements_folder, statement))
                        file_name = [f for f in listdir(d) if os.path.isfile(os.path.join(d,f))][0]
                        local_file = open(os.path.join(d, file_name))
                        djangofile = File(local_file)
                        challenge_obj.statement_10q.save('10q.html', djangofile)
                        local_file.close()
                    elif statement == "SC 13G":
                        d = (os.path.join(financial_statements_folder, statement))
                        file_name = [f for f in listdir(d) if os.path.isfile(os.path.join(d,f))][0]
                        local_file = open(os.path.join(d, file_name))
                        djangofile = File(local_file)
                        challenge_obj.statement_13_g.save('13g.html', djangofile)
                        local_file.close()
                    elif statement == "13F-HR":
                        d = (os.path.join(financial_statements_folder, statement))
                        file_name = [f for f in listdir(d) if os.path.isfile(os.path.join(d,f))][0]
                        local_file = open(os.path.join(d, file_name))
                        djangofile = File(local_file)
                        challenge_obj.statement_13f_hr.save('13fhr.html', djangofile)
                        local_file.close()
                    elif statement == "SD":
                        d = (os.path.join(financial_statements_folder, statement))
                        file_name = [f for f in listdir(d) if os.path.isfile(os.path.join(d,f))][0]
                        local_file = open(os.path.join(d, file_name))
                        djangofile = File(local_file)
                        challenge_obj.statement_sd.save('sd.html', djangofile)
                        local_file.close()


                challenge_obj.save()
