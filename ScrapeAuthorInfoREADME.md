To run this file:

1. Need link of published article from pubMed
2. Run the file locally in your terminal (python3 scrapAuthorInfo.py)
3. Will be prompted for link of published article
4. pubMedSearch() will populate the dictionary (name: [affiliation, email])
5. getBasicAuthorInfoFromSpreadsheet() prints out the name and affiliation list info dictionary (namesAndInfo{})
6. Eventual functionality is for this to populate a spreadsheet with the name and affiliation list information into separate columns
7. Dictionary can be accessed by the object.getNamesAndInfo()
