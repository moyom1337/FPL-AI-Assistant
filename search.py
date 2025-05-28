import requests
import pandas as pd

# Fetch player data
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(FPL_API_URL).json()

def search_player(name_query):
    players_df = pd.DataFrame(data["elements"])
    players_df["full_name"] = players_df["first_name"] + " " + players_df["second_name"]
    matching = players_df[players_df["second_name"].str.contains(name_query, case=False)]
    return matching[["id", "full_name", "now_cost", "total_points"]]

print(search_player("Mb"))
