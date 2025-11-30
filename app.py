import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# App config
st.set_page_config(
    page_title="Football Player Scouting Dashboard",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Football Player Scouting Dashboard")
st.caption("Compare and analyze Premier League players using FPL data (2025-26 season)")

# Check if data exists, if not fetch it
DATA_FILE = Path(__file__).parent / "data" / "players.csv"

if not DATA_FILE.exists():
    with st.spinner("Fetching player data..."):
        from scraper import download_fpl_data, clean_fpl_data
        DATA_FILE.parent.mkdir(exist_ok=True)
        df = download_fpl_data()
        if not df.empty:
            df = clean_fpl_data(df)
            df.to_csv(DATA_FILE, index=False)
        else:
            st.error("Could not fetch player data. Please try again later.")
            st.stop()

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    # Map team IDs to names if needed
    team_map = {
        1: "Arsenal", 2: "Aston Villa", 3: "Bournemouth", 4: "Brentford",
        5: "Brighton", 6: "Chelsea", 7: "Crystal Palace", 8: "Everton",
        9: "Fulham", 10: "Ipswich", 11: "Leicester", 12: "Liverpool",
        13: "Man City", 14: "Man Utd", 15: "Newcastle", 16: "Nott'm Forest",
        17: "Southampton", 18: "Spurs", 19: "West Ham", 20: "Wolves"
    }
    if df["team"].dtype in ["int64", "float64"]:
        df["team"] = df["team"].map(team_map)
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Position filter
positions = ["All"] + sorted(df["position"].dropna().unique().tolist())
selected_position = st.sidebar.selectbox("Position", positions)

# Team filter
teams = ["All"] + sorted(df["team"].dropna().unique().tolist())
selected_team = st.sidebar.selectbox("Team", teams)

# Price range filter
if "price" in df.columns:
    min_price, max_price = float(df["price"].min()), float(df["price"].max())
    price_range = st.sidebar.slider("Price Range (£m)", min_price, max_price, (min_price, max_price), step=0.5)

# Minutes played filter
min_minutes = st.sidebar.number_input("Minimum Minutes Played", min_value=0, value=90)

# Apply filters
filtered_df = df.copy()

if selected_position != "All":
    filtered_df = filtered_df[filtered_df["position"] == selected_position]

if selected_team != "All":
    filtered_df = filtered_df[filtered_df["team"] == selected_team]

if "price" in df.columns:
    filtered_df = filtered_df[
        (filtered_df["price"] >= price_range[0]) &
        (filtered_df["price"] <= price_range[1])
    ]

filtered_df = filtered_df[filtered_df["minutes"] >= min_minutes]

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Player List", "📊 Compare Players", "📈 Analytics", "💎 Hidden Gems", "🔄 Transfer Picks"])

with tab1:
    st.header(f"Players ({len(filtered_df)} found)")

    with st.expander("ℹ️ Column definitions"):
        st.markdown("""
        - **Price**: Current FPL price in £millions
        - **Total Points**: FPL points earned this season
        - **Minutes**: Total minutes played
        - **Goals/Assists**: Goals scored and assists provided
        - **Form**: Average points per game over last 5 gameweeks
        """)

    # Search
    search = st.text_input("Search player name")
    if search:
        filtered_df = filtered_df[filtered_df["player"].str.contains(search, case=False, na=False)]

    # Display table
    display_cols = ["player", "position", "team", "price", "total_points", "minutes", "goals", "assists", "form"]
    available_cols = [c for c in display_cols if c in filtered_df.columns]

    # Sort options
    sort_col = st.selectbox("Sort by", available_cols, index=available_cols.index("total_points") if "total_points" in available_cols else 0)
    sort_order = st.checkbox("Ascending", value=False)

    st.dataframe(
        filtered_df[available_cols].sort_values(sort_col, ascending=sort_order),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.header("Compare Players")

    with st.expander("ℹ️ About the radar chart metrics"):
        st.markdown("""
        **FPL ICT Index** - Official Premier League metrics:

        - **Influence**: Impact on a match (goals, assists, key passes, tackles won)
        - **Creativity**: Chance creation (key passes, crosses, through balls, assists)
        - **Threat**: Goal threat (shots, touches in box, goal attempts)
        - **ICT Index**: Combined score of Influence + Creativity + Threat

        **Performance metrics**:
        - **Form**: Average points over last 5 gameweeks
        - **Pts/Game**: Total points ÷ games played

        *Radar chart normalizes all values to 0-100 scale for comparison.*
        """)

    col1, col2 = st.columns(2)

    player_list = sorted(filtered_df["player"].dropna().unique().tolist())

    with col1:
        player1 = st.selectbox("Player 1", [""] + player_list, key="p1")

    with col2:
        player2 = st.selectbox("Player 2", [""] + player_list, key="p2")

    if player1 and player2:
        # Get player stats
        p1_stats = filtered_df[filtered_df["player"] == player1].iloc[0]
        p2_stats = filtered_df[filtered_df["player"] == player2].iloc[0]

        # FPL-specific metrics for radar chart
        radar_metrics = ["influence", "creativity", "threat", "ict_index", "form", "points_per_game"]
        radar_labels = ["Influence", "Creativity", "Threat", "ICT Index", "Form", "Pts/Game"]
        available_metrics = [m for m in radar_metrics if m in df.columns and df[m].notna().any()]
        available_labels = [radar_labels[i] for i, m in enumerate(radar_metrics) if m in available_metrics]

        if available_metrics:
            # Normalize stats for radar chart (0-100 scale)
            max_vals = df[available_metrics].max()

            p1_values = [(p1_stats[m] / max_vals[m] * 100) if pd.notna(p1_stats[m]) and max_vals[m] > 0 else 0 for m in available_metrics]
            p2_values = [(p2_stats[m] / max_vals[m] * 100) if pd.notna(p2_stats[m]) and max_vals[m] > 0 else 0 for m in available_metrics]

            # Create radar chart
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=p1_values + [p1_values[0]],
                theta=available_labels + [available_labels[0]],
                fill='toself',
                name=player1,
                opacity=0.7
            ))

            fig.add_trace(go.Scatterpolar(
                r=p2_values + [p2_values[0]],
                theta=available_labels + [available_labels[0]],
                fill='toself',
                name=player2,
                opacity=0.7
            ))

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title="Player Comparison (Normalized to 100)"
            )

            st.plotly_chart(fig, use_container_width=True)

        # Side by side stats
        st.subheader("Stats Comparison")

        compare_metrics = ["total_points", "minutes", "goals", "assists", "clean_sheets", "yellow_cards", "bonus", "price", "form", "points_per_game"]
        compare_labels = ["Total Points", "Minutes", "Goals", "Assists", "Clean Sheets", "Yellow Cards", "Bonus", "Price (£m)", "Form", "Pts/Game"]

        compare_data = []
        for label, metric in zip(compare_labels, compare_metrics):
            if metric in df.columns:
                v1 = p1_stats.get(metric, "N/A")
                v2 = p2_stats.get(metric, "N/A")
                compare_data.append({"Stat": label, player1: v1, player2: v2})

        compare_df = pd.DataFrame(compare_data)
        st.dataframe(compare_df, use_container_width=True, hide_index=True)
    else:
        st.info("Select two players to compare")

