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

async function friendAction(username, action) {
    // map "action" to HTTP method and needed query params
    const actionMap = {
        "add":    { method: "POST" },
        "remove": { method: "DELETE" },
        "accept": { method: "PATCH", accept: true },
        "ignore": { method: "PATCH", accept: false }
    };

    const config = actionMap[action];
    if (!config) return;

    // define the base URL for all friend actions
    let url = `/api/players/${encodeURIComponent(username)}/friend`;

    // append the query param for PATCH requests (accept/ignore)
    if (config.method === "PATCH") {
        url += `?accept=${config.accept}`;
    }

    try {
        const response = await fetch(url, { method: config.method });

        if (!response.ok) {
            // extract error message from response if available
            const errorData = await response.json().catch(() => ({}));
            alert(errorData.detail || `Error: ${response.status}`);
            return;
        }

        // Success
		return true;

    } catch (err) {
        console.error("Connection error:", err);
        alert("Failed to reach the server. Please check your connection.");
    }

	return false;
}

/* --- FRIEND ACTION HANDLERS --- */
async function handleAddFriendClick(username, button) {
	if (!button) return;
	if (button.dataset.sent) return;
	button.dataset.sent = '1';
	button.querySelector('.p-action-label').textContent = 'Sent!';
	button.classList.add('p-action-btn-active');
	button.disabled = true;
	try {
		const success = await friendAction(username, 'add');
		if (!success) {
			button.querySelector('.p-action-label').textContent = 'Add friend';
			button.classList.remove('p-action-btn-active');
			button.disabled = false;
			delete button.dataset.sent;
		}
	} catch (err) {
		button.querySelector('.p-action-label').textContent = 'Add friend';
		button.classList.remove('p-action-btn-active');
		button.disabled = false;
		delete button.dataset.sent;
	}
}

async function handleAcceptRequest(button) {
	const username = button.dataset.username;
	const card = button.closest('.friend-card');
	if (!card) return;
	try {
		const success = await friendAction(username, 'accept');
		if (success) {
			card.classList.add('is-accepted');
			const actions = card.querySelector('.friend-card-actions');
			if (actions) {
				actions.innerHTML = '<div class="friend-action-result accepted">✓ Friend added</div>';
			}
			decrementPendingBadge();
		}
	} catch (err) {
		console.error('Error accepting request:', err);
	}
}

async function handleIgnoreRequest(button) {
	const username = button.dataset.username;
	const card = button.closest('.friend-card');
	if (!card) return;
	try {
		const success = await friendAction(username, 'ignore');
		if (success) {
			card.style.transition = 'opacity .3s ease, transform .3s ease, max-height .3s ease, margin .3s ease, padding .3s ease';
			card.style.opacity = '0';
			card.style.transform = 'scale(.95)';
			setTimeout(() => card.remove(), 300);
			decrementPendingBadge();
		}
	} catch (err) {
		console.error('Error ignoring request:', err);
	}
}

async function handleRemoveFriend(button) {
	const username = button.dataset.username;
	if (!confirm('Remove ' + username + ' from your friends?')) return;
	const card = button.closest('.friend-card');
	if (!card) return;
	try {
		const success = await friendAction(username, 'remove');
		if (success) {
			card.style.transition = 'opacity .3s ease, transform .3s ease';
			card.style.opacity = '0';
			card.style.transform = 'scale(.95)';
			setTimeout(() => card.remove(), 300);
		}
	} catch (err) {
		console.error('Error removing friend:', err);
	}
}

function decrementPendingBadge() {
	const badge = document.querySelector('.nav-friends-badge');
	if (!badge) return;
	const current = parseInt(badge.textContent, 10) || 0;
	const next = Math.max(0, current - 1);
	if (next === 0) {
		badge.remove();
	} else {
		badge.textContent = next;
	}
	const tabBadge = document.querySelector('[data-tab="pending"] .friends-tab-count');
	if (tabBadge) {
		tabBadge.textContent = next;
		if (next === 0) tabBadge.classList.remove('has-pending');
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
		throw new Error('Failed to update favorite state: status ' + response.status);
	}
}

