To run this file:

1. Need link of published article from pubMed
2. Run the file locally in your terminal (python3 scrapAuthorInfo.py)
3. Will be prompted for link of published article
4. pubMedSearch() will populate the dictionary (name: [affiliation, email])
5. getBasicAuthorInfoFromSpreadsheet() prints out the name and affiliation list info dictionary (namesAndInfo{})
6. Eventual functionality is for this to populate a spreadsheet with the name and affiliation list information into separate columns
7. Dictionary can be accessed by the object.getNamesAndInfo()


How the file/program works:
1. Initially takes in a link
2. Then goes through the author information section
3. Asynchronously for every author/name:
   1. copy the full author's name (This is because if you directly click the name, their name becomes abbrieviated; search results less acurate
   
   2. Search their name up on the pubmed search bar with the following filters:
      1. Filter by the past two years
      2. Sort by recent
   3. Go through each article in the search result (EDGE CASE: if only ONE article, the search result automatically loads article)
      1. Look for the author's name
      2. Identify if they have an affiliation
      3. If affiliation is found, store affiliation and email if it exists and break out of the loop. Else keep going until
         affiliation is found or there are no more search articles (In this case None is put for both affiliation and email
      4. Store the author name as the key in the self.namesAndInfo dictionary and the affiliationListInfo (affiliation, email) as the 
           value
4. Return the dictionary / Dictionary is updated for user to retrieve using getNamesAndInfo()
            
