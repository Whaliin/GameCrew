/* ============================================================
   ranks.js — Ranks per game.

   Maps game slug → list of rank names in ascending order.
   Loaded globally so the rank popup can populate dropdowns
   based on the current game.

   When you add a new game to the site, also add its ranks here
   AND in the matching Python dict in app/routers/ranks.py so
   the backend can validate submitted ranks.
   ============================================================ */
(function () {
	'use strict';

	window.GameCrewRanks = {
		// FPS
		'cs2': ['Silver I', 'Silver II', 'Silver III', 'Silver IV', 'Silver Elite', 'Silver Elite Master', 'Gold Nova I', 'Gold Nova II', 'Gold Nova III', 'Gold Nova Master', 'Master Guardian I', 'Master Guardian II', 'Master Guardian Elite', 'Distinguished Master Guardian', 'Legendary Eagle', 'Legendary Eagle Master', 'Supreme Master First Class', 'Global Elite'],
		'valorant': ['Iron 1', 'Iron 2', 'Iron 3', 'Bronze 1', 'Bronze 2', 'Bronze 3', 'Silver 1', 'Silver 2', 'Silver 3', 'Gold 1', 'Gold 2', 'Gold 3', 'Platinum 1', 'Platinum 2', 'Platinum 3', 'Diamond 1', 'Diamond 2', 'Diamond 3', 'Ascendant 1', 'Ascendant 2', 'Ascendant 3', 'Immortal 1', 'Immortal 2', 'Immortal 3', 'Radiant'],
		'overwatch2': ['Bronze 5', 'Bronze 4', 'Bronze 3', 'Bronze 2', 'Bronze 1', 'Silver 5', 'Silver 4', 'Silver 3', 'Silver 2', 'Silver 1', 'Gold 5', 'Gold 4', 'Gold 3', 'Gold 2', 'Gold 1', 'Platinum 5', 'Platinum 4', 'Platinum 3', 'Platinum 2', 'Platinum 1', 'Diamond 5', 'Diamond 4', 'Diamond 3', 'Diamond 2', 'Diamond 1', 'Master 5', 'Master 4', 'Master 3', 'Master 2', 'Master 1', 'Grandmaster 5', 'Grandmaster 4', 'Grandmaster 3', 'Grandmaster 2', 'Grandmaster 1', 'Champion'],
		'apex': ['Rookie IV', 'Rookie III', 'Rookie II', 'Rookie I', 'Bronze IV', 'Bronze III', 'Bronze II', 'Bronze I', 'Silver IV', 'Silver III', 'Silver II', 'Silver I', 'Gold IV', 'Gold III', 'Gold II', 'Gold I', 'Platinum IV', 'Platinum III', 'Platinum II', 'Platinum I', 'Diamond IV', 'Diamond III', 'Diamond II', 'Diamond I', 'Master', 'Apex Predator'],
		'r6siege': ['Copper V', 'Copper IV', 'Copper III', 'Copper II', 'Copper I', 'Bronze V', 'Bronze IV', 'Bronze III', 'Bronze II', 'Bronze I', 'Silver V', 'Silver IV', 'Silver III', 'Silver II', 'Silver I', 'Gold V', 'Gold IV', 'Gold III', 'Gold II', 'Gold I', 'Platinum V', 'Platinum IV', 'Platinum III', 'Platinum II', 'Platinum I', 'Emerald V', 'Emerald IV', 'Emerald III', 'Emerald II', 'Emerald I', 'Diamond V', 'Diamond IV', 'Diamond III', 'Diamond II', 'Diamond I', 'Champion'],
		'codwarzone': ['Bronze I', 'Bronze II', 'Bronze III', 'Silver I', 'Silver II', 'Silver III', 'Gold I', 'Gold II', 'Gold III', 'Platinum I', 'Platinum II', 'Platinum III', 'Diamond I', 'Diamond II', 'Diamond III', 'Crimson I', 'Crimson II', 'Crimson III', 'Iridescent I', 'Iridescent II', 'Iridescent III', 'Top 250'],
		'haloinfinite': ['Bronze I', 'Bronze II', 'Bronze III', 'Bronze IV', 'Bronze V', 'Bronze VI', 'Silver I', 'Silver II', 'Silver III', 'Silver IV', 'Silver V', 'Silver VI', 'Gold I', 'Gold II', 'Gold III', 'Gold IV', 'Gold V', 'Gold VI', 'Platinum I', 'Platinum II', 'Platinum III', 'Platinum IV', 'Platinum V', 'Platinum VI', 'Diamond I', 'Diamond II', 'Diamond III', 'Diamond IV', 'Diamond V', 'Diamond VI', 'Onyx'],
		'thefinals': ['Bronze 4', 'Bronze 3', 'Bronze 2', 'Bronze 1', 'Silver 4', 'Silver 3', 'Silver 2', 'Silver 1', 'Gold 4', 'Gold 3', 'Gold 2', 'Gold 1', 'Platinum 4', 'Platinum 3', 'Platinum 2', 'Platinum 1', 'Diamond 4', 'Diamond 3', 'Diamond 2', 'Diamond 1', 'Ruby'],
		'xdefiant': ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master'],
		'splitgate': ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond'],

		// Battle Royale
		'fortnite': ['Bronze I', 'Bronze II', 'Bronze III', 'Silver I', 'Silver II', 'Silver III', 'Gold I', 'Gold II', 'Gold III', 'Platinum I', 'Platinum II', 'Platinum III', 'Diamond I', 'Diamond II', 'Diamond III', 'Elite', 'Champion', 'Unreal'],
		'pubg': ['Bronze V', 'Bronze IV', 'Bronze III', 'Bronze II', 'Bronze I', 'Silver V', 'Silver IV', 'Silver III', 'Silver II', 'Silver I', 'Gold V', 'Gold IV', 'Gold III', 'Gold II', 'Gold I', 'Platinum V', 'Platinum IV', 'Platinum III', 'Platinum II', 'Platinum I', 'Diamond V', 'Diamond IV', 'Diamond III', 'Diamond II', 'Diamond I', 'Master', 'Grand Master'],
		'naraka': ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Asura'],

		// MOBA
		'lol': ['Iron IV', 'Iron III', 'Iron II', 'Iron I', 'Bronze IV', 'Bronze III', 'Bronze II', 'Bronze I', 'Silver IV', 'Silver III', 'Silver II', 'Silver I', 'Gold IV', 'Gold III', 'Gold II', 'Gold I', 'Platinum IV', 'Platinum III', 'Platinum II', 'Platinum I', 'Emerald IV', 'Emerald III', 'Emerald II', 'Emerald I', 'Diamond IV', 'Diamond III', 'Diamond II', 'Diamond I', 'Master', 'Grandmaster', 'Challenger'],
		'wildrift': ['Iron IV', 'Iron III', 'Iron II', 'Iron I', 'Bronze IV', 'Bronze III', 'Bronze II', 'Bronze I', 'Silver IV', 'Silver III', 'Silver II', 'Silver I', 'Gold IV', 'Gold III', 'Gold II', 'Gold I', 'Platinum IV', 'Platinum III', 'Platinum II', 'Platinum I', 'Emerald IV', 'Emerald III', 'Emerald II', 'Emerald I', 'Diamond IV', 'Diamond III', 'Diamond II', 'Diamond I', 'Master', 'Grandmaster', 'Challenger'],
		'dota2': ['Herald 1', 'Herald 2', 'Herald 3', 'Herald 4', 'Herald 5', 'Guardian 1', 'Guardian 2', 'Guardian 3', 'Guardian 4', 'Guardian 5', 'Crusader 1', 'Crusader 2', 'Crusader 3', 'Crusader 4', 'Crusader 5', 'Archon 1', 'Archon 2', 'Archon 3', 'Archon 4', 'Archon 5', 'Legend 1', 'Legend 2', 'Legend 3', 'Legend 4', 'Legend 5', 'Ancient 1', 'Ancient 2', 'Ancient 3', 'Ancient 4', 'Ancient 5', 'Divine 1', 'Divine 2', 'Divine 3', 'Divine 4', 'Divine 5', 'Immortal'],
		'mobilelegends': ['Warrior III', 'Warrior II', 'Warrior I', 'Elite III', 'Elite II', 'Elite I', 'Master IV', 'Master III', 'Master II', 'Master I', 'Grandmaster V', 'Grandmaster IV', 'Grandmaster III', 'Grandmaster II', 'Grandmaster I', 'Epic V', 'Epic IV', 'Epic III', 'Epic II', 'Epic I', 'Legend V', 'Legend IV', 'Legend III', 'Legend II', 'Legend I', 'Mythic', 'Mythical Honor', 'Mythical Glory', 'Mythical Immortal'],
		'smite': ['Bronze V', 'Bronze IV', 'Bronze III', 'Bronze II', 'Bronze I', 'Silver V', 'Silver IV', 'Silver III', 'Silver II', 'Silver I', 'Gold V', 'Gold IV', 'Gold III', 'Gold II', 'Gold I', 'Platinum V', 'Platinum IV', 'Platinum III', 'Platinum II', 'Platinum I', 'Diamond V', 'Diamond IV', 'Diamond III', 'Diamond II', 'Diamond I', 'Master', 'Grandmaster'],
		'paladins': ['Bronze V', 'Bronze IV', 'Bronze III', 'Bronze II', 'Bronze I', 'Silver V', 'Silver IV', 'Silver III', 'Silver II', 'Silver I', 'Gold V', 'Gold IV', 'Gold III', 'Gold II', 'Gold I', 'Platinum V', 'Platinum IV', 'Platinum III', 'Platinum II', 'Platinum I', 'Diamond V', 'Diamond IV', 'Diamond III', 'Diamond II', 'Diamond I', 'Master', 'Grandmaster'],

		// Hero shooter / arcade
		'marvelrivals': ['Bronze III', 'Bronze II', 'Bronze I', 'Silver III', 'Silver II', 'Silver I', 'Gold III', 'Gold II', 'Gold I', 'Platinum III', 'Platinum II', 'Platinum I', 'Diamond III', 'Diamond II', 'Diamond I', 'Grandmaster III', 'Grandmaster II', 'Grandmaster I', 'Celestial III', 'Celestial II', 'Celestial I', 'Eternity', 'One Above All'],
		'rocketleague': ['Bronze I', 'Bronze II', 'Bronze III', 'Silver I', 'Silver II', 'Silver III', 'Gold I', 'Gold II', 'Gold III', 'Platinum I', 'Platinum II', 'Platinum III', 'Diamond I', 'Diamond II', 'Diamond III', 'Champion I', 'Champion II', 'Champion III', 'Grand Champion I', 'Grand Champion II', 'Grand Champion III', 'Supersonic Legend'],
		'brawlstars': ['Bronze I', 'Bronze II', 'Bronze III', 'Silver I', 'Silver II', 'Silver III', 'Gold I', 'Gold II', 'Gold III', 'Diamond I', 'Diamond II', 'Diamond III', 'Mythic I', 'Mythic II', 'Mythic III', 'Legendary I', 'Legendary II', 'Legendary III', 'Masters'],

		// Card / Strategy
		'hearthstone': ['Bronze 10', 'Bronze 5', 'Silver 10', 'Silver 5', 'Gold 10', 'Gold 5', 'Platinum 10', 'Platinum 5', 'Diamond 10', 'Diamond 5', 'Legend'],
		'mtgarena': ['Bronze 4', 'Bronze 3', 'Bronze 2', 'Bronze 1', 'Silver 4', 'Silver 3', 'Silver 2', 'Silver 1', 'Gold 4', 'Gold 3', 'Gold 2', 'Gold 1', 'Platinum 4', 'Platinum 3', 'Platinum 2', 'Platinum 1', 'Diamond 4', 'Diamond 3', 'Diamond 2', 'Diamond 1', 'Mythic'],
		'starcraft2': ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'Grandmaster'],
		'clashroyale': ['Tour 1: Goblin Stadium', 'Tour 2: P.E.K.K.A Playhouse', 'Tour 3: Royal Arena', 'Tour 4: Frozen Peak', 'Tour 5: Spell Valley', 'Tour 6: Builder Workshop', 'Tour 7: Champion'],

		// Sports
		'fifa': ['Division 10', 'Division 9', 'Division 8', 'Division 7', 'Division 6', 'Division 5', 'Division 4', 'Division 3', 'Division 2', 'Division 1', 'Elite Division'],

		// Fighting
		'streetfighter6': ['Rookie 1', 'Rookie 2', 'Rookie 3', 'Iron 1', 'Iron 2', 'Iron 3', 'Bronze 1', 'Bronze 2', 'Bronze 3', 'Silver 1', 'Silver 2', 'Silver 3', 'Gold 1', 'Gold 2', 'Gold 3', 'Platinum 1', 'Platinum 2', 'Platinum 3', 'Diamond 1', 'Diamond 2', 'Diamond 3', 'Master'],
		'tekken8': ['Beginner', 'Mentor', 'Expert', 'Cavalry', 'Vanguard', 'Warrior', 'Strategist', 'Fighter', 'Combatant', 'Brawler', 'Vanquisher', 'Destroyer', 'Eliminator', 'Garyu', 'Shinryu', 'Tenryu', 'Mighty Ruler', 'Flame Ruler', 'Battle Ruler', 'Fujin', 'Raijin', 'Kishin', 'Bushin', 'Tekken King', 'Tekken Emperor', 'Tekken God'],

		// Survival / Extraction
		'tarkov': ['Beginner (Lvl 1-15)', 'Casual (Lvl 16-25)', 'Veteran (Lvl 26-40)', 'Hardline (Lvl 41-60)', 'Battle-hardened (Lvl 61-79)', 'Kappa (Lvl 80+)'],

		// Newer / niche
		'arcraiders': ['Recruit', 'Operator', 'Specialist', 'Veteran', 'Elite Raider', 'Legendary Raider'],

		// Casual / no official rank — fallback so the popup still works
		'minecraft': ['Newcomer', 'Hobbyist', 'Builder', 'Engineer', 'Architect', 'Master Builder'],
	};
})();
