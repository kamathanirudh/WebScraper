from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import pytz
import logging
<<<<<<< HEAD
import os
=======
>>>>>>> 1e2c8b76114b1faa53a772a4827bb1f0588bfdc4
from configparser import ConfigParser

# Read configuration settings
config = ConfigParser()
<<<<<<< HEAD
config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config.read(config_path)
=======
config.read("webscraping\\config.ini")
>>>>>>> 1e2c8b76114b1faa53a772a4827bb1f0588bfdc4

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger_gn_24h = logging.getLogger(__name__)

# Initialize df as an empty DataFrame
df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', "Main Link Used"])

def scrape_news(article, url):
    """
    Scrapes the given article for headline, link, and timestamp.

    Args:
    - article (bs4.element.Tag): The article tag to scrape.
    - url (str): The main URL used for scraping.

    Returns:
    - None
    """
    global df
    real_time = None  # Initialize real_time here to handle the scope

    try:
        # Extract the main div and anchor elements containing the headline and link
        div_element = article.find('div', class_=config.get("googlenews_continous", "article_div_class"))
        anchor_element = div_element.find('a', class_=config.get("googlenews_continous", "anchor_tag_class"))
        relative_link = anchor_element['href']
        absolute_link = "https://news.google.com/" + relative_link  # Construct the absolute link

        # Extract the date and time information
        div_date_element = article.find('div', class_=config.get("googlenews_continous", "date_div_class"))
        date_element = div_date_element.find('time', class_=config.get("googlenews_continous", "time_element_class"))
        datetime_value = date_element.get('datetime')
        
        # Convert the datetime to IST (Indian Standard Time)
        ist_tz = pytz.timezone('Asia/Kolkata')
        dt = datetime.strptime(datetime_value, '%Y-%m-%dT%H:%M:%SZ')
        ist_dt = dt.replace(tzinfo=pytz.utc).astimezone(ist_tz)
        real_time = ist_dt.strftime('%Y-%m-%d %H:%M:%S %Z')

        # Check if the article link already exists in the DataFrame
        if df.empty or absolute_link not in df['Link'].values:
            # Add the new article only if it's newer than the most recent one in the DataFrame
            if df.empty or (real_time and real_time > df['DateStamp'].max()):
                new_row = [anchor_element.text, absolute_link, real_time, url]
                df.loc[len(df)] = new_row
                df = df.sort_values(by='DateStamp', ascending=False)  # Sort by DateStamp in descending order
                logger_gn_24h.info(f"Scraped article: {anchor_element.text}")
                logger_gn_24h.debug("Sorted Dataframe")
    except Exception as e:
        logger_gn_24h.error(f"Error scraping article: {e}")

def scrape_google_news():
    """
    Scrapes Google News for the latest articles.

    Args:
    - None

    Returns:
    - None
    """
    try:
        url = config.get("googlenews_continous", "base_url_scraped")  # Get the base URL for scraping
        page = requests.get(url)  # Send a GET request to the URL
        soup = BeautifulSoup(page.text, 'html.parser')  # Parse the HTML content using BeautifulSoup
        
        # Find all articles in the parsed HTML
        articles = soup.find_all('article', class_=config.get("googlenews_continous", "article_class"))
        
        for article in articles:
            scrape_news(article, url)  # Scrape each article found
    except Exception as e:
        logger_gn_24h.error(f"Error scraping Google News: {e}")

def final_scrape_googlenews():
    """
    Clears the existing DataFrame and performs a fresh scrape for Google News articles.

    Args:
    - None

    Returns:
    - pd.DataFrame: Updated DataFrame containing the scraped news articles.
    """
    global df
    df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', "Main Link Used"])  # Initialize a new DataFrame
    scrape_google_news()  # Perform the scrape
    return df  # Return the updated DataFrame
