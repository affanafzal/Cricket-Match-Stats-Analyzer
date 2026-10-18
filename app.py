"""
Cricket Match Stats Analyzer
A beginner-friendly Pandas project with CSV storage and an interactive Streamlit UI.

Run:
    python -m pip install -r requirements.txt
    streamlit run app.py
"""
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
MATCHES_FILE = DATA_DIR / "matches.csv"
INNINGS_FILE = DATA_DIR / "innings.csv"
BALLS_FILE = DATA_DIR / "player_match_stats.csv"
CLEAN_FILE = DATA_DIR / "cleaned_player_match_stats.csv"
PLAYER_SUMMARY_FILE = DATA_DIR / "player_career_summary.csv"

MATCH_COLUMNS = ["match_id", "tournament", "team_a", "team_b", "number_of_teams",
                 "overs_limit", "match_date", "venue", "winner"]
STAT_COLUMNS = ["match_id", "tournament", "team", "opponent", "player", "matches_played",
                "runs", "balls_faced", "fours", "sixes", "wickets", "overs_bowled",
                "runs_conceded", "bowler_wicket_limit", "dismissals"]
BALL_COLUMNS = ["match_id", "innings", "over_number", "ball_number", "batting_team",
                "bowling_team", "batter", "bowler", "runs_batter", "runs_extras",
                "wicket", "wicket_type"]

def read_csv(path, columns):
    if path.exists():
        df = pd.read_csv(path)
        for c in columns:
            if c not in df.columns:
                df[c] = pd.NA
        return df[columns]
    return pd.DataFrame(columns=columns)

def initialize_files():
    for path, cols in [(MATCHES_FILE, MATCH_COLUMNS), (INNINGS_FILE, ["match_id","innings","team","total_runs","wickets_lost","overs_faced"]),
                       (BALLS_FILE, STAT_COLUMNS), (CLEAN_FILE, STAT_COLUMNS), (PLAYER_SUMMARY_FILE, [])]:
        if not path.exists():
            pd.DataFrame(columns=cols).to_csv(path, index=False)

def add_match(tournament, team_a, team_b, number_of_teams, overs_limit, match_date, venue, winner):
    matches = read_csv(MATCHES_FILE, MATCH_COLUMNS)
    next_id = 1 if matches.empty else int(pd.to_numeric(matches["match_id"], errors="coerce").max()) + 1
    row = {"match_id": next_id, "tournament": tournament.strip(), "team_a": team_a.strip(),
           "team_b": team_b.strip(), "number_of_teams": int(number_of_teams),
           "overs_limit": int(overs_limit), "match_date": str(match_date), "venue": venue.strip(),
           "winner": winner.strip() if winner else ""}
    pd.concat([matches, pd.DataFrame([row])], ignore_index=True).to_csv(MATCHES_FILE, index=False)
    return next_id

def add_player_stats(row):
    df = read_csv(BALLS_FILE, STAT_COLUMNS)
    # One row is one player's performance in one match; do not duplicate the same player in a match.
    if not df.empty:
        same = ((df["match_id"].astype(str) == str(row["match_id"])) &
                (df["team"].astype(str).str.casefold() == str(row["team"]).casefold()) &
                (df["player"].astype(str).str.casefold() == str(row["player"]).casefold()))
        if same.any():
            raise ValueError("This player already has a stats row for this match and team.")
    pd.concat([df, pd.DataFrame([row])], ignore_index=True).to_csv(BALLS_FILE, index=False)

