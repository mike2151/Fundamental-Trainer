from django.core.management.base import BaseCommand
from challenge.models import Challenge
import os
import json
from django.core.files import File
from os import listdir
from investmenttrainer.utils import caching

class Command(BaseCommand):

    help = "Builds models from scraper results"

    def handle(self, *args, **kwargs):
        base_stocks_dir = os.path.join(os.path.abspath(os.path.join(__file__ ,"../../../../../..")),"scraper/stocks")
        all_years  = [str(o) for o in os.listdir(base_stocks_dir) if os.path.isdir(os.path.join(base_stocks_dir,o))]
        all_tickers_not_processed = []
        for year in all_years:
            stocks_dir = os.path.join(base_stocks_dir, year)
            stock_recorded = {}
            all_challenges = Challenge.objects.all()
            for challenge in all_challenges:
                ticker = challenge.stock_ticker
                if ticker not in stock_recorded:
                    stock_recorded[ticker] = True
            # iterate through all folders and get tickers not yet processed
            all_tickers  = [str(o) for o in os.listdir(stocks_dir) if os.path.isdir(os.path.join(stocks_dir,o))]
            tickers_not_processed = []
            for ticker in all_tickers:
                if ticker not in stock_recorded:
                    tickers_not_processed.append(ticker)

            # now make challenge objects for all of the unprocessed tickers
            all_tickers_not_processed += tickers_not_processed
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
                        stock_percent = info_json["percent_result"]
                        stock_industry = info_json["industry"]
                        stock_sector = info_json["sector"]
                        info.close()

                    with open(historic_data_file, "r") as historic_file:
                        historic_content = historic_file.read()
                        historic_file.close()


                    # model creation
                    challenge_obj = Challenge(stock_name=stock_name,
                                              stock_ticker = ticker,
                                              stock_industry=stock_industry,
                                              stock_sector=stock_sector,
                                              time_label_full = year,
                                              time_label_url = year.lower().replace(" ", "_"),
                                              stock_description = stock_description,
                                              window_date=moment,
                                              result = stock_result,
                                              result_amount_percent = stock_percent,
                                              historic_data = historic_content)
                    challenge_obj.save()
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
        # add years to caching
        types = caching.get_value("challenge_types")
        if types is None:
            types = []
        new_types = set(types + all_years)
        list_new_types = list(new_types)
        caching.set_value("challenge_types", list_new_types)
        caching.set_value("num_types_challenges", len(list_new_types))
        
        challenge_count = Challenge.objects.all().count()
        caching.set_value("num_questions", challenge_count)

        new_tickers_count = len(set(all_tickers_not_processed))
        curr_count_tickers = caching.get_value("num_securities")
        if curr_count_tickers is None:
            curr_count_tickers = 0
        caching.set_value("num_securities", new_tickers_count + curr_count_tickers)