function setupFavoriteButton() {
    const btn = document.getElementById('fav-btn');
	if (!btn) return;

    btn.addEventListener('click', async (e) => {
        e.preventDefault();

		if (btn.disabled) return; // prevent multiple clicks while processing
        
        const slug = btn.dataset.favSlug;
        const isCurrentlyActive = btn.classList.contains('active');
        const newState = !isCurrentlyActive; // toggle the state

        // add pulsing animation
		btn.disabled = true; // disable button while processing
        btn.classList.add('is-pulsing');
        btn.addEventListener('animationend', () => btn.classList.remove('is-pulsing'), { once: true });

        try {
            await setFavoriteState(slug, newState);

			// TODO: set the visibility of the "edit profile" for the game

            // update the UI
            btn.classList.toggle('active', newState);
            const label = btn.querySelector('.fav-label');
            if (label) {
                label.textContent = newState ? 'Remove from favorites' : 'Add to favorites';
            }
        } catch (error) {
            alert('Something went wrong. Please try again.');
        } finally {
			// re-enable the button
			btn.disabled = false;
		}
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
	const displayValue = game.display_value || game.rank;
	if (displayValue) {
		rankEl.className = 'game-tile-rank';
		rankEl.textContent = displayValue;
	} else {
		rankEl.className = 'game-tile-rank unranked';
		rankEl.textContent = 'Unknown';
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
	const friendBtn = document.createElement('button');
	friendBtn.className = 'action-button';
	friendBtn.textContent = 'Add as friend';
	friendBtn.addEventListener('click', () => handleAddFriendClick(data.username, friendBtn));
	elements.profileButtons.appendChild(friendBtn);
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
		['Platform',   withFallback(data.platform, 'N/A')],
		['Languages',  Array.isArray(data.languages) ? data.languages.join(', ') : withFallback(data.languages, 'N/A')],
		['Availability', Array.isArray(data.playtimes) ? data.playtimes.join(', ') : withFallback(data.playtimes, 'N/A')],
	];
	rows.forEach(([label, value]) => createInfoRow(elements.infoBox, label, value));
}

function escapeHtmlText(str) {
	const div = document.createElement('div');
	div.textContent = String(str);
	return div.innerHTML;
}

function renderProfileGames(gamePanel, games) {
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

	const friendBtn = document.createElement('button');
	friendBtn.type = 'button';
	friendBtn.className = 'p-action-btn p-action-btn-friend';
	friendBtn.dataset.username = player.username || '';
	friendBtn.setAttribute('aria-label', `Add ${player.username || 'player'} as friend`);
	friendBtn.innerHTML =
		`<span class="p-action-icon" aria-hidden="true"></span>` +
		`<span class="p-action-label">Add friend</span>`;
	friendBtn.addEventListener('click', async e => {
		e.stopPropagation();
		await handleAddFriendClick(friendBtn.dataset.username, friendBtn);
	});

	const profileBtn = document.createElement('button');
	profileBtn.type = 'button';
	profileBtn.className = 'p-action-btn p-action-btn-profile';
	profileBtn.dataset.username = player.username || '';
	profileBtn.setAttribute('aria-label', `Show full profile for ${player.username || 'player'}`);
	profileBtn.innerHTML =
		`<span class="p-action-icon" aria-hidden="true"></span>` +
		`<span class="p-action-label">Show profile</span>`;
	profileBtn.addEventListener('click', e => {
		e.stopPropagation();
		goProfile(profileBtn.dataset.username);
	});

	actions.appendChild(friendBtn);
	actions.appendChild(profileBtn);

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
	// Read rank metadata from the DOM to avoid embedding globals
	const pageEl = document.querySelector('[data-game-slug="' + gameSlug + '"]');
	let ranks = null;
	let displayField = null;
	if (pageEl) {
		const opts = pageEl.getAttribute('data-rank-options');
		const df = pageEl.getAttribute('data-rank-display-field');
		try {
			ranks = opts ? JSON.parse(opts) : null;
		} catch (err) {
			ranks = null;
		}
		try {
			displayField = df && df !== 'null' ? JSON.parse(df) : null;
		} catch (err) {
			displayField = df && df !== 'null' ? df : null;
		}
	}

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

	// Form with select + submit (we handle submit via fetch JSON)
	const form = document.createElement('form');
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
	submitBtn.textContent = 'Update rank';
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

	// Handle submission via fetch to backend API
	form.addEventListener('submit', async (e) => {
		e.preventDefault();
		if (!displayField) {
			showPopup({ title: 'Update failed', body: 'No display field configured for this game.', variant: 'muted' });
			return;
		}
		const value = select.value;
		if (!value) return;

		submitBtn.disabled = true;
		try {
			const res = await fetch('/api/games/' + encodeURIComponent(gameSlug) + '/info', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ [displayField]: value }),
			});

			if (res.status === 204) {
				closePopup();
				showPopup({ title: 'Rank updated', body: 'Your rank was updated.', variant: 'success' });

				// Update in-page displays for this game (if present)
				const main = document.querySelector('[data-game-slug="' + gameSlug + '"]');
				if (main) {
					const btnCurrent = main.querySelector('.rank-btn-current');
					if (btnCurrent) btnCurrent.textContent = value;
					const displayVal = main.querySelector('.rank-display-value');
					if (displayVal) displayVal.textContent = value;
				}
			} else {
				let errText = 'Could not update rank.';
				try {
					const body = await res.json();
					errText = body.detail || errText;
				} catch (err) {}
				showPopup({ title: 'Update failed', body: errText, variant: 'muted' });
			}
		} catch (err) {
			showPopup({ title: 'Update failed', body: 'Network error', variant: 'muted' });
		} finally {
			submitBtn.disabled = false;
		}
	});
}

