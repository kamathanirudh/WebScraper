import streamlit as st
import pandas as pd
from datetime import datetime as dt
import os
from openpyxl import load_workbook
import schedule
import time
from zipfile import BadZipFile
import logging

# Importing your scraping functions
from livemint import final_scrape_livemint
from economictimes import final_scrape_economictimes
from googlenews_last_24h import final_scrape_googlenews
from googlenews_queried import final_scrape_google_news2
from reddit_queried import final_scrape_reddit_news

from configparser import ConfigParser

# Configure logging
logging.basicConfig(
    filename='app.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'  # 'w' mode will overwrite the file each time the script runs
)
logger = logging.getLogger(__name__)


config = ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config.read(config_path)

# Function to create or update Excel file with multiple sheets
def update_excel_file(dataframes, mode='append'):
    excel_filename = config.get('main', 'excel_file_path')
    
    if os.path.exists(excel_filename):
        try:
            # Load the workbook
            wb = load_workbook(excel_filename)
        except BadZipFile:
            st.error(f"Error: The file '{excel_filename}' is not a valid Excel file or is corrupted.")
            return
        with pd.ExcelWriter(excel_filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            for sheet_name, new_df in dataframes.items():
                if mode == 'new' and sheet_name in wb.sheetnames:
                    # Delete the existing sheet
                    del wb[sheet_name]
                
                if sheet_name in wb.sheetnames and mode != 'new':
                    # Load existing data
                    existing_df = pd.read_excel(excel_filename, sheet_name=sheet_name)
                    # Concatenate new data with existing data, with new data first
                    updated_df = pd.concat([new_df, existing_df]).drop_duplicates()
                else:
                    updated_df = new_df
                
                # Remove any duplicate rows
                updated_df = updated_df.drop_duplicates()
                
                # Write updated data to Excel sheet
                updated_df.to_excel(writer, sheet_name=sheet_name.strip(), index=False)
            writer._save()
        wb.close()
    else:
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            for sheet_name, df in dataframes.items():
                df.to_excel(writer, sheet_name=sheet_name.strip(), index=False)

    st.success(f"Excel file '{excel_filename}' updated successfully at {dt.now()}.")

# Function to update selected dataframes
def update_dataframes():
    try:
        # Update Livemint dataframe
        selected_df = final_scrape_livemint()
        dataframes = {"Livemint": selected_df}
        update_excel_file(dataframes)
        
        # Update Economic Times dataframe
        selected_df = final_scrape_economictimes()
        dataframes = {"Economic Times": selected_df}
        update_excel_file(dataframes)
        
        # Update Google News Last 24h dataframe
        selected_df = final_scrape_googlenews()
        dataframes = {"Google News Last 24h": selected_df}
        update_excel_file(dataframes)
        
        logger.info("Scheduled update_dataframes() completed successfully.")
    except Exception as e:
        logger.error(f"Error updating dataframes: {e}")

# Streamlit app title and sidebar for update interval
st.title("Dataframe Selector and Excel Updater")
update_interval = st.sidebar.number_input("Enter update interval in minutes", min_value=1, step=1, value=5)

# Schedule the update function to run based on user-defined interval
schedule.every(update_interval).minutes.do(update_dataframes)

# Notes for each selection
notes = {
    "Select Query for Google news": [
        "Displays the all data from googlenews by searching 'Query' when: 'number of days' d in google news search bar",
        "New dataframe is appended to old dataframe",
        "Dataframe sorted according to Date, recent always on top, for each query"
    ],
    "Reddit": [
        "Uses PRAW API to search KEYWORD in the entered SUBREDDIT",
        "New dataframe is appended to old dataframe"
    ],
    "Last 24h headlines in Google news": [
        "Displays the most recent news in the last 24h on the top",
        "The program then scans for new news published, every 'X' minutes (entered by user in sidebar)",
        "Any new news will be appended and Dataframe is sorted according to DateStamp",
        "Searches Larsen and Toubro when:1d on GoogleNews search bar"
    ],
    "Livemint": [
        "Fetches latest news from Livemint.",
        "Uses Latest News on Larsen&Toubro LTD (companyid-s0003025), LTIMindtree and LTTS news from livemint.com",
        "The program then scans for new news published, every 'X' minutes (entered by user in sidebar)",
        "Any new news will be appended, with recent news on top"
    ],
    "Economic Times": [
        "Fetches latest news from Economic Times.",
        "Uses L&T LTD news from Economic times website and shows the most recent news in the dataframe",
        "The program then scans for new news published, every 'X' minutes (entered by user in sidebar)",
        "Any new news will be appended, with recent news on top"
    ]
}

# Sidebar selection for Dataframe
dataframes_keys = list(notes.keys())  # Use keys from notes for selection options
selection = st.sidebar.selectbox("Select Dataframe", dataframes_keys)

# Display notes based on selection
if selection in notes:
    st.sidebar.subheader(f"Working of '{selection}':")
    st.sidebar.markdown(
        f"""
        <div style="background-color: #ffeb3b; padding: 10px; border-radius: 5px; color: black;">
        <ul style="font-size: small;">
        {" ".join([f"<li>{note}</li>" for note in notes[selection]])}
        </ul>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Main content based on selection
if selection == "Select Query for Google news":
    search_query = st.text_input("Enter your search query for Google News:")
    num_days = st.text_input("Enter number of days:")
    selected_df = final_scrape_google_news2(search_query, num_days)
    st.dataframe(selected_df)
    # Give update_excel_file(dataframes, mode="new") if you want a new sheet and delete the old sheet    
    # Update Excel file with the selected dataframe
    dataframes = {"Google News": selected_df}
    update_excel_file(dataframes)

elif selection == "Reddit":
    my_keyword = st.text_input("Enter your Keyword to search:")
    my_subreddit = st.text_input("Enter your Subreddit to search:")
    selected_df = final_scrape_reddit_news(my_subreddit, my_keyword)
    st.dataframe(selected_df)
    # Give update_excel_file(dataframes, mode="new") if you want a new sheet and delete the old sheet
    # Update Excel file with the selected dataframe
    dataframes = {"Reddit": selected_df}
    update_excel_file(dataframes)

elif selection == "Last 24h headlines in Google news":
    selected_df = final_scrape_googlenews()
    st.dataframe(selected_df)
    
    # Update Excel file with the selected dataframe
    dataframes = {"Google News Last 24h": selected_df}
    update_excel_file(dataframes)

elif selection == "Livemint":
    selected_df = final_scrape_livemint()
    st.dataframe(selected_df)
    
    # Update Excel file with the selected dataframe
    dataframes = {"Livemint": selected_df}
    update_excel_file(dataframes)

elif selection == "Economic Times":
    selected_df = final_scrape_economictimes()
    st.dataframe(selected_df)
    
    # Update Excel file with the selected dataframe
    dataframes = {"Economic Times": selected_df}
    update_excel_file(dataframes)

# Run Streamlit app
while True:
    schedule.run_pending()
    time.sleep(1)
