import datetime
import requests

## for data processing
import numpy as np
import pandas as pd


class DateGenerator():

    ## Create date array
    def date_generate(self, start_date, end_date):
        ## make sure in right format
        start = datetime.datetime.strptime(start_date, "%Y/%m/%d")
        end = datetime.datetime.strptime(end_date, "%Y/%m/%d")
        date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days)]
        return np.array([i.strftime("%Y/%m/%d") for i in date_generated])

    def date_segment(self, interval, day_data):
        ## avoid division error
        num_of_day = day_data.shape[0]
        num_of_rest = num_of_day % interval

        ## extract days input to data
        if num_of_rest != 0:

            main_days = num_of_day - num_of_rest
            main = day_data[:main_days]
            rest = day_data[main_days:]

            main = main.reshape(-1, interval)

            interval_day_main_s = main[:, 0]  ## list of data's date
            interval_day_main_e = main[:, -1]

            interval_day_rest = rest[[0, -1]]  ## list of data's date which cannot be divided

            ## add rest into the array
            interval_day_main_s = np.append(interval_day_main_s, interval_day_rest[0])
            interval_day_main_e = np.append(interval_day_main_e, interval_day_rest[1])

        else:  ## remainder = 0
            main = day_data.reshape(-1, interval)

            interval_day_main_s = main[:, 0]  ## list of data's date
            interval_day_main_e = main[:, -1]

        return interval_day_main_s, interval_day_main_e


class Crawler():

    def crawl_to_text(self, URL, data, file_name):
        re = requests.post(URL, data=data)

        with open(file_name, "w") as F:
            F.write(re.text)

    ## transfer to df
    def to_Dataframe(self, file_name):
        new_lines = list()

        with open(file_name, "r") as F:
            line = F.readlines()

            for i in line:
                new_line = "," + i  ## convert to csv readable
                new_lines.append(new_line)

        with open(file_name, "w") as F:
            F.write(' '.join(str(i) for i in new_lines))

        df = pd.read_csv(file_name, index_col=0)
        ## change the column
        col = df.columns[1:]
        df = df.iloc[:, :-1]
        df.columns = col

        return df

def main():
    df = pd.DataFrame()
    URL = "https://www.taifex.com.tw/cht/3/dlFutDataDown"
    data = {
        "down_type": 1,
        "commodity_id": "T5F",
        "queryStartDate": "2020/07/30",
        "queryEndDate": "2020/08/08",
    }

    Date = DateGenerator()
    date_inside = Date.date_generate(start_date="2015/06/30", end_date="2020/08/08")
    start_day_array, end_day_array  = Date.date_segment(interval = 20, day_data=date_inside)


    for i in range(len(start_day_array)):
        data["queryStartDate"] = start_day_array[i]
        data["queryEndDate"] = end_day_array[i]

        crawler = Crawler()
        crawler.crawl_to_text(URL, data, "T5F.txt")
        tmp_next = crawler.to_Dataframe("T5F.txt")
        df = pd.concat([df, tmp_next], axis = 0)

        print(start_day_array[i], end_day_array[i], " complete")

    df.to_csv("T5F.csv")


if __name__ == '__main__':
    main()


