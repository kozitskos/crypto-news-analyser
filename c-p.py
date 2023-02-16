from ntpath import realpath
from posixpath import dirname
import requests
from pprint import pprint,pformat
from lxml import html
import os
import openai
from bs4 import BeautifulSoup
import itertools
import time
import sqlite3
import os
from os.path import dirname, realpath
from concurrent.futures import ThreadPoolExecutor
import json



from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 

import logging


def create_database():
	crypto_news = """CREATE TABLE crypto_news (
	  source TEXT,
	  link TEXT,
	  user TEXT,
	  reputation int,
	  followers int,
	  title TEXT,
	  article TEXT,
	  analyzed TEXT
	);"""

	crypto_prediction = """CREATE TABLE crypto_prediction (
	  link TEXT,
	  asset TEXT,
	  prediction TEXT,
	  score int
	);"""

	logging.warning("DB not found")
	DB = sqlite3.connect(DATABASE)
	c = DB.cursor()
	c.execute(crypto_news)
	c.execute(crypto_prediction)
	DB.commit()
	DB.close()
	
	logging.info("DB created")

global DATABASE
CURR_DIR= dirname(realpath(__file__))
DATABASE=os.path.join(CURR_DIR, "data.db")

if os.path.isfile(DATABASE) is False:
	create_database()

def gpt_request(article):
	openai.api_key = "api_key"


	prompt="Extract from article the entities such as stocks or cryptocurrency and predict if price of it will go up or down and please write it in the following format:\ncurrency, prediction, level of certinty in percents generating json response:\n\n\n🔥Hi, friends! Today is a day of meme coins. DOGE pumps by 10%. I'm sure that if we have the bullish BTC , DOGE and SHIB will make +20% at least.\n\nAll this growth is related to rumors on Twitter . Lots of news was published about accepting crypto as the payment method in this social network. Of course, DOGE is the first on the list to PUMP. As usual, SHIB is growing too.\n\nI check the info about the biggest holders. The same as DOGE, SHIB is absolutely centralized coin. 41% of the total supply is accumulated in 1 wallet.\n\n📊 MY TRADING PLAN FOR SHIB:\n1. false breakout of $0.0114-0.0116 value area\n2. volume growth\n3. bullish BTC\n\n🚩The next possible entry point is during the test of $0.012-0.0121 as the support.\n\n✅ MY TARGETS FOR SHIB:\n🔥 $0.0131 - the key level, local high\n🔥 $0.0137 - the key level\n🔥 $0.0152 -the key level and global high\n\nTraders, do you believe in the bright future of such crypto as SHIB, DOGE, FLOKI? Share your thought in the comments!\n\n💻Friends, press the \"boost\"🚀 button, write comments and share with your friends - it will be the best THANK YOU.\n\nP.S. Personally, I open an entry if the price shows it according to my strategy.\nAlways do your analysis before making a trade.\n\n{ \"SHIB\": { \"prediction\": \"up\", \"level_of_certainty\": \"90%\" }, \"DOGE\": { \"prediction\": \"up\", \"level_of_certainty\": \"80%\" }, \"FLOKI\": { \"prediction\": \"up\", \"level_of_certainty\": \"70%\" } }\n\n#######\n\nExtract from article the entities such as stocks or cryptocurrency and predict if price of it will go up or down and please write it in the following format:\ncurrency, prediction, level of certinty in percents generating json response:\n\nAvalanche ‘bull trap’ risks pushing AVAX price down by 30% in February\nThe price of AVAX has more than doubled in 2023, but a growing divergence between several key metrics hints at a bearish reversal ahead.\n\n1775\nTotal views\n5\nTotal shares\nListen to article\n\n2:40\nAvalanche ‘bull trap’ risks pushing AVAX price down by 30% in FebruaryALTCOIN WATCH\nOwn this piece of history\nCollect this article as an NFT\n\n\n\nAvalanche \nAVAX\n\ntickers down\n$21.33\n\n bulls should brace themselves for impact led by a growing divergence between several key indicators on the daily-timeframe chart.\n\nAVAX price chart paints bearish divergence\nThe daily AVAX chart shows a classic bearish divergence between its price and relative strength index (RSI), a momentum oscillator forming since Jan. 11.\n\nIn other words, the price of AVAX has been making higher highs since the said date. But, on the other hand, the coin’s daily RSI has been forming lower highs. This divergence suggests a slowdown in the momentum of the AVAX/USD pair, which may lead to a price reversal.\n\n\nAVAX/USD daily price chart. Source: TradingView\nIn addition, the declining volumes during the course of AVAX’s ongoing uptrend also hint at the same bearish cues.\n\nThe price-RSI and price-volume divergences appear as AVAX price continues its 2023 uptrend. Notably, Avalanche has rallied by more than 100% year-to-date to $22.50 as of Feb. 2, helped by improving risk-on sentiments and news of its partnership with Amazon.\n\nAdvertisement\nMarkets Pro: The Fastest Newsfeed In Crypto Now Available To The Public >>>\nOn Jan. 31, Avalanche partnered with Intain, a structured finance platform that facilitates more than $5.5 billion in assets across more than 25 deals to run its digital marketplace IntainMARKETS via IntainMARKETS Subnet.\n\nThe price of AVAX rallied nearly 20% after the announcement.\n\nAVAX’s price risks drop 30% in February\nAVAX’s price has successfully closed above two key resistance levels: a multi-month descending trendline (blacked) and its 200-day exponential moving average (200-day EMA; the blue wave) during the ongoing rally. \n\n\nAVAX/USD daily price chart. Source: TradingView\nAvalanche now eyes a breakout above $22.75, which has been serving as resistance since August 2022, for a potential breakout to $30 as its next upside target. This level also coincides with the falling wedge breakout target discussed in this analysis.\n\nIn other words, an approximately 30% gain from the current price levels. \n\nConversely, a pullback from the resistance level, fueled by the bearish divergence indicators discussed above, could send AVAX’s price toward its 50-day EMA (the red wave) at approximately $15–$16, down about 30% from current prices.\n\n{ \"AVAX\": { \"prediction\": \"down\", \"level_of_certainty\": \"70%\" } }\n\n#######\n\nExtract from article the entities such as stocks or cryptocurrency and predict if price of it will go up or down and please write it in the following format:\ncurrency, prediction, level of certinty in percents generating json response:\n",

	prompt = str(prompt) + str(article)

	response = openai.Completion.create(
	model="text-davinci-003",
	prompt=prompt,
	temperature=0,
	max_tokens=256,
	top_p=1,
	frequency_penalty=0,
	presence_penalty=0
	)
	
	text = response["choices"][0]["text"]
	text_string = str(text)
	edited_text = text_string.replace("\n", "").replace("\\n\\n", "")

	
	return edited_text 

def check_link_not_in_database(link):
	DB = sqlite3.connect(DATABASE)
	c = DB.cursor()
	query = (f"SELECT link FROM crypto_news WHERE link = \"{link}\" LIMIT 1;")
	res = c.execute(query)
	if res.fetchone() is None:
		DB.close()
		print("True")
		return True
	else:
		DB.close()
		print("False")
		return False


def insert_values_to_crypto_news(source, link, title, article, analyzed, user=None, reputation=None, followers=None):
	query = """INSERT INTO crypto_news (source, link, user, reputation, followers, title, article, analyzed) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
	DB = sqlite3.connect(DATABASE)
	c = DB.cursor()
	data = (source, link, user, reputation, followers, title, article, analyzed)
	c.execute(query, data)
	DB.commit()
	DB.close()

def insert_values_to_crypto_prediction(link, asset, prediction, score):
	query = """INSERT INTO crypto_prediction (link, asset, prediction, score) VALUES (?, ?, ?, ?);"""
	DB = sqlite3.connect(DATABASE)
	c = DB.cursor()
	data = (link, asset, prediction, score)
	c.execute(query, data)
	DB.commit()
	DB.close()

def get_article_to_analyse():
	while True:
		query = """SELECT link, title, article FROM crypto_news WHERE analyzed = "No" LIMIT 1;"""
		DB = sqlite3.connect(DATABASE)
		c = DB.cursor()
		res  = c.execute(query)
		response = res.fetchone()
		print("response=",response)
		if response is None:
			DB.close()
			time.sleep(2)
		else:
			link, title, article = response
			text = str(title) +"\n" + str(article)
			print("text=",text)
			data = gpt_request(text)
			print("data=",data)
			parsed_data = json.loads(data)

			print(len(parsed_data))

			for coin, values in parsed_data.items():
				prediction = values["prediction"]
				certainty = values["level_of_certainty"]
				print(f"Coin: {coin}, Prediction: {prediction}, Certainty: {certainty}")
				insert_values_to_crypto_prediction(link, coin, prediction, certainty)
			# insert_values_to_crypto_prediction(link, "BTC", "up", "85%")


			c.execute("UPDATE crypto_news SET analyzed='YES' WHERE link=?", (link,))
			DB.commit()
			DB.close



def get_reviews_list():
	idea_page = "https://www.tradingview.com/markets/cryptocurrencies/ideas/" #?sort=recent"
	page = requests.get(idea_page)


	html = page.content

	soup = BeautifulSoup(html, "html.parser")

	reviews_list = []
		# Find lements with a specific class
	descriptions = soup.find_all(class_="tv-widget-idea__title apply-overflow-tooltip js-widget-idea__popup")	
	users = soup.find_all(class_="tv-card-user-info__main-wrap js-userlink-popup", href=True)

	for user,description in zip(users, descriptions):
		reviews_list.append({'user_link': user['href'], 'description_link': description['href']})
	print("reviews_list:",pformat(reviews_list))
	return True, reviews_list

def get_user_info(user_url):
	user_url = "https://www.tradingview.com" + user_url
	page = requests.get(user_url)

	# Parse the HTML content of the page
	# tree = html.fromstring(page.content)

	html = page.content

	soup = BeautifulSoup(html, "html.parser")

	# Find lements with a specific class
	elements = soup.find_all(class_="tv-profile__social-item-value")


	reputation = float(elements[0].text)
	followers = float(elements[4].text)

	return reputation, followers


def get_full_descriptions_reveiw():
	while True:
		done, reviews_list = get_reviews_list()
		if done:
			options = webdriver.ChromeOptions() 
			options.add_argument('--headless')
			with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) as driver: 
				for review in reviews_list:
					url = str("https://www.tradingview.com" + review['description_link'])
					if check_link_not_in_database(url):
						print("url=",url)
						user = review['user_link']
						reputation, followers = get_user_info(user)
						driver.get(url)
						html_source = driver.page_source
						soup = BeautifulSoup(html_source, "html.parser")
						title = soup.find(class_="tv-chart-view__title-name js-chart-view__name")
						title= title.text
						description = soup.find(class_="tv-chart-view__description selectable")
						description = description.text
						print("title_time",title)
						print("description",description)
						insert_values_to_crypto_news("TradingView_Ideas", url, title, description, 'No', user=user, reputation=reputation, followers=followers)
				
				time.sleep(60*2)




def get_news():
	news_link = "https://www.tradingview.com/markets/cryptocurrencies/news/"
	page = requests.get(news_link)

	html = page.content
	news_list = []
# Use BeautifulSoup to parse the HTML
	soup = BeautifulSoup(html, "html.parser")
	articles = soup.find_all(class_="card-gaCYEutU", href=True)
	for a in articles:
		news_list.append(str(a["href"]))
		print(a["href"])

	return True, news_list
### MAIN PROGRAM ###
def parse_news():
	while True:
		done, news = get_news()
		if done:
			headers = {
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}

			session = requests.Session()
			session.headers.update(headers)


			for n in news:
				time.sleep(1)
				news_link = str("https://www.tradingview.com" + str(n))
				if check_link_not_in_database(news_link):
					print(news_link)
					page = session.get(news_link)
					if page.status_code == 200:

						# Parse the HTML content of the page
						# tree = html.fromstring(page.content)

						html = page.content
						news_list = []
					# Use BeautifulSoup to parse the HTML
						soup = BeautifulSoup(html, "html.parser")
						
						title = soup.find(class_="title-jEK_kEtx")
						title = title.text
						body = soup.find(class_="body-jEK_kEtx body-op4L5uvo content-op4L5uvo")
						if body is not None:
							article = body.text
							title_and_article = str(title) + "/n" + str(article)
							print(article)
							source = soup.find(class_="logoContainer-_D5mEkne")
							source = source.a["href"]
							print("source=",source)
							insert_values_to_crypto_news(str(source), str(news_link), str(title), str(article), 'No')
					else:
						logging.warning("Request failed with status code:", page.status_code, "url:", page)
			time.sleep(60*2)

pool = ThreadPoolExecutor(max_workers=3)
parsed_news_thread = pool.submit(parse_news)
parsed_reviews_thread = pool.submit(get_full_descriptions_reveiw)
articles_analyzed = pool.submit(get_article_to_analyse)
parsed_news_thread.done()
parsed_reviews_thread.done()
articles_analyzed.done()