def calculate_stats(df):
    """Clean numeric values and derive strike rate, batting average and bowling economy."""
    clean = df.copy()
    text_cols = ["tournament", "team", "opponent", "player"]
    for c in text_cols:
        clean[c] = clean[c].fillna("").astype(str).str.strip()
    numeric = ["match_id","matches_played","runs","balls_faced","fours","sixes","wickets",
               "overs_bowled","runs_conceded","bowler_wicket_limit","dismissals"]
    for c in numeric:
        clean[c] = pd.to_numeric(clean[c], errors="coerce").fillna(0)
    clean = clean[(clean["player"] != "") & (clean["team"] != "")]
    clean = clean.drop_duplicates(subset=["match_id","team","player"], keep="last")
    clean["strike_rate"] = (clean["runs"] / clean["balls_faced"].replace(0, pd.NA) * 100).fillna(0).round(2)
    # Batting average = runs / times dismissed, not runs / matches.
    clean["batting_average"] = (clean["runs"] / clean["dismissals"].replace(0, pd.NA)).fillna(0).round(2)
    clean["boundary_runs"] = clean["fours"] * 4 + clean["sixes"] * 6
    clean["boundary_count"] = clean["fours"] + clean["sixes"]
    clean["bowling_economy"] = (clean["runs_conceded"] / clean["overs_bowled"].replace(0, pd.NA)).fillna(0).round(2)
    clean["bowling_limit_ok"] = clean["overs_bowled"] <= clean["bowler_wicket_limit"] * 1.0
    return clean

def career_summary(clean):
    if clean.empty:
        return pd.DataFrame(columns=["player","team","matches_played","runs","balls_faced","fours","sixes",
                                     "boundary_count","boundary_runs","wickets","runs_conceded","dismissals",
                                     "strike_rate","batting_average","bowling_economy"])
    # Count distinct matches represented, rather than summing a manually entered match count.
    group = clean.groupby(["player","team"], dropna=False).agg(
        matches_played=("match_id","nunique"), runs=("runs","sum"), balls_faced=("balls_faced","sum"),
        fours=("fours","sum"), sixes=("sixes","sum"), wickets=("wickets","sum"),
        runs_conceded=("runs_conceded","sum"), overs_bowled=("overs_bowled","sum"),
        dismissals=("dismissals","sum"), boundary_count=("boundary_count","sum"),
        boundary_runs=("boundary_runs","sum")
    ).reset_index()
    group["strike_rate"] = (group["runs"] / group["balls_faced"].replace(0, pd.NA) * 100).fillna(0).round(2)
    group["batting_average"] = (group["runs"] / group["dismissals"].replace(0, pd.NA)).fillna(0).round(2)
    group["bowling_economy"] = (group["runs_conceded"] / group["overs_bowled"].replace(0, pd.NA)).fillna(0).round(2)
    return group.sort_values(["runs","wickets"], ascending=False)

initialize_files()
st.set_page_config(page_title="Cricket Match Stats Analyzer", page_icon="🏏", layout="wide")
st.title("🏏 Cricket Match Stats Analyzer")
st.caption("A Pandas-powered mini analysis system for tournaments, matches, batting, bowling and player career summaries.")
st.info("Enter one row per player's performance per match. For a player who did not bat or bowl, enter 0 for those figures. Match totals and ball-by-ball scorecards can be added as a future extension.")

matches = read_csv(MATCHES_FILE, MATCH_COLUMNS)
stats = read_csv(BALLS_FILE, STAT_COLUMNS)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Add Match", "👤 Add Player Stats", "📊 Dashboard", "🔎 Explore Data", "📁 Downloads"])

