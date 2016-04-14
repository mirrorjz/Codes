import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd


"""
Part 1: download the captions from the websites
"""
url = 'http://www.newyorksocialdiary.com/party-pictures'
link_list = []
ref_date = datetime(2014, 12, 1)

for i in range(1, 28):
   if i == 1:
       response = requests.get(url)
       #print response.url
       #print response.text[:1000]
   else:
       response = requests.get(url, params={"page": i - 1})
       
   soup = BeautifulSoup(response.text)
   #print soup.prettify()
   event_list = soup.find_all('span', attrs={'class': 'field-content'}) 
   # print len(event_list)
   N = len(event_list) / 2   # number of events on this page
   for j in range(N):
       index = 2 * j
       date_tag = str(event_list[index+1])
       date = re.findall(r'\w+\s\d+,\s\d\d\d\d', date_tag)[0]
       # time converted to datetime
       # date is like "December 23, 2015"
       cdate = datetime.strptime(date, '%B %d, %Y')
       if cdate < ref_date:
           link = event_list[index].a['href']
           link_list.append((link,cdate))   # Here the link_list has a tuple info for each page
       
print len(link_list)  # should be 1192
print link_list[:5]


"""
The following code captures the all the captions from the websites, this is an aggressive verion
to find all the captions
"""

# common link
caption_lists = []
url_c = 'http://www.newyorksocialdiary.com'
for link in link_list:
    url_id = url_c + link[0]
    response = requests.get(url_id)
    soup = BeautifulSoup(response.text)
    if link[1] > datetime(2007, 9, 4):    
        cond1 = soup.find_all("div", {'class': 'photocaption'}, text=True)
        cond2 = soup.find_all("td", {'class': 'photocaption'}, text=True)
        if cond1: 
            caption_lists = caption_lists + cond1
        if cond2:
            caption_lists = caption_lists + cond2
    # Pages older than Sept 4th, 2007 has different styles of captions
    else:
        cond3 = soup.find_all("font", {'size': 1, 'face': 'Verdana, Arial, Helvetica, sans-serif'}, text=True)       
        if cond3:
            caption_lists = caption_lists + cond3
        
print len(caption_lists)  
print caption_lists[:10]
    

"""
Use pandas to save the data
"""
captions_more = pd.DataFrame({'captions': caption_lists})
captions_more.to_csv('captions_more.csv')
    

    









