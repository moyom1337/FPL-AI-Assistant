import requests
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Connect to fpl api
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
response = requests.get(FPL_API_URL)
FIXTURES_API_URL = "https://fantasy.premierleague.com/api/fixtures/"
fixtures = requests.get(FIXTURES_API_URL).json()

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

data = response.json()

# Create a DataFrame for positions
positions_df = pd.DataFrame(data["element_types"])
positions_df = positions_df.rename(columns={"id": "element_type", "singular_name": "position"})

# Create a Dataframe for players
players_df = pd.DataFrame(data["elements"])
players_df = players_df.merge(positions_df[["element_type", "position"]], on="element_type", how="left")

# Create a DataFrame for teams
teams_df = pd.DataFrame(data["teams"])

next_fixture_fdr = {}

for fixture in fixtures:
    if fixture["event"] is not None:
        home_id = fixture["team_h"]
        away_id = fixture["team_a"]
        
        # If not already added (i.e., first upcoming fixture), add it
        if home_id not in next_fixture_fdr:
            next_fixture_fdr[home_id] = fixture["team_h_difficulty"]
        if away_id not in next_fixture_fdr:
            next_fixture_fdr[away_id] = fixture["team_a_difficulty"]

# Add the fixture difficulty rating to the players DataFrame
players_df["fdr_next"] = players_df["team"].map(next_fixture_fdr)

# Fill NaN values in 'fdr_next' with 0
players_df["fdr_next"] = players_df["fdr_next"].fillna(0)

# Encode positions using numbers
players_df["position_code"] = players_df["position"].map({
    "Goalkeeper": 1,
    "Defender": 2,
    "Midfielder": 3,
    "Forward": 4
})

features = ["form", "total_points", "minutes", "now_cost", "threat", "creativity", "influence", "fdr_next", "position_code"]
target = "event_points"  

# Train Test Split to predict points
X = players_df[features]
y = players_df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Model evaluation
y_pred = model.predict(X_test)

# Decided on mae for evaluation metric
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")

# Take in the player ID and use trained model to predict points for player.
def predict_player_points(player_id):
    player = players_df[players_df["id"] == player_id][features]
    prediction = model.predict(player)
    return prediction[0]

player_id = 328  # use search.py to find player ID
player_row = players_df[players_df["id"] == player_id]

if not player_row.empty:
    full_name = player_row.iloc[0]["first_name"] + " " + player_row.iloc[0]["second_name"]

predicted_points = predict_player_points(player_id)
print(f"Predicted Points for {full_name}: {predicted_points}")

# Close the database connection
conn.close()
