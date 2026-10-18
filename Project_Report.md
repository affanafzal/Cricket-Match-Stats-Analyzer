# Cricket Match Stats Analyzer — Short Project Report

## 1. Problem statement
Cricket statistics are often stored in separate or messy tables, making it difficult to compare players, count appearances, measure batting performance, and review bowling figures. This project provides a small interactive application to record match details and player performances, clean the records with Pandas, calculate key metrics, and export processed datasets.

## 2. Dataset description
The project starts with empty CSV templates so the user can enter their own real match data. The application creates:
- `matches.csv`: tournament, two teams, number of tournament teams, overs limit, date, venue, and winner.
- `player_match_stats.csv`: one row per player per match, including team/opponent, runs, balls faced, fours, sixes, wickets, overs bowled, runs conceded, bowler overs limit, and dismissals.
- `cleaned_player_match_stats.csv`: cleaned player-match data with derived statistics.
- `player_career_summary.csv`: aggregated player/team totals and appearances across recorded matches.
- `innings.csv`: optional template for innings-level totals.

No real-world findings are pre-filled because the user supplies the dataset. After entering matches, the dashboard reports top run scorers, wicket takers, boundary leaders, and individual player records.

## 3. Methods used
- **Load:** read CSV files into Pandas DataFrames.
- **Inspect:** show raw match and player records in tables.
- **Clean:** normalize text, convert numeric columns, handle missing numeric values, remove incomplete player/team rows, and drop duplicate player-match records.
- **Manipulate/combine:** filter by team and tournament; aggregate player records with `groupby`; combine rows with `concat`.
- **Analyze:** calculate strike rate (`runs / balls faced × 100`), batting average (`runs / dismissals`), boundary runs (`4 × fours + 6 × sixes`), boundary count (`fours + sixes`), bowling economy, match appearances, and bowling-limit checks.
- **Export:** save cleaned player-match data and career summaries to CSV.

## 4. Key findings
The application calculates findings from the data entered by the user. The dashboard identifies leading run scorers, leading wicket takers, players with the most boundaries, match appearances, strike rates, batting averages, and bowling economy. Since the initial files are blank, actual rankings appear only after match and player records have been entered.

## 5. Conclusion
This project demonstrates how Python and Pandas can transform raw cricket records into cleaned, summarized information that supports player comparison and tournament analysis. CSV files keep the data portable and make the project easy to submit and extend.

## Important assumptions / limitations
- Add one player row per match and team. A player who plays several matches should have a separate row for each match.
- Matches played are calculated as the number of distinct match IDs recorded for that player/team.
- Batting average is total runs divided by dismissals; not-out innings do not count as dismissals.
- Strike rate is calculated from runs and balls faced. Bowling economy currently uses the entered overs value, so decimal overs notation such as `3.4` is approximate; exact economy should use legal balls converted to overs (3 overs and 4 balls = 20 balls).
- This version records two teams per match and player-level summary figures; it is not a ball-by-ball scoring engine. For an individual bowler, enter the maximum allowed overs in the bowler-limit field and the app rejects an entry above that limit.
