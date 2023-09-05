# Imports Organization
from datetime import datetime
import re
import os
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Logins import SQLLogins
from DataPush import SQLPush
from Logins import spreadsheet_id
from flask import Flask

app = Flask(__name__)

# Constants
SPREADSHEET_ID = spreadsheet_id
WORKSHEET_ID = 70759221
HEADLESS_OPTION = "--headless"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('csgob-389204-ef557f063d62.json', scope)
client = gspread.authorize(credentials)
sheet_url = 'https://docs.google.com/spreadsheets/d/1PXuQusF0yxEinjeFRLshDLhqOQOpDvrDRdfUafGI2eE/edit#gid=0'
sheet = client.open_by_url(sheet_url)

def extract_data(link):
    chrome_bin_path = os.environ.get('GOOGLE_CHROME_BIN', "chromedriver")
    chrome_options = Options()
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = chrome_bin_path
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    
    headers = ['Date', 'Username', 'Team', 'Opponent', 'Kills', 'Deaths', 'Assists', 'KD Diff', 'ADR', 'HS', 'FK Diff']
    data_list = []

    driver.get(link)
    soup = BeautifulSoup(driver.page_source, "lxml")
    table_data = soup.find("table", {"class": "table table-hover table-striped table-sm"})
    table_body = table_data.find("tbody")
    table_trs = table_body.find_all("tr")
    split_link = link.split("?")

    for trs in table_trs:
        tds = trs.find_all("td")
        logo_picture = soup.find("picture", {"class": "logo tt mr-0"})
        title = logo_picture['title']

        date_span = trs.find("span", {"class": "sct text-muted"})
        date_text = date_span.text.strip()
        date_obj = datetime.strptime(date_text, "%b %d, %H:%M")
        formatted_date = date_obj.strftime("%m/%d")
        
        try:
            data_dict = {
                "Date": str(formatted_date),
                "Username": re.search(r'[^/]+$', split_link[0]).group(),
                "Team": title,
                "Opponent": tds[1].text.replace("\n", "").strip(),
                "Kills": tds[2].text.replace("\n", "").strip(),
                "Deaths": tds[3].text.replace("\n", "").strip(),
                "Assists": str(tds[4].text.replace("\n", "").strip()),
                "KD Diff": tds[5].text.replace("\n", "").strip(),
                "ADR": tds[6].text.replace("\n", "").strip(),
                "HS": tds[7].text.replace("\n", "").strip(),
                "FK Diff": tds[8].text.replace("\n", "").strip(),
            }

            data_list.append(data_dict)
        except:
            pass

    driver.quit()
    return data_list


def main():
    links = sheet.worksheet("URL").col_values(3)[1:]
    sql_push = SQLPush()

    for link in links:
        try:
            data = extract_data(link)
            appended_link = link + "?s2=2"
            appended_data = extract_data(appended_link)

            combined_data = data + appended_data
            print(combined_data)
        except Exception as e:
            print(f"Error processing link {link}: {str(e)}")
        
        #sql_push.create_data(combined_data)

if __name__ == "__main__":
    main()