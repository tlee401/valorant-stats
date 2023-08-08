import snowflake.connector
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import time

conn = snowflake.connector.connect(
    user='******',
    password='******',
    account='*******',
    warehouse='COMPUTE_WH',
    database='VALORANT_DATABASE',
    schema='VALORANT_SCHEMA'
)

def getValorantMapStats():
    resultString = ""
    for rankNum in range(3, 28):
        baseURL = f"https://blitz.gg/valorant/stats/maps?sortBy=attackingRoundWinRate&sortDirection=DESC&mode=competitive&rank={rankNum}"
        response = requests.get(baseURL)
        time.sleep(5)
        soup = BeautifulSoup(response.content, "html.parser")
        mapNames = soup.find_all('a', class_ = "⚡ac0808b4")
        mapStats = soup.find_all('div', class_ = "⚡a43e6c6f column ⚡904d395")
        for mapNum in range(0, len(mapNames)):
            formatted_date = date.today().strftime("%Y-%m-%d")
            resultString += mapNames[mapNum].text + "," + str(rankNum) + "," + formatted_date
            for statsNum in range(4*mapNum, 4*(mapNum + 1)):
                stat = mapStats[statsNum].text
                stat = stat.replace("%", "")
                stat = stat.replace(",", "")
                resultString += "," + stat
            resultString += "\n"
    return resultString

def getValorantAgentStats():
    resultString = ""
    response = requests.get("https://blitz.gg/valorant/stats/maps")
    time.sleep(5)
    soup = BeautifulSoup(response.content, "html.parser")
    mapNames = soup.find_all('a', class_ = "⚡ac0808b4")
    for rankNum in range(3, 28):
        for mapName in mapNames:
            mapNameString = mapName.text.lower()
            baseURL = f"https://blitz.gg/valorant/stats/agents?sortBy=winRate&type=general&sortDirection=DESC&mode=competitive&rank={rankNum}&map={mapNameString}"
            response = requests.get(baseURL)
            time.sleep(5)
            soup = BeautifulSoup(response.content, "html.parser")  
            agentStats = soup.find_all('div', class_ = "⚡a3efd15e column ⚡904d395")
            agentNames = soup.find_all('div', class_ = "⚡aa23a74f column ⚡904d395 sticky")
            for agentNum in range(0, len(agentNames)):
                formatted_date = date.today().strftime("%Y-%m-%d")
                resultString += agentNames[agentNum].text + "," + str(mapNameString) + "," + str(rankNum) + "," + formatted_date
                for statsNum in range(8*agentNum + 1, 8*(agentNum + 1)):
                    stat = agentStats[statsNum].text
                    stat = stat.replace(",", "")
                    stat = stat.replace("  /  ", ",")
                    stat = stat.replace(" ", "")
                    stat = stat.replace("%", "")
                    resultString += "," + stat
                resultString += "\n"
    return resultString

def getValorantGunStats():
    resultString = ""
    response = requests.get("https://blitz.gg/valorant/stats/maps")
    time.sleep(5)
    soup = BeautifulSoup(response.content, "html.parser")
    mapNames = soup.find_all('a', class_ = "⚡ac0808b4")
    for rankNum in range(3, 28):
        for mapName in mapNames:
            mapNameString = mapName.text.lower()
            baseURL = f"https://blitz.gg/valorant/stats/weapons?sortBy=avgDamage&type=all&sortDirection=DESC&mode=competitive&rank={rankNum}&map={mapNameString}"
            response = requests.get(baseURL)
            time.sleep(5)
            soup = BeautifulSoup(response.content, "html.parser")  
            gunStats = soup.find_all('div', class_ = "⚡a3efd15e column ⚡904d395")
            gunNames = soup.find_all('div', class_ = "⚡aa81fafd column ⚡904d395 sticky")
            for gunNum in range(0, len(gunNames)):
                formatted_date = date.today().strftime("%Y-%m-%d")
                resultString += gunNames[gunNum].text + "," + str(mapNameString) + "," + str(rankNum) + "," + formatted_date
                for statsNum in range(5*gunNum + 1, 5*(gunNum + 1)):
                    stat = gunStats[statsNum].text
                    stat = stat.replace(",", "")
                    stat = stat.replace(" ", "")
                    stat = stat.replace("%", "")
                    resultString += "," + stat
                resultString += "\n"
    return resultString

print("Starting map stat downloads...")

file_path = "/Users/timothylee/Documents/PythonProjects/valorant_map_stats.txt"
file = open(file_path, "w")
file.write(getValorantMapStats())
file.close()

print("Map stat download complete. Starting agent stat download...")

file_path = "/Users/timothylee/Documents/PythonProjects/valorant_agent_stats.txt"
file = open(file_path, "w")
file.write(getValorantAgentStats())
file.close()

print("Agent stat download complete. Starting gun stat download...")

file_path = "/Users/timothylee/Documents/PythonProjects/valorant_gun_stats.txt"
file = open(file_path, "w")
file.write(getValorantGunStats())
file.close()

print("Downloads complete. Uploading CSV files to Snowflake database...")

# # CODE USED TO READ IN CSV FILE OF HOUSE LISTINGS
file_path_maps = '/Users/timothylee/Documents/PythonProjects/valorant_map_stats.txt'
file_path_agents = '/Users/timothylee/Documents/PythonProjects/valorant_agent_stats.txt'
file_path_guns = '/Users/timothylee/Documents/PythonProjects/valorant_gun_stats.txt'
file_name_maps = "valorant_map_stats.txt"
file_name_agents = "valorant_agent_stats.txt"
file_name_guns = "valorant_gun_stats.txt"
stage_name = 'TEMP_STAGE'
table_name_maps = 'MAP_STATS'
table_name_agents = 'AGENT_STATS'
table_name_guns = 'GUN_STATS'

# Create a Snowflake cursor
cursor = conn.cursor()

# Create a temporary stage for file upload
cursor.execute(f"CREATE TEMPORARY STAGE {stage_name}")

# Upload the CSV file to the stage
cursor.execute(f"PUT 'file://{file_path_maps}' @{stage_name}")
cursor.execute(f"PUT 'file://{file_path_agents}' @{stage_name}")
cursor.execute(f"PUT 'file://{file_path_guns}' @{stage_name}")

# Load data from the staged CSV file into the table
cursor.execute(f"COPY INTO {table_name_maps} FROM @{stage_name}/{file_name_maps} FILE_FORMAT=(TYPE=CSV)")
cursor.execute(f"COPY INTO {table_name_agents} FROM @{stage_name}/{file_name_agents} FILE_FORMAT=(TYPE=CSV)")
cursor.execute(f"COPY INTO {table_name_guns} FROM @{stage_name}/{file_name_guns} FILE_FORMAT=(TYPE=CSV)")

# Close the cursor
cursor.close()

# Close the connection
conn.close()

print("Upload complete.")