CREATE TABLE IF NOT EXISTS autofill (
    discord_id INTEGER PRIMARY KEY,
    uuid TEXT,
    username TEXT
);

CREATE TABLE IF NOT EXISTS linked_accounts (
    discord_id INTEGER PRIMARY KEY,
    uuid TEXT
);

CREATE TABLE IF NOT EXISTS voting_data (
    discord_id INTEGER PRIMARY KEY,
    total_votes INTEGER,
    weekend_votes INTEGER,
    last_vote REAL
);

CREATE TABLE IF NOT EXISTS themes_data (
    discord_id INTEGER PRIMARY KEY,
    owned_themes TEXT,
    selected_theme TEXT
);

CREATE TABLE IF NOT EXISTS command_usage (
    discord_id INTEGER PRIMARY KEY,
    overall INTEGER
);

CREATE TABLE IF NOT EXISTS configured_reset_times (
    discord_id INTEGER PRIMARY KEY,
    timezone INTEGER,
    reset_hour INTEGER
);

CREATE TABLE IF NOT EXISTS default_reset_times (
    uuid TEXT PRIMARY KEY,
    timezone INTEGER,
    reset_hour INTEGER
);

CREATE TABLE IF NOT EXISTS permissions (
    discord_id INTEGER PRIMRAY KEY,
    permissions TEXT
);

CREATE TABLE IF NOT EXISTS growth_data (
    timestamp REAL,
    discord_id INTEGER,
    action TEXT,
    growth TEXT
);

CREATE TABLE IF NOT EXISTS reaction_roles (
    guild_id INTEGER,
    role_id INTEGER
);

CREATE TABLE IF NOT EXISTS gifts (
    gift_id TEXT PRIMARY KEY,
    purchaser_id INTEGER,
    purchaser_name TEXT DEFAULT 'unknown',
    purchaser_avatar TEXT DEFAULT 'https://cdn.discordapp.com/embed/avatars/0.png',
    purchase_timestamp REAL DEFAULT (strftime('%s', 'now', 'utc')),
    package TEXT,
    duration REAL,
    max_redemptions INTEGER DEFAULT 1,
    max_redemptions_per_user INTEGER DEFAULT -1
);

CREATE TABLE IF NOT EXISTS gift_redemptions (
    gift_id TEXT,
    redemption_id INTEGER,
    timestamp REAL DEFAULT (strftime('%s', 'now', 'utc')),
    redeemer_id INTEGER,
    redeemer_name TEXT DEFAULT 'unknown',
    redeemer_avatar TEXT DEFAULT 'https://cdn.discordapp.com/embed/avatars/0.png',
    FOREIGN KEY (gift_id) REFERENCES gifts(gift_id)
);

-- Adds dynamic redemptions id on a per gift basis
CREATE TRIGGER IF NOT EXISTS redemption_id_trigger
AFTER INSERT ON gift_redemptions
BEGIN
    UPDATE gift_redemptions
    SET redemption_id = (SELECT IFNULL(MAX(redemption_id), 0) + 1 FROM gift_redemptions WHERE gift_id = NEW.gift_id)
    WHERE rowid = NEW.rowid;
END;

CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id INTEGER NOT NULL UNIQUE,
    creation_timestamp REAL DEFAULT (strftime('%s', 'now', 'utc')),
    permissions TEXT,
    blacklisted INTEGER DEFAULT 0,
    CONSTRAINT check_blacklisted CHECK (blacklisted = 0 OR blacklisted = 1)
);

CREATE TABLE IF NOT EXISTS subscriptions_active (
  discord_id INTEGER PRIMARY KEY NOT NULL,
  package TEXT NOT NULL,
  expires REAL -- Can be null if subscription is lifetime
);

CREATE TABLE IF NOT EXISTS subscriptions_paused (
  id INTEGER PRIMARY KEY AUTOINCREMENT, -- To differentiate different paused packages (since there can be multiple)
  discord_id INTEGER NOT NULL,
  package TEXT NOT NULL,
  duration_remaining REAL, -- Can be null if subscription is lifetime
  UNIQUE(id, discord_id)
);

