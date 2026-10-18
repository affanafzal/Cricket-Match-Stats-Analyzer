# Cricket Match Stats Analyzer

## Run the project
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Run:
   ```bash
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```
4. Your browser will open the interactive application.
5. Add a match in **Add Match**, then enter each player's stats in **Add Player Stats**.
6. Use Dashboard / Explore Data, then export cleaned files in Downloads.

## Important data-entry notes
- Enter one row for each player's performance in each match.
- Record runs, balls faced, fours, sixes, wickets, bowling overs, runs conceded and dismissals.
- Enter a player with zero runs/balls/wickets if they played but did not bat or bowl.
- For batting average, enter dismissals (usually 0 for not out, 1 for out).
- Bowler limit is checked against overs entered. Cricket over notation is not decimal arithmetic; `3.4` means 3 overs and 4 balls. This beginner version uses the entered value for bowling economy, so use whole overs for approximate economy or extend the calculation for exact legal-ball precision.
- The initial CSVs are empty templates; add your own match data.

## Files
- `app.py`: application source.
- `requirements.txt`: dependencies.
- `data/`: raw CSV templates and empty processed-output templates.
- `Project_Report.md`: short submission report.
