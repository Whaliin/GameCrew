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
	const response = await fetch(`/api/players/${encodeURIComponent(username)}`);
	if (!response.ok) {
		throw new Error(`Profile request failed with status ${response.status}`);
	}
	return response.json();
}

async function addFriend(username) {
	const response = await fetch(`/api/players/${encodeURIComponent(username)}/friend`, {
		method: 'POST',
	});
	if (!response.ok && response.status !== 204) {
		throw new Error(`Friend request failed with status ${response.status}`);
	}
}

async function removeFriend(username) {
	const response = await fetch(`/api/players/${encodeURIComponent(username)}/friend`, {
		method: 'DELETE',
	});
	if (!response.ok && response.status !== 204) {
		throw new Error(`Remove friend failed with status ${response.status}`);
	}
}

async function respondToFriendRequest(username, accept) {
	const url = `/api/players/${encodeURIComponent(username)}/friend?accept=${accept ? 'true' : 'false'}`;
	const response = await fetch(url, {
		method: 'PATCH',
	});
	if (!response.ok && response.status !== 204) {
		throw new Error(`Friend request action failed with status ${response.status}`);
	}
}

async function deleteAccount() {
	const response = await fetch('/delete-account', {
		method: 'DELETE',
	});
	if (!response.ok && response.status !== 302) {
		throw new Error(`Delete account failed with status ${response.status}`);
	}
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

/* --- FAVORITE GAMES --- */
async function setFavoriteState(slug, active) {
	const response = await fetch(`/api/games/${encodeURIComponent(slug)}/favorite`, {
		method: active ? 'PUT' : 'DELETE',
	});
	if (!response.ok && response.status !== 204) {
		throw new Error(`Favorite update failed with status ${response.status}`);
	}
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
	// Support two explicit server-rendered buttons: add and remove.
	const addBtn = document.getElementById('fav-add-btn');
	const removeBtn = document.getElementById('fav-remove-btn');

	if (!addBtn && !removeBtn) return;

	const slug = (addBtn || removeBtn).dataset.favSlug;
	if (!slug) return;

	async function handleToggle(isAdd) {
		try {
			await setFavoriteState(slug, isAdd);
			if (isAdd) {
				if (addBtn) addBtn.hidden = true;
				if (removeBtn) removeBtn.hidden = false;
			} else {
				if (addBtn) addBtn.hidden = false;
				if (removeBtn) removeBtn.hidden = true;
			}
		} catch (error) {
			console.error('Favorite toggle failed:', error);
			alert('TODO: favorite toggling needs the /api/games favorite endpoints wired and available.');
		}
	}

	if (addBtn) {
		addBtn.addEventListener('click', event => { event.preventDefault(); handleToggle(true); });
	}
	if (removeBtn) {
		removeBtn.addEventListener('click', event => { event.preventDefault(); handleToggle(false); });
	}
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
	const rows = [
		['Username',   withFallback(data.username, 'Unknown')],
		['Region',     withFallback(data.region ? data.region.toUpperCase() : null, 'N/A')],
		['Age',        withFallback(data.age ? data.age + ' yrs' : data.age_range, 'N/A')],
		['Platform',   Array.isArray(data.platforms) ? data.platforms.join(', ') : withFallback(data.platforms, 'N/A')],
		['Playtime',   Array.isArray(data.playtimes) ? data.playtimes.join(', ') : withFallback(data.playtimes, 'N/A')],
		['Languages',  Array.isArray(data.languages) ? data.languages.join(', ') : withFallback(data.languages, 'N/A')],
	];
	rows.forEach(([label, value]) => createInfoRow(elements.infoBox, label, value));
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

	fetchProfile(username)
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
	const hasRank = !!player.display_value;
	const hasAge = !!player.age;

	if (hasRank || hasAge) {
		const stats = document.createElement('div');
		stats.className = 'p-stats';

		if (hasRank) {
			const rank = document.createElement('span');
			rank.className = 'p-rank';
			rank.textContent = player.display_value;
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
	void gameSlug;
	void currentRank;
	// TODO: restore the rank picker after the backend exposes a rank options source and save endpoint.
	alert("TODO: rank editing is disabled until the backend provides rank options and a save route for this game.");
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

function showMissingBackendAlert(message) {
	alert(message);
}

function setupLandingPage() {
	const counters = document.querySelectorAll('.lp-stat-num[data-count]');
	if (!counters.length) {
		return;
	}

	function formatStat(el, current) {
		const suffix   = el.dataset.suffix || '';
		const divisor  = parseFloat(el.dataset.divisor) || 1;
		const decimals = parseInt(el.dataset.decimals || '0', 10);
		const value    = current / divisor;
		const display  = decimals > 0 ? value.toFixed(decimals) : Math.round(value).toString();
		el.textContent = display + suffix;
	}

	function animateCounter(el) {
		const target   = parseFloat(el.dataset.count);
		const duration = 1400;
		const start    = performance.now();

		function tick(now) {
			const elapsed  = now - start;
			const progress = Math.min(elapsed / duration, 1);
			const eased    = 1 - Math.pow(1 - progress, 3);
			const current  = target * eased;
			formatStat(el, current);
			if (progress < 1) requestAnimationFrame(tick);
			else formatStat(el, target);
		}

		requestAnimationFrame(tick);
	}

	if ('IntersectionObserver' in window) {
		const observer = new IntersectionObserver(function (entries) {
			entries.forEach(function (entry) {
				if (entry.isIntersecting) {
					animateCounter(entry.target);
					observer.unobserve(entry.target);
				}
			});
		}, { threshold: 0.3 });

		counters.forEach(function (el) { observer.observe(el); });
	} else {
		counters.forEach(animateCounter);
	}

	// Live feed removed per project decision — no placeholder or simulated feed.
}

function setupMultiSelect(root) {
	const trigger = root.querySelector('.multi-select-trigger');
	const dropdown = root.querySelector('.multi-select-dropdown');
	const tagsEl = root.querySelector('[data-tags]');
	const search = root.querySelector('.multi-select-search');
	const options = Array.from(root.querySelectorAll('.multi-select-option'));
	const empty = root.querySelector('.multi-select-empty');
	const placeholder = '<span class="multi-select-placeholder">Select languages…</span>';

	function escapeText(str) {
		const div = document.createElement('div');
		div.textContent = String(str);
		return div.innerHTML;
	}

	function renderTags() {
		const checked = options.filter(o => o.querySelector('input').checked);
		if (!checked.length) {
			tagsEl.innerHTML = placeholder;
			return;
		}
		tagsEl.innerHTML = '';
		checked.forEach(opt => {
			const value = opt.dataset.value;
			const chip = document.createElement('span');
			chip.className = 'multi-select-chip';
			chip.innerHTML = '<span>' + escapeText(value) + '</span><button type="button" class="multi-select-chip-x" aria-label="Remove ' + escapeText(value) + '">×</button>';
			chip.querySelector('button').addEventListener('click', e => {
				e.stopPropagation();
				opt.querySelector('input').checked = false;
				renderTags();
			});
			tagsEl.appendChild(chip);
		});
	}

	function openDropdown() {
		dropdown.hidden = false;
		trigger.setAttribute('aria-expanded', 'true');
		root.classList.add('is-open');
		if (search) {
			search.value = '';
			filterOptions('');
			setTimeout(() => search.focus(), 50);
		}
	}

	function closeDropdown() {
		dropdown.hidden = true;
		trigger.setAttribute('aria-expanded', 'false');
		root.classList.remove('is-open');
	}

	function filterOptions(query) {
		const q = (query || '').toLowerCase().trim();
		let visibleCount = 0;
		options.forEach(opt => {
			const value = (opt.dataset.value || '').toLowerCase();
			const match = !q || value.includes(q);
			opt.style.display = match ? '' : 'none';
			if (match) visibleCount++;
		});
		if (empty) empty.hidden = visibleCount > 0;
	}

	trigger.addEventListener('click', e => {
		e.stopPropagation();
		if (dropdown.hidden) openDropdown();
		else closeDropdown();
	});

	options.forEach(opt => {
		opt.querySelector('input').addEventListener('change', renderTags);
	});

	if (search) {
		search.addEventListener('input', () => filterOptions(search.value));
		search.addEventListener('click', e => e.stopPropagation());
		search.addEventListener('keydown', e => {
			if (e.key === 'Escape') closeDropdown();
		});
	}

	document.addEventListener('click', e => {
		if (!root.contains(e.target)) closeDropdown();
	});

	renderTags();
}

function setupSettingsPage() {
	const links  = document.querySelectorAll('[data-settings-link]');
	const panels = document.querySelectorAll('[data-settings-panel]');

	if (!links.length || !panels.length) {
		return;
	}

	function showPanel(name) {
		panels.forEach(function (panel) {
			panel.hidden = panel.dataset.settingsPanel !== name;
		});
		links.forEach(function (link) {
			link.classList.toggle('active', link.dataset.settingsLink === name);
		});
	}

	links.forEach(function (link) {
		link.addEventListener('click', function (event) {
			event.preventDefault();
			const name = link.dataset.settingsLink;
			showPanel(name);
			history.replaceState(null, '', '#' + name);
		});
	});

	const initial = window.location.hash.replace('#', '');
	if (initial && document.querySelector('[data-settings-panel="' + initial + '"]')) {
		showPanel(initial);
	}

	document.querySelectorAll('[data-multi-select]').forEach(setupMultiSelect);
}

function setupFriendsPage() {
	const tabs = document.querySelectorAll('[data-tab]');
	const panels = document.querySelectorAll('[data-panel]');

	if (!tabs.length || !panels.length) {
		return;
	}

	function showTab(target) {
		tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === target));
		panels.forEach(p => p.hidden = p.dataset.panel !== target);
	}

	tabs.forEach(tab => {
		tab.addEventListener('click', () => {
			const target = tab.dataset.tab;
			showTab(target);
			history.replaceState(null, '', '#' + target);
		});
	});

	const initial = window.location.hash.replace('#', '');
	if (initial && document.querySelector('[data-tab="' + initial + '"]')) {
		showTab(initial);
	}

	const searchInput = document.getElementById('friends-search-input');
	if (searchInput) {
		searchInput.addEventListener('input', () => {
			const query = searchInput.value.toLowerCase().trim();
			document.querySelectorAll('[data-panel="all"] .friend-card').forEach(card => {
				const name = (card.dataset.username || '').toLowerCase();
				card.style.display = (!query || name.includes(query)) ? '' : 'none';
			});
		});
	}
}

function setupGamePage() {
	const gamePage = document.getElementById('page-spel');
	if (!gamePage) {
		return;
	}

	setupGameFiltersSearch();
	setupFavoriteButton();
}

async function handleDeleteAccountClick() {
	const confirmation = prompt('This will permanently delete your account.\nType DELETE to confirm:');
	if (confirmation !== 'DELETE') {
		return;
	}

	try {
		await deleteAccount();
		window.location.href = '/';
	} catch (error) {
		console.error('Delete account failed:', error);
		alert('TODO: deleting accounts requires the backend delete route to return a success response for the UI flow.');
	}
}

function setupSharedDelegation() {
	document.addEventListener('click', async event => {
		const navTarget = event.target.closest('[data-nav-action]');
		if (navTarget) {
			const action = navTarget.dataset.navAction;
			if (action === 'home') goHome();
			else if (action === 'login') goLogin();
			else if (action === 'register') goRegister();
			else if (action === 'back') history.back();
			else if (action === 'scroll-games-left') scrollNavGames(-1);
			else if (action === 'scroll-games-right') scrollNavGames(1);
			else if (action === 'game') goGame(navTarget.dataset.gameSlug);
			return;
		}

		const profileTarget = event.target.closest('[data-profile-open]');
		if (profileTarget) {
			openProfile(profileTarget.dataset.profileOpen);
			return;
		}

		const profileAction = event.target.closest('[data-profile-action]');
		if (profileAction) {
			const username = profileAction.dataset.username;
			const action = profileAction.dataset.profileAction;
			if (action === 'close') {
				closeProfile();
				return;
			}
			if (action === 'discord') {
				showDiscord(event, profileAction);
			} else if (action === 'platform') {
				showPlatform(event, profileAction);
			} else if (action === 'add-friend') {
				try {
					await addFriend(username);
					alert('Friend request sent.');
				} catch (error) {
					console.error('Friend request failed:', error);
					alert('TODO: friend requests need the backend route to stay available.');
				}
			}
			return;
		}

		const friendAction = event.target.closest('[data-friend-action]');
		if (friendAction) {
			const username = friendAction.dataset.username;
			const action = friendAction.dataset.friendAction;
			const card = friendAction.closest('.friend-card');
			try {
				if (action === 'accept') {
					await respondToFriendRequest(username, true);
					adjustPendingBadge(-1);
				} else if (action === 'ignore') {
					await respondToFriendRequest(username, false);
					adjustPendingBadge(-1);
				} else if (action === 'remove') {
					await removeFriend(username);
				}
				if (card) {
					card.remove();
				}
			} catch (error) {
				console.error('Friend action failed:', error);
				alert('TODO: friend actions need the current backend routes to stay available.');
			}
			return;
		}

		const settingsAction = event.target.closest('[data-settings-action]');
		if (settingsAction && settingsAction.dataset.settingsAction === 'delete-account') {
			await handleDeleteAccountClick();
			return;
		}

		const rankButton = event.target.closest('[data-rank-action]');
		if (rankButton) {
			openRankPopup(rankButton.dataset.gameSlug, rankButton.dataset.currentRank || null);
		}
	});

	document.addEventListener('keydown', event => {
		const profileTarget = event.target.closest('[data-profile-open]');
		if (!profileTarget) {
			return;
		}
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			openProfile(profileTarget.dataset.profileOpen);
		}
	});

	document.addEventListener('change', event => {
		const avatarInput = event.target.closest('[data-avatar-input]');
		if (avatarInput) {
			previewAvatar(avatarInput);
		}
	});
}

function adjustPendingBadge(delta) {
	const badge = document.querySelector('.nav-friends-badge');
	const tabBadge = document.querySelector('[data-tab="pending"] .friends-tab-count');
	if (!badge && !tabBadge) {
		return;
	}

	const current = parseInt(badge?.textContent || tabBadge?.textContent || '0', 10) || 0;
	const next = Math.max(0, current + delta);

	if (badge) {
		if (next === 0) {
			badge.remove();
		} else {
			badge.textContent = next;
		}
	}

	if (tabBadge) {
		tabBadge.textContent = next;
		if (next === 0) {
			tabBadge.classList.remove('has-pending');
		}
	}
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
	const response = await fetch(`/api/search/games/${encodeURIComponent(gameSlug)}/players`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(filters),
	});
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

	let latestRequestId = 0;
	const tagSearchInput = document.getElementById('filter-tag-search');

	function getSelectedFilterValue(group) {
		const selected = document.querySelector(`.filter-btn.on[data-filter-group="${group}"]`);
		return selected?.dataset.filterValue || '';
	}

	function collectSchemaFilters() {
		const schemaFilters = {};
		const standardGroups = new Set(['playtime', 'platform', 'language']);

		document.querySelectorAll('#page-spel [data-filter-group]').forEach(control => {
			const group = control.dataset.filterGroup;
			if (!group || standardGroups.has(group)) {
				return;
			}

			if (control.tagName === 'SELECT') {
				if (control.value) {
					schemaFilters[group] = control.value;
				}
				return;
			}

			if (control.type === 'checkbox') {
				if (!schemaFilters[group]) {
					schemaFilters[group] = [];
				}
				if (control.checked) {
					schemaFilters[group].push(control.value);
				}
				return;
			}

			if (control.type === 'range') {
				schemaFilters[group] = control.value;
			}
		});

		Object.keys(schemaFilters).forEach(key => {
			if (Array.isArray(schemaFilters[key]) && schemaFilters[key].length === 0) {
				delete schemaFilters[key];
			}
		});

		return schemaFilters;
	}
	
	const triggerSearch = debounce(async () => {
		const requestId = ++latestRequestId;
		playersGrid.innerHTML = '<p>Searching players…</p>';
	
		const ageBounds = ageFilterController?.getAgeBounds() ?? { ageLo: null, ageHi: null };
		const languageSelect = document.getElementById('filter-language');
		const tagSearch = tagSearchInput?.value?.trim().replace(/^@/, '') || '';
	
		const filters = {
			name_contains: tagSearch || null,
			age_lo:   ageBounds.ageLo,
			age_hi:   ageBounds.ageHi,
			playtime: getSelectedFilterValue('playtime') ? [getSelectedFilterValue('playtime')] : [],
			platform: getSelectedFilterValue('platform') ? [getSelectedFilterValue('platform')] : [],
			language: languageSelect?.value ? [languageSelect.value] : [],
			schema_filters: collectSchemaFilters(),
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

		document.querySelectorAll(`.filter-btn[data-filter-group="${group}"]`).forEach(groupBtn => {
			groupBtn.classList.remove('on');
		});
		if (!isOn) {
			button.classList.add('on');
		}

		triggerSearch();
	});

	if (tagSearchInput) {
		tagSearchInput.addEventListener('input', triggerSearch);
	}

	const languageSelect = document.getElementById('filter-language');
	if (languageSelect) {
		languageSelect.addEventListener('change', triggerSearch);
	}

	gamePage.addEventListener('change', event => {
		if (event.target.closest('[data-filter-group]')) {
			triggerSearch();
		}
	});

	gamePage.addEventListener('input', event => {
		if (event.target.matches('[data-filter-group]') && event.target.type === 'range') {
			triggerSearch();
		}
	});

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

	// Load initial player list on page load
	triggerSearch();
}

function previewAvatar(input) {
	const file = input.files && input.files[0];
	const filenameEl = document.getElementById('avatar-filename');
	const previewImg = document.getElementById('avatar-preview-img');
	if (!file) {
		return;
	}

	if (file.size > 2 * 1024 * 1024) {
		alert('Image is too large. Max 2 MB.');
		input.value = '';
		return;
	}

	if (filenameEl) {
		filenameEl.textContent = file.name;
	}

	const reader = new FileReader();
	reader.onload = e => {
		if (previewImg) {
			previewImg.src = e.target.result;
		}
	};
	reader.readAsDataURL(file);

	// TODO: avatar uploads still need the backend multipart endpoint and storage flow.
	showMissingBackendAlert('TODO: avatar uploads need the backend /api/profile/settings/avatar endpoint before this can save.');
}

setupLandingPage();
setupSettingsPage();
setupFriendsPage();
setupGamePage();
setupSharedDelegation();