from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL", "sqlite:///jokenpo.db")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if database_url.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"sslmode": "require"}
    }

db = SQLAlchemy(app)


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    user_choice = db.Column(db.String(20), nullable=False)
    computer_choice = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(30), nullable=False)


@app.route("/")
def index():
    return "Servidor NOUS API do Aluno rodando com sucesso!"


# CRUD PLAYERS

@app.route("/players", methods=["POST"])
def create_player():
    data = request.json
    player = Player(name=data["name"])

    db.session.add(player)
    db.session.commit()

    return jsonify({
        "message": "Jogador criado!",
        "id": player.id,
        "name": player.name
    }), 201


@app.route("/players", methods=["GET"])
def list_players():
    players = Player.query.all()

    return jsonify([
        {
            "id": player.id,
            "name": player.name
        }
        for player in players
    ])


@app.route("/players/<int:id>", methods=["PUT"])
def update_player(id):
    player = Player.query.get_or_404(id)
    data = request.json

    player.name = data["name"]
    db.session.commit()

    return jsonify({
        "message": "Jogador atualizado!",
        "id": player.id,
        "name": player.name
    })


@app.route("/players/<int:id>", methods=["DELETE"])
def delete_player(id):
    player = Player.query.get_or_404(id)

    Match.query.filter_by(player_id=id).delete()
    db.session.delete(player)
    db.session.commit()

    return jsonify({
        "message": "Jogador e partidas relacionadas deletados!"
    })


# CRUD MATCHES

@app.route("/play", methods=["POST"])
def play_game():
    data = request.json

    player_id = data["player_id"]
    user_choice = data["choice"].lower()

    if user_choice not in ["pedra", "papel", "tesoura"]:
        return jsonify({"error": "Escolha inválida"}), 400

    player = Player.query.get_or_404(player_id)

    computer_choice = random.choice(["pedra", "papel", "tesoura"])
    result = determine_winner(user_choice, computer_choice)

    match = Match(
        player_id=player.id,
        user_choice=user_choice,
        computer_choice=computer_choice,
        result=result
    )

    db.session.add(match)
    db.session.commit()

    return jsonify({
        "message": "Partida criada!",
        "id": match.id,
        "player_id": match.player_id,
        "user_choice": match.user_choice,
        "computer_choice": match.computer_choice,
        "result": match.result
    }), 201


@app.route("/matches", methods=["GET"])
def list_matches():
    matches = Match.query.all()

    return jsonify([
        {
            "id": match.id,
            "player_id": match.player_id,
            "user_choice": match.user_choice,
            "computer_choice": match.computer_choice,
            "result": match.result
        }
        for match in matches
    ])


@app.route("/matches/<int:id>", methods=["PUT"])
def update_match(id):
    match = Match.query.get_or_404(id)
    data = request.json

    if data["user_choice"] not in ["pedra", "papel", "tesoura"]:
        return jsonify({"error": "Escolha inválida"}), 400

    match.user_choice = data["user_choice"]
    match.computer_choice = data["computer_choice"]
    match.result = determine_winner(match.user_choice, match.computer_choice)

    db.session.commit()

    return jsonify({
        "message": "Partida atualizada!",
        "id": match.id,
        "player_id": match.player_id,
        "user_choice": match.user_choice,
        "computer_choice": match.computer_choice,
        "result": match.result
    })


@app.route("/matches/<int:id>", methods=["DELETE"])
def delete_match(id):
    match = Match.query.get_or_404(id)

    db.session.delete(match)
    db.session.commit()

    return jsonify({
        "message": "Partida deletada!"
    })


def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "Empate"

    if (
        (user_choice == "pedra" and computer_choice == "tesoura") or
        (user_choice == "tesoura" and computer_choice == "papel") or
        (user_choice == "papel" and computer_choice == "pedra")
    ):
        return "Você"

    return "Computador"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=80)