from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import json
import sys

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-ssl-errors=yes')
    # options.add_argument('--ignore-certificate-errors')

    # # Set user agent
    # user_agent = 'userMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    # options.add_argument(f'user-agent={user_agent}')
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--no-sandbox')
    # options.add_argument('-headless')
    driver = webdriver.Chrome(options=options)  # Make sure you have ChromeDriver installed
    return driver

def get_olympic_data():
    driver = setup_driver()
    data = []
    try:
        # Navigate to the Olympic medal table page
        driver.get("https://olympics.com/fr/paris-2024/medailles/athlete-medailles")
        
        # Wait for the medal table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class='emotion-srm-1xycdp4']"))
        )

        # Scroll step by step to load all content
        line_height = 900
        height = driver.execute_script("return document.body.scrollHeight")
        number_of_lines = height // line_height
        for i in range(number_of_lines)[1:number_of_lines-1]:
            driver.execute_script(f"window.scrollTo(0, {line_height * i});")
            time.sleep(1)
            data_record = extract_olympic_data(driver.page_source)
            data.extend(data_record)
        return data
    finally:
        driver.quit()

def extract_olympic_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # container_div = soup.find("div", {'data-test-id': 'virtuoso-item-list'})
    # print(container_div)

    countries_data = []
    for row in soup.find_all("div", {"class": "emotion-srm-1xycdp4"}):
        flag_src = row.find("img", class_="eph8xjg0")["src"]

        medals = row.find_all("span", class_="e1oix8v91")
        country_code = medals[0].text
        athletes = medals[1].text
        try:
            gold = int(medals[2].text) 
            silver = int(medals[3].text)
            bronze = int(medals[4].text)
            total = int(medals[5].text)
        except:
            gold = 0
            silver = 0
            bronze = 0
            total = 0

        if country_code not in countries_data:
            countries_data.append({
                "flag": flag_src,
                "athlete": athletes,
                "code": country_code,
                "gold": gold,
                "silver": silver,
                "bronze": bronze,
                "total": total
                
            })

    return countries_data

# Main execution
data = get_olympic_data()

saving_path = sys.argv[1] if len(sys.argv) > 1 else "data/medals.json"
with open(saving_path, "w") as file:
    json.dump(data, file)