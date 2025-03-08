import requests
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

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

data = response.json()

# Dataframe creation
players_df = pd.DataFrame(data["elements"])
features = ["form", "total_points", "minutes", "now_cost", "threat", "creativity", "influence"]
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

def predict_player_points(player_id):
    player = players_df[players_df["id"] == player_id][features]
    prediction = model.predict(player)
    return prediction[0]

player_id = 328  # use search.py to find player ID
predicted_points = predict_player_points(player_id)
print(f"Predicted Points for Player {player_id}: {predicted_points}")
