import requests
import pandas as pd

# Fetch player data
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(FPL_API_URL).json()

# Make Dataframe
players_df = pd.DataFrame(data["elements"])
players_df = players_df[["id", "first_name", "second_name", "now_cost", "total_points"]]
player_name = "Salah"

# Search for players that have names containing player_name
matching = players_df[players_df["second_name"].str.contains(player_name, case=False)]
print(matching)