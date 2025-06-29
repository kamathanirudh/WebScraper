from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import re
import logging
<<<<<<< HEAD
import os

from configparser import ConfigParser
config = ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config.read(config_path)
=======

from configparser import ConfigParser
config = ConfigParser()
config.read("webscraping\\config.ini")
>>>>>>> 1e2c8b76114b1faa53a772a4827bb1f0588bfdc4

# Configure logging for this module
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger_et = logging.getLogger(__name__)

# Initialize an empty DataFrame
df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', 'Main URL used'])

def scrape_news(url):
    """
    Scrapes individual news article details and updates the global DataFrame `df`.

    Args:
    - url (str): The URL of the page to scrape.

    Returns:
    - None
    """
    global df

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for failed requests
        soup = BeautifulSoup(response.content, "html.parser")

        flag = False
        while not flag:
            article = soup.find('div', class_=config.get("economictimes", "article_class").strip())
            h3_tag = soup.find(config.get("economictimes", "title_size").strip())

            if h3_tag:
                a_tag = article.find(config.get("economictimes", "anchor_tag").strip())
                href = a_tag.get('href')

            if a_tag:
                text = h3_tag.text.strip()
                if href.startswith("/"):
                    href = config.get("economictimes", "base_link").strip() + href

                story_date_div = article.find('div', class_=config.get("economictimes", "date_div_class"))

                if story_date_div:
                    time_tag = story_date_div.find('time')

                if time_tag:
                    date_time_str = time_tag.text.strip()
                    pattern = config.get("economictimes", "regex_pattern_for_date")
                    matches = re.match(pattern, date_time_str)

                    if matches:
                        day = matches.group(1).strip()
                        month = matches.group(2).strip()
                        year = matches.group(3).strip()
                        time = matches.group(4).strip()
                        date_string = f"{day} {month} {year} {time}"
                        datetime_object = datetime.strptime(date_string, '%d %b %Y %I:%M%p')
                        logger_et.info(f"Scraped article: {text}")

                        new_row = [text, href, datetime_object, url]

                        if df.empty:
                            df.loc[len(df)] = new_row
                            flag = True
                        else:
                            for index, row in df.iterrows():
                                if text in row["Headline"]:
                                    flag = True
                                    break

                            if not flag:
                                df.loc[len(df)] = new_row
    except requests.exceptions.RequestException as e:
        logger_et.error(f"Error scraping {url}: {e}")

def scrape_economictimes_news():
    """
    Scrapes news articles from Economic Times using the configured URL.

    Returns:
    - None
    """
    url = config.get("economictimes", "base_url_scraped")

    try:
        page = requests.get(url)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, 'html.parser')
        scrape_news(url)
        df.sort_values(by='DateStamp', ascending=False, inplace=True)
    except requests.exceptions.RequestException as e:
        logger_et.error(f"Error fetching {url}: {e}")

def final_scrape_economictimes():
    """
    Final function to scrape Economic Times news and return the updated DataFrame.

    Returns:
    - pd.DataFrame: Updated DataFrame containing scraped news articles.
    """
    global df
    df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', "Main URL used"])

    try:
        scrape_economictimes_news()
    except Exception as e:
        logger_et.error(f"Error in scraping Economic Times: {e}")

    return df