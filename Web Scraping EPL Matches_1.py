#!/usr/bin/env python
# coding: utf-8

# ## Web Scraping EPL Matches
# 
# In this project we will extract data on two season(2020-2021 and 2021-2022) from 'fbref.com'. 
# 
# We will start by accessing the url and turning it to text format to later parse through and get the data we want.

# In[1]:


import requests 


# In[2]:


url = 'https://fbref.com/en/comps/9/2021-2022/2021-2022-Premier-League-Stats'


# In[3]:


data = requests.get(url)  ## download the page


# In[44]:


from bs4 import BeautifulSoup ## allows us to navigate and fetch data from url's


# In[7]:


soup = BeautifulSoup(data.text)  ## parsing the downloaded html


# In[45]:


standings_table = soup.select('table.stats_table')[0] ## selecting tables elements in the page with class "stats_table"


# In[10]:


links = standings_table.find_all('a')


# In[11]:


links = [l.get('href') for l in links]


# In[12]:


links = [l for l in links if '/squads' in l]  ## looking for links with "/squads" in them


# In[13]:


links


# ##### Above is a list of the relative links for each team's stats. We will take these relative links and turn them to absolute links that we can use to extract stat tables from

# In[14]:


full_urls = [f'https://fbref.com{l}' for l in links]  ## adding string to beginning of each link to make absolute links


# In[15]:


full_urls


# In[16]:


team_url = full_urls[0]


# In[17]:


data = requests.get(team_url)


# In[18]:


import pandas as pd


# In[19]:


matches = pd.read_html(data.text, match = 'Scores & Fixtures')  ##


# In[21]:


matches[0]


# In[22]:


soup = BeautifulSoup(data.text)


# In[23]:


link = soup.find_all('a')


# In[24]:


link = [l.get('href') for l in link ]


# In[25]:


link = [l for l in link if l and 'all_comps/shooting/' in l]


# In[26]:


link


# In[27]:


data = requests.get(f'https://fbref.com{link[0]}')


# In[28]:


shooting = pd.read_html(data.text, match = 'Shooting')[0]


# In[29]:


shooting.head()


# In[30]:


shooting.columns = shooting.columns.droplevel()


# In[31]:


shooting.head()


# ##### In the past few lines of code we extracted two stat tables and now we will merge them together(this table is only for 2021-2022 season).

# In[32]:


team_data = matches[0].merge(shooting[['Date','Sh', 'SoT', 'Dist','FK','PK','PKatt']], on = 'Date')


# In[33]:


team_data


# In[34]:


matches[0].shape


# ## Bringing It All Together
# 
# Now that we have a framework of what we need to do, we will put it all under a 'for' loop to extract stats for both season (2020-2021 and 2021-2022) and put them all in one dataframe. This dataframe will be saved as a '.csv' and could be used for data cleaning and to later extract uselful information out of the data.

# In[ ]:


years = list(range(2022,2020, -1))
all_matches = []
standings_url = 'https://fbref.com/en/comps/9/2021-2022/2021-2022-Premier-League-Stats'

import time

for year in years:
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text)
    standings_table = soup.select('table.stats_table')[0]
    
    links = [l.get('href') for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads' in l]
    team_urls = [f'https://fbref.com{l}' for l in links] 
    
    previous_season = soup.select('a.prev')[0].get('href')
    standings_url = f'https://fbref.com{previous_season}'
    
    for team_url in team_urls:
        team_name = team_url.split('/')[-1].replace('-Stats', '').replace('-',' ')
        data = requests.get(team_url)
        matches = pd.read_html(data.text, match ='Scores & Fixtures')[0]
        
        soup = BeautifulSoup(data.text)
        links = [l.get('href') for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        data = requests.get(f'https://fbref.com{links[0]}')
        shooting = pd.read_html(data.text, match = 'Shooting')[0]
        shooting.columns = shooting.columns.droplevel()
        
        try:
            team_data = matches.merge(shooting[['Date','Sh', 'SoT', 'Dist','FK','PK','PKatt']], on = 'Date')
        except ValueError:
            continue 
            
        team_data = team_data[team_data['Comp'] == 'Premier League']
        team_data['Season'] = year
        team_data['Team'] = team_name
        all_matches.append(team_data)
        time.sleep(1.5)


# In[39]:


match_df = pd.concat(all_matches)


# In[40]:


match_df.columns = [c.lower() for c in match_df.columns]


# In[41]:


match_df


# In[43]:


match_df.to_csv('matches_1.csv')


# In[ ]:




