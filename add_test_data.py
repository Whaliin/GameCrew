from sqlalchemy import select

from app.database import SessionLocal, init_database
from app.models import Game, Player, PlayerGameProfile


def get_or_create_game(db, slug: str, display_name: str) -> Game:
	game = db.scalar(select(Game).where(Game.slug == slug))
	if game is not None:
		return game

	game = Game(slug=slug, display_name=display_name)
	db.add(game)
	db.flush()
	return game


def get_or_create_player(db, username: str, avatar_url: str, bio: str, password_hash: str) -> Player:
	player = db.scalar(select(Player).where(Player.username == username))
	if player is not None:
		return player

	player = Player(
		username=username,
		avatar_url=avatar_url,
		bio=bio,
		password_hash=password_hash,
	)
	db.add(player)
	db.flush()
	return player


def get_or_create_player_game_profile(db, player_id: int, game_id: int, rank_label: str) -> PlayerGameProfile:
	profile = db.scalar(
		select(PlayerGameProfile).where(
			PlayerGameProfile.player_id == player_id,
			PlayerGameProfile.game_id == game_id,
		)
	)
	if profile is not None:
		return profile

	profile = PlayerGameProfile(player_id=player_id, game_id=game_id, rank_label=rank_label)
	db.add(profile)
	db.flush()
	return profile


def seed_test_data() -> None:
	init_database()

	games_to_seed = [
		{"slug": "cs2", "display_name": "Counter-Strike 2"},
		{"slug": "lol", "display_name": "League of Legends"},
		{"slug": "valorant", "display_name": "Valorant"},
		{"slug": "arcraiders", "display_name": "ARC Raiders"},
		{"slug": "mobilelegends", "display_name": "Mobile Legends"},
	]

	with SessionLocal() as db:
		games_by_slug = {}
		for game_data in games_to_seed:
			game = get_or_create_game(
				db,
				slug=game_data["slug"],
				display_name=game_data["display_name"],
			)
			games_by_slug[game.slug] = game

		player = get_or_create_player(
			db,
			username="eren9s",
			avatar_url="/static/img/profiles/default.jpg",
			bio="Passionerad FPS-spelare som letar efter ett seriost lag for ranked.",
			password_hash="dev_only_seed_hash_change_me",
		)

		get_or_create_player_game_profile(
			db,
			player_id=player.id,
			game_id=games_by_slug["cs2"].id,
			rank_label="Global Elite",
		)
		get_or_create_player_game_profile(
			db,
			player_id=player.id,
			game_id=games_by_slug["valorant"].id,
			rank_label="Immortal",
		)
		get_or_create_player_game_profile(
			db,
			player_id=player.id,
			game_id=games_by_slug["lol"].id,
			rank_label="Diamond",
		)

		db.commit()

		print("Seed complete: test games, player, and player-game profiles are available.")


if __name__ == "__main__":
	seed_test_data()
