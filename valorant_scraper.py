import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import time



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

print("Downloads complete.")