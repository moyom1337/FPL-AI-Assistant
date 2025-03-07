import requests
import sqlite3

# Connect to fpl api
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

response = requests.get(FPL_API_URL)

# Print the number of players in FPL
if response.status_code == 200:
    data = response.json()
    print("Total players:", len(data["elements"])) 
else:
    print("Failed to fetch data")

conn = sqlite3.connect("fpl.db")
cursor = conn.cursor()

# Create the 'players' table to store player info
cursor.execute('''
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    second_name TEXT,
    team TEXT,
    total_points INTEGER,
    now_cost INTEGER
)
''')

for player in data["elements"]:
    cursor.execute('''
    INSERT OR REPLACE INTO players (id, first_name, second_name, team, total_points, now_cost)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (player["id"], player["first_name"], player["second_name"], player["team"], player["total_points"], player["now_cost"]))

conn.commit()
conn.close()
print("Data inserted successfully!")

# Example - All players that play for specified team

response = requests.get(FPL_API_URL)
if response.status_code == 200:
    data = response.json()

    team_players = [p for p in data["elements"] if p["team"] == 1] # Arsenal's team id is 1, alphabetical order
    sorted_players = sorted(team_players, key=lambda p: p["total_points"], reverse=True)

    # Display results
    for player in sorted_players:
        print(f"{player['first_name']} {player['second_name']} - {player['now_cost'] / 10}M - {player['total_points']} pts")
else:
    print("Failed to fetch data")