import praw
import pandas as pd
import datetime
import logging
from configparser import ConfigParser

# Read configuration settings
config = ConfigParser()
config.read("webscraping\\config.ini")

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger_reddit = logging.getLogger(__name__)

# Define Reddit app credentials using configuration settings
reddit = praw.Reddit(
    client_id=config.get("reddit", "praw_client_id"),
    client_secret=config.get("reddit", "praw_client_secret"),
    user_agent=config.get("reddit", "praw_user_agent")
)

def scrape_news(my_subreddit, my_keyword):
    """
    Scrapes new posts from the specified subreddit that contain the given keyword.

    Args:
    - my_subreddit (str): The name of the subreddit to scrape.
    - my_keyword (str): The keyword to search for in the post titles.

    Returns:
    - None
    """
    global df
    
    # Initialize DataFrame if not already done
    if 'df' not in globals():
        df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', 'Keyword', 'Subreddit'])
    
    # Check if the subreddit name is provided and not empty
    if my_subreddit:
        try:
            subreddit = reddit.subreddit(my_subreddit)  # Access the specified subreddit
            for post in subreddit.new(limit=None):  # Iterate over new posts
                if my_keyword.lower() in post.title.lower():  # Check if keyword is in post title (case insensitive)
                    title = post.title
                    url = post.url
                    timestamp = datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Check if the URL already exists in the DataFrame
                    if df.empty or not any(df['Link'] == url):
                        new_row = {'Headline': title, 'Link': url, 'DateStamp': timestamp, 'Keyword': my_keyword, 'Subreddit': my_subreddit}
                        df.loc[len(df)] = new_row  # Add new row to DataFrame using loc
                        logger_reddit.info(f"Scraped article: {title}")
                    else:
                        logger_reddit.info(f"Article already exists in DataFrame: {title}")
        except praw.exceptions.ClientException as e:
            logger_reddit.error(f"Error fetching subreddit '{my_subreddit}': {e}")
        except Exception as e:
            logger_reddit.error(f"Unexpected error: {e}")
    else:
        logger_reddit.warning("Subreddit name is empty or not provided.")

def final_scrape_reddit_news(my_subreddit, my_keyword):
    """
    Clears the existing DataFrame and performs a fresh scrape for the specified subreddit and keyword.

    Args:
    - my_subreddit (str): The name of the subreddit to scrape.
    - my_keyword (str): The keyword to search for in the post titles.

    Returns:
    - pd.DataFrame: Updated DataFrame containing the scraped news articles.
    """
    global df
    
    # Clear the existing DataFrame to ensure fresh scrape results
    df = pd.DataFrame(columns=['Headline', 'Link', 'DateStamp', 'Keyword', 'Subreddit'])
    
    # Scrape news for the specified subreddit and keyword
    scrape_news(my_subreddit, my_keyword)
    
    return df
