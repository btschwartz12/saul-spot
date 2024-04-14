import requests
from bs4 import BeautifulSoup
import os

# Replace `your_base_url` with the actual base URL of the website
base_url = "https://subslikescript.com"

# URL of the menu page that lists all episodes
menu_page_url = base_url + "/series/Better_Call_Saul-3032476"

response = requests.get(menu_page_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all season divs
seasons = soup.find_all("div", class_="season")

for season in seasons:
    season_title = season.find("h4").get_text().strip()
    episodes = season.find_all("a")
    
    # Create a directory for the season
    season_dir = f"transcripts/{season_title.replace(' ', '_')}"
    if not os.path.exists(season_dir):
        os.makedirs(season_dir)
    
    episode_number = 1
    
    for episode in episodes:
        episode_name = episode.get_text().strip()
        episode_url = base_url + episode['href']
        
        # Fetch the episode page
        episode_response = requests.get(episode_url)
        episode_soup = BeautifulSoup(episode_response.content, 'html.parser')
        
        # Assuming the transcript is within a div with class "full-script"
        transcript = episode_soup.find("div", class_="full-script").get_text(separator="\n").strip()
        
        # Save the transcript
        with open(f"{season_dir}/{episode_number}-{episode_name.replace('/', '_')}.txt", "w", encoding="utf-8") as file:
            file.write(transcript)
        
        print(f"Transcript for {season_title} episode {episode_number} has been downloaded and saved.")
        episode_number += 1

print("All transcripts have been downloaded and saved.")
