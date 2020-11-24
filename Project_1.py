from bs4 import BeautifulSoup as bf
from urllib.parse import urljoin
import requests as res
import re
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# Get total value and the difference
def sum_or_diff(scores):
    score = scores.split('-')
    total = 0
    for num in score:
        total += int(num)
    return [total, abs(int(score[0]) - int(score[1]))]

# Initialize page to crawl 
base = 'http://comp20008-jh.eng.unimelb.edu.au:9889/sample/'
seed_item = 'index.html'
seed_url = base + seed_item
soup = bf(res.get(seed_url).text, 'html.parser')
visited = {}; visited[seed_url] = soup.h1.string
# Remove index.html
links = soup.findAll('a')
seed_link = soup.findAll('a', href=re.compile("^index.html"))
# to_visit_relative = list(set(links) - set(seed_link))
to_visit_relative = [l for l in links if l not in seed_link]
# Resolve to absolute urls
to_visit = [urljoin(seed_url, link['href']) for link in to_visit_relative]

# Find all outbound links on succsesor pages and explore each one
pages_visited = 1
while (to_visit):
    # consume the list of urls
    link = to_visit.pop(0)
    # scarping
    soup = bf(res.get(link).text, 'html.parser')
    # add headline to visited list
    visited[link] = soup.h1.string
    # mark the item as visited, i.e., add to visited list, remove from to_visit
    new_links = soup.findAll('a')
    for new_link in new_links:
        new_item = new_link['href']
        new_url = urljoin(link, new_item)
        if new_url not in visited and new_url not in to_visit:
            to_visit.append(new_url)
    pages_visited += 1
# We do not need the main page's url and its title   
del visited[seed_url]
# Exporting to CSV
pd.DataFrame({"url":list(visited.keys()), "headline":list(visited.values())}).to_csv(r'task1.csv', index = False)

# Open rugby.json and extract team informations
with open("rugby.json") as json_file:
    team_names = [group['name'] for group in json.load(json_file)['teams']]
    
webs = {}; teams = []; largest = []
# Access each articles to obtain informations
for url in list(visited.keys()):
    # Get the html elements
    page = res.get(url)
    soup = bf(page.text, "html.parser")
    # Get the text body containing headline and main article 
    article = soup.h1.string + soup.body.text.strip()
    # To deal with invalid score
    score_pattern = r'\d{1,4}-\d{1,4}'
    searching = (re.findall(score_pattern, article))
    invalids = r'\d{3,4}-\d{1,4}'
    errors = (re.findall(invalids, article)) if (re.findall(invalids, article)) else []
    valid = [score for score in searching if score not in errors]
    
    if(valid):
        # To find the largest scores
        scores = {}
        for pair in valid:
            total = sum_or_diff(pair)
            scores[pair] = total      
        # To find the first team name appearing in the article     
        names = {}
        for name in team_names:
            name_search = (re.search(name, article, re.IGNORECASE))
            if(name_search):
                names[name] = name_search.span()[0]  
        if(names):
            largest.append(max(scores, key=scores.get))
            teams.append(min(names, key=names.get))
            webs[url] = soup.h1.string
# Start Making csv file for task 2                
tasks = pd.DataFrame({"url":list(webs.keys()), "headline":list(webs.values()), "team":teams, "score":largest})
tasks.to_csv(r'task2.csv', index=False)  

# Find the average score difference
tasks.groupby("team").count()['headline']
tasks["avg_game_difference"] = [sum_or_diff(i)[1] for i in tasks["score"]]
tasks.groupby("avg_game_difference").count()
task3 = tasks.groupby("team").sum()
task3["avg_game_difference"] = task3["avg_game_difference"] / tasks.groupby("team").count()["url"]
task3 = pd.DataFrame({"team":task3.index.values, "avg_game_difference":task3["avg_game_difference"]})
task3.to_csv(r'task3.csv', index=False)

# To find top 5 team that has most article written about and plot in bar chart
task4 = tasks.groupby("team").count().sort_values(by=["url"], ascending = False)
top5_sorted = task4[:5]
top5_sorted.index
plt.bar(top5_sorted.index, top5_sorted["url"], color="Grey")
plt.xlabel("Team", size=20, color="Orange")
plt.ylabel("Frequence", size=20, color="Green")
plt.title("Most frequently written team", size=25, color="Blue")
plt.savefig('task4.png',bbox_inches='tight')
plt.show()

# To compare the number of articles written about each team
# With their average game_difference then plot in chart
group = list(set(tasks["team"]))
result = {}; name_order = []
for name in group:
    result[task4.loc[name]["url"]] = task3.loc[name]["avg_game_difference"]
# To get sorted keys for better analysing
# And get names in and order
result = dict(sorted(result.items()))
for num in result.keys():
    order = [name_order.append(name) for name in group if 
                  task4.loc[name]["url"] == num]
# To plot data with double bars
plt.style.use('seaborn-whitegrid') 
ax = plt.subplots()[1]
index = np.arange(len(group))
bar_width = 0.25; opacity = 0.9
ax.bar(index, list(result.keys()), bar_width, alpha=opacity, color='g', 
       label='Article num')
ax.bar(index+bar_width, list(result.values()), bar_width, alpha=opacity, color='b', 
       label='Avg diff')
ax.set_xlabel('Team', size=20, color="Orange")
ax.set_title('Average Game Score Difference Each Team', size=15, color="Brown")
ax.set_xticks(index + bar_width / 2)
ax.set_xticklabels(name_order, rotation = -10)
ax.legend()
plt.savefig('task5.png',bbox_inches='tight')
plt.show()