CREATE TABLE IF NOT EXISTS bedwars_stats_snapshots (
    snapshot_id TEXT NOT NULL PRIMARY KEY,
    Experience INTEGER,
    wins_bedwars INTEGER,
    losses_bedwars INTEGER,
    final_kills_bedwars INTEGER,
    final_deaths_bedwars INTEGER,
    kills_bedwars INTEGER,
    deaths_bedwars INTEGER,
    beds_broken_bedwars INTEGER,
    beds_lost_bedwars INTEGER,
    games_played_bedwars INTEGER,
    eight_one_wins_bedwars INTEGER,
    eight_one_losses_bedwars INTEGER,
    eight_one_final_kills_bedwars INTEGER,
    eight_one_final_deaths_bedwars INTEGER,
    eight_one_kills_bedwars INTEGER,
    eight_one_deaths_bedwars INTEGER,
    eight_one_beds_broken_bedwars INTEGER,
    eight_one_beds_lost_bedwars INTEGER,
    eight_one_games_played_bedwars INTEGER,
    eight_two_wins_bedwars INTEGER,
    eight_two_losses_bedwars INTEGER,
    eight_two_final_kills_bedwars INTEGER,
    eight_two_final_deaths_bedwars INTEGER,
    eight_two_kills_bedwars INTEGER,
    eight_two_deaths_bedwars INTEGER,
    eight_two_beds_broken_bedwars INTEGER,
    eight_two_beds_lost_bedwars INTEGER,
    eight_two_games_played_bedwars INTEGER,
    four_three_wins_bedwars INTEGER,
    four_three_losses_bedwars INTEGER,
    four_three_final_kills_bedwars INTEGER,
    four_three_final_deaths_bedwars INTEGER,
    four_three_kills_bedwars INTEGER,
    four_three_deaths_bedwars INTEGER,
    four_three_beds_broken_bedwars INTEGER,
    four_three_beds_lost_bedwars INTEGER,
    four_three_games_played_bedwars INTEGER,
    four_four_wins_bedwars INTEGER,
    four_four_losses_bedwars INTEGER,
    four_four_final_kills_bedwars INTEGER,
    four_four_final_deaths_bedwars INTEGER,
    four_four_kills_bedwars INTEGER,
    four_four_deaths_bedwars INTEGER,
    four_four_beds_broken_bedwars INTEGER,
    four_four_beds_lost_bedwars INTEGER,
    four_four_games_played_bedwars INTEGER,
    two_four_wins_bedwars INTEGER,
    two_four_losses_bedwars INTEGER,
    two_four_final_kills_bedwars INTEGER,
    two_four_final_deaths_bedwars INTEGER,
    two_four_kills_bedwars INTEGER,
    two_four_deaths_bedwars INTEGER,
    two_four_beds_broken_bedwars INTEGER,
    two_four_beds_lost_bedwars INTEGER,
    two_four_games_played_bedwars INTEGER,
    items_purchased_bedwars INTEGER,
    eight_one_items_purchased_bedwars INTEGER,
    eight_two_items_purchased_bedwars INTEGER,
    four_three_items_purchased_bedwars INTEGER,
    four_four_items_purchased_bedwars INTEGER,
    two_four_items_purchased_bedwars INTEGER
);

CREATE TABLE IF NOT EXISTS session_info (
    session INTEGER,
    uuid TEXT,
    snapshot_id TEXT NOT NULL UNIQUE,
    creation_timestamp REAL NOT NULL,
    PRIMARY KEY (session, uuid)
);

CREATE TABLE IF NOT EXISTS historical_info (
    uuid TEXT,
    period TEXT,
    level REAL,
    snapshot_id TEXT NOT NULL UNIQUE,
    PRIMARY KEY (uuid, period)
);

CREATE TABLE IF NOT EXISTS rotational_info (
    uuid TEXT NOT NULL,
    rotation TEXT NOT NULL,
    last_reset_timestamp REAL DEFAULT (strftime('%s', 'now', 'utc')),
    snapshot_id TEXT NOT NULL UNIQUE,
    PRIMARY KEY (uuid, rotation)
);

-- SELECT s.session, s.uuid, s.date, s.level, bs.*
-- FROM sessions s
-- INNER JOIN bedwars_stats_snapshot bs
-- ON s.snapshot_id = bs.snapshot_id ORDER BY s.session;

