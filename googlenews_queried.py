from bs4 import BeautifulSoup
import requests
import pandas as pd
import pytz
from datetime import datetime
from urllib.parse import quote
import logging
from configparser import ConfigParser

# Read configuration settings
config = ConfigParser()
config.read("webscraping\\config.ini")

# Configure logging for this module
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger_gnq = logging.getLogger(__name__)

# Initialize an empty DataFrame
df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', 'Search Query', 'Number of days'])

def scrape_news(article, search_query, num_days):
    """
    Scrapes individual news article details and updates the global DataFrame `df`.

    Args:
    - article (BeautifulSoup tag): The article tag containing news details.
    - search_query (str): The search query used for scraping.
    - num_days (int): Number of days parameter used for scraping.

    Returns:
    - None
    """
    global df

    try:
        # Extract relevant elements from the article
        div_element = article.find('div', class_=config.get("googlenews_query", "article_div_class"))
        anchor_element = div_element.find('a', class_=config.get("googlenews_query", "anchor_tag_class"))
        relative_link = anchor_element['href']
        absolute_link = config.get("googlenews_query", "base_link") + relative_link

        # Check if the link already exists in the DataFrame
        if absolute_link not in df['Link'].values:
            div_date_element = article.find('div', class_=config.get("googlenews_query", "date_div_class"))
            date_element = div_date_element.find('time', class_=config.get("googlenews_query", "time_element_class"))
            datetime_value = date_element.get('datetime')

            # Convert datetime to IST timezone
            ist_tz = pytz.timezone('Asia/Kolkata')
            dt = datetime.strptime(datetime_value, '%Y-%m-%dT%H:%M:%SZ')
            ist_dt = dt.replace(tzinfo=pytz.utc).astimezone(ist_tz)
            real_time = ist_dt.strftime('%Y-%m-%d %H:%M:%S %Z')

            # Prepare new row for DataFrame
            new_row = [anchor_element.text, absolute_link, real_time, search_query, num_days]

            # Update DataFrame and sort by DateStamp
            df.loc[len(df)] = new_row
            df = df.sort_values(by='DateStamp', ascending=False)
            logger_gnq.info(f"Scraped article: {anchor_element.text}")
            logger_gnq.debug("Sorted Dataframe")

    except AttributeError as e:
        logger_gnq.error(f"Error scraping article element: {e}")
    except Exception as e:
        logger_gnq.error(f"Unexpected error: {e}")

def scrape_google_news2(search_query, num_days):
    """
    Scrapes Google News based on the provided search query and number of days.

    Args:
    - search_query (str): The search query for Google News.
    - num_days (int): Number of days parameter for the search.

    Returns:
    - None
    """
    global df

    if search_query:
        try:
            if num_days:
                # Construct the URL for the Google News search query
                url = config.get("googlenews_query", "base_url_scraped") + quote(search_query + " when:" + str(num_days) + "d")
                
                # Send the HTTP request to fetch the page
                page = requests.get(url)
                page.raise_for_status()  # Raise an HTTPError for bad responses
                
                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(page.text, 'html.parser')
                articles = soup.find_all('article', class_=config.get("googlenews_query", "article_class"))

                # Iterate through each article and scrape its details
                for article in articles:
                    scrape_news(article, search_query, num_days)
        except requests.RequestException as e:
            logger_gnq.error(f"HTTP request error: {e}")
        except Exception as e:
            logger_gnq.error(f"Unexpected error: {e}")
    else:
        logger_gnq.warning("Search query is empty or not provided.")

def final_scrape_google_news2(search_query, num_days):
    """
    Final function to scrape Google News and return the updated DataFrame.

    Args:
    - search_query (str): The search query for Google News.
    - num_days (int): Number of days parameter for the search.

    Returns:
    - pd.DataFrame: Updated DataFrame containing scraped news articles.
    """
    global df 
    
    # Reinitialize DataFrame to ensure fresh results
    df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', "Search Query", "Number of days"])
    
    # Perform the scraping
    scrape_google_news2(search_query, num_days)
    
    return df
