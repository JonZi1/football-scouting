# Football Player Scouting Dashboard

A Streamlit app to scout and compare Premier League players using official Fantasy Premier League data.

## Features

- **Filter players** by position, team, price range, and minutes played
- **Search** for specific players
- **Compare players** side-by-side with radar charts (Influence, Creativity, Threat, ICT Index, Form)
- **Analytics tab** with top scorers, top assists, best value players, and price vs points visualization
- Data from the 2025-26 Premier League season

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Fetch player data
python scraper.py

# Run the app
streamlit run app.py
```

## Data Source

Player statistics are fetched from the official [Fantasy Premier League API](https://fantasy.premierleague.com/) via the [vaastav/Fantasy-Premier-League](https://github.com/vaastav/Fantasy-Premier-League) repository. Data is updated weekly during the season.

## Tech Stack

- Python
- Streamlit
- pandas
- Plotly

## Author

Built by Jon Zisi
