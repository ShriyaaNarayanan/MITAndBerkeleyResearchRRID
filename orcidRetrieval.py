from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from bs4 import BeautifulSoup
import requests
import re
from difflib import SequenceMatcher
from threading import Thread


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def normalize(name):
    keywords = ['university', 'institute', 'college', 'department', 'centre', 'laboratory', 'school', 'of', 'the', 'and', 'for', 'research', 'sciences']
    name = name.lower()
    
    for keyword in keywords:
        if keyword in name:
            name = name.replace(keyword, '')
    
    return name

def has_essential_keywords(affiliation, keywords):
    affiliation = affiliation.lower()
    return any(keyword.lower() in affiliation for keyword in keywords)

def searchOrcid(name, affiliation, similarity_threshold=0.5, callback=None):
    def run_search(affiliation):
        driver = webdriver.Chrome()
        # firstName = name.split(" ")[0]
        # lastName = name.split(" ")[1] if len(name.split(" ")) > 1 else ""
        driver.get("https://orcid.org/")
        time.sleep(2)

        searchBox = driver.find_element(By.CSS_SELECTOR, "#cy-search")
        searchBox.send_keys(name)
        searchBox.send_keys(Keys.RETURN)

        normalized_affiliation = normalize(affiliation)
        affiliation_keywords = normalized_affiliation.split()

        time.sleep(4)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#main > app-results > div > table > tbody"))
        )
        rows = driver.find_elements(By.CSS_SELECTOR, "#main > app-results > div > table > tbody > tr")

        orcid_id = None
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if cols:
                first_name = cols[1].text
                last_name = cols[2].text
                full_name = first_name + " " + last_name
                other_names = cols[3].text
                affiliation = cols[4].text
                name_similarity = similar(full_name.lower(), name.lower())
                        
                if name_similarity >= similarity_threshold and has_essential_keywords(affiliation, affiliation_keywords):
                    orcid_link = cols[0].find_element(By.TAG_NAME, "a")
                    orcid_id = orcid_link.text
                    break

        driver.quit()
        if callback:
            callback(orcid_id)

    Thread(target=run_search, args=(affiliation,)).start()


def orcidPubMed(url):    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    details = soup.find(id='article-details')
    if details:
        article_text = details.get_text()
    else:
        article_text = soup.get_text()

    pattern = re.compile(
        r"FAU - ([\w\s,]+)\r?\n"
        r"AU  - [\w\s]+\r?\n"
        r"(?:AUID- ORCID: (\d{4}-\d{4}-\d{4}-\d{3}[\dX])\r?\n)?",
        re.MULTILINE
    )

    for match in pattern.finditer(article_text):
        orcid_id = match.group(2) if match.group(2) else None
        return orcid_id
    return None

result = searchOrcid("Hwan Shin Tae T", "Department of Physiology, Ajou University School of Medicine, Suwon, Republic of Korea.")
print(result)

