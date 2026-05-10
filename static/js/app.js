/* --- UTILITY FUNCTIONS --- */
function withFallback(value, fallback) {
	return value || fallback;
}

/*
	Utility function to debounce another function, preventing it from being called too frequently.
	Useful for optimizing search input or filter changes to avoid excessive API calls.
*/
function debounce(callback, waitMs) {
	let timeoutId;
	return (...args) => {
		clearTimeout(timeoutId);
		timeoutId = setTimeout(() => callback(...args), waitMs);
	};
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

/* --- FAVORITE GAMES (localStorage-backed for now) --- */
/*
	Favorites are persisted client-side under "gamecrew:favorites".
	When the backend gains a /api/me/favorites endpoint, swap the
	read/write helpers below to fetch/PUT calls — the rest of the
	UI logic stays the same.
*/
const FAV_STORAGE_KEY = 'gamecrew:favorites';

function readFavorites() {
	try {
		const raw = localStorage.getItem(FAV_STORAGE_KEY);
		const parsed = JSON.parse(raw || '[]');
		return Array.isArray(parsed) ? parsed : [];
	} catch (error) {
		return [];
	}
}

function writeFavorites(slugs) {
	try {
		localStorage.setItem(FAV_STORAGE_KEY, JSON.stringify(slugs));
	} catch (error) {
		console.warn('Could not persist favorites:', error);
	}
}

function isFavorite(slug) {
	return readFavorites().includes(slug);
}

function toggleFavorite(slug) {
	const list = readFavorites();
	const index = list.indexOf(slug);
	if (index >= 0) {
		list.splice(index, 1);
		writeFavorites(list);
		return false; // no longer a favorite
	}
	list.push(slug);
	writeFavorites(list);
	return true; // newly favorited
}

function paintFavoriteButton(button, active) {
	const icon  = button.querySelector('.fav-icon');
	const label = button.querySelector('.fav-label');

	button.classList.toggle('active', active);
	button.setAttribute('aria-pressed', active ? 'true' : 'false');

	if (icon) {
		icon.textContent = active ? '★' : '☆';
	}
	if (label) {
		label.textContent = active ? 'Remove from favorites' : 'Add to favorites';
	}
}

function setupFavoriteButton() {
	const button = document.getElementById('fav-btn');
	if (!button) {
		return;
	}
	const slug = button.dataset.favSlug;
	if (!slug) {
		return;
	}

	paintFavoriteButton(button, isFavorite(slug));

	button.addEventListener('click', () => {
		const nowActive = toggleFavorite(slug);
		paintFavoriteButton(button, nowActive);

		// short pulse so the user sees the state change
		button.classList.remove('is-pulsing');
		void button.offsetWidth; // force reflow to restart animation
		button.classList.add('is-pulsing');
	});
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

	const info = document.createElement('div');
	info.className = 'game-tile-info';

	const nameEl = document.createElement('div');
	nameEl.className = 'game-tile-name';
	nameEl.textContent = game.name || 'Unknown';
	info.appendChild(nameEl);

	const rankEl = document.createElement('div');
	if (game.rank) {
		rankEl.className = 'game-tile-rank';
		rankEl.textContent = game.rank;
	} else {
		rankEl.className = 'game-tile-rank unranked';
		rankEl.textContent = 'Unranked';
	}
	info.appendChild(rankEl);

	link.appendChild(info);
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
	// If we're on a game page (/game/{slug}), show that game's rank prominently
	const gameSlugMatch = window.location.pathname.match(/^\/game\/([^/]+)/);
	const currentGameSlug = gameSlugMatch ? gameSlugMatch[1] : null;

	if (currentGameSlug && Array.isArray(data.game_ranks)) {
		const gameRank = data.game_ranks.find(r => r.game_slug === currentGameSlug);
		if (gameRank) {
			const highlight = document.createElement('div');
			highlight.className = 'info-row info-row-highlight';
			highlight.innerHTML =
				'<span class="lbl">' + escapeHtmlText(gameRank.game_name || currentGameSlug) + ' rank</span>' +
				'<span class="val val-rank">' + escapeHtmlText(gameRank.rank_name) + '</span>';
			elements.infoBox.appendChild(highlight);
		}
	}

	const rows = [
		['Username',   withFallback(data.username, 'Unknown')],
		['Region',     withFallback(data.region ? data.region.toUpperCase() : null, 'N/A')],
		['Age',        withFallback(data.age ? data.age + ' yrs' : data.age_range, 'N/A')],
		['Platform',   withFallback(data.platform, 'N/A')],
		['Languages',  Array.isArray(data.languages) ? data.languages.join(', ') : withFallback(data.languages, 'N/A')],
	];
	rows.forEach(([label, value]) => createInfoRow(elements.infoBox, label, value));
}

function escapeHtmlText(str) {
	const div = document.createElement('div');
	div.textContent = String(str);
	return div.innerHTML;
}

function renderProfileGames(gamePanel, games) {
	if (!Array.isArray(games) || games.length === 0) {
		games = [
			{ slug: 'cs2', name: 'Counter-Strike 2', image_url: '/static/img/games/cs2.jpg', rank: 'Master Guardian II' },
			{ slug: 'valorant', name: 'Valorant', image_url: '/static/img/games/valorant.jpg', rank: 'Diamond 1' },
			{ slug: 'lol', name: 'League of Legends', image_url: '/static/img/games/lol.jpg', rank: null },
			{ slug: 'arcraiders', name: 'ARC Raiders', image_url: '/static/img/games/arcraiders.jpg', rank: 'Veteran' }
		];
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

/* --- AGE RANGE SLIDER --- */
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

		// Clamp the ACTIVE input only — never push the other one.
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
		progress.style.left   = `calc(8px + ${lowPercent / 100} * (100% - 16px))`;
		progress.style.right  = `calc(8px + ${(100 - highPercent) / 100} * (100% - 16px))`;

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
const DISCORD_SVG_PATH = 'M20.317 4.37a19.79 19.79 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.099.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.029zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z';

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

	// Top row — avatar + meta side by side
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
	meta.appendChild(name);

	// Stats row — rank · age (only show what we have)
	const hasRank = !!player.rank;
	const hasAge = !!player.age;

	if (hasRank || hasAge) {
		const stats = document.createElement('div');
		stats.className = 'p-stats';

		if (hasRank) {
			const rank = document.createElement('span');
			rank.className = 'p-rank';
			rank.textContent = player.rank;
			stats.appendChild(rank);
		}

		if (hasRank && hasAge) {
			const dot = document.createElement('span');
			dot.className = 'p-stat-divider';
			dot.textContent = '·';
			stats.appendChild(dot);
		}

		if (hasAge) {
			const age = document.createElement('span');
			age.className = 'p-age';
			age.textContent = player.age + ' yrs';
			stats.appendChild(age);
		}

		meta.appendChild(stats);
	}

	top.appendChild(avatarWrap);
	top.appendChild(meta);

	// Action buttons row
	const actions = document.createElement('div');
	actions.className = 'p-actions';
	actions.addEventListener('click', e => e.stopPropagation());
	actions.addEventListener('keydown', e => e.stopPropagation());

	const discordBtn = document.createElement('button');
	discordBtn.type = 'button';
	discordBtn.className = 'p-action-btn p-action-btn-discord';
	discordBtn.dataset.discord = player.discord || '';
	discordBtn.dataset.username = player.username || '';
	discordBtn.setAttribute('aria-label', `Show Discord for ${player.username || 'player'}`);
	discordBtn.innerHTML =
		`<svg class="p-action-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="${DISCORD_SVG_PATH}"/></svg>` +
		`<span class="p-action-label">Discord</span>`;
	discordBtn.addEventListener('click', e => showDiscord(e, discordBtn));

	const platformBtn = document.createElement('button');
	platformBtn.type = 'button';
	platformBtn.className = 'p-action-btn p-action-btn-platform';
	platformBtn.dataset.platform = player.platform || '';
	platformBtn.dataset.username = player.username || '';
	platformBtn.setAttribute('aria-label', `Show platform for ${player.username || 'player'}`);
	platformBtn.innerHTML =
		`<svg class="p-action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">` +
			`<rect x="2" y="4" width="20" height="13" rx="2" ry="2"/>` +
			`<line x1="8" y1="21" x2="16" y2="21"/>` +
			`<line x1="12" y1="17" x2="12" y2="21"/>` +
		`</svg>` +
		`<span class="p-action-label">Platform</span>`;
	platformBtn.addEventListener('click', e => showPlatform(e, platformBtn));

	actions.appendChild(discordBtn);
	actions.appendChild(platformBtn);

	card.appendChild(top);
	card.appendChild(actions);

	return card;
}

/* ── Player card actions ── */

function showDiscord(event, btn) {
	event.stopPropagation();
	const tag = btn.dataset.discord;
	const user = btn.dataset.username || 'this player';

	if (!tag) {
		showPopup({
			title: user + "'s Discord",
			body: "This player hasn't linked a Discord account.",
			variant: 'muted',
		});
		return;
	}

	showPopup({
		title: user + "'s Discord",
		body: tag,
		variant: 'discord',
		copyable: true,
	});
}

function showPlatform(event, btn) {
	event.stopPropagation();
	const platform = btn.dataset.platform;
	const user = btn.dataset.username || 'this player';

	if (!platform) {
		showPopup({
			title: user + "'s platform",
			body: "This player hasn't set a platform yet.",
			variant: 'muted',
		});
		return;
	}

	showPopup({
		title: user + ' plays on',
		body: platform,
		variant: 'platform',
		platform: platform,
	});
}

/* ── Rank picker popup — opens from rank button on game page ── */
function openRankPopup(gameSlug, currentRank) {
	const ranks = (window.GameCrewRanks && window.GameCrewRanks[gameSlug]) || null;

	if (!ranks || !ranks.length) {
		showPopup({
			title: 'No ranks available',
			body: "This game doesn't have a ranking system configured yet.",
			variant: 'muted',
		});
		return;
	}

	closePopup();

	const overlay = document.createElement('div');
	overlay.className = 'info-popup-overlay';
	overlay.id = 'info-popup-overlay';
	overlay.setAttribute('role', 'dialog');
	overlay.setAttribute('aria-modal', 'true');

	const box = document.createElement('div');
	box.className = 'info-popup info-popup-rank';

	// Close button
	const closeBtn = document.createElement('button');
	closeBtn.type = 'button';
	closeBtn.className = 'info-popup-close';
	closeBtn.setAttribute('aria-label', 'Close popup');
	closeBtn.addEventListener('click', closePopup);

	// Header
	const title = document.createElement('div');
	title.className = 'info-popup-title';
	title.textContent = currentRank ? 'Update your rank' : 'Set your rank';

	const note = document.createElement('div');
	note.className = 'info-popup-note';
	note.innerHTML = currentRank
		? 'Current: <strong>' + escapeHtml(currentRank) + '</strong><br>You can change your rank once every 24 hours.'
		: 'Your rank locks for 24 hours after each change. Pick carefully.';

	box.appendChild(closeBtn);
	box.appendChild(title);
	box.appendChild(note);

	// Form with select + submit
	const form = document.createElement('form');
	form.method = 'post';
	form.action = '/game/' + encodeURIComponent(gameSlug) + '/rank';
	form.className = 'rank-popup-form';

	const selectWrap = document.createElement('div');
	selectWrap.className = 'select-wrap';
	const select = document.createElement('select');
	select.name = 'rank_name';
	select.required = true;

	const placeholder = document.createElement('option');
	placeholder.value = '';
	placeholder.textContent = 'Choose your rank…';
	placeholder.disabled = true;
	if (!currentRank) placeholder.selected = true;
	select.appendChild(placeholder);

	ranks.forEach(rank => {
		const opt = document.createElement('option');
		opt.value = rank;
		opt.textContent = rank;
		if (rank === currentRank) opt.selected = true;
		select.appendChild(opt);
	});

	selectWrap.appendChild(select);
	form.appendChild(selectWrap);

	const submitBtn = document.createElement('button');
	submitBtn.type = 'submit';
	submitBtn.className = 'btn-primary rank-popup-submit';
	submitBtn.textContent = currentRank ? 'Update rank' : 'Save rank';
	form.appendChild(submitBtn);

	box.appendChild(form);

	overlay.appendChild(box);
	document.body.appendChild(overlay);
	document.body.classList.add('modal-open');

	overlay.addEventListener('click', e => {
		if (e.target === overlay) closePopup();
	});

	// Focus the select for keyboard users
	setTimeout(() => select.focus(), 50);
}

function escapeHtml(str) {
	const div = document.createElement('div');
	div.textContent = String(str);
	return div.innerHTML;
}

/* ── Reusable info popup ── */

const PLATFORM_ICONS = {
	pc:          { label: 'PC',          symbol: '🖥' },
	playstation: { label: 'PlayStation', symbol: 'PS' },
	ps:          { label: 'PlayStation', symbol: 'PS' },
	ps4:         { label: 'PlayStation 4', symbol: 'PS' },
	ps5:         { label: 'PlayStation 5', symbol: 'PS' },
	xbox:        { label: 'Xbox',        symbol: 'XB' },
	switch:      { label: 'Nintendo Switch', symbol: 'SW' },
	mobile:      { label: 'Mobile',      symbol: '📱' },
	ios:         { label: 'iOS',         symbol: 'iOS' },
	android:     { label: 'Android',     symbol: 'AND' },
};

function getPlatformVisual(platform) {
	const key = platform.toLowerCase().replace(/[^a-z0-9]/g, '');
	return PLATFORM_ICONS[key] || { label: platform, symbol: platform.slice(0, 2).toUpperCase() };
}

function showPopup(opts) {
	closePopup();

	const overlay = document.createElement('div');
	overlay.className = 'info-popup-overlay';
	overlay.id = 'info-popup-overlay';
	overlay.setAttribute('role', 'dialog');
	overlay.setAttribute('aria-modal', 'true');

	const box = document.createElement('div');
	box.className = 'info-popup info-popup-' + (opts.variant || 'default');

	// Close button
	const closeBtn = document.createElement('button');
	closeBtn.type = 'button';
	closeBtn.className = 'info-popup-close';
	closeBtn.setAttribute('aria-label', 'Close popup');
	closeBtn.addEventListener('click', closePopup);

	// Big symbol on top (only for platform / discord variants)
	if (opts.variant === 'platform' && opts.platform) {
		const visual = getPlatformVisual(opts.platform);
		const icon = document.createElement('div');
		icon.className = 'info-popup-symbol';
		icon.textContent = visual.symbol;
		box.appendChild(icon);
	} else if (opts.variant === 'discord') {
		const icon = document.createElement('div');
		icon.className = 'info-popup-symbol info-popup-symbol-discord';
		icon.innerHTML =
			`<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">` +
			`<path d="${DISCORD_SVG_PATH}"/></svg>`;
		box.appendChild(icon);
	}

	// Title
	const title = document.createElement('div');
	title.className = 'info-popup-title';
	title.textContent = opts.title || '';

	// Body
	const body = document.createElement('div');
	body.className = 'info-popup-body';
	body.textContent = opts.body || '';

	box.appendChild(closeBtn);
	box.appendChild(title);
	box.appendChild(body);

	// Optional copy button (Discord variant)
	if (opts.copyable && opts.body) {
		const copyBtn = document.createElement('button');
		copyBtn.type = 'button';
		copyBtn.className = 'info-popup-copy';
		copyBtn.textContent = 'Copy tag';
		copyBtn.addEventListener('click', () => {
			const text = opts.body;
			const done = () => {
				copyBtn.textContent = 'Copied!';
				copyBtn.classList.add('is-copied');
				setTimeout(() => {
					copyBtn.textContent = 'Copy tag';
					copyBtn.classList.remove('is-copied');
				}, 1400);
			};
			if (navigator.clipboard && navigator.clipboard.writeText) {
				navigator.clipboard.writeText(text).then(done, done);
			} else {
				const ta = document.createElement('textarea');
				ta.value = text;
				ta.style.position = 'fixed';
				ta.style.left = '-9999px';
				document.body.appendChild(ta);
				ta.select();
				try { document.execCommand('copy'); } catch (e) { /* ignore */ }
				document.body.removeChild(ta);
				done();
			}
		});
		box.appendChild(copyBtn);
	}

	overlay.appendChild(box);
	document.body.appendChild(overlay);
	document.body.classList.add('modal-open');

	overlay.addEventListener('click', e => {
		if (e.target === overlay) closePopup();
	});
}

function closePopup() {
	const existing = document.getElementById('info-popup-overlay');
	if (existing) {
		existing.remove();
		// Don't unset modal-open if profile modal is still open
		const profileCard = document.getElementById('profile-card');
		if (!profileCard || profileCard.classList.contains('hidden')) {
			document.body.classList.remove('modal-open');
		}
	}
}

// Esc closes popup too
document.addEventListener('keydown', event => {
	if (event.key === 'Escape') closePopup();
});

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
	if (Array.isArray(filters.ranks)) { filters.ranks.forEach(r => params.append('rank', r)); }

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

	populateRankFilter(gameSlug);

	let latestRequestId = 0;

	function getSelectedFilterValue(group) {
		const selected = document.querySelector(`.filter-btn.on[data-filter-group="${group}"]`);
		return selected?.dataset.filterValue || '';
	}

	function getSelectedFilterValues(group) {
		return Array.from(document.querySelectorAll(`.filter-btn.on[data-filter-group="${group}"]`))
			.map(btn => btn.dataset.filterValue);
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
			ranks:    getSelectedFilterValues('rank'),
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

	document.addEventListener('click', event => {
		const button = event.target.closest('.filter-btn[data-filter-group]');
		if (!button) {
			return;
		}

		const group = button.dataset.filterGroup;
		const isOn  = button.classList.contains('on');

		// Multi-select for rank, single-select for everything else
		if (group === 'rank') {
			button.classList.toggle('on');
		} else {
			document.querySelectorAll(`.filter-btn[data-filter-group="${group}"]`).forEach(groupBtn => {
				groupBtn.classList.remove('on');
			});
			if (!isOn) {
				button.classList.add('on');
			}
		}

		triggerSearch();
	});

	const languageSelect = document.getElementById('filter-language');
	if (languageSelect) {
		languageSelect.addEventListener('change', triggerSearch);
	}

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
setupFavoriteButton();