import pandas as pd
import os

class DataLoader:
    """Loads the local data and cleans it"""

    def __init__(self, year, league):
        self.year = year
        self.league = league
        self.data = None

    def load_data(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "..", "data", str(self.year), "standings", self.league + ".json")
        standings = pd.read_json(file_path)
        reduced_standings, full_standings = self.clean_data(standings)
        return [reduced_standings, full_standings]
    
    def clean_data(self, df):
        df.drop(columns=["status", "update"], inplace=True)
        df.rename(columns={"all": "total"}, inplace=True)

        for column in ["team", "total", "home", "away"]:
            expanded_df = pd.json_normalize(df[column])
            expanded_df.columns = [f"{column}_{col}" for col in expanded_df.columns]

            df = pd.concat([df, expanded_df], axis=1)
            df = df.drop(column, axis=1)

        #df.set_index("rank", inplace=True)
        reduced_df = df[["rank", "team_logo", "team_name", "total_played", "total_win", "total_draw", "total_lose", "total_goals.for", "total_goals.against", "points"]]
        full_df = df[["rank", "team_logo", "team_name", "total_played", "total_win", "total_draw", "total_lose", "total_goals.for", "total_goals.against",
                      "home_win", "home_draw", "home_lose", "home_goals.for", "away_draw", "away_lose", "away_goals.for", "away_goals.against", "points"]]
        
        return reduced_df, full_df