/* --- UTILITY FUNCTIONS --- */
function withFallback(value, fallback) {
	return value || fallback;
}

/* --- NAVIGATION FUNCTIONS --- */
function goHome()              { window.location.href = '/'; }
function goGame(id)            { window.location.href = `/game/${id}`; }
function goLogin()             { window.location.href = '/login'; }
function goRegister()          { window.location.href = '/register'; }
function goProfile(username)   { window.location.href = `/profile/${username}`; }

/* --- API FUNCTIONS --- */
async function fetchProfile(username) {
	const response = await fetch(`/api/players/${username}`);
	if (!response.ok) {
		throw new Error('Network response was not ok');
	}
	return response.json();
}

async function addFriend(username) {
	// TODO: implement when sessions/friend list backend exists
	alert('Feature not implemented yet');
}

/* --- NAVIGATION SCROLLING --- */
function scrollNavGames(direction) {
	const track = document.getElementById('nav-games-track');
	if (!track) {
		return;
	}
	const distance = Math.max(track.clientWidth * 0.8, 220);
	track.scrollBy({ left: distance * direction, behavior: 'smooth' });
}

/* --- RANK CATALOG (per game) --- */
const RANKS_BY_GAME = {
	cs2:           ['Silver', 'Gold Nova', 'Master Guardian', 'Legendary Eagle', 'Supreme', 'Global Elite'],
	counterstrike: ['Silver', 'Gold Nova', 'Master Guardian', 'Legendary Eagle', 'Supreme', 'Global Elite'],
	lol:           ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Emerald', 'Diamond', 'Master', 'Grandmaster', 'Challenger'],
	valorant:      ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ascendant', 'Immortal', 'Radiant'],
	arcraiders:    ['Rookie', 'Raider', 'Veteran', 'Elite', 'Legend'],
	mobilelegends: ['Warrior', 'Elite', 'Master', 'Grandmaster', 'Epic', 'Legend', 'Mythic', 'Mythical Glory'],
	apex:          ['Rookie', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'Apex Predator'],
	minecraft:     ['Casual', 'Builder', 'Survivalist', 'Veteran', 'Master Crafter'],
};

/*
	Build rank filter buttons for the current game. Falls back to "no ranks"
	state if the game has no rank tiers defined.
*/
function populateRankFilter(gameSlug) {
	const container = document.getElementById('filter-rank-options');
	if (!container) {
		return;
	}
	const ranks = RANKS_BY_GAME[gameSlug] || [];

	if (ranks.length === 0) {
		container.innerHTML = '<span class="filter-empty">No rank tiers for this game</span>';
		return;
	}

	container.innerHTML = '';
	ranks.forEach(rank => {
		const btn = document.createElement('button');
		btn.type = 'button';
		btn.className = 'filter-btn';
		btn.dataset.filterGroup = 'rank';
		btn.dataset.filterValue = rank;
		btn.textContent = rank;
		container.appendChild(btn);
	});
}

/* --- PROFILE CARD LOGIC --- */
function createInfoRow(infobox, label, value) {
	const row = document.createElement('div');
	row.className = 'info-row';
	row.innerHTML = `<span class="lbl">${label}</span><span class="val">${value}</span>`;
	infobox.appendChild(row);
}

function createGameIcon(gamePanel, game) {
	const link = document.createElement('a');
	link.className = 'game-tile';
	link.href = `/game/${game.slug}`;

	const img = document.createElement('img');
	img.src = game.image_url;
	img.alt = game.name;
	link.appendChild(img);

	gamePanel.appendChild(link);
}

function getProfileCardElements() {
	const card = document.getElementById('profile-card');
	if (!card) {
		return null;
	}

	const profilePanel  = card.getElementsByClassName('profile-panel')[0];
	const loading       = card.querySelector('#profile-loading');
	const infoBox       = card.getElementsByClassName('info-box')[0];
	const gamePanel     = card.getElementsByClassName('games-panel')[0];
	const avatarImage   = profilePanel.querySelector('.profile-avatar img');
	const bioText       = infoBox.querySelector('.bio-text');
	const profileButtons = profilePanel.querySelector('.profile-buttons');

	return { card, loading, infoBox, gamePanel, avatarImage, bioText, profileButtons };
}

function showProfileCard(card, loading) {
	card.classList.remove('hidden');
	card.setAttribute('aria-hidden', 'false');
	document.body.classList.add('modal-open');
	loading.style.display = 'block';
}

