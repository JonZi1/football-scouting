# Football Player Scouting Dashboard

A Streamlit app to scout and compare Premier League players using official Fantasy Premier League data.

**Live Demo**: [fpl-scouting.streamlit.app](https://fpl-scouting.streamlit.app/)

## Features

### Player List
- Filter by position, team, price range, and minutes played
- Search for specific players
- Sort by any column

### Compare Players
- Side-by-side radar chart comparison
- Metrics: Influence, Creativity, Threat, ICT Index, Form, Points/Game
- Detailed stats table

### Analytics
- Top scorers and assist leaders
- Best value players (Points per £m)
- Price vs Points scatter plot

### Hidden Gems
Identifies undervalued players using statistical analysis:
- **Expected Points**: Based on league average points-per-million ratio
- **Overperformance**: Actual Points - Expected Points
- **Over %**: Percentage above/below expected performance
- Filter by position and max price

### Transfer Recommendations
Find better alternatives to your current players:
- Weighted recommendation score combining:
  - Points improvement (×2 weight)
  - Value efficiency improvement (×10 weight)
  - Price savings (×3 weight)
- Adjustable budget slider
- Position filtering

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Fetch player data (optional - app auto-fetches on first load)
python scraper.py

# Run the app
streamlit run app.py
```

## Data Source

Player statistics are fetched from the official [Fantasy Premier League API](https://fantasy.premierleague.com/) via the [vaastav/Fantasy-Premier-League](https://github.com/vaastav/Fantasy-Premier-League) repository.

### Key Metrics Explained

| Metric | Description |
|--------|-------------|
| **Influence** | Impact on a match (goals, assists, key passes, tackles won) |
| **Creativity** | Chance creation (key passes, crosses, through balls) |
| **Threat** | Goal threat (shots, touches in box, goal attempts) |
| **ICT Index** | Combined Influence + Creativity + Threat score |
| **Form** | Average points over last 5 gameweeks |
| **Pts/£m** | Total Points ÷ Price (value efficiency) |

## Tech Stack

- Python
- Streamlit
- pandas
- Plotly

## Author

Built by Jon Zisi