-- Should probably do something about this monstrosity
CREATE TABLE IF NOT EXISTS sessions (
    session INTEGER,
    uuid TEXT,
    date TEXT,
    level INTEGER,
    Experience INTEGER,
    wins_bedwars INTEGER,
    losses_bedwars INTEGER,
    final_kills_bedwars INTEGER,
    final_deaths_bedwars INTEGER,
    kills_bedwars INTEGER,
    deaths_bedwars INTEGER,
    beds_broken_bedwars INTEGER,
    beds_lost_bedwars INTEGER,
    games_played_bedwars INTEGER,
    eight_one_wins_bedwars INTEGER,
    eight_one_losses_bedwars INTEGER,
    eight_one_final_kills_bedwars INTEGER,
    eight_one_final_deaths_bedwars INTEGER,
    eight_one_kills_bedwars INTEGER,
    eight_one_deaths_bedwars INTEGER,
    eight_one_beds_broken_bedwars INTEGER,
    eight_one_beds_lost_bedwars INTEGER,
    eight_one_games_played_bedwars INTEGER,
    eight_two_wins_bedwars INTEGER,
    eight_two_losses_bedwars INTEGER,
    eight_two_final_kills_bedwars INTEGER,
    eight_two_final_deaths_bedwars INTEGER,
    eight_two_kills_bedwars INTEGER,
    eight_two_deaths_bedwars INTEGER,
    eight_two_beds_broken_bedwars INTEGER,
    eight_two_beds_lost_bedwars INTEGER,
    eight_two_games_played_bedwars INTEGER,
    four_three_wins_bedwars INTEGER,
    four_three_losses_bedwars INTEGER,
    four_three_final_kills_bedwars INTEGER,
    four_three_final_deaths_bedwars INTEGER,
    four_three_kills_bedwars INTEGER,
    four_three_deaths_bedwars INTEGER,
    four_three_beds_broken_bedwars INTEGER,
    four_three_beds_lost_bedwars INTEGER,
    four_three_games_played_bedwars INTEGER,
    four_four_wins_bedwars INTEGER,
    four_four_losses_bedwars INTEGER,
    four_four_final_kills_bedwars INTEGER,
    four_four_final_deaths_bedwars INTEGER,
    four_four_kills_bedwars INTEGER,
    four_four_deaths_bedwars INTEGER,
    four_four_beds_broken_bedwars INTEGER,
    four_four_beds_lost_bedwars INTEGER,
    four_four_games_played_bedwars INTEGER,
    two_four_wins_bedwars INTEGER,
    two_four_losses_bedwars INTEGER,
    two_four_final_kills_bedwars INTEGER,
    two_four_final_deaths_bedwars INTEGER,
    two_four_kills_bedwars INTEGER,
    two_four_deaths_bedwars INTEGER,
    two_four_beds_broken_bedwars INTEGER,
    two_four_beds_lost_bedwars INTEGER,
    two_four_games_played_bedwars INTEGER,
    items_purchased_bedwars INTEGER,
    eight_one_items_purchased_bedwars INTEGER,
    eight_two_items_purchased_bedwars INTEGER,
    four_three_items_purchased_bedwars INTEGER,
    four_four_items_purchased_bedwars INTEGER,
    two_four_items_purchased_bedwars INTEGER,
    PRIMARY KEY (session, uuid)
);

CREATE TABLE IF NOT EXISTS historical (
    uuid TEXT,
    period TEXT,
    level REAL,
    Experience INTEGER,
    wins_bedwars INTEGER,
    losses_bedwars INTEGER,
    final_kills_bedwars INTEGER,
    final_deaths_bedwars INTEGER,
    kills_bedwars INTEGER,
    deaths_bedwars INTEGER,
    beds_broken_bedwars INTEGER,
    beds_lost_bedwars INTEGER,
    games_played_bedwars INTEGER,
    eight_one_wins_bedwars INTEGER,
    eight_one_losses_bedwars INTEGER,
    eight_one_final_kills_bedwars INTEGER,
    eight_one_final_deaths_bedwars INTEGER,
    eight_one_kills_bedwars INTEGER,
    eight_one_deaths_bedwars INTEGER,
    eight_one_beds_broken_bedwars INTEGER,
    eight_one_beds_lost_bedwars INTEGER,
    eight_one_games_played_bedwars INTEGER,
    eight_two_wins_bedwars INTEGER,
    eight_two_losses_bedwars INTEGER,
    eight_two_final_kills_bedwars INTEGER,
    eight_two_final_deaths_bedwars INTEGER,
    eight_two_kills_bedwars INTEGER,
    eight_two_deaths_bedwars INTEGER,
    eight_two_beds_broken_bedwars INTEGER,
    eight_two_beds_lost_bedwars INTEGER,
    eight_two_games_played_bedwars INTEGER,
    four_three_wins_bedwars INTEGER,
    four_three_losses_bedwars INTEGER,
    four_three_final_kills_bedwars INTEGER,
    four_three_final_deaths_bedwars INTEGER,
    four_three_kills_bedwars INTEGER,
    four_three_deaths_bedwars INTEGER,
    four_three_beds_broken_bedwars INTEGER,
    four_three_beds_lost_bedwars INTEGER,
    four_three_games_played_bedwars INTEGER,
    four_four_wins_bedwars INTEGER,
    four_four_losses_bedwars INTEGER,
    four_four_final_kills_bedwars INTEGER,
    four_four_final_deaths_bedwars INTEGER,
    four_four_kills_bedwars INTEGER,
    four_four_deaths_bedwars INTEGER,
    four_four_beds_broken_bedwars INTEGER,
    four_four_beds_lost_bedwars INTEGER,
    four_four_games_played_bedwars INTEGER,
    two_four_wins_bedwars INTEGER,
    two_four_losses_bedwars INTEGER,
    two_four_final_kills_bedwars INTEGER,
    two_four_final_deaths_bedwars INTEGER,
    two_four_kills_bedwars INTEGER,
    two_four_deaths_bedwars INTEGER,
    two_four_beds_broken_bedwars INTEGER,
    two_four_beds_lost_bedwars INTEGER,
    two_four_games_played_bedwars INTEGER,
    items_purchased_bedwars INTEGER,
    eight_one_items_purchased_bedwars INTEGER,
    eight_two_items_purchased_bedwars INTEGER,
    four_three_items_purchased_bedwars INTEGER,
    four_four_items_purchased_bedwars INTEGER,
    two_four_items_purchased_bedwars INTEGER,
    PRIMARY KEY (uuid, period)
);