with tab1:
    st.subheader("Create a match / tournament record")
    with st.form("match_form", clear_on_submit=True):
        c1,c2 = st.columns(2)
        tournament = c1.text_input("Tournament name", placeholder="e.g., University Cricket Cup")
        number_of_teams = c2.number_input("Number of teams in tournament", min_value=2, max_value=256, value=8, step=1)
        c3,c4 = st.columns(2)
        team_a = c3.text_input("Team 1 name")
        team_b = c4.text_input("Team 2 name")
        c5,c6 = st.columns(2)
        overs_limit = c5.number_input("Match overs limit", min_value=1, max_value=100, value=20, step=1)
        match_date = c6.date_input("Match date")
        c7,c8 = st.columns(2)
        venue = c7.text_input("Venue (optional)")
        winner = c8.text_input("Winner (optional; can enter Tie/No Result)")
        submitted = st.form_submit_button("Save Match")
        if submitted:
            if not tournament.strip() or not team_a.strip() or not team_b.strip():
                st.error("Please enter tournament and both team names.")
            elif team_a.strip().casefold() == team_b.strip().casefold():
                st.error("Team 1 and Team 2 must be different.")
            else:
                mid = add_match(tournament, team_a, team_b, number_of_teams, overs_limit, match_date, venue, winner)
                st.success(f"Match saved with Match ID {mid}. Use this ID when adding player stats.")
    st.dataframe(read_csv(MATCHES_FILE, MATCH_COLUMNS), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Add an individual player's match performance")
    matches = read_csv(MATCHES_FILE, MATCH_COLUMNS)
    if matches.empty:
        st.warning("First add a match in the Add Match tab.")
    else:
        match_options = {f"ID {r.match_id}: {r.tournament} — {r.team_a} vs {r.team_b} ({r.match_date})": int(r.match_id)
                         for r in matches.itertuples(index=False)}
        chosen = st.selectbox("Choose match", list(match_options))
        mid = match_options[chosen]
        matchrow = matches[pd.to_numeric(matches["match_id"], errors="coerce") == mid].iloc[0]
        team_options = [str(matchrow["team_a"]), str(matchrow["team_b"])]
        with st.form("player_form", clear_on_submit=True):
            c1,c2 = st.columns(2)
            team = c1.selectbox("Player's team", team_options)
            player = c2.text_input("Player full name")
            opponent = team_options[1] if team == team_options[0] else team_options[0]
            c3,c4,c5 = st.columns(3)
            runs = c3.number_input("Runs scored", min_value=0, max_value=1000, value=0)
            balls_faced = c4.number_input("Balls faced", min_value=0, max_value=1000, value=0)
            dismissals = c5.number_input("Times dismissed in this match (usually 0 or 1)", min_value=0, max_value=10, value=0)
            c6,c7,c8 = st.columns(3)
            fours = c6.number_input("Fours (4s)", min_value=0, max_value=200, value=0)
            sixes = c7.number_input("Sixes (6s)", min_value=0, max_value=200, value=0)
            wickets = c8.number_input("Wickets taken", min_value=0, max_value=10, value=0)
            c9,c10,c11 = st.columns(3)
            overs_bowled = c9.number_input("Overs bowled (e.g. 3.4 means 3 overs and 4 balls)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f")
            runs_conceded = c10.number_input("Runs conceded while bowling", min_value=0, max_value=1000, value=0)
            bowler_over_limit = c11.number_input("Bowler's maximum overs allowed", min_value=1, max_value=int(matchrow["overs_limit"]), value=min(4, int(matchrow["overs_limit"])))
            save_player = st.form_submit_button("Save Player Stats")
            if save_player:
                if not player.strip():
                    st.error("Enter the player's name.")
                elif int(fours)*4 + int(sixes)*6 > int(runs):
                    st.warning("Boundary runs exceed total runs. Please check the figures.")
                elif float(overs_bowled) > float(bowler_over_limit):
                    st.error(f"Overs bowled exceed this player's limit of {bowler_over_limit}.")
                else:
                    row = {"match_id":mid, "tournament":matchrow["tournament"], "team":team, "opponent":opponent,
                           "player":player.strip(), "matches_played":1, "runs":int(runs), "balls_faced":int(balls_faced),
                           "fours":int(fours), "sixes":int(sixes), "wickets":int(wickets), "overs_bowled":float(overs_bowled),
                           "runs_conceded":int(runs_conceded), "bowler_wicket_limit":int(bowler_over_limit),
                           "dismissals":int(dismissals)}
                    try:
                        add_player_stats(row)
                        st.success(f"Saved stats for {player}. Strike rate and averages are calculated automatically.")
                    except ValueError as e:
                        st.error(str(e))
    st.caption("Overs are entered in cricket notation: 3.4 means 3 overs and 4 balls, not 3.4 decimal overs. Economy calculations are approximate unless overs are converted to balls; use standard legal-ball totals for exact economy.")

with tab3:
    st.subheader("Tournament and player performance dashboard")
    matches = read_csv(MATCHES_FILE, MATCH_COLUMNS)
    stats = read_csv(BALLS_FILE, STAT_COLUMNS)
    clean = calculate_stats(stats)
    summary = career_summary(clean)
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Matches recorded", len(matches))
    m2.metric("Teams recorded", len(set(matches.get("team_a", pd.Series(dtype=str)).dropna().astype(str)) | set(matches.get("team_b", pd.Series(dtype=str)).dropna().astype(str))))
    m3.metric("Player-match records", len(clean))
    m4.metric("Unique players", clean["player"].nunique() if not clean.empty else 0)
    if clean.empty:
        st.info("Add matches and player statistics to see analytics.")
    else:
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Top run scorers**")
            st.dataframe(summary[["player","team","matches_played","runs","strike_rate","batting_average"]].head(10), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("**Top wicket takers**")
            st.dataframe(summary.sort_values("wickets", ascending=False)[["player","team","matches_played","wickets","runs_conceded","bowling_economy"]].head(10), use_container_width=True, hide_index=True)
        st.markdown("**Boundary leaderboard**")
        st.dataframe(summary.sort_values("boundary_count", ascending=False)[["player","team","matches_played","fours","sixes","boundary_count","boundary_runs"]].head(10), use_container_width=True, hide_index=True)
        selected_player = st.selectbox("Inspect a player's complete career summary", sorted(clean["player"].unique()))
        st.dataframe(summary[summary["player"] == selected_player], use_container_width=True, hide_index=True)
        st.markdown("**Player performance by match**")
        st.dataframe(clean[clean["player"] == selected_player], use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Filter, inspect, clean and analyze data")
    stats = read_csv(BALLS_FILE, STAT_COLUMNS)
    clean = calculate_stats(stats)
    if clean.empty:
        st.info("No player records yet.")
    else:
        c1,c2 = st.columns(2)
        teams = ["All"] + sorted(clean["team"].dropna().unique().tolist())
        tournaments = ["All"] + sorted(clean["tournament"].dropna().unique().tolist())
        selected_team = c1.selectbox("Filter by team", teams)
        selected_tournament = c2.selectbox("Filter by tournament", tournaments)
        view = clean.copy()
        if selected_team != "All": view = view[view["team"] == selected_team]
        if selected_tournament != "All": view = view[view["tournament"] == selected_tournament]
        st.dataframe(view, use_container_width=True, hide_index=True)
        st.markdown("**Quick summary (filtered records)**")
        st.dataframe(view.groupby("team").agg(players=("player","nunique"), total_runs=("runs","sum"),
            total_fours=("fours","sum"), total_sixes=("sixes","sum"), total_wickets=("wickets","sum")).reset_index(),
            use_container_width=True, hide_index=True)
        st.download_button("Download filtered CSV", view.to_csv(index=False).encode("utf-8"), "filtered_player_stats.csv", "text/csv")

with tab5:
    st.subheader("Export files for submission")
    stats = read_csv(BALLS_FILE, STAT_COLUMNS)
    clean = calculate_stats(stats)
    summary = career_summary(clean)
    st.write("Export the cleaned player-match dataset and career-level player summary.")
    if st.button("Refresh and export cleaned datasets"):
        clean.to_csv(CLEAN_FILE, index=False)
        summary.to_csv(PLAYER_SUMMARY_FILE, index=False)
        st.success("Cleaned and summary CSV files exported to the data folder.")
    st.download_button("Download cleaned player-match dataset", clean.to_csv(index=False).encode("utf-8"), "cleaned_player_match_stats.csv", "text/csv")
    st.download_button("Download career summary", summary.to_csv(index=False).encode("utf-8"), "player_career_summary.csv", "text/csv")
    st.download_button("Download match dataset", read_csv(MATCHES_FILE, MATCH_COLUMNS).to_csv(index=False).encode("utf-8"), "matches.csv", "text/csv")
    st.download_button("Download raw player stats", stats.to_csv(index=False).encode("utf-8"), "player_match_stats.csv", "text/csv")