/* ── Game profile modal — only open/close; HTML & fields come from template ── */
function openGameProfilePopup() {
	const modal = document.getElementById('profile-schema-modal');
	if (!modal) return;
	modal.classList.remove('hidden');
	modal.setAttribute('aria-hidden', 'false');
	document.body.classList.add('modal-open');
}

function closeGameProfilePopup() {
	const modal = document.getElementById('profile-schema-modal');
	if (!modal) return;
	modal.classList.add('hidden');
	modal.setAttribute('aria-hidden', 'true');
	document.body.classList.remove('modal-open');
}

// Close on Esc and overlay click
document.addEventListener('keydown', e => {
	if (e.key === 'Escape') closeGameProfilePopup();
});
document.addEventListener('click', e => {
	const modal = document.getElementById('profile-schema-modal');
	if (modal && e.target === modal) closeGameProfilePopup();
});

// Bind submit handler for server-rendered profile form: serialize selects and POST JSON
document.addEventListener('DOMContentLoaded', () => {
	const form = document.getElementById('profile-schema-form');
	if (!form) return;

	form.addEventListener('submit', async (e) => {
		e.preventDefault();
		const endpoint = form.dataset.apiEndpoint;
		const displayField = form.dataset.displayField;
		const submitBtn = form.querySelector('button[type="submit"]');
		const payload = {};

		form.querySelectorAll('select[name]').forEach(sel => {
			const name = sel.name;
			if (sel.multiple) {
				const vals = Array.from(sel.options).filter(o => o.selected).map(o => o.value);
				if (vals.length) payload[name] = vals;
			} else {
				const v = sel.value;
				if (v) payload[name] = v;
			}
		});

		if (submitBtn) submitBtn.disabled = true;
		try {
			const res = await fetch(endpoint, {
				method: 'POST',
				credentials: 'same-origin',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload),
			});

			if (res.status === 204) {
				closeGameProfilePopup();
				showPopup({ title: 'Profile updated', body: 'Your profile was updated.', variant: 'success' });

				if (displayField && payload[displayField]) {
					const main = document.querySelector('[data-game-slug]');
					if (main) {
						const btnCurrent = main.querySelector('.rank-btn-current');
						const displayVal = main.querySelector('.rank-display-value');
						const newVal = Array.isArray(payload[displayField]) ? payload[displayField].join(', ') : payload[displayField];
						if (btnCurrent) btnCurrent.textContent = newVal;
						if (displayVal) displayVal.textContent = newVal;
					}
				}
			} else {
				let errText = 'Could not update profile.';
				try {
					const body = await res.json();
					errText = body.detail || errText;
				} catch (err) {}
				showPopup({ title: 'Update failed', body: errText, variant: 'muted' });
			}
		} catch (err) {
			showPopup({ title: 'Update failed', body: 'Network error', variant: 'muted' });
		} finally {
			if (submitBtn) submitBtn.disabled = false;
		}
	});
});

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
		icon.innerHTML = `<span class="info-popup-symbol-icon" aria-hidden="true"></span>`;
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

setupGameFiltersSearch();
setupFavoriteButton();