function hideProfileCard(card) {
	card.classList.add('hidden');
	card.setAttribute('aria-hidden', 'true');
	document.body.classList.remove('modal-open');
}

function resetProfileCard(elements) {
	elements.infoBox.querySelectorAll('.info-row').forEach(row => row.remove());
	elements.gamePanel.querySelectorAll('.game-tile').forEach(tile => tile.remove());
	elements.bioText.textContent = '';
	elements.avatarImage.src = '/static/img/profiles/default.jpg';
	elements.avatarImage.alt = 'Loading...';
	elements.loading.textContent = 'Loading profile…';
	elements.loading.style.display = 'block';
	elements.profileButtons.querySelectorAll('.action-button').forEach(btn => btn.remove());
}

function addActionButton(element, label, onClick) {
	const button = document.createElement('button');
	button.className = 'action-button';
	button.textContent = label;
	button.addEventListener('click', onClick);
	element.appendChild(button);
}

function renderProfileData(elements, data) {
	setProfileAvatar(elements, data);
	renderProfileInfoRows(elements, data);
	elements.bioText.textContent = withFallback(data.bio, 'No bio available.');
	renderProfileGames(elements.gamePanel, data.games);
	addActionButton(elements.profileButtons, 'Add as friend', () => addFriend(data.username));
	addActionButton(elements.profileButtons, 'Open full profile', () => goProfile(data.username));
	elements.loading.style.display = 'none';
}

function renderProfileError(elements, username, error) {
	elements.loading.textContent = 'Could not load profile. Try again.';
	createInfoRow(elements.infoBox, 'Username', username);
	elements.bioText.textContent = 'Something went wrong while loading the profile.';
	console.error('Error fetching player profile:', error);
}

function setProfileAvatar(elements, data) {
	elements.avatarImage.src = withFallback(data.avatar_url, '/static/img/profiles/default.jpg');
	elements.avatarImage.alt = withFallback(data.username, 'Player avatar');
}

function renderProfileInfoRows(elements, data) {
	const rows = [
		['Username',   withFallback(data.username, 'Unknown')],
		['Tag',        withFallback(data.user_tag, 'N/A')],
		['Rank',       withFallback(data.rank, 'N/A')],
		['Age Range',  withFallback(data.age_range, 'N/A')],
		['Platform',   withFallback(data.platform, 'N/A')],
		['Playtime',   withFallback(data.playtime, 'N/A')],
		['Languages',  withFallback(data.languages, 'N/A')],
	];
	rows.forEach(([label, value]) => createInfoRow(elements.infoBox, label, value));
}

function renderProfileGames(gamePanel, games) {
	if (!Array.isArray(games)) {
		return;
	}
	games.forEach(game => createGameIcon(gamePanel, game));
}

function openProfile(username) {
	const elements = getProfileCardElements();
	if (!elements) {
		return;
	}
	showProfileCard(elements.card, elements.loading);
	resetProfileCard(elements);

	fetch(`/api/players/${username}`)
		.then(response => response.json())
		.then(data => renderProfileData(elements, data))
		.catch(error => renderProfileError(elements, username, error));
}

function closeProfile() {
	const elements = getProfileCardElements();
	if (!elements) {
		return;
	}
	hideProfileCard(elements.card);
}

/* --- EVENT LISTENERS --- */
document.addEventListener('keydown', event => {
	if (event.key === 'Escape') {
		closeProfile();
	}
});

document.addEventListener('click', event => {
	const elements = getProfileCardElements();
	if (!elements || elements.card.classList.contains('hidden')) {
		return;
	}
	if (event.target === elements.card) {
		closeProfile();
	}
});

function debounce(callback, waitMs) {
	let timeoutId;
	return (...args) => {
		clearTimeout(timeoutId);
		timeoutId = setTimeout(() => callback(...args), waitMs);
	};
}

