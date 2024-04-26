import streamlit as st
import pandas as pd
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import requests, openpyxl
from datetime import datetime
import re
from streamlit_gsheets import GSheetsConnection
# pip install requests-html
link = ""
namesAndInfo = {}
s = HTMLSession()
excel  = openpyxl.Workbook()
# ^^ prints out ['Sheet']
# active sheet is where we load the data
sheet = excel.active
sheet.title = 'Authors and Basic Info from PubMed'
sheet.append(['Author Name', 'Affiliation', 'Email'])
currYear = int(datetime.now().strftime("%Y"))
yearMinusTwo = currYear-2
headers = {"x-api-key": "4BiGxN4Qtm989Br5PVykF71iYSZepRHk1tr7ycdA"}

def search_authors(author_name, headers):
    """
    Searches for the author by author name, and returns several information about that author due to 
    duplicate author names.
    """
    url = "https://api.semanticscholar.org/graph/v1/author/search"
    params = {
        "query": author_name,
        "limit": 5,
        "fields": "authorId,name,aliases,affiliations,homepage,paperCount,citationCount,hIndex"
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Error searching for authors: {response.status_code}")
        return []


class basicAuthorInfoFromPubMed:
    def __init__(self, link):
        self.link = link
        self.namesAndInfo = {}
        self.headers = {"x-api-key": "4BiGxN4Qtm989Br5PVykF71iYSZepRHk1tr7ycdA"}



    # returns the main namesAndInfo dictionary
    def getNamesAndInfo(self):
        return self.namesAndInfo

    def search_authors(self, author_name):
        """
        Searches for the author by author name, and returns several information about that author due to 
        duplicate author names.
        """
        url = "https://api.semanticscholar.org/graph/v1/author/search"
        params = {
            "query": author_name,
            "limit": 5,
            "fields": "authorId,name,aliases,affiliations,homepage,paperCount,citationCount,hIndex"
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f"Error searching for authors: {response.status_code}")
            return []

    # returns the author names from a given link
    def getAuthorNamesOnly(self):
        names = []
        site = s.get(self.link)
        soup = BeautifulSoup(site.text, 'html.parser')
        place = soup.find(class_="authors-list")
        namesAndDetails = place.find_all(class_ = "authors-list-item")
        namesAndDetails = place.find_all(class_="authors-list-item")
        for name in namesAndDetails:
            innerclass = name.find(class_ = "full-name")
            if (innerclass):
            innerclass = name.find(class_="full-name")
            if innerclass:
                stringName = innerclass.get("data-ga-label")
                if stringName:
                    names.append(stringName)
        return names

    # Asynchrnously returns a specific author's information: affiliation and email (If they exist) 
    # From a research article link
    async def getSpecificAuthorNameInfo(self, link, name, session):
    async def getSpecificAuthorNameInfo(self,link, name,session):
        async with session.get(link) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            place = soup.find(class_="authors-list")
            try:
                namesAndDetails = place.find_all(class_="authors-list-item")
                namesAndDetails = place.find_all(class_ = "authors-list-item")
                for namer in namesAndDetails:
                    innerclass = namer.find(class_="full-name")
                    if innerclass:
                    innerclass = namer.find(class_ = "full-name")
                    if (innerclass):
                        stringName = innerclass.get("data-ga-label")
                        if stringName and stringName == name:
                            affiliationClass = namer.find(class_="affiliation-links")
                            if affiliationClass:
                                newAffiliationClass = affiliationClass.find(class_="affiliation-link")
                                affiliationListInfo1 = newAffiliationClass["title"]
                                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', affiliationListInfo1)
                                if email_match:
                                    email = email_match.group()
                                    oldAffiliation = affiliationListInfo1.replace(email, '').replace('title="', '').replace('"', '')
                                    affiliation = oldAffiliation.rsplit(". ", 2)[0] if oldAffiliation else None
                        if (stringName):
                            if (stringName == name):
                                affiliationClass = namer.find(class_="affiliation-links")
                                if affiliationClass:
                                    newAffiliationClass = affiliationClass.find(class_="affiliation-link")
                                    affiliationListInfo1 = newAffiliationClass["title"]
                                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', affiliationListInfo1)
                                    if (email_match):
                                        email = email_match.group()
                                        oldAffiliation = affiliationListInfo1.replace(email, '').replace('title="', '').replace('"', '')
                                        affiliation = oldAffiliation.rsplit(". ", 2)[0]
                                    else:
                                        affiliation = affiliationListInfo1.replace('title="', '').replace('"', '').strip()
                                    if (email_match):
                                        affiliationListInfo = [affiliation, email]
                                    else:
                                        affiliationListInfo = [affiliation, None]
                                    namesAndInfo[stringName] = affiliationListInfo
                                else:
                                    email = None
                                    affiliation = affiliationListInfo1.replace('title="', '').replace('"', '').strip() if affiliationListInfo1 else None

                                affiliationListInfo = [affiliation, email]  # Ensure this is a list with complete strings
                                self.namesAndInfo[stringName] = affiliationListInfo
                            else:
                                self.namesAndInfo[stringName] = [None, None]
                            return self.namesAndInfo[stringName]
            except Exception as e:
                print(f"Error processing author details: {e}")
                                    namesAndInfo[stringName] = None
                                try:
                                    namesAndInfo[stringName] = affiliationListInfo
                                    return affiliationListInfo
                                except Exception as e:
                                    return None
                    else :
                        print("did not find class full-name")
            except:
                return None


    # Goes through all research paper links after searching up an author's name in PubMed
    # until it finds an affiliation
    # Or until there are no more research paper links       
    async def fetch_affiliation(self, session, name, search_url, authorId, paperCount):
    async def fetch_affiliation(self, session, name, search_url, semantic_id, paper_count):
        async with session.get(search_url) as response:
            html = await response.text()
            affiliation = None
    async def fetch_affiliation(self, session, name, search_url, authorId, paperCoun
                        break

            if affiliation is not None:
                self.namesAndInfo[name] = affiliation + [authorId, paperCount]
                self.namesAndInfo[name] = affiliation + [semantic_id, paper_count]
            else:
                self.namesAndInfo[name] = [None, None, authorId, paperCount]
                #print(name, None)
                self.namesAndInfo[name] = None



    async def pubMedSearch(self):
        names = self.getAuthorNamesOnly()
        search_tasks = []
        async with aiohttp.ClientSession() as session:
            for name in names:
                # Initialize variables before the if statement
                authorId = None
                paperCount = None
                semantic_scholar_info = search_authors(name, headers=self.headers)
                semantic_id = None
                paper_count = None
                semantic_scholar_info = self.search_authors(name)
                if semantic_scholar_info:
                    authorId = semantic_scholar_info[0]['authorId'] if 'authorId' in semantic_scholar_info[0] else None
                    paperCount = semantic_scholar_info[0]['paperCount'] if 'paperCount' in semantic_scholar_info[0] else None

                    semantic_id = semantic_scholar_info[0]['authorId'] if 'authorId' in semantic_scholar_info[0] else None
                    paper_count = semantic_scholar_info[0]['paperCount'] if 'paperCount' in semantic_scholar_info[0] else None
                first_and_last_list = name.split(" ")
                search_url = "https://pubmed.ncbi.nlm.nih.gov/?term=" + "+".join(first_and_last_list)
                search_url += "&filter=years." + str(yearMinusTwo) + "-" + str(currYear) + "&sort=date"
                search_tasks.append(asyncio.create_task(self.fetch_affiliation(session, name, search_url, authorId, paperCount)))
                search_tasks.append(asyncio.create_task(self.fetch_affiliation(session, name, search_url, semantic_id, paper_count)))

            results = await asyncio.gather(*search_tasks)
            return results
async def returnNothing(self):
names = []
affiliation = []
emails = []
semantic_id = []
paper_count = []
st.title("PubMed Searching")
st.write("Type in a pubMed link to a published article to retrieve the author affiliation!")
async def main():
    Officiallink = st.text_input('Enter your PubMedLink: ', "Link")
    g = basicAuthorInfoFromPubMed(Officiallink)
    print("Inside main")
    if 'affiliationData' not in st.session_state:
        if g.link != "Link":
        if g.link !="Link":
            await g.pubMedSearch()
            namesAndInfo = g.getNamesAndInfo() 
            for name in namesAndInfo:
                names.append(name)
                # Safely access nested list data
                if namesAndInfo[name] and len(namesAndInfo[name]) > 0 and namesAndInfo[name][0]:
                    author_details = namesAndInfo[name][0]
                    # Check and append affiliation
                    if author_details and len(author_details) > 0:
                        affiliation.append(author_details[0] if author_details[0] else None)
                if (namesAndInfo[name]):
                    if (namesAndInfo[name][0] != None):
                        affiliation.append(namesAndInfo[name][0])
                    else:
                        affiliation.append(None)
                    # Check and append email
                    if len(author_details) > 1:
                        emails.append(author_details[1] if author_details[1] else None)
                    if (namesAndInfo[name][0][1] != None):
                        emails.append(namesAndInfo[name][1])
                    else:
                        emails.append(None)
                    if (namesAndInfo[name][0][2] != None):
                        semantic_id.append(namesAndInfo[name][2])
                    else:
                        semantic_id.append(None)
                    if (namesAndInfo[name][0][3] != None):
                        paper_count.append(namesAndInfo[name][3])
                    else:
                        paper_count.append(None)
                else:
                    affiliation.append(None)
                    emails.append(None)

            df = pd.DataFrame({
                "Link": Officiallink,
                "Authors": names, 
                "Affiliation": [info[0] if info and len(info) > 0 else None for info in namesAndInfo.values()],
                "Emails": [info[1] if info and len(info) > 1 else None for info in namesAndInfo.values()],
                "Semantic ID": [info[2] for info in namesAndInfo.values() if info and len(info) > 2],
                "Paper Count": [info[3] for info in namesAndInfo.values() if info and len(info) > 3]
            })
                "Authors" : names, 
                "Affiliation" : affiliation,
                "Emails                                   " : emails,
                # will need to update the data frame accordingly
                "Semantic ID": semantic_id,
                "Paper Count": paper_count

            })
            # Setting value of session
            if 'affiliationData' not in st.session_state:
                st.session_state['affiliationData'] = df

    if 'affiliationData' in st.session_state:
    if 'affiliationData'  in st.session_state:
        newDf = st.session_state['affiliationData']

        def dataframe_with_selections(newDf: pd.DataFrame, init_value: bool = False) -> pd.DataFrame:
        def dataframe_with_selections(newDf: pd.DataFrame, init_value: bool = False) ->
        selection = dataframe_with_selections(newDf)

        placeholder = st.empty()
        with placeholder.container():
        with placeholder.container(border=True):
            st.write("Your selection:")
            st.write(selection)
        if st.button('SAVE'):
        if (st.button('SAVE')):
            # Create database to have the rows in selection
            st.write("You have saved your selection!")
            conn = st.connection("gsheets", type=GSheetsConnection)
            df2 = conn.read(
                worksheet="Sheet1",
                ttl="0m",
                usecols=[0, 1, 2, 3],
                # Number of columns will need to change based on what additional info
                # Need to directly change the column names as well
            )
            df2.dropna(subset=['Authors'], inplace=True)
            newdf = df2.append(selection)
            df2.drop(columns=["Emails"], inplace=True)
            df2 = conn.update(
                        worksheet="Sheet1",
                        data=newdf,
                    )
            placeholder.empty()
            if 'affiliationData' in st.session_state:
                del st.session_state['affiliationData']
                #st.switch_page("app.py")
                st.rerun()

        if st.button('RESET', type="primary"):
            # Reload the page and erase the current selection
            placeholder.empty()
            st.write("Reset was clicked!")
            st.write("Reset was clicked!") 
            if 'affiliationData' in st.session_state:
                del st.session_state['affiliationData']
                st.rerun()

                #st.switch_page("app.py")
        if st.button("View Google Sheets Link"):
            st.write("(https://docs.google.com/spreadsheets/d/1kvdksFYHQtPQF0BZtAzcS6azYuUqpyiPS8u9a6iIrlw/edit?usp=sharing)")

if __name__ == "__main__":
    asyncio.run(main())