CREATE TABLE IF NOT EXISTS trackers_new (
    uuid TEXT NOT NULL,
    tracker TEXT NOT NULL,
    last_reset_timestamp REAL DEFAULT (strftime('%s', 'now', 'utc')),
    Experience INTEGER,
    wins_bedwars INTEGER,
    losses_bedwars INTEGER,
    final_kills_bedwars INTEGER,
    final_deaths_bedwars INTEGER,
    kills_bedwars INTEGER,
    deaths_bedwars INTEGER,
    beds_broken_bedwars INTEGER,
    beds_lost_bedwars INTEGER,
    games_played_bedwars INTEGER,
    eight_one_wins_bedwars INTEGER,
    eight_one_losses_bedwars INTEGER,
    eight_one_final_kills_bedwars INTEGER,
    eight_one_final_deaths_bedwars INTEGER,
    eight_one_kills_bedwars INTEGER,
    eight_one_deaths_bedwars INTEGER,
    eight_one_beds_broken_bedwars INTEGER,
    eight_one_beds_lost_bedwars INTEGER,
    eight_one_games_played_bedwars INTEGER,
    eight_two_wins_bedwars INTEGER,
    eight_two_losses_bedwars INTEGER,
    eight_two_final_kills_bedwars INTEGER,
    eight_two_final_deaths_bedwars INTEGER,
    eight_two_kills_bedwars INTEGER,
    eight_two_deaths_bedwars INTEGER,
    eight_two_beds_broken_bedwars INTEGER,
    eight_two_beds_lost_bedwars INTEGER,
    eight_two_games_played_bedwars INTEGER,
    four_three_wins_bedwars INTEGER,
    four_three_losses_bedwars INTEGER,
    four_three_final_kills_bedwars INTEGER,
    four_three_final_deaths_bedwars INTEGER,
    four_three_kills_bedwars INTEGER,
    four_three_deaths_bedwars INTEGER,
    four_three_beds_broken_bedwars INTEGER,
    four_three_beds_lost_bedwars INTEGER,
    four_three_games_played_bedwars INTEGER,
    four_four_wins_bedwars INTEGER,
    four_four_losses_bedwars INTEGER,
    four_four_final_kills_bedwars INTEGER,
    four_four_final_deaths_bedwars INTEGER,
    four_four_kills_bedwars INTEGER,
    four_four_deaths_bedwars INTEGER,
    four_four_beds_broken_bedwars INTEGER,
    four_four_beds_lost_bedwars INTEGER,
    four_four_games_played_bedwars INTEGER,
    two_four_wins_bedwars INTEGER,
    two_four_losses_bedwars INTEGER,
    two_four_final_kills_bedwars INTEGER,
    two_four_final_deaths_bedwars INTEGER,
    two_four_kills_bedwars INTEGER,
    two_four_deaths_bedwars INTEGER,
    two_four_beds_broken_bedwars INTEGER,
    two_four_beds_lost_bedwars INTEGER,
    two_four_games_played_bedwars INTEGER,
    items_purchased_bedwars INTEGER,
    eight_one_items_purchased_bedwars INTEGER,
    eight_two_items_purchased_bedwars INTEGER,
    four_three_items_purchased_bedwars INTEGER,
    four_four_items_purchased_bedwars INTEGER,
    two_four_items_purchased_bedwars INTEGER,
    PRIMARY KEY (uuid, tracker)
);