/* --- AGE RANGE SLIDER (FIXED) --- */
/*
	Two key fixes vs iter 1:
	  1. CLAMP THE ACTIVE THUMB instead of pushing the other one.
	     If user drags the low past high, low is clamped DOWN to high.
	     If user drags the high below low, high is clamped UP to low.
	     This prevents the "gliching" where both thumbs jumped together.
	  2. DYNAMIC z-index — whichever thumb is being grabbed is on top,
	     so it's always reachable even when both are at the same position.
*/
function setupAgeRangeFilter(onChange) {
	const container = document.querySelector('[data-age-range-filter]');
	if (!container) {
		return null;
	}

	const labels = Array.from(container.querySelectorAll('.age-range-marks span'))
		.map(mark => mark.textContent?.trim() || '')
		.filter(Boolean);
	if (labels.length === 0) {
		return null;
	}

	const lowInput  = container.querySelector('[data-age-input="low"]');
	const highInput = container.querySelector('[data-age-input="high"]');
	const lowLabel  = container.querySelector('[data-age-low]');
	const highLabel = container.querySelector('[data-age-high]');
	const progress  = container.querySelector('[data-age-progress]');

	if (!lowInput || !highInput || !lowLabel || !highLabel || !progress) {
		return null;
	}

	const maxIndex = labels.length - 1;

	function clampInputs(changed) {
		let low  = Number(lowInput.value);
		let high = Number(highInput.value);

		// FIX: clamp the ACTIVE input only — never push the other one.
		if (low > high) {
			if (changed === 'low') {
				low = high;
				lowInput.value = String(low);
			} else {
				high = low;
				highInput.value = String(high);
			}
		}

		const lowPercent  = (low  / maxIndex) * 100;
		const highPercent = (high / maxIndex) * 100;

		lowLabel.textContent  = labels[low];
		highLabel.textContent = labels[high];
		progress.style.left   = `${lowPercent}%`;
		progress.style.right  = `${100 - highPercent}%`;

		if (typeof onChange === 'function' && changed !== 'init') {
			onChange();
		}
	}

	function getAgeBounds() {
		const lowIndex   = Number(lowInput.value);
		const highIndex  = Number(highInput.value);
		const lowText    = labels[lowIndex]  || labels[0];
		const highText   = labels[highIndex] || labels[maxIndex];

		const ageLo            = Number.parseInt(lowText, 10);
		const isUnboundedHigh  = highIndex === maxIndex && highText.includes('+');
		const parsedHigh       = Number.parseInt(highText, 10);

		return {
			ageLo: Number.isNaN(ageLo) ? null : ageLo,
			ageHi: isUnboundedHigh || Number.isNaN(parsedHigh) ? null : parsedHigh,
		};
	}

	// FIX: dynamic z-index so the grabbed thumb is always on top.
	function setActive(input) {
		lowInput.classList.remove('active');
		highInput.classList.remove('active');
		input.classList.add('active');
	}
	function clearActive() {
		lowInput.classList.remove('active');
		highInput.classList.remove('active');
	}

	[lowInput, highInput].forEach(input => {
		input.addEventListener('pointerdown',   () => setActive(input));
		input.addEventListener('focus',         () => setActive(input));
		input.addEventListener('pointerup',     clearActive);
		input.addEventListener('pointercancel', clearActive);
		input.addEventListener('blur',          clearActive);
	});

	lowInput.addEventListener('input',  () => clampInputs('low'));
	highInput.addEventListener('input', () => clampInputs('high'));
	clampInputs('init');

	return { getAgeBounds };
}

/* --- PLAYER CARDS --- */
function createPlayerCard(player) {
	const card = document.createElement('div');
	card.className = 'player-card';
	card.tabIndex = 0;
	card.setAttribute('role', 'button');
	card.addEventListener('click', () => openProfile(player.username));
	card.addEventListener('keydown', event => {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			openProfile(player.username);
		}
	});

	const top = document.createElement('div');
	top.className = 'p-top';

	const avatarWrap = document.createElement('div');
	avatarWrap.className = 'p-avatar-wrap';

	const avatar = document.createElement('img');
	avatar.className = 'p-avatar';
	avatar.src = withFallback(player.avatar_url, '/static/img/profiles/default.jpg');
	avatar.alt = `${withFallback(player.username, 'Player')} avatar`;

	const status = document.createElement('span');
	status.className = `p-status ${withFallback(player.status, 'online')}`;

	avatarWrap.appendChild(avatar);
	avatarWrap.appendChild(status);

	const meta = document.createElement('div');
	meta.className = 'p-meta';

	const name = document.createElement('div');
	name.className = 'p-name';
	name.textContent = withFallback(player.username, 'Unknown');

	const tag = document.createElement('div');
	tag.className = 'p-tag';
	tag.textContent = withFallback(player.user_tag, '#unknown');

	meta.appendChild(name);
	meta.appendChild(tag);

	if (player.rank) {
		const rank = document.createElement('div');
		rank.className = 'p-rank';
		rank.textContent = player.rank;
		meta.appendChild(rank);
	}

	top.appendChild(avatarWrap);
	top.appendChild(meta);
	card.appendChild(top);

	return card;
}

