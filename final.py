import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from random import randint

# main input
# http://comp20008-jh.eng.unimelb.edu.au:9889/main/

# testing input:
# http://comp20008-jh.eng.unimelb.edu.au:9889/sample/


#=================================TASK 1 & 2===================================
#initial page to crawl
base_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/sample/'
rugby_file_name = 'rugby.json'
tail_url = ''
rugby_name_record = [] # store team name from rugby.json
visited_url = [] # record visited url
headline = [] # record headline of each article
team_name_article = [] # record the name first mentioned in each article
all_score = [] # store all possible score for each article
max_score_of_article = '' # store the max score of the article, 0 if non found
max_score_record = [] # store all max scores of all articles
max_sum_score = 0 #store the max sum of max score for each article
team_name_found = 0 # toggle telling if there is a team name in article or not 

#Crawl welcome page 
seed_url = base_url + tail_url 
page = requests.get(seed_url)
soup = bs(page.text, 'html.parser')

#Open rugby.json file and load to rugby_data
with open(rugby_file_name) as f:
    rugby_data = json.load(f)
    
#List of team name for reference 
for team in rugby_data['teams']: #"teams" can be replaced by key in dictionary
    rugby_name_record.append(team['name'])

# Take url of first page after welcome page 
tail_url = soup.find("a")["href"]
seed_url = base_url + tail_url

while True:
    team_name_found = 0 # toggle telling if a team name is found yet or not
    max_sum_score = 0 # store max sum each score in article
    all_score = [] #store all score in article 
    max_score_of_article = 0 #should be digit-digit, but 0 is used for compare
    score1 = 0 #team 1 score
    score2 = 0 #team 2 score
    first_name = '' #buffer to store name with smallest index
    min_index = -1 # minimum index of the country name found in the article
    
    #=======================================
    #I. ACCESSING ARTICLE 
    page = requests.get(seed_url)
    soup = bs(page.text, 'html.parser')  

    #=======================================
    #II. RECORD URL AND HEADLINE
    visited_url.append(seed_url)
    headline.append(soup.h1.text) 
    
    #=======================================
    
    #III. FIND FIRST VALID NAME IN ARTICLE 
    
    #1. Create arrays of paragraph in the articles:
    essay = soup.h1.text   #taking in headline
    for para in soup.findAll('p'):
        essay += para.text
        
    #2. Looping through each paragragh in para_list to find for team name
    for name_try in rugby_name_record:
        if essay.find(name_try) != -1:
            team_name_found = 1
            if essay.find(name_try) < min_index or min_index == -1:
                first_name = name_try
                min_index = essay.find(name_try)
        else:
            continue
        
    # Assign name to "NULL" if no valid name is found
    if team_name_found == 0:  
        team_name_article.append("NULL")
    elif team_name_found == 1:
        team_name_article.append(first_name)
        
    #=======================================    
    
    #IV. FIND MAXIMUM SCORE IN ARTICLE ()
    
    #1. Find for score
    all_score = re.findall(r' \d{1,3}-\d{1,3}', essay)
    
    #2. Looping through all_score to find the maximum score of article
    if re.findall(r' \d{1,3}-\d{1,3}',essay):
        for score in all_score:
            #findall will return a list and index 0 to access that element
            score1 = int(re.findall(r'\d{1,3}-', score)[0].strip("-"))
            score2 = int(re.findall(r'-\d{1,3}', score)[0].strip("-"))        
            if (score1 + score2) >= max_sum_score:
                max_sum_score = score1 + score2
                max_score_of_article = score.strip()
        
    #3. Recording max score of the article and its difference
    max_score_record.append(max_score_of_article)
    
    #======================================= 
    
    #V. FIND LINK OF THE NEXT PAGE FOR THE LOOP
    tail_url = soup.find("div", id = "links").find_all('a')[1]["href"]
    seed_url = base_url + tail_url
    
    if seed_url in visited_url:
        break

#=======================================
#Convert to numpy array for dataframe (used to produce csv output file)
headline_column = pd.Series(headline)
visited_url_column = pd.Series(visited_url)
team_column = pd.Series(team_name_article)
score_column = pd.Series(max_score_record)

# Making csv file for task 1
df_task1 = pd.DataFrame({"url":visited_url_column, "headline":headline_column})
df_task1.to_csv("task1.csv", index=False)

#=======================================
# Making csv file for task 2
df_task2 = pd.DataFrame({"url":visited_url_column, "headline":headline_column,
                         "team":team_column, "score":score_column})

df_task2 = df_task2[df_task2.team != "NULL"]
df_task2 = df_task2[df_task2.score != 0]
df_task2.to_csv("task2.csv", index=False)



#==================================TASK 3======================================

score_difference = [] # score difference for each valid article
name_in_valid_article = [] # storing the names written in each article
team_num_article = {} # storing number of articles 
team_ave_difference = {} #storing average difference of each team, used in task
#4 and 5
  
for team in df_task2["team"]:
    name_in_valid_article.append(team)

# Using regex to find score difference 
for score in df_task2["score"]:
    score1 = int(re.findall(r'\d{1,3}-',score)[0].strip("-"))
    score2 = int(re.findall(r'-\d{1,3}',score)[0].strip("-"))
    score_difference.append(abs(score1 - score2))

for i in range(len(score_difference)):
    if name_in_valid_article[i] not in team_ave_difference:
        team_ave_difference[name_in_valid_article[i]] =\
            int(score_difference[i])
        team_num_article[name_in_valid_article[i]] = 1
    else:
        team_ave_difference[name_in_valid_article[i]] +=\
            int(score_difference[i])
        team_num_article[name_in_valid_article[i]] += 1

for i in rugby_name_record:
    if i in team_ave_difference:
        team_ave_difference[i] = team_ave_difference[i]/team_num_article[i]
        
#=======================================
# Making csv file for task 3
task3_team = pd.Series(list(team_ave_difference.keys()))
task3_ave = pd.Series(list(team_ave_difference.values()))
df_task3 = pd.DataFrame({"team": task3_team, "avg_game_difference": task3_ave})
df_task3.to_csv('task3.csv', index = False)


#===================================TASK4======================================

task4_team = pd.Series(list(team_num_article.keys()))
task4_num  = pd.Series(list(team_num_article.values()))
df_task4 = pd.DataFrame({"team": task4_team, "num articles":task4_num})
df_task4 = df_task4.sort_values(by = ['num articles'], ascending = False)
df_task4 = df_task4.head(5)                         

plt.figure(figsize=(5,7))
plt.bar(df_task4['team'], df_task4['num articles'])
plt.ylabel('Number of articles') 
plt.title("Graph of five teams with most written articles")
plt.yticks(np.arange(0, max(team_num_article.values()) + 2, 1))
plt.savefig('task4.png')


#===================================TASK 5=====================================
plt.figure()
x = list(team_num_article.values())
y = list(team_ave_difference.values())
legends = list(team_num_article.keys())
colors = []
for i in range(len(x)):
    colors.append('#%06X' % randint(0, 0xFFFFFF))

for i in range(len(x)):
    plt.scatter(x[i],y[i], c = colors[i], label = legends[i])
    plt.legend()
    
plt.xticks(np.arange(0, max(team_num_article.values()) + 2, 1))    
plt.xlabel('Number of mentioned articles')
plt.ylabel('Average game difference')
plt.title('Average game difference vs. number of mentioned articles')
plt.savefig('task5.png')