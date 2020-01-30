import os
import random
import json
from notable_stock import NotableStock
import shutil
import argparse
import sys
import csv

PROCESSED_STOCKS_FILE_NAME = "processed_stocks.json"

def get_nasdaq_other_tickers():
    file_path = os.path.join(os.getcwd(), "stock_sources/otherlisted.txt")
    stock_tickers = []
    with open(file_path, "r") as listed_file:
        lines = listed_file.readlines()
        for line in lines[1:]:
            stock_ticker = line.split("|")[0]
            stock_tickers.append(stock_ticker)
    return stock_tickers


def get_nasdaq_tickers():
    file_path = os.path.join(os.getcwd(), "stock_sources/nasdaq.txt")
    stock_tickers = []
    with open(file_path, "r") as listed_file:
        lines = listed_file.readlines()
        for line in lines[1:]:
            stock_ticker = line.split("|")[0]
            stock_tickers.append(stock_ticker)
    return stock_tickers

def get_nyse_tickers():
    file_path = os.path.join(os.getcwd(), "stock_sources/nyse_csv.csv")
    stock_tickers = []
    with open(file_path, "r") as listed_file:
        csv_reader = csv.reader(listed_file, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            stock_tickers.append(row)
    return stock_tickers

def has_ticker_been_processed(ticker):
    with open(os.path.join(os.getcwd(), PROCESSED_STOCKS_FILE_NAME), "r") as processed_stocks_file:
        file_contents = processed_stocks_file.read()
        if len(file_contents) < 3:
            return False
        json_file = json.loads(file_contents)
        return str(ticker.upper()) in json_file

def mark_ticker_processed(ticker):
    current_json = {}
    with open(os.path.join(os.getcwd(), PROCESSED_STOCKS_FILE_NAME), "r") as processed_stocks_file:
        file_content = processed_stocks_file.read()
        if len(file_content) < 3:
            file_content = "{}"
        current_json = json.loads(file_content)
        processed_stocks_file.close()

    current_json[ticker] = True
    with open(os.path.join(os.getcwd(), PROCESSED_STOCKS_FILE_NAME), "w") as write_file:
        write_file.write(json.dumps(current_json))
        write_file.close()

def is_ticker_name_valid(ticker):
    if "$" in ticker:
        return False
    return True

def get_new_ticker():
    all_list_of_tickers = []
    nasdaq_tickers = get_nasdaq_tickers()
    other_tickers = get_nasdaq_other_tickers()
    nyse_tickers = get_nyse_tickers()

    all_list_of_tickers.append(nasdaq_tickers)
    all_list_of_tickers.append(other_tickers)
    all_list_of_tickers.append(nyse_tickers)

    random_ticker = ""
    while True:
        random_ticker = random.choice(random.choice(all_list_of_tickers))
        if not is_ticker_name_valid(random_ticker):
            continue
        if isinstance(random_ticker, list):
            random_ticker = random_ticker[0]
        if not has_ticker_been_processed(random_ticker):
            break
    return random_ticker

if __name__ == "__main__":
    if (len(sys.argv) != 4):
        print("USE THE FOLLOWING FLOW:")
        print("python3 make_challenges.py label num_days threshold")
        print("EXAMPLE")
        print("python3 make_challenges.py '1 Year' 270 .7")
        sys.exit()
    label = sys.argv[1]
    num_days = int(sys.argv[2])
    threshold = float(sys.argv[3])

    ticker = ""
    notable_stock_obj = None
    ticker_repeat_cond = True
    while ticker_repeat_cond:
        ticker = get_new_ticker()
        notable_stock_obj = NotableStock(ticker, num_days, threshold)
        if notable_stock_obj.is_stock_notable():
            ticker_repeat_cond = False

    # make folders and corresponding for each moment
    subfolders = ["statements", "historic_data", "info"]
    if not os.path.isdir(os.path.join(os.getcwd(), "stocks/" + label)):
        os.mkdir(os.path.join(os.getcwd(), "stocks/" + label))
    stock_path = os.path.join(os.getcwd(), "stocks/" + label + "/" + str(ticker))
    os.mkdir(stock_path)
    for moment in notable_stock_obj.get_notable_moments_date():
        ticker_date_path = os.path.join(stock_path, moment)
        os.mkdir(ticker_date_path)
        # sub directories
        for sub_dir in subfolders:
            new_path = os.path.join(ticker_date_path, sub_dir)
            os.mkdir(new_path)

    #
    # GET THE DATA AND WRITE
    #

    moments_to_delete = []
    any_stocks_downloaded = False
    for moment in notable_stock_obj.get_notable_moments_date():
        moment_idx = notable_stock_obj.get_notable_moments_date().index(moment)

        base_dir = os.path.join(stock_path, moment)

        # financial documents
        num_files = notable_stock_obj.get_recent_financial_documents_for_date(moment, label)
        if num_files == 0:
            moments_to_delete.append(moment)
            continue
        else:
            any_stocks_downloaded = True

        # go through each file and change to html
        statements_dir = os.path.join(base_dir, "statements")
        for subdir, dirs, files in os.walk(statements_dir):
            for file in files:
                if file.endswith(".txt"):
                    renamee = os.path.join(subdir, file)
                    # filter out unneccessary language in file
                    file_contents = ""
                    with open(renamee, "r") as read_file:
                        file_contents = read_file.read()
                        read_file.close()
                    try:
                        file_contents = file_contents[file_contents.lower().index("<html>"):]
                    except:
                        try:
                            file_contents = file_contents[file_contents.lower().index("<text>"):]
                        except:
                            pass

                    if "13-G" in renamee or "13g" in renamee:
                        file_contents = file_contents.replace("<TEXT>", "<html>")
                        file_contents = file_contents.replace("</TEXT>", "</html>")
                        file_contents = file_contents.replace("\n", "<br>\n")

                    new_file_contents = ""
                    is_parsing_document = False
                    temp_document = ""
                    add_document = True
                    for line in file_contents.split("\n"):
                        if is_parsing_document:
                            if "<FILENAME>" in line:
                                if ".htm" not in line:
                                    add_document = False
                                temp_document += line + "\n"
                                continue
                            else:
                                add_cond = True
                                if ".css" in line or ".js" in line or ".jpg" in line:
                                    add_cond = False
                                if add_cond:
                                    temp_document += line + "\n"

                                if "</DOCUMENT>" in line:
                                    if add_document:
                                        new_file_contents += temp_document
                                    is_parsing_document = False
                                    temp_document = ""
                                    add_document = True
                                continue
                        if "<DOCUMENT>" in line:
                            is_parsing_document = True
                            temp_document = line
                            continue

                        add_cond = True
                        if ".css" in line or ".js" in line or ".jpg" in line:
                            add_cond = False
                        if add_cond:
                            new_file_contents += line + "\n"

                    with open(renamee, "w") as write_file:
                        write_file.write(new_file_contents)
                        write_file.close()
                    pre, ext = os.path.splitext(renamee)
                    os.rename(renamee, pre + ".html")


        # historic data
        historic_data = notable_stock_obj.get_past_n_days_historic(moment, 1000)
        write_file_path = os.path.join(base_dir, "historic_data/historic_data.csv")
        with open(write_file_path, "w") as write_file:
            write_file.write(historic_data.to_csv(index=True))
            write_file.close()

        # info
        write_file_path = os.path.join(base_dir, "info/info.json")
        info = {}
        info["name"] = notable_stock_obj.get_company_name()
        info["ticker"] = ticker
        info["description"] = notable_stock_obj.get_company_description()
        info["result"] = notable_stock_obj.get_notable_moments_results()[moment_idx]
        info["percent_result"] = notable_stock_obj.get_notable_moments_percent()[moment_idx]
        info["industry"] = notable_stock_obj.get_company_industry()
        info["sector"] = notable_stock_obj.get_company_sector()
        with open(write_file_path, "w") as write_file:
            write_file.write(json.dumps(info))
            write_file.close()

    # delete folders which are of no use
    for moment in moments_to_delete:
        folder_to_remove = os.path.join(stock_path, moment)
        shutil.rmtree(folder_to_remove)

    if not any_stocks_downloaded:
        shutil.rmtree(stock_path)
    else:
        mark_ticker_processed(ticker)
        print("PROCESSED " + ticker)
