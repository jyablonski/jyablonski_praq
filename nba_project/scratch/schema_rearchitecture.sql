ALTER TABLE nba_source.reddit_posts SET SCHEMA bronze;
ALTER TABLE nba_source.reddit_comments SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_player_contracts SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_league_transactions SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_player_stats_snapshot SET SCHEMA bronze;
ALTER TABLE nba_source.internal_team_attributes SET SCHEMA bronze;
ALTER TABLE nba_source.internal_player_attributes SET SCHEMA bronze;
ALTER TABLE nba_source.player_attributes SET SCHEMA bronze;
ALTER TABLE nba_source.play_in_details SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_team_opponent_shooting_stats SET SCHEMA bronze;
ALTER TABLE nba_source.twitter_tweets SET SCHEMA bronze;
ALTER TABLE nba_source.twitter_tweepy_legacy SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_team_adv_stats_snapshot SET SCHEMA bronze;
ALTER TABLE nba_source.aws_twitter_tweets_source SET SCHEMA bronze;
ALTER TABLE nba_source.internal_team_standings_override SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_team_preseason_odds SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_player_pbp SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_player_boxscores SET SCHEMA bronze;
ALTER TABLE nba_source.internal_team_top_players SET SCHEMA bronze;
ALTER TABLE nba_source.internal_league_inactive_dates SET SCHEMA bronze;
ALTER TABLE nba_source.draftkings_game_odds SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_player_shooting_stats SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_player_injuries SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_league_schedule SET SCHEMA bronze;
ALTER TABLE nba_source.bbref_player_contracts_backup SET SCHEMA bronze;


-- ml
ALTER TABLE ml.ml_game_predictions_backup SET SCHEMA gold;
ALTER TABLE ml.ml_game_predictions SET SCHEMA gold;
ALTER TABLE ml.ml_tonights_games SET SCHEMA silver;
ALTER TABLE ml.ml_tonights_games_audit SET SCHEMA silver;



-- marts
ALTER TABLE marts.feature_flags SET SCHEMA gold;
ALTER TABLE marts.feature_flags_audit SET SCHEMA gold;
ALTER TABLE marts.feedback SET SCHEMA gold;
ALTER TABLE marts.incidents SET SCHEMA gold;
ALTER TABLE marts.incidents_audit SET SCHEMA gold;
ALTER TABLE marts.rest_api_users SET SCHEMA gold;
ALTER TABLE marts.rest_api_users_audit SET SCHEMA gold;
ALTER TABLE marts.user_predictions SET SCHEMA gold;
ALTER TABLE marts.user_predictions_audit SET SCHEMA gold;
ALTER TABLE marts.user_predictions_historic SET SCHEMA gold;


-- ml schema triggers
DROP TRIGGER IF EXISTS ml_tonights_games_audit_trigger ON silver.ml_tonights_games;
DROP FUNCTION IF EXISTS ml_tonights_games_audit_trigger_function();

-- marts schema triggers
DROP TRIGGER IF EXISTS feature_flags_audit_trigger ON gold.feature_flags;
DROP FUNCTION IF EXISTS feature_flags_audit_trigger_function();

DROP TRIGGER IF EXISTS incidents_audit_trigger ON gold.incidents;
DROP FUNCTION IF EXISTS incidents_audit_trigger_function();

DROP TRIGGER IF EXISTS rest_api_users_audit_trigger ON gold.rest_api_users;
DROP FUNCTION IF EXISTS rest_api_users_audit_trigger_function();

DROP TRIGGER IF EXISTS user_predictions_audit_trigger ON gold.user_predictions;
DROP FUNCTION IF EXISTS user_predictions_audit_trigger_function();