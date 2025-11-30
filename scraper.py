"""
Football Player Data Fetcher

Downloads player statistics from Kaggle datasets.
Uses the Football Player Stats 2024-2025 dataset.
"""

import pandas as pd
from pathlib import Path
import urllib.request
import zipfile
import os

OUTPUT_DIR = Path(__file__).parent / "data"

# Kaggle dataset URL (direct CSV download)
# Using a reliable football dataset
DATASET_URL = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2025-26/players_raw.csv"


def download_fpl_data() -> pd.DataFrame:
    """Download Fantasy Premier League player data."""
    print("Downloading FPL player data...")
    print("=" * 50)

    try:
        df = pd.read_csv(DATASET_URL)
        print(f"Downloaded {len(df)} players")
        return df
    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame()


def clean_fpl_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare FPL data for the dashboard."""
    if df.empty:
        return df

    # Map position IDs to names
    position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

    # Select and rename columns
    cleaned = pd.DataFrame({
        "player": df["first_name"] + " " + df["second_name"],
        "team": df["team"].astype(str),
        "position": df["element_type"].map(position_map),
        "price": df["now_cost"] / 10,  # Convert to millions
        "total_points": df["total_points"],
        "minutes": df["minutes"],
        "goals": df["goals_scored"],
        "assists": df["assists"],
        "clean_sheets": df["clean_sheets"],
        "goals_conceded": df["goals_conceded"],
        "yellow_cards": df["yellow_cards"],
        "red_cards": df["red_cards"],
        "bonus": df["bonus"],
        "influence": pd.to_numeric(df["influence"], errors="coerce"),
        "creativity": pd.to_numeric(df["creativity"], errors="coerce"),
        "threat": pd.to_numeric(df["threat"], errors="coerce"),
        "ict_index": pd.to_numeric(df["ict_index"], errors="coerce"),
        "selected_by_percent": pd.to_numeric(df["selected_by_percent"], errors="coerce"),
        "form": pd.to_numeric(df["form"], errors="coerce"),
        "points_per_game": pd.to_numeric(df["points_per_game"], errors="coerce"),
    })

    # Add league column (all FPL data is Premier League)
    cleaned["league"] = "Premier League"

    return cleaned


def create_sample_data() -> pd.DataFrame:
    """Create sample data for demo purposes if download fails."""
    print("Creating sample data for demo...")

    # Sample data covering top players from different leagues
    sample_data = [
        # Premier League
        {"player": "Erling Haaland", "team": "Manchester City", "position": "FWD", "league": "Premier League",
         "age": 24, "minutes": 1800, "goals": 15, "assists": 4, "xG": 13.5, "xAG": 2.1, "progressive_carries": 25,
         "progressive_passes": 18, "yellow_cards": 1, "red_cards": 0},
        {"player": "Mohamed Salah", "team": "Liverpool", "position": "MID", "league": "Premier League",
         "age": 32, "minutes": 1650, "goals": 12, "assists": 8, "xG": 10.2, "xAG": 5.5, "progressive_carries": 45,
         "progressive_passes": 52, "yellow_cards": 0, "red_cards": 0},
        {"player": "Cole Palmer", "team": "Chelsea", "position": "MID", "league": "Premier League",
         "age": 22, "minutes": 1700, "goals": 10, "assists": 6, "xG": 8.5, "xAG": 4.8, "progressive_carries": 38,
         "progressive_passes": 65, "yellow_cards": 2, "red_cards": 0},
        {"player": "Bukayo Saka", "team": "Arsenal", "position": "MID", "league": "Premier League",
         "age": 23, "minutes": 1600, "goals": 7, "assists": 9, "xG": 6.2, "xAG": 7.1, "progressive_carries": 55,
         "progressive_passes": 70, "yellow_cards": 3, "red_cards": 0},
        {"player": "Alexander Isak", "team": "Newcastle", "position": "FWD", "league": "Premier League",
         "age": 25, "minutes": 1500, "goals": 11, "assists": 3, "xG": 9.8, "xAG": 2.5, "progressive_carries": 22,
         "progressive_passes": 15, "yellow_cards": 1, "red_cards": 0},

        # La Liga
        {"player": "Robert Lewandowski", "team": "Barcelona", "position": "FWD", "league": "La Liga",
         "age": 36, "minutes": 1700, "goals": 14, "assists": 5, "xG": 12.1, "xAG": 3.2, "progressive_carries": 18,
         "progressive_passes": 22, "yellow_cards": 2, "red_cards": 0},
        {"player": "Lamine Yamal", "team": "Barcelona", "position": "MID", "league": "La Liga",
         "age": 17, "minutes": 1400, "goals": 6, "assists": 10, "xG": 4.5, "xAG": 8.2, "progressive_carries": 65,
         "progressive_passes": 48, "yellow_cards": 1, "red_cards": 0},
        {"player": "Kylian Mbappe", "team": "Real Madrid", "position": "FWD", "league": "La Liga",
         "age": 26, "minutes": 1550, "goals": 10, "assists": 3, "xG": 11.5, "xAG": 2.8, "progressive_carries": 42,
         "progressive_passes": 25, "yellow_cards": 1, "red_cards": 0},
        {"player": "Vinicius Junior", "team": "Real Madrid", "position": "MID", "league": "La Liga",
         "age": 24, "minutes": 1600, "goals": 8, "assists": 7, "xG": 7.2, "xAG": 5.5, "progressive_carries": 72,
         "progressive_passes": 35, "yellow_cards": 4, "red_cards": 0},
        {"player": "Antoine Griezmann", "team": "Atletico Madrid", "position": "FWD", "league": "La Liga",
         "age": 33, "minutes": 1450, "goals": 7, "assists": 6, "xG": 6.8, "xAG": 5.2, "progressive_carries": 28,
         "progressive_passes": 45, "yellow_cards": 2, "red_cards": 0},

        # Bundesliga
        {"player": "Harry Kane", "team": "Bayern Munich", "position": "FWD", "league": "Bundesliga",
         "age": 31, "minutes": 1750, "goals": 18, "assists": 6, "xG": 15.5, "xAG": 4.2, "progressive_carries": 20,
         "progressive_passes": 28, "yellow_cards": 1, "red_cards": 0},
        {"player": "Florian Wirtz", "team": "Bayer Leverkusen", "position": "MID", "league": "Bundesliga",
         "age": 21, "minutes": 1500, "goals": 8, "assists": 9, "xG": 6.5, "xAG": 7.8, "progressive_carries": 48,
         "progressive_passes": 72, "yellow_cards": 1, "red_cards": 0},
        {"player": "Jamal Musiala", "team": "Bayern Munich", "position": "MID", "league": "Bundesliga",
         "age": 21, "minutes": 1400, "goals": 7, "assists": 5, "xG": 5.8, "xAG": 4.5, "progressive_carries": 58,
         "progressive_passes": 42, "yellow_cards": 0, "red_cards": 0},
        {"player": "Victor Boniface", "team": "Bayer Leverkusen", "position": "FWD", "league": "Bundesliga",
         "age": 23, "minutes": 1200, "goals": 9, "assists": 4, "xG": 8.2, "xAG": 3.1, "progressive_carries": 25,
         "progressive_passes": 18, "yellow_cards": 2, "red_cards": 0},
        {"player": "Serhou Guirassy", "team": "Borussia Dortmund", "position": "FWD", "league": "Bundesliga",
         "age": 28, "minutes": 1350, "goals": 10, "assists": 2, "xG": 9.5, "xAG": 1.8, "progressive_carries": 15,
         "progressive_passes": 12, "yellow_cards": 1, "red_cards": 0},

        # Serie A
        {"player": "Marcus Thuram", "team": "Inter Milan", "position": "FWD", "league": "Serie A",
         "age": 27, "minutes": 1600, "goals": 11, "assists": 5, "xG": 9.2, "xAG": 3.8, "progressive_carries": 35,
         "progressive_passes": 22, "yellow_cards": 3, "red_cards": 0},
        {"player": "Lautaro Martinez", "team": "Inter Milan", "position": "FWD", "league": "Serie A",
         "age": 27, "minutes": 1550, "goals": 12, "assists": 3, "xG": 10.5, "xAG": 2.5, "progressive_carries": 28,
         "progressive_passes": 18, "yellow_cards": 2, "red_cards": 0},
        {"player": "Rafael Leao", "team": "AC Milan", "position": "MID", "league": "Serie A",
         "age": 25, "minutes": 1450, "goals": 6, "assists": 7, "xG": 5.2, "xAG": 5.8, "progressive_carries": 68,
         "progressive_passes": 32, "yellow_cards": 1, "red_cards": 0},
        {"player": "Victor Osimhen", "team": "Napoli", "position": "FWD", "league": "Serie A",
         "age": 26, "minutes": 1100, "goals": 8, "assists": 2, "xG": 7.5, "xAG": 1.8, "progressive_carries": 18,
         "progressive_passes": 10, "yellow_cards": 2, "red_cards": 1},
        {"player": "Paulo Dybala", "team": "Roma", "position": "FWD", "league": "Serie A",
         "age": 31, "minutes": 1300, "goals": 7, "assists": 6, "xG": 6.2, "xAG": 5.5, "progressive_carries": 32,
         "progressive_passes": 48, "yellow_cards": 1, "red_cards": 0},

        # Ligue 1
        {"player": "Bradley Barcola", "team": "PSG", "position": "MID", "league": "Ligue 1",
         "age": 22, "minutes": 1500, "goals": 9, "assists": 6, "xG": 7.5, "xAG": 4.8, "progressive_carries": 55,
         "progressive_passes": 35, "yellow_cards": 1, "red_cards": 0},
        {"player": "Ousmane Dembele", "team": "PSG", "position": "MID", "league": "Ligue 1",
         "age": 27, "minutes": 1400, "goals": 7, "assists": 8, "xG": 6.2, "xAG": 6.5, "progressive_carries": 62,
         "progressive_passes": 42, "yellow_cards": 2, "red_cards": 0},
        {"player": "Jonathan David", "team": "Lille", "position": "FWD", "league": "Ligue 1",
         "age": 24, "minutes": 1650, "goals": 12, "assists": 4, "xG": 10.8, "xAG": 3.2, "progressive_carries": 22,
         "progressive_passes": 18, "yellow_cards": 0, "red_cards": 0},
        {"player": "Mason Greenwood", "team": "Marseille", "position": "FWD", "league": "Ligue 1",
         "age": 23, "minutes": 1500, "goals": 10, "assists": 3, "xG": 8.5, "xAG": 2.5, "progressive_carries": 35,
         "progressive_passes": 25, "yellow_cards": 3, "red_cards": 0},
        {"player": "Goncalo Ramos", "team": "PSG", "position": "FWD", "league": "Ligue 1",
         "age": 23, "minutes": 900, "goals": 5, "assists": 2, "xG": 4.8, "xAG": 1.5, "progressive_carries": 12,
         "progressive_passes": 10, "yellow_cards": 1, "red_cards": 0},
    ]

    df = pd.DataFrame(sample_data)
    print(f"Created {len(df)} sample players across 5 leagues")
    return df


def main():
    """Main entry point."""
    print("Football Player Data Fetcher")
    print("=" * 50 + "\n")

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Try to download FPL data first
    df = download_fpl_data()

    if not df.empty:
        df = clean_fpl_data(df)
    else:
        # Fall back to sample data
        df = create_sample_data()

    if df.empty:
        print("\nNo data available!")
        return

    # Save to CSV
    output_file = OUTPUT_DIR / "players.csv"
    df.to_csv(output_file, index=False)

    print("\n" + "=" * 50)
    print(f"Saved {len(df)} players to {output_file}")
    if "league" in df.columns:
        print(f"Leagues: {df['league'].unique().tolist()}")
    print(f"Columns: {df.columns.tolist()}")


if __name__ == "__main__":
    main()
