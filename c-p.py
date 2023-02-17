
import requests
from pprint import pprint,pformat
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
import re



from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 

import logging

global OPEN_AI_API_KEY

OPEN_AI_API_KEY = "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"


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
	openai.api_key = OPEN_AI_API_KEY


	prompt="Extract from article the entities such as stocks or cryptocurrency and predict if price of it will go up or down and please write it in the following format:\ncurrency, prediction, level of certinty in percents generating json response:\n\n\n🔥Hi, friends! Today is a day of meme coins. DOGE pumps by 10%. I'm sure that if we have the bullish BTC , DOGE and SHIB will make +20% at least.\n\nAll this growth is related to rumors on Twitter . Lots of news was published about accepting crypto as the payment method in this social network. Of course, DOGE is the first on the list to PUMP. As usual, SHIB is growing too.\n\nI check the info about the biggest holders. The same as DOGE, SHIB is absolutely centralized coin. 41% of the total supply is accumulated in 1 wallet.\n\n📊 MY TRADING PLAN FOR SHIB:\n1. false breakout of $0.0114-0.0116 value area\n2. volume growth\n3. bullish BTC\n\n🚩The next possible entry point is during the test of $0.012-0.0121 as the support.\n\n✅ MY TARGETS FOR SHIB:\n🔥 $0.0131 - the key level, local high\n🔥 $0.0137 - the key level\n🔥 $0.0152 -the key level and global high\n\nTraders, do you believe in the bright future of such crypto as SHIB, DOGE, FLOKI? Share your thought in the comments!\n\n💻Friends, press the \"boost\"🚀 button, write comments and share with your friends - it will be the best THANK YOU.\n\nP.S. Personally, I open an entry if the price shows it according to my strategy.\nAlways do your analysis before making a trade.\n\n{ \"SHIB\": { \"prediction\": \"up\", \"level_of_certainty\": \"90%\" }, \"DOGE\": { \"prediction\": \"up\", \"level_of_certainty\": \"80%\" }, \"FLOKI\": { \"prediction\": \"up\", \"level_of_certainty\": \"70%\" } }\n\n#######\n\nExtract from article the entities such as stocks or cryptocurrency and predict if price of it will go up or down and please write it in the following format:\ncurrency, prediction, level of certinty in percents generating json response:\n\nAvalanche ‘bull trap’ risks pushing AVAX price down by 30% in February\nThe price of AVAX has more than doubled in 2023, but a growing divergence between several key metrics hints at a bearish reversal ahead.\n\n1775\nTotal views\n5\nTotal shares\nListen to article\n\n2:40\nAvalanche ‘bull trap’ risks pushing AVAX price down by 30% in FebruaryALTCOIN WATCH\nOwn this piece of history\nCollect this article as an NFT\n\n\n\nAvalanche \nAVAX\n\ntickers down\n$21.33\n\n bulls should brace themselves for impact led by a growing divergence between several key indicators on the daily-timeframe chart.\n\nAVAX price chart paints bearish divergence\nThe daily AVAX chart shows a classic bearish divergence between its price and relative strength index (RSI), a momentum oscillator forming since Jan. 11.\n\nIn other words, the price of AVAX has been making higher highs since the said date. But, on the other hand, the coin’s daily RSI has been forming lower highs. This divergence suggests a slowdown in the momentum of the AVAX/USD pair, which may lead to a price reversal.\n\n\nAVAX/USD daily price chart. Source: TradingView\nIn addition, the declining volumes during the course of AVAX’s ongoing uptrend also hint at the same bearish cues.\n\nThe price-RSI and price-volume divergences appear as AVAX price continues its 2023 uptrend. Notably, Avalanche has rallied by more than 100% year-to-date to $22.50 as of Feb. 2, helped by improving risk-on sentiments and news of its partnership with Amazon.\n\nAdvertisement\nMarkets Pro: The Fastest Newsfeed In Crypto Now Available To The Public >>>\nOn Jan. 31, Avalanche partnered with Intain, a structured finance platform that facilitates more than $5.5 billion in assets across more than 25 deals to run its digital marketplace IntainMARKETS via IntainMARKETS Subnet.\n\nThe price of AVAX rallied nearly 20% after the announcement.\n\nAVAX’s price risks drop 30% in February\nAVAX’s price has successfully closed above two key resistance levels: a multi-month descending trendline (blacked) and its 200-day exponential moving average (200-day EMA; the blue wave) during the ongoing rally. \n\n\nAVAX/USD daily price chart. Source: TradingView\nAvalanche now eyes a breakout above $22.75, which has been serving as resistance since August 2022, for a potential breakout to $30 as its next upside target. This level also coincides with the falling wedge breakout target discussed in this analysis.\n\nIn other words, an approximately 30% gain from the current price levels. \n\nConversely, a pullback from the resistance level, fueled by the bearish divergence indicators discussed above, could send AVAX’s price toward its 50-day EMA (the red wave) at approximately $15–$16, down about 30% from current prices.\n\n{ \"AVAX\": { \"prediction\": \"down\", \"level_of_certainty\": \"70%\" } }\n\n#######\n\nExtract from article the entities such as stocks or cryptocurrency and predict if price of it will go up or down and please write it in the following format:\ncurrency, prediction, level of certinty in percents generating json response:\n",

	prompt = str(prompt) + str(article)

	response = openai.Completion.create(
	model="text-davinci-003",
	prompt=prompt,
	temperature=0,
	max_tokens=500,
	top_p=1,
	frequency_penalty=0,
	presence_penalty=0
	)
	
	text = response["choices"][0]["text"]
	
	
	return text 

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


def parse_json_from_string(string_with_json):
	# Example string containing JSON object and other information
	print("string_with_json=",string_with_json)
	# Define regular expression pattern to match JSON object
	json_pattern = r'{\s*"([^"]*)"\s*:\s*({.*?})\s*}'




	# Search for JSON object in string
	json_match = re.search(json_pattern, string_with_json)

	# Extract JSON object if match is found
	if json_match:
		json_object = json.loads(json_match.group())
		print(json_object)
	else:
		print("No JSON object found in string")

	return json_object


# Function to retrieve the next unanalyzed article from the crypto_news table
def get_article_to_analyse():
    # Run an infinite loop until an unanalyzed article is found
    while True:
        # Define the SQL query to select the next unanalyzed article from the crypto_news table
        query = """SELECT link, title, article FROM crypto_news WHERE analyzed = "No" LIMIT 1;"""

        # Connect to the database and execute the query
        DB = sqlite3.connect(DATABASE)
        c = DB.cursor()
        res  = c.execute(query)
        response = res.fetchone()

        # If there are no unanalyzed articles, close the database connection and wait for 2 seconds before checking again
        if response is None:
            DB.close()
            time.sleep(2)
        # If an unanalyzed article is found, extract the link, title and article text and send it to GPT for analysis
        else:
            link, title, article = response
            text = str(title) +"\n" + str(article)
            print("text=",text)
            data = gpt_request(text)
            parsed_data = parse_json_from_string(data)

            # For each coin detected in the article, retrieve its predicted value and level of certainty from the GPT response and insert it into the crypto_prediction table
            for coin, values in parsed_data.items():
                prediction = values["prediction"]
                certainty = values["level_of_certainty"]
                print(f"Coin: {coin}, Prediction: {prediction}, Certainty: {certainty}")
                insert_values_to_crypto_prediction(link, coin, prediction, certainty)

            # Update the analyzed column of the crypto_news table for the current article to indicate that it has been analyzed
            c.execute("UPDATE crypto_news SET analyzed='YES' WHERE link=?", (link,))
            DB.commit()
            DB.close()


# Function to retrieve a list of reviews from the TradingView ideas page
def get_reviews_list():
    # Define the URL of the TradingView ideas page and make a GET request to retrieve its HTML content
    idea_page = "https://www.tradingview.com/markets/cryptocurrencies/ideas/" #?sort=recent"
    page = requests.get(idea_page)

    # Extract the HTML content from the response
    html = page.content

    # Create a BeautifulSoup object from the HTML content
    soup = BeautifulSoup(html, "html.parser")

    # Initialize an empty list to store the reviews
    reviews_list = []

    # Find all elements on the page with a specific class that contains the review description and the user who posted it
    descriptions = soup.find_all(class_="tv-widget-idea__title apply-overflow-tooltip js-widget-idea__popup")	
    users = soup.find_all(class_="tv-card-user-info__main-wrap js-userlink-popup", href=True)

    # Loop through the description and user elements and append them as key-value pairs to the reviews_list list
    for user, description in zip(users, descriptions):
        reviews_list.append({'user_link': user['href'], 'description_link': description['href']})

    # Print the reviews_list using pformat for pretty formatting, and return it along with a success flag
    print("reviews_list:", pformat(reviews_list))
    return True, reviews_list


# Function to retrieve user information from a TradingView user profile page
def get_user_info(user_url):
    # Append the user URL to the TradingView base URL and make a GET request to retrieve its HTML content
    user_url = "https://www.tradingview.com" + user_url
    page = requests.get(user_url)

    # Extract the HTML content from the response
    html = page.content

    # Create a BeautifulSoup object from the HTML content
    soup = BeautifulSoup(html, "html.parser")

    # Find all elements on the page with a specific class that contains the user's reputation and follower count
    elements = soup.find_all(class_="tv-profile__social-item-value")

    # Extract the reputation and follower count from the elements and convert them to floats
    reputation = float(elements[0].text)
    followers = float(elements[4].text)

    # Return the reputation and follower count as a tuple
    return reputation, followers


# Function to retrieve the full descriptions for a list of TradingView idea reviews
def get_full_descriptions_reveiw():
    # Loop continuously to retrieve the reviews list until it is successfully retrieved
    while True:
        done, reviews_list = get_reviews_list()
        if done:
            # Create a headless Chrome webdriver
            options = webdriver.ChromeOptions() 
            options.add_argument('--headless')
            with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) as driver: 
                # Loop through each review in the reviews list
                for review in reviews_list:
                    # Construct the URL for the review and check if it is already in the database
                    url = str("https://www.tradingview.com" + review['description_link'])
                    if check_link_not_in_database(url):
                        # Print the URL for debugging purposes
                        print("url=",url)
                        
                        # Extract the user information for the review and open the review URL in the webdriver
                        user = review['user_link']
                        reputation, followers = get_user_info(user)
                        driver.get(url)
                        
                        # Extract the title and description of the review from the HTML content of the page
                        html_source = driver.page_source
                        soup = BeautifulSoup(html_source, "html.parser")
                        title = soup.find(class_="tv-chart-view__title-name js-chart-view__name")
                        title= title.text
                        description = soup.find(class_="tv-chart-view__description selectable")
                        description = description.text
                        
                        # Print the title and description for debugging purposes
                        print("title_time",title)
                        print("description",description)
                        
                        # Insert the review information into the database
                        insert_values_to_crypto_news("TradingView_Ideas", url, title, description, 'No', user=user, reputation=reputation, followers=followers)
                
                # Wait for 2 minutes before checking for new reviews
                time.sleep(60*2)
		

		# Note: Selenium is used in this function to render JavaScript code on a web page. 
		# Although it may seem like a heavy way to scrape the data, it may be necessary in cases where the data cannot be obtained using more lightweight libraries 
		# like requests_html. 

		# In particular, certain websites may require JavaScript to load before the desired content can be scraped,
		#  and this can be achieved using tools like Selenium which can render and interact with web pages like a user would. 
		# While Selenium may have some performance drawbacks, it is a useful tool when other methods for extracting data are not available.



def get_news():
	# The URL of the webpage to be scraped
	news_link = "https://www.tradingview.com/markets/cryptocurrencies/news/"
	
	# Send a GET request to the webpage and retrieve the HTML content
	page = requests.get(news_link)
	html = page.content

	# Initialize an empty list to store the links to the news articles
	news_list = []

	# Parse the HTML content using BeautifulSoup
	soup = BeautifulSoup(html, "html.parser")

	# Find all elements with a specific class and a href attribute, which in this case correspond to the links to the news articles
	articles = soup.find_all(class_="card-gaCYEutU", href=True)

	# For each link to a news article, add it to the list of news articles and print the link
	for a in articles:
		news_list.append(str(a["href"]))
		print(a["href"])

	# Return a tuple indicating that the function completed successfully, along with the list of news articles
	return True, news_list


# This function parse_news() uses a session to access the https://www.tradingview.com website and scrape news articles. 
# It is doing this because in the past, the user was banned from the platform they were scraping. 
# By using a session, they can simulate a real user accessing the site which can help avoid detection and ban.

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
articles_analyzer_thread = pool.submit(get_article_to_analyse)
parsed_news_thread.done()
parsed_reviews_thread.done()
articles_analyzer_thread.done()


