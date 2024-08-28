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
    driver = webdriver.Chrome()  # Make sure you have ChromeDriver installed
    return driver

def get_olympic_data():
    driver = setup_driver()
    data = []
    try:
        # Navigate to the Olympic medal table page
        driver.get("https://olympics.com/fr/paris-2024/medailles")
        
        # Wait for the medal table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='noc-row']"))
        )

        # Scroll step by step to load all content
        line_height = 900
        for i in range(10)[1:8]:
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
    for row in soup.find_all("div", {"data-testid": "noc-row"}):
        # print(row)  
        country_info = row.find("div", class_=re.compile('^emotion-srm-'))
        country_name = country_info.find("span", class_="euzfwma5").text.strip()
        country_code = country_info.find("span", class_="euzfwma4").text.strip()

        medals = row.find_all("span", class_="e1oix8v91")
        try:
            gold = int(medals[1].text) 
            silver = int(medals[2].text)
            bronze = int(medals[3].text)
            total = int(medals[4].text)
        except:
            gold = 0
            silver = 0
            bronze = 0
            total = 0
        if country_code not in countries_data:
            countries_data.append({
                "country": country_name,
                "code": country_code,
                "gold": gold,
                "silver": silver,
                "bronze": bronze,
                "total": total

            })
        # if country code already exists, update the medals count
        # if country_code not in countries_data:
        #     countries_data[country_code]["medals"]["gold"] += gold

    return countries_data

# Main execution
data = get_olympic_data()
saving_path = sys.argv[1] if len(sys.argv) > 1 else "data/medals_per_country.json"
with open(saving_path, "w") as file:
    json.dump(data, file)
