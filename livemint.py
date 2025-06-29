from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging
<<<<<<< HEAD
import os
=======
>>>>>>> 1e2c8b76114b1faa53a772a4827bb1f0588bfdc4
from datetime import datetime
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
logger_livemint = logging.getLogger(__name__)

# Initialize df as an empty DataFrame
df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', "Main URL Used"])

def scrape_news(url):
    """
    Scrapes the given URL for headline, link, and timestamp.

    Args:
    - url (str): The URL to scrape.

    Returns:
    - None
    """
    global df
    
    try:
        response = requests.get(url)  # Send a GET request to the URL
        soup = BeautifulSoup(response.content, "html.parser")  # Parse the HTML content using BeautifulSoup

        flag = False  # Initialize flag to track if the article already exists in the DataFrame
        
        # Loop until a new article is found or all articles are checked
        while not flag:
            article = soup.find('div', class_=config.get("livemint", "article_class"))  # Find the article div
            h2_tag = article.find(config.get("livemint", "title_size"))  # Find the h2 tag containing the title
            
            if h2_tag:
                a_tag = h2_tag.find(config.get("livemint", "anchor_tag"))  # Find the anchor tag within the h2 tag
            if a_tag:
                text = a_tag.text.strip()  # Extract the text from the anchor tag
                href = a_tag['href']  # Extract the href (link) from the anchor tag

            # Prepare a new row for the DataFrame
            new_row = [text, href, None, url]
            
            try:
                # Check if the DataFrame is empty
                if df.empty:
                    new_row_df = pd.DataFrame([new_row], columns=df.columns)  # Create a new DataFrame row
                    df = pd.concat([new_row_df, df], ignore_index=True)  # Concatenate the new row with the existing DataFrame
                    logger_livemint.info(f"Scraped article: {text}")
                    flag = True  # Set flag to True indicating a new article is found
                else:
                    # Check if the article already exists in the DataFrame
                    for index, row in df.iterrows():
                        if text in row["Headline"]:
                            flag = True  # Set flag to True indicating the article already exists
                            break
                    if not flag:
                        new_row_df = pd.DataFrame([new_row], columns=df.columns)  # Create a new DataFrame row
                        df = pd.concat([new_row_df, df], ignore_index=True)  # Concatenate the new row with the existing DataFrame
                        logger_livemint.info(f"Scraped article: {text}")
            except Exception as e:
                logger_livemint.error(f"Error scraping article: {e}")
    except Exception as e:
        logger_livemint.error(f"Error accessing URL '{url}': {e}")

def scrape_livemint_news():
    """
    Scrapes Livemint for news articles.

    Args:
    - None

    Returns:
    - None
    """
    global df
    
    try:
        # List of URLs to scrape
        urls = [
            config.get("livemint", "base_url_scraped_larsentoubro"),
            config.get("livemint", "base_url_scraped_ltts"),
            config.get("livemint", "base_url_scraped_ltimindtree")
        ]
        
        # Scrape each URL in the list
        for url in urls:
            page = requests.get(url)  # Send a GET request to the URL
            soup = BeautifulSoup(page.text, 'html.parser')  # Parse the HTML content using BeautifulSoup
            scrape_news(url)  # Scrape the news articles from the parsed HTML
    except Exception as e:
        logger_livemint.error(f"Error scraping Livemint news: {e}")

def final_scrape_livemint():
    """
    Clears the existing DataFrame and performs a fresh scrape for Livemint news articles.

    Args:
    - None

    Returns:
    - pd.DataFrame: Updated DataFrame containing the scraped news articles.
    """
    global df
    df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', "Main URL Used"])  # Initialize a new DataFrame
    scrape_livemint_news()  # Perform the scrape
    return df  # Return the updated DataFrame
