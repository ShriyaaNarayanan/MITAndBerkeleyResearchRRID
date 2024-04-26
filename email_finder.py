import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pdfplumber
from io import BytesIO

def get_html(url):
    response = requests.get(url)
    return response.text

def get_pubmed_external_links(url):
    html_content = get_html(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    link_list = soup.find('ul', class_='linkout-category-links')

    if link_list:
        links = link_list.find_all('a')
        hrefs = [link['href'] for link in links if 'href' in link.attrs]
        return hrefs
    else:
        return None

def get_email_from_page_html(url):
    html_content = get_html(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    a_tags = soup.find_all('a', href=True)
    mailto_regex = re.compile(r'mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
    
    unique_emails = set()

    for tag in a_tags:
        href = tag['href']
        match = mailto_regex.search(href)
        if match:
            unique_emails.add(match.group(1))

    return list(unique_emails)

def extract_text_from_pdf_url(url):
    # Send a GET request to fetch the PDF content from the URL
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception for bad responses

    # Use BytesIO to convert bytes to a file-like object which pdfplumber can read
    with pdfplumber.open(BytesIO(response.content)) as pdf:
        text = ""
        # Extract text from each page
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return

def get_author_names(url):
    names = []
    html_content = get_html(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    place = soup.find(class_="authors-list")
    namesAndDetails = place.find_all(class_ = "authors-list-item")
    for name in namesAndDetails:
        innerclass = name.find(class_ = "full-name")
        if (innerclass):
            stringName = innerclass.get("data-ga-label")
            if stringName:
                names.append(stringName)
    return names

def get_pubmed_doi(url):
    html_content = get_html(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    element = soup.find(class_='id-link')

    if element and element.has_attr('href'):
        href = element['href']
        return href
    return

def get_email_by_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome()
    driver.get(url)
    email_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "mailto:")]')
    if email_elements:
        unique_emails = set()
        for ele in email_elements:
            email_address = ele.get_attribute('href').replace('mailto:', '')
            unique_emails.add(email_address)
        driver.quit()
        return list(unique_emails)
    else:
        driver.quit()
        return

def name_to_email_matcher(emails, names):
    """emails are a list of retrieved email addresses"""
    """names are a list of full names of the authors"""
    matches = {}
    no_match_emails = []
    for email in emails:
        email_prefix = email.split('@')[0]
        match_success = False
        for name in names:
            name_parts = name.split()
            first_name, last_name = name_parts[0].lower(), name_parts[-1].lower()
            full_shortened_name = first_name+last_name
            full_actual_name = re.sub(r'[^a-zA-Z]', '', name)
            if first_name in email_prefix or last_name in email_prefix or email_prefix in first_name or email_prefix in last_name or email_prefix in full_shortened_name or email_prefix in full_actual_name:
                matches[email] = name
                match_success = True
                break
        if not match_success :
            no_match_emails.append(email)
    if len(no_match_emails)>0:
        for email in no_match_emails:
            matches[email] = "NO NAME MATCH FOUND"
    return matches

def master(url):
    try:
        doi = get_pubmed_doi(url)
    except:
        print("Error in getting the paper DOI")
    if not doi:
        print("Failed to get paper DOI")
    try:
        emails = get_email_by_selenium(doi)
    except:
        print("Error in retrieving emails from paper DOI site")
    if not emails:
        print("No emails retrieved")
    names = get_author_names(url)
    matches = name_to_email_matcher(emails, names)
    print(matches)
    return


url = "https://pubmed.ncbi.nlm.nih.gov/31922268/"

master(url)