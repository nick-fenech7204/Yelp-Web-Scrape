#!/usr/bin/env python
# coding: utf-8

# In[10]:


import requests
from bs4 import BeautifulSoup
import re
from bs4 import SoupStrainer
from urllib.parse import unquote
import pandas as pd
import os


# In[11]:


def construct_link(): 
    print('''Hello! This webscraper will pull all relevant business information for you, 
please enter the information below (Be aware this may take up to 30 minutes to complete, 
also please no numbers or symbols).''')
    print('===========================================')
    global industry
    global city
    global state
    while True: 
        try:
            industry = input('Please type in an Industry: ').capitalize().replace(' ', '')
            city = input('Please type in a City: ').capitalize().replace(' ', '')
            state = input('Please type in the acronym of the city\'s state (New York = NY): ').strip().upper()
            
            if industry.isalpha() and city.isalpha() and state.isalpha() and len(state) == 2:
                test_url = f"https://www.yelp.com/search?find_desc={industry}&find_loc={city}%2C+{state}&start="
                break
            else:
                print('I\'m sorry, one of your responses was invalid. Please try again.')
        except ValueError:
            print('I\'m sorry, one of your responses was invalid. Please try again.')
        
    return test_url
  


# In[12]:


def get_indv_business_links(url_needed): 
    
    print("Step 1: Obtaining all the links from each individual page.")
    global page_numbers
    page_numbers = range(0,231,10)
    link_lst = []
    #initiate a blank list for the links

    for page_number in page_numbers:

        url = f'{url_needed}{page_number}'
        result = requests.get(url).text 
        doc = BeautifulSoup(result, 'html.parser')
        #parse html down to the link string
        body = doc.find('body')
        main = body.find('ul')
        title_link = main.find_all('h3')

        for i in title_link:
            a_tag = i.find('a')
            #parsed down to the correct html area
            if a_tag:
                href_value = a_tag.get('href')
                link = 'https://yelp.com'+ href_value
                link_lst.append(link)
                # pull the link from href and contcatinating https://yelp.com + link
    
    return link_lst


# In[13]:




def getting_org_data(list_of_links): 
    
    print('Step 2: Working on Getting all the information from each page.')
    contact_list = []

    for url2 in list_of_links:

        page_result = requests.get(url2).text
        info_pages= BeautifulSoup(page_result, 'html.parser')
        #pulling liinks from list and iterating through for each link
        body2 = info_pages.find('body')
        aside = body2.find('aside')
        #parsing down the heirarchy of html docs to the block containing the information needed
        try:
            if aside:
                phone_number = aside.find_all('p', class_ = 'css-1p9ibgf')
                address = aside.find_all('p', class_ = 'css-qyp8bo')
                business_website = aside.find('a')
                #parsing down to the correct html script that contains the string value 
                spcbody = body2.find_all('a', class_='css-19v1rkv')  # Extract from body, not aside

                spclst = []
                for x in spcbody:
                    if 'find_desc' in x.get('href'):
                        spclst.append(x.text)

                if business_website:
                    main = body2.find('main')
                    #have to move to main to grab the business name, (unsure if i should move this out of an if statment)
                    business_name = body2.find('h1', class_='css-1se8maq').text
                    business_website2 = business_website.get('href')
                    bizzy_website = business_website2.removeprefix('/biz_redir?url=')
                    decoded_url = unquote(bizzy_website).split('&')
                    # conducting string manipulation for the correct link to the business 
                    contact_list.append((business_name,decoded_url[0],phone_number[1].text,
                    address[0].text,', '.join(spclst)))
                    #appedning the sliced string of each part if html text infomation, 

        except (AttributeError, IndexError, ValueError): 
            pass 
    
    return contact_list


# In[14]:


def create_dataframe(data):

    print(f'Step 3: Done! You can now see a CSV file and Excel file for {industry} in {city}, {state} within your Downloads folder.') 
    headers2 = ['Business Name', 'Website', 'Phone', 'Address', 'Specialty']

    df = pd.DataFrame(data, columns= headers2)
    df = df.set_index("Business Name")
    df = df.replace(to_replace='Get Directions', value= 'Phone Number Unavailable')
    df = df.replace(r'^/map/.*', 'Website Unavailable', regex=True)
    df2 = df

    downloads_folder = os.path.expanduser("~") + os.sep + "Downloads"
    filepath_csv = os.path.join(downloads_folder, f"{industry}_in_{city},{state}--yelp_scrap.csv")
    filepath_excel = os.path.join(downloads_folder, f"{industry}_in_{city},{state}--yelp_scrap.xlsx")

    df2.to_csv(filepath_csv)
    df2.to_excel(filepath_excel)

    return None


# In[15]:


if __name__ == "__main__":
    create_dataframe(getting_org_data(get_indv_business_links(construct_link())))

