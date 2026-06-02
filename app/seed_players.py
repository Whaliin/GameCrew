"""
This script seeds the database with dummy player profiles for testing purposes.

To run:
python -m app.seed_players
"""

# Seeding player profiles

import json

from app.auth.hashing import hash_password
from app.database import SessionLocal
from app.models import Player, PlayerProfile, Region, Platform, Language, Playtime, Game, PlayerGameProfile, Friendship
from app.schemas import GameProfileSpec
from random import choice, randint, sample
from datetime import datetime, timedelta
from random import randint, choices

def _pick_sample_size(max_size: int) -> int:
	"""Helper function to pick a random sample size between 1 and max_size.
	This function is heavily weighted towards smaller sample sizes to create varied but realistic data 
	(most people play on 1-2 platforms, speak 1-2 languages, and have 1-2 playtimes).
	"""
	# The buckets represent the possible sample sizes (1,2,3,4,5)
	buckets = [1, 2, 3, 4, 5]
	# 1: chance of picking the first bucket, 2: chance of picking the second bucket, etc,
	weights = [50, 30, 10, 5, 5]
	size = choices(buckets, weights=weights, k=1)[0]
	return min(size, max_size)

def _pick_random_time(days_back: int = 30):
	"""Helper function to pick a random datetime within the last days_back days (default 30)."""
	return datetime.now() - timedelta(days=randint(0, days_back), minutes=randint(0, 1440))

def seed_player_profiles() -> None:
	"""Seed player profiles with dummy data for testing purposes."""
	

	db = SessionLocal()
	try:
		# Check if there are any existing player profiles to avoid duplicates
		# if db.query(PlayerProfile).first() is not None:
		# 	return
		
		# Get the existing values available for selection in the player profiles so we can assign valid values
		regions = db.query(Region).all()
		if not regions:
			raise Exception("No regions found in the database. Please seed the default regions first.")
		
		platforms = db.query(Platform).all()
		if not platforms:
			raise Exception("No platforms found in the database. Please seed the default platforms first.")
		
		languages = db.query(Language).all()
		if not languages:
			raise Exception("No languages found in the database. Please seed the default languages first.")

		playtimes = db.query(Playtime).all()
		if not playtimes:
			raise Exception("No playtimes found in the database. Please seed the default playtimes first.")
		
		games = db.query(Game).all()
		if not games:
			raise Exception("No games found in the database. Please seed the default games first.")
		
		# Add 1000 dummy player profiles with random valid data for testing purposes.

		# generate a single password hash to use for all the dummy profiles
		dummy_password_hash = hash_password("1")

		# check the highest dummy player username to avoid conflicts
		existing_dummy_players = db.query(Player).filter(Player.username.like("player%")).all()
		existing_dummy_indices = [int(player.username[6:]) for player in existing_dummy_players if player.username[6:].isdigit()]

		print("Seeding player profiles...")
		for i in range(1000):
			if i % 100 == 0:
				print(f"Seeding player profile {i+1}/1000...")

			# skip creating a profile if it would conflict with an existing player
			if i in existing_dummy_indices:
				continue 

			player = Player(
				username=f"player{i}",
				password_hash=dummy_password_hash
			)
			db.add(player)
			db.flush()  # Flush to get the player ID for the profile (updates the object)

			profile = PlayerProfile(
				player_id=player.id,
				region_id=choice(regions).id,
				birth_year=randint(1975, 2005),
				private=choice([True, False]),
				bio=f"This is the bio of player{i}. I am a gamer who loves playing games and making friends. Looking for people to play with!",
				steam_url=choice([f"https://steamcommunity.com/id/player{i}", None]),
				discord=choice([f"player{i}#1234", None]),
				riot_id=choice([f"player{i}#NA1", None]),
				last_update=_pick_random_time(60)
			)
			db.add(profile)

			# Add random selections of platforms, languages, playtimes for each player profile.
			# Distribution is weighted towards smaller sample size to create more realistic data.
			platforms_sample = sample(platforms, k=_pick_sample_size(len(platforms)))
			player.platforms.extend(platforms_sample)

			languages_sample = sample(languages, k=_pick_sample_size(len(languages)))
			player.languages.extend(languages_sample)

			playtimes_sample = sample(playtimes, k=_pick_sample_size(len(playtimes)))
			player.playtimes.extend(playtimes_sample)

			# For the game profiles, we can add some JSON data based on the game's schema_spec.
			# Pick a random assortment of games for each player profile to create varied test data.
			games_sample = sample(games, k=randint(1, len(games)))
			for game in games_sample:
				# Get the schema class for the game based on the schema_spec field
				# and generate some random valid data based on the field annotations defined in the schema.
				schema_class = GameProfileSpec.get_schema(game.schema_spec)
				if schema_class is None:
					continue  # Skip if no valid schema class is found

				# 20% of profiles will have empty game profile data (to test how the system handles missing/empty data)
				# For the rest, generate random valid data based on the validation rules defined in the schema.
				if choice([False, False, False, False, True]):  # 20% chance of being True
					continue  # Skip adding game profile data for this player and game, leaving it empty.

				profile_data = {}
				field_specs = schema_class.to_form_schema()["fields"]
				for field_name, field_spec in field_specs.items():
					rules = field_spec.get("validation", {})
					allowed_values = rules.get("allowedvalues", None)
					if allowed_values:
						# If there are allowed values, pick a random one (or multiple if multi is True)
						if rules.get("multi", False):
							profile_data[field_name] = sample(allowed_values, k=_pick_sample_size(len(allowed_values)))
						else:
							profile_data[field_name] = choice(allowed_values)
					else:
						# If there are no allowed values, generate a random value based on the derived validation metadata.
						if "min" in rules and "max" in rules:
							profile_data[field_name] = randint(int(rules["min"]), int(rules["max"]))
						elif "min_length" in rules and "max_length" in rules:
							length = randint(int(rules["min_length"]), int(rules["max_length"]))
							profile_data[field_name] = f"{field_name}_{i}"[:length]
						else:
							profile_data[field_name] = f"{field_name}_{i}"
					
				# Add the game profile data as a JSON string in the PlayerGameProfile table
				db.add(PlayerGameProfile(player_id=player.id, game_id=game.id, data=json.dumps(profile_data)))

		# After adding all the player profiles and related data,
		# add some random friendships between players.
		player_ids = [player.id for player in db.query(Player).all()]
		seen_friendships = set()  # To track existing friendships and prevent duplicates
		print("Seeding friendships between players...")
		for i in range(2000):  # Add 2000 random friendships
			if i % 200 == 0:
				print(f"Seeding friendship {i+1}/2000...")
			sender_id, receiver_id = choice(player_ids), choice(player_ids)

			if sender_id == receiver_id:  
				continue # Prevent self-friendship (already enforced by the database constraint, but we can avoid the error by checking here)

			if (sender_id, receiver_id) in seen_friendships or (receiver_id, sender_id) in seen_friendships:
				continue # Skip if a friendship already exists between these two players (in either direction)

			seen_friendships.add((sender_id, receiver_id))  # Mark this friendship as seen

			# Add the friendship with a random accepted status (70% accepted, 30% pending) to create varied test data.
			accept_state = choice([True, True, True, False])  # 70% chance of being True
			db.add(Friendship(sender_id=sender_id, receiver_id=receiver_id, accepted=accept_state, accepted_at=_pick_random_time() if accept_state else None))

		# Commit all the changes to the database after seeding.
		db.commit()
	except Exception:
		# On exception, rollback the transaction
		db.rollback()
		raise
	finally:
		# Always close the database connection
		db.close()

if __name__ == "__main__":
	seed_player_profiles()