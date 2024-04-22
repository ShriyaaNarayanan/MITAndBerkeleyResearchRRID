1. I have created a variable called self.namesAndInfo. This is a dictionary which (using the rest of your code) can be used to easily populate each author's orcID,
Semantic Scholar ID, and Number of Recent articles. (Comment in lines 144, 145)
2. There is a data frame which I have created that you can add the rest of the information to (This currently only contains the author name, affiliation, and potential email
if it exists (Comment in line 181, data frame is called df)
3. When updating the google spreadsheet the number of columns will need to change depending on your information (Comment on line 218)
4. Another thing to note is you would need to directly change the column name on the google spreadsheet
5. I have taken care of the rest of the implementation in terms of loading the website and connecting and populating the google sheet!
6. When checking if it works on the website, if you commit and push your code, you can directly see this on pubmedinfo.streamlit.app
7. The link to the google spreadsheet is: https://docs.google.com/spreadsheets/d/1kvdksFYHQtPQF0BZtAzcS6azYuUqpyiPS8u9a6iIrlw/edit#gid=0