function setupHashTabs(options) {
	const tabSelector = options.tabSelector;
	const panelSelector = options.panelSelector;
	const tabDataKey = options.tabDataKey;
	const panelDataKey = options.panelDataKey;

	const tabs = document.querySelectorAll(tabSelector);
	const panels = document.querySelectorAll(panelSelector);
	if (!tabs.length || !panels.length) {
		return null;
	}

	function showTab(target) {
		tabs.forEach(tab => {
			tab.classList.toggle('active', tab.dataset[tabDataKey] === target);
		});
		panels.forEach(panel => {
			panel.hidden = panel.dataset[panelDataKey] !== target;
		});
	}

	tabs.forEach(tab => {
		tab.addEventListener('click', event => {
			event.preventDefault();
			const target = tab.dataset[tabDataKey];
			showTab(target);
			history.replaceState(null, '', '#' + target);
		});
	});

	const initial = window.location.hash.replace('#', '');
	if (initial && document.querySelector(tabSelector + '[data-' + tabDataKey.replace(/[A-Z]/g, match => '-' + match.toLowerCase()) + '="' + initial + '"]')) {
		showTab(initial);
	}

	return showTab;
}

function setupGameTagSearch() {
	const input = document.getElementById('filter-tag-search');
	if (!input) return;

	input.addEventListener('input', () => {
		const query = input.value.toLowerCase().trim().replace(/^@/, '');
		document.querySelectorAll('.player-card').forEach(card => {
			const name = (card.querySelector('.p-name')?.textContent || '').toLowerCase();
			card.style.display = (!query || name.includes(query)) ? '' : 'none';
		});
	});
}

function setupFriendsPage() {
	setupHashTabs({
		tabSelector: '[data-tab]',
		panelSelector: '[data-panel]',
		tabDataKey: 'tab',
		panelDataKey: 'panel',
	});

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
		const checked = options.filter(option => option.querySelector('input').checked);
		if (!checked.length) {
			tagsEl.innerHTML = placeholder;
			return;
		}

		tagsEl.innerHTML = '';
		checked.forEach(option => {
			const value = option.dataset.value;
			const chip = document.createElement('span');
			chip.className = 'multi-select-chip';
			chip.innerHTML = '<span>' + escapeText(value) + '</span><button type="button" class="multi-select-chip-x" aria-label="Remove ' + escapeText(value) + '">×</button>';
			chip.querySelector('button').addEventListener('click', event => {
				event.stopPropagation();
				option.querySelector('input').checked = false;
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
		const normalizedQuery = (query || '').toLowerCase().trim();
		let visibleCount = 0;
		options.forEach(option => {
			const value = (option.dataset.value || '').toLowerCase();
			const match = !normalizedQuery || value.includes(normalizedQuery);
			option.style.display = match ? '' : 'none';
			if (match) visibleCount++;
		});
		if (empty) empty.hidden = visibleCount > 0;
	}

	trigger.addEventListener('click', event => {
		event.stopPropagation();
		if (dropdown.hidden) openDropdown();
		else closeDropdown();
	});

	options.forEach(option => {
		option.querySelector('input').addEventListener('change', renderTags);
	});

	if (search) {
		search.addEventListener('input', () => filterOptions(search.value));
		search.addEventListener('click', event => event.stopPropagation());
		search.addEventListener('keydown', event => {
			if (event.key === 'Escape') closeDropdown();
		});
	}

	document.addEventListener('click', event => {
		if (!root.contains(event.target)) closeDropdown();
	});

	renderTags();
}

function setupSettingsPage() {
	setupHashTabs({
		tabSelector: '[data-settings-link]',
		panelSelector: '[data-settings-panel]',
		tabDataKey: 'settingsLink',
		panelDataKey: 'settingsPanel',
	});

	document.querySelectorAll('[data-multi-select]').forEach(setupMultiSelect);
}

function confirmDeleteAccount() {
	const confirmation = prompt('This will permanently delete your account.\nType DELETE to confirm:');
	if (confirmation === 'DELETE') {
		fetch('/api/profile/delete-account', {
			method: 'DELETE',
			credentials: 'same-origin',
		}).then(res => {
			if (res.status === 204) {
				window.location.href = '/';
			} else {
				alert('Account deletion failed.');
			}
		}).catch(() => {
			alert('Network error. Account deletion failed.');
		});
	}
}

function validateProfilePictureUpload(input) {
	const file = input.files && input.files[0];
	if (!file) return;

	// file size check — max 5 MB
	// 				 MB, KB,    BYTE
	const MAX_SIZE = 5 * 1024 * 1024;
	if (file.size > MAX_SIZE) {
		alert('Image is too large. Max 5 MB.');
		input.value = '';
		return;
	}
	
	// file type check
	const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
	if (!allowedTypes.includes(file.type)) {
		alert('Invalid file type. Please upload a JPEG, PNG, or WEBP image.');
		input.value = '';
		return;
	}

	// trigger auto submit
	input.form.submit();
}

setupGameTagSearch();
setupFriendsPage();
setupSettingsPage();