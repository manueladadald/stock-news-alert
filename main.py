import requests
from datetime import date, timedelta
from twilio.rest import Client
import data

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
twilio_sid = data.twilio_sid
twilio_token = data.twilio_token
twilio_number = data.twilio_number
account_sid = twilio_sid
auth_token = twilio_token
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://api.newscatcherapi.com/v2/search?"
api_key_alpha = data.api_key_alpha
news_key = data.news_key

parameters_1 = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK_NAME,
    "outputsize": "compact",
    "datatype": "json",
    "apikey": api_key_alpha
}

parameters_2 = {
    "q": COMPANY_NAME,
    "lang": "en",
    "sort_by": "date",
    "page_size": "3",
    "page": "1",
}

headers = {
    "x-api-key": data.x_api_key
}

response_1 = requests.get(STOCK_ENDPOINT, params=parameters_1)
response_1.raise_for_status()
data_1 = response_1.json()

yesterday_date = date.today() - timedelta(days=1)
while yesterday_date.weekday() >= 5:
    yesterday_date = yesterday_date - timedelta(days=1)

day_before_date = yesterday_date - timedelta(days=1)
while day_before_date.weekday() >= 5:
    day_before_date = day_before_date - timedelta(days=1)

yesterday = float(data_1["Time Series (Daily)"][str(yesterday_date)]["4. close"])
day_before = float(data_1["Time Series (Daily)"][str(day_before_date)]["4. close"])
variation = yesterday - day_before
percentage = (100 * variation) / yesterday

if percentage >= 5:
    response_2 = requests.get(NEWS_ENDPOINT, params=parameters_2, headers=headers)
    response_2.raise_for_status()
    data_2 = response_2.json()
    news = 3
    n = 0

    while news > 0:
        news_title = data_2["articles"][n]["title"]
        news_brief = data_2["articles"][n]["excerpt"]
        news_link = data_2["articles"][n]["link"]

        if yesterday > day_before:
            client = Client(account_sid, auth_token)
            message = client.messages \
                .create(
                body=f"{STOCK_NAME}: 🔺{round(percentage, 1)}%\n\nHeadline: {news_title}\n\nBrief: {news_brief}\n\nLink: {news_link}",
                from_=twilio_number,
                to=data.phone_number)

            print(message.status)
            n += 1
            news -= 1

        elif day_before > yesterday:
            client = Client(account_sid, auth_token)
            message = client.messages \
                .create(
                body=f"{STOCK_NAME}: 🔻{round(percentage, 1)}%\n\nHeadline: {news_title}\n\nBrief: {news_brief}\n\nLink: {news_link}",
                from_=twilio_number,
                to=data.phone_number)

            print(message.status)
            n += 1
            news -= 1