with tab3:
    st.header("Analytics")

    with st.expander("ℹ️ About the analytics"):
        st.markdown("""
        **Best Value Players (Pts/£m)**: `Total Points ÷ Price`

        Higher value = more points per million spent. Useful for budget optimization.

        **Price vs Points Chart**: Scatter plot showing relationship between cost and output.
        - Players in top-left = cheap + high points (best value)
        - Players in bottom-right = expensive + low points (poor value)
        """)

    col1, col2 = st.columns(2)

    with col1:
        # Top scorers
        st.subheader("Top Scorers")
        top_scorers = filtered_df.nlargest(10, "goals")[["player", "team", "goals", "minutes"]]
        st.dataframe(top_scorers, use_container_width=True, hide_index=True)

    with col2:
        # Top assists
        st.subheader("Top Assists")
        top_assists = filtered_df.nlargest(10, "assists")[["player", "team", "assists", "minutes"]]
        st.dataframe(top_assists, use_container_width=True, hide_index=True)

    # Value analysis: Points per million
    st.subheader("Best Value Players (Points per £m)")
    if "price" in filtered_df.columns and "total_points" in filtered_df.columns:
        value_df = filtered_df[filtered_df["price"] > 0].copy()
        value_df["value"] = value_df["total_points"] / value_df["price"]
        best_value = value_df.nlargest(15, "value")[["player", "team", "position", "price", "total_points", "value"]]
        best_value["value"] = best_value["value"].round(2)
        st.dataframe(best_value, use_container_width=True, hide_index=True)

    # Scatter plot: Price vs Points
    st.subheader("Price vs Total Points")
    if "price" in filtered_df.columns and "total_points" in filtered_df.columns:
        fig = px.scatter(
            filtered_df[filtered_df["minutes"] > 0],
            x="price",
            y="total_points",
            color="position",
            hover_data=["player", "team"],
            labels={"price": "Price (£m)", "total_points": "Total Points"},
            title="Player Value Analysis"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("💎 Hidden Gems - Undervalued Players")
    st.caption("Players delivering more value than their price suggests")

    with st.expander("ℹ️ How are these metrics calculated?"):
        st.markdown("""
        **Expected Points**: Based on the league average points-per-million ratio. A £6m player is expected to score `6 × avg_pts_per_£m`.

        **Overperformance**: `Actual Points - Expected Points`. Positive = player exceeds expectations for their price.

        **Over %**: Percentage above/below expected: `(Overperformance / Expected) × 100`

        **Pts/£m (Value Score)**: Simple efficiency metric: `Total Points / Price`. Higher = better value.

        *Players shown have 200+ minutes played to ensure statistical relevance.*
        """)

    # Calculate value metrics
    gems_df = filtered_df[
        (filtered_df["price"] > 0) &
        (filtered_df["minutes"] >= 200) &
        (filtered_df["total_points"] > 0)
    ].copy()

    if not gems_df.empty:
        # Value score: points per million
        gems_df["value_score"] = gems_df["total_points"] / gems_df["price"]

        # Expected points based on price (linear regression concept)
        avg_points_per_price = gems_df["total_points"].sum() / gems_df["price"].sum()
        gems_df["expected_points"] = gems_df["price"] * avg_points_per_price
        gems_df["overperformance"] = gems_df["total_points"] - gems_df["expected_points"]
        gems_df["overperformance_pct"] = (gems_df["overperformance"] / gems_df["expected_points"] * 100).round(1)

        # Filter by position
        gem_position = st.selectbox("Filter by position", ["All", "GK", "DEF", "MID", "FWD"], key="gem_pos")
        if gem_position != "All":
            gems_df = gems_df[gems_df["position"] == gem_position]

        # Price cap filter
        max_price_filter = st.slider("Maximum price (£m)", 4.0, 15.0, 8.0, 0.5, key="gem_price")
        gems_df = gems_df[gems_df["price"] <= max_price_filter]

        # Top hidden gems
        st.subheader(f"🏆 Top Undervalued Players (under £{max_price_filter}m)")

        top_gems = gems_df.nlargest(10, "overperformance")[
            ["player", "team", "position", "price", "total_points", "expected_points", "overperformance", "overperformance_pct", "value_score"]
        ].copy()
        top_gems["expected_points"] = top_gems["expected_points"].round(1)
        top_gems["overperformance"] = top_gems["overperformance"].round(1)
        top_gems["value_score"] = top_gems["value_score"].round(2)
        top_gems.columns = ["Player", "Team", "Pos", "Price (£m)", "Points", "Expected Pts", "Overperformance", "Over %", "Pts/£m"]

        st.dataframe(top_gems, use_container_width=True, hide_index=True)

        # Visualization
        st.subheader("Value Analysis Chart")
        # Use absolute value for size, only show overperformers
        chart_df = gems_df[gems_df["overperformance"] > 0].copy()
        fig = px.scatter(
            chart_df,
            x="price",
            y="total_points",
            color="position",
            size="overperformance",
            hover_data=["player", "team", "value_score"],
            labels={"price": "Price (£m)", "total_points": "Total Points"},
            title="Overperforming Players (bubble size = overperformance)"
        )
        # Add expected value line
        fig.add_scatter(
            x=[gems_df["price"].min(), gems_df["price"].max()],
            y=[gems_df["price"].min() * avg_points_per_price, gems_df["price"].max() * avg_points_per_price],
            mode="lines",
            name="Expected Value Line",
            line=dict(dash="dash", color="gray")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Players above the dashed line are overperforming their price point")
    else:
        st.info("Not enough data to calculate hidden gems")

with tab5:
    st.header("🔄 Transfer Recommendations")
    st.caption("Find better alternatives to your current players")

    with st.expander("ℹ️ How are recommendations calculated?"):
        st.markdown("""
        **Recommendation Score**: Weighted formula combining three factors:

        `Score = (Points Difference × 2) + (Value Improvement × 10) + (Price Savings × 3)`

        - **Points Difference**: How many more/fewer points than your current player
        - **Value Improvement**: Difference in Pts/£m efficiency
        - **Price Savings**: Bonus for cheaper alternatives (frees up budget)

        *Only players with 200+ minutes are considered to ensure reliability.*
        """)

    # Select a player to replace
    all_players = sorted(df[df["minutes"] >= 90]["player"].dropna().unique().tolist())
    selected_player = st.selectbox("Select a player to replace", [""] + all_players, key="replace_player")

    if selected_player:
        current = df[df["player"] == selected_player].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Current Player")
            st.metric("Player", current["player"])
            st.metric("Team", current["team"])
            st.metric("Position", current["position"])
            st.metric("Price", f"£{current['price']}m")
            st.metric("Total Points", current["total_points"])
            if current["price"] > 0:
                st.metric("Points/£m", round(current["total_points"] / current["price"], 2))

        # Find alternatives
        with col2:
            st.subheader("Search Criteria")
            budget = st.slider(
                "Max budget (£m)",
                float(current["price"]) - 2,
                float(current["price"]) + 2,
                float(current["price"]),
                0.5,
                key="budget_slider"
            )
            same_position = st.checkbox("Same position only", value=True)

        # Find alternatives
        alternatives = df[
            (df["player"] != selected_player) &
            (df["price"] <= budget) &
            (df["price"] > 0) &
            (df["minutes"] >= 200)
        ].copy()

        if same_position:
            alternatives = alternatives[alternatives["position"] == current["position"]]

        # Calculate comparison metrics
        alternatives["value_score"] = alternatives["total_points"] / alternatives["price"]
        alternatives["points_diff"] = alternatives["total_points"] - current["total_points"]
        alternatives["price_diff"] = alternatives["price"] - current["price"]
        alternatives["value_diff"] = alternatives["value_score"] - (current["total_points"] / current["price"] if current["price"] > 0 else 0)

        # Recommendation score (weighted: points improvement + value improvement + savings)
        alternatives["rec_score"] = (
            alternatives["points_diff"] * 2 +  # Weight points heavily
            alternatives["value_diff"] * 10 +   # Value improvement
            (current["price"] - alternatives["price"]) * 3  # Savings bonus
        )

        st.subheader("🎯 Recommended Replacements")

        if not alternatives.empty:
            top_alternatives = alternatives.nlargest(5, "rec_score")[
                ["player", "team", "position", "price", "total_points", "value_score", "points_diff", "price_diff"]
            ].copy()
            top_alternatives["value_score"] = top_alternatives["value_score"].round(2)
            top_alternatives["points_diff"] = top_alternatives["points_diff"].astype(int)
            top_alternatives["price_diff"] = top_alternatives["price_diff"].round(1)
            top_alternatives.columns = ["Player", "Team", "Pos", "Price (£m)", "Points", "Pts/£m", "Pts vs Current", "Price Diff"]

            st.dataframe(top_alternatives, use_container_width=True, hide_index=True)

            # Best pick highlight
            if len(top_alternatives) > 0:
                best = alternatives.nlargest(1, "rec_score").iloc[0]

                st.success(f"**Top Pick: {best['player']}** ({best['team']})")

                rec_cols = st.columns(3)
                with rec_cols[0]:
                    points_change = int(best["points_diff"])
                    st.metric("Points Change", f"{'+' if points_change >= 0 else ''}{points_change}")
                with rec_cols[1]:
                    price_change = round(best["price_diff"], 1)
                    st.metric("Price Change", f"{'+'if price_change >= 0 else ''}£{price_change}m")
                with rec_cols[2]:
                    st.metric("Value Score", round(best["value_score"], 2))
        else:
            st.warning("No alternatives found within the specified criteria")
    else:
        st.info("Select a player above to find replacement recommendations")

# Footer
st.divider()
st.caption("Data source: Fantasy Premier League API (2025-26 season) | Built by Jon Zisi")
