CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    user_choice VARCHAR(20) NOT NULL,
    computer_choice VARCHAR(20) NOT NULL,
    result VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_player
        FOREIGN KEY(player_id)
        REFERENCES players(id)
);