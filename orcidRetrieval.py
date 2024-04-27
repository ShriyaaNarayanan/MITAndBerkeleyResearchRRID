import asyncio
import aiohttp
from difflib import SequenceMatcher
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import re

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def normalize(name):
    # Only normalize by checking if keywords are included, instead of removing them
    keywords = ['university', 'institute', 'college', 'department', 'center', 'lab', 'school', 'research']
    name = name.lower()
    for keyword in keywords:
        if keyword in name:
            return True
    return False

async def searchOrcid(name, affiliation, pubmed_link, similarity_threshold=0.7):
    orcid_id = orcidPubMed(pubmed_link)
    if orcid_id:
        return orcid_id
    
    normalized_affiliation_present = normalize(affiliation)
    url = f"https://pub.orcid.org/v3.0/expanded-search/?q={name.replace(' ', '+')}"
    headers = {'Accept': 'application/vnd.orcid+xml'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                ns = {'common': 'http://www.orcid.org/ns/common', 'search': 'http://www.orcid.org/ns/search', 'expanded-search': 'http://www.orcid.org/ns/expanded-search'}
                tree = ET.fromstring(content)
                for result in tree.findall('.//expanded-search:expanded-result', namespaces=ns):
                    orcid_id = result.find('expanded-search:orcid-id', ns).text if result.find('expanded-search:orcid-id', ns) is not None else None
                    given_names = result.find('expanded-search:given-names', ns).text if result.find('expanded-search:given-names', ns) is not None else ""
                    family_names = result.find('expanded-search:family-names', ns).text if result.find('expanded-search:family-names', ns) is not None else ""
                    full_name = f"{given_names} {family_names}"
                    institution_names = [elem.text.lower() for elem in result.findall('expanded-search:institution-name', ns)]

                    if similar(full_name.lower(), name.lower()) >= similarity_threshold and normalized_affiliation_present:
                        for inst_name in institution_names:
                            if normalize(inst_name):  # Check if normalized name includes the keyword
                                return orcid_id
                return "No suitable ORCID ID found"
            else:
                return "Error fetching ORCID"

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

# async def main():
#     authors_and_affiliations = [
#         ('Shaherin Basith', 'Department of Physiology, Ajou University School of Medicine, Suwon, Republic of Korea'),
#         ('Balachandran Manavalan', 'Department of Physiology, Ajou University School of Medicine, Suwon, Republic of Korea'),
#         ('Tae Hwan Shin', 'Department of Physiology, Ajou University School of Medicine, Suwon, Republic of Korea'),
#         ('Gwang Lee', 'Department of Physiology, Ajou University School of Medicine, Suwon, Republic of Korea')
#     ]

#     orcid_search_tasks = [searchOrcid(name, affiliation) for name, affiliation in authors_and_affiliations]
#     orcid_ids = await asyncio.gather(*orcid_search_tasks)

#     for name, orcid in zip([name for name, _ in authors_and_affiliations], orcid_ids):
#         print(f"Author: {name}, ORCID ID: {orcid}")

# asyncio.run(main())
