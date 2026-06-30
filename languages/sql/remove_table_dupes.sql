select distinct * from ml_models.tonights_games_ml;

CREATE TABLE ml_models.tonights_games_ml2 (LIKE ml_models.tonights_games_ml);

INSERT INTO ml_models.tonights_games_ml2(
	index, home_team, away_team, proper_date, home_team_rank, home_days_rest, home_team_avg_pts_scored, home_team_avg_pts_scored_opp, home_team_win_pct, home_team_win_pct_last10, home_is_top_players, away_team_rank, away_days_rest, away_team_avg_pts_scored, away_team_avg_pts_scored_opp, away_team_win_pct, away_team_win_pct_last10, away_is_top_players, home_team_predicted_win_pct, away_team_predicted_win_pct)
SELECT DISTINCT *
FROM ml_models.tonights_games_ml;

truncate table ml_models.tonights_games_ml;

INSERT INTO ml_models.tonights_games_ml(
	index, home_team, away_team, proper_date, home_team_rank, home_days_rest, home_team_avg_pts_scored, home_team_avg_pts_scored_opp, home_team_win_pct, home_team_win_pct_last10, home_is_top_players, away_team_rank, away_days_rest, away_team_avg_pts_scored, away_team_avg_pts_scored_opp, away_team_win_pct, away_team_win_pct_last10, away_is_top_players, home_team_predicted_win_pct, away_team_predicted_win_pct)
SELECT *
FROM ml_models.tonights_games_ml2;

select * from ml_models.tonights_games_ml where proper_date = '2023-05-20';

drop table ml_models.tonights_games_ml2;