from requests_html import HTMLSession
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import requests, openpyxl
from datetime import datetime
import re
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


class basicAuthorInfoFromPubMed:

    # initializes class
    def __init__(self, link):
        self.link = link
        self.namesAndInfo = {}
        
    # returns the main namesAndInfo dictionary
    def getNamesAndInfo(self):
        return self.namesAndInfo

    # returns the author names from a given link
    def getAuthorNamesOnly(self):
        names = []
        site = s.get(self.link)
        soup = BeautifulSoup(site.text, 'html.parser')
        place = soup.find(class_="authors-list")
        namesAndDetails = place.find_all(class_ = "authors-list-item")
        for name in namesAndDetails:
            innerclass = name.find(class_ = "full-name")
            if (innerclass):
                stringName = innerclass.get("data-ga-label")
                if stringName:
                    names.append(stringName)
        return names
    
    # Asynchrnously returns a specific author's information: affiliation and email (If they exist) 
    # From a research article link
    async def getSpecificAuthorNameInfo(self,link, name,session):
        async with session.get(link) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            place = soup.find(class_="authors-list")
            try:
                namesAndDetails = place.find_all(class_ = "authors-list-item")
                for namer in namesAndDetails:
                    innerclass = namer.find(class_ = "full-name")
                    if (innerclass):
                        stringName = innerclass.get("data-ga-label")
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
    async def fetch_affiliation(self, session, name, search_url):
        async with session.get(search_url) as response:
            html = await response.text()
            affiliation = None
            soup = BeautifulSoup(html, 'html.parser')
            # This checks for the edge case where there is only one research paper link in the time frame
            # In this case, a set of links do not pop up, but the research paper directly pops up
            if (soup.find(class_="single-result-redirect-message") is not None):
                affiliation = await self.getSpecificAuthorNameInfo(search_url, name,session)
            # The below is for traversing through all of the links until one is found or there are no more links within the given parameters
            else:
                for div in soup.find_all('div', class_='docsum-content'):
                    linker = div.find('a')['href']
                    linker = "https://pubmed.ncbi.nlm.nih.gov" + linker
                    affiliation = await self.getSpecificAuthorNameInfo(linker, name,session)
                    if affiliation is not None:
                        break

            if affiliation is not None:
                self.namesAndInfo[name] = affiliation
            else:
                #print(name, None)
                self.namesAndInfo[name] = None
    

    
    async def pubMedSearch(self):
        
        # This is the main function for performing a search on pubMed to retrieve all affiliations
        # Given a specific research article link
        # This function asynchronously gets all of the author's affiliations to have a faster runtime
        names = self.getAuthorNamesOnly()
        search_tasks = []
        async with aiohttp.ClientSession() as session:
            for name in names:
                first_and_last_list = name.split(" ")
                search_url = "https://pubmed.ncbi.nlm.nih.gov/?term="+first_and_last_list[0]
                for i in range(1, len(first_and_last_list)):
                    search_url += "+" + first_and_last_list[i]
                search_url += "&filter=years."+str(yearMinusTwo)+"-"+str(currYear)+"&sort=date"
                search_tasks.append(asyncio.create_task(self.fetch_affiliation(session, name, search_url)))

            results = await asyncio.gather(*search_tasks)
            return results
        
    

    async def getAuthorNamesAndInfoInSpreadsheet(self):
        await self.pubMedSearch()
        # this is for populating a spreadsheet which can be finalized later once all information is collected
        '''
        self.namesAndInfo = self.getNamesAndInfo()
        for name in namesAndDetails:
            innerclass = name.find(class_ = "full-name")
            stringName = innerclass["data-ga-label"]
            if stringName in self.namesAndInfo:
                if (self.namesAndInfo[stringName]):
                    affiliationListInfo = self.namesAndInfo[stringName]
                    affiliation = affiliationListInfo[0]
                    if len(affiliationListInfo)>1:
                        email = affiliationListInfo[1]
                        sheet.append([stringName, affiliation, email])
                    else:
                        sheet.append([stringName, affiliation])
            else:
                pass
            '''
        print("These are the names: ", self.namesAndInfo)
        #excel.save("Author Names And Info.xlsx")

            
    
    
    
    
        
        

async def main():
    #g = basicAuthorInfoFromPubMed("https://pubmed.ncbi.nlm.nih.gov/36609584/")
    #await g.getAuthorNamesAndInfoInSpreadsheet()
    inputLink = input("What published article would you like author information about? ")
    n = basicAuthorInfoFromPubMed(inputLink)
    await n.getAuthorNamesAndInfoInSpreadsheet
    h = basicAuthorInfoFromPubMed("https://pubmed.ncbi.nlm.nih.gov/36215063/")
    await h.getAuthorNamesAndInfoInSpreadsheet()
    #n = basicAuthorInfoFromPubMed("https://pubmed.ncbi.nlm.nih.gov/23407571/")
    #n.findAuthorAffiliationSynchronously("Geoffrey Johnston")
    #await n.getAuthorNamesAndInfoInSpreadsheet()

asyncio.run(main())