function renderPlayersGrid(gridElement, players) {
	gridElement.innerHTML = '';

	if (!Array.isArray(players) || players.length === 0) {
		const empty = document.createElement('p');
		empty.textContent = 'No players found — try adjusting your filters.';
		gridElement.appendChild(empty);
		return;
	}

	players.forEach(player => {
		gridElement.appendChild(createPlayerCard(player));
	});
}

async function fetchFilteredPlayers(gameSlug, filters) {
	const params = new URLSearchParams();

	if (filters.ageLo !== null)  { params.set('age_lo', String(filters.ageLo)); }
	if (filters.ageHi !== null)  { params.set('age_hi', String(filters.ageHi)); }
	if (filters.playtime)        { params.set('playtime', filters.playtime); }
	if (filters.platform)        { params.set('platform', filters.platform); }
	if (filters.language)        { params.set('language', filters.language); }
	if (filters.rank)            { params.set('rank',     filters.rank); }

	const response = await fetch(`/api/search/games/${encodeURIComponent(gameSlug)}/players?${params.toString()}`);
	if (!response.ok) {
		throw new Error(`Search request failed with status ${response.status}`);
	}

	return response.json();
}

function setupGameFiltersSearch() {
	const gamePage    = document.getElementById('page-spel');
	const playersGrid = document.querySelector('#page-spel .players-grid');
	const gameSlug    = gamePage?.dataset.gameSlug;

	if (!gamePage || !playersGrid || !gameSlug) {
		setupAgeRangeFilter();
		return;
	}

	// Populate rank filter for this game
	populateRankFilter(gameSlug);

	let latestRequestId = 0;

	function getSelectedFilterValue(group) {
		const selected = document.querySelector(`.filter-btn.on[data-filter-group="${group}"]`);
		return selected?.dataset.filterValue || '';
	}

	const triggerSearch = debounce(async () => {
		const requestId = ++latestRequestId;
		playersGrid.innerHTML = '<p>Searching players…</p>';

		const ageBounds = ageFilterController?.getAgeBounds() ?? { ageLo: null, ageHi: null };
		const languageSelect = document.getElementById('filter-language');

		const filters = {
			ageLo:    ageBounds.ageLo,
			ageHi:    ageBounds.ageHi,
			playtime: getSelectedFilterValue('playtime'),
			platform: getSelectedFilterValue('platform'),
			language: languageSelect?.value || '',
			rank:     getSelectedFilterValue('rank'),
		};

		try {
			const payload = await fetchFilteredPlayers(gameSlug, filters);
			if (requestId !== latestRequestId) {
				return;
			}
			renderPlayersGrid(playersGrid, payload.results);
		} catch (error) {
			if (requestId !== latestRequestId) {
				return;
			}
			playersGrid.innerHTML = '<p>Could not load players right now.</p>';
			console.error('Player search failed:', error);
		}
	}, 180);

	const ageFilterController = setupAgeRangeFilter(triggerSearch);

	// EVENT DELEGATION — handles both static buttons (playtime/platform)
	// and dynamically-added rank buttons.
	document.addEventListener('click', event => {
		const button = event.target.closest('.filter-btn[data-filter-group]');
		if (!button) {
			return;
		}

		const group = button.dataset.filterGroup;
		const isOn  = button.classList.contains('on');

		document.querySelectorAll(`.filter-btn[data-filter-group="${group}"]`).forEach(groupBtn => {
			groupBtn.classList.remove('on');
		});

		if (!isOn) {
			button.classList.add('on');
		}

		triggerSearch();
	});

	// Language dropdown
	const languageSelect = document.getElementById('filter-language');
	if (languageSelect) {
		languageSelect.addEventListener('change', triggerSearch);
	}

	// Reset button — clears all filter buttons, language, and age range.
	const resetBtn = document.getElementById('filter-reset');
	if (resetBtn) {
		resetBtn.addEventListener('click', () => {
			document.querySelectorAll('.filter-btn.on').forEach(b => b.classList.remove('on'));
			if (languageSelect) {
				languageSelect.value = '';
			}
			const lowInput  = document.querySelector('[data-age-input="low"]');
			const highInput = document.querySelector('[data-age-input="high"]');
			if (lowInput && highInput) {
				lowInput.value  = lowInput.min;
				highInput.value = highInput.max;
				lowInput.dispatchEvent(new Event('input'));
				highInput.dispatchEvent(new Event('input'));
			}
			triggerSearch();
		});
	}
}

setupGameFiltersSearch();