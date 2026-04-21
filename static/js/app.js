function goHome() {
  	window.location.href = '/';
}

function goGame(id) {
  	window.location.href = `/game/${id}`;
}

function goLogin() {
  	window.location.href = '/login';
}

function scrollNavGames(direction) {
	// direction: -1 for left, 1 for right
	const track = document.getElementById('nav-games-track');
	// if track is null or undefined do nothing 
  	if (!track) {
    	return;
  	}

  	// scroll by 80% of the track width or a minimum of 220px, whichever is greater
  	const distance = Math.max(track.clientWidth * 0.8, 220);
  	track.scrollBy({ left: distance * direction, behavior: 'smooth' });
}

function createInfoRow(infobox, label, value) {
	const row = document.createElement('div');
	row.className = 'info-row';
	row.innerHTML = `<span class="lbl">${label}</span><span class="val">${value}</span>`;
	infobox.appendChild(row);
}

function createGameIcon(gamePanel, game) {
	/*
	<a class="game-tile" href="/game/{{ game.slug }}"><img
				src="{{ game.image_url }}"
				alt="{{ game.name }}" /></a>
	*/
	// Create the link element
	const link = document.createElement('a');
	link.className = 'game-tile';
	link.href = `/game/${game.slug}`;

	// Create the image element
	const img = document.createElement('img');
	img.src = game.image_url;
	img.alt = game.name;
	// Make sure we add the image as a child
	link.appendChild(img);

	// Add the link to the game panel
	gamePanel.appendChild(link);
}

/*
	Get all relevant elements for the profile modal in one place to avoid repeated DOM queries
*/
function getProfileModalElements() {
	const card = document.getElementById('profile-card');
	if (!card) {
		return null;
	}

	const profilePanel = card.getElementsByClassName('profile-panel')[0];
	const loading = card.querySelector('#profile-loading');
	const infoBox = card.getElementsByClassName('info-box')[0];
	const gamePanel = card.getElementsByClassName('games-panel')[0];
	const avatarImage = profilePanel.querySelector('.profile-avatar img');
	const bioText = infoBox.querySelector('.bio-text');

	return { card, loading, infoBox, gamePanel, avatarImage, bioText };
}

/*
	Show the profile card modal and display the "loading" state while fetching profile data
*/
function showProfileCard(card, loading) {
	card.classList.remove('hidden');
	card.setAttribute('aria-hidden', 'false');
	document.body.classList.add('modal-open');
	loading.style.display = 'block';
}

/*
	Hide the profile card modal and reset any dynamic content (prepare for next open)
*/
function hideProfileCard(card) {
	card.classList.add('hidden');
	card.setAttribute('aria-hidden', 'true');
	document.body.classList.remove('modal-open');
}

/*
	Reset the profile card content to a clean state before loading new data
*/
function resetProfileCard(elements) {
	elements.infoBox.querySelectorAll('.info-row').forEach(row => row.remove());
	elements.gamePanel.querySelectorAll('.game-tile').forEach(tile => tile.remove());
	elements.bioText.textContent = '';
	elements.avatarImage.src = '/static/img/profiles/default.jpg';
	elements.avatarImage.alt = 'Loading...';
	elements.loading.textContent = 'Laddar profil...';
	elements.loading.style.display = 'block';
}

/*
	Render the fetched profile data into the modal
*/
function renderProfileData(elements, data) {
	setProfileAvatar(elements, data);
	renderProfileInfoRows(elements, data);
	elements.bioText.textContent = withFallback(data.bio, 'No bio available.');
	renderProfileGames(elements.gamePanel, data.games);
	elements.loading.style.display = 'none';
}

/*
	Render an error state in the profile modal if fetching data fails
*/
function renderProfileError(elements, username, error) {
	elements.loading.textContent = 'Kunde inte ladda profil. Forsok igen.';
	createInfoRow(elements.infoBox, 'Username', username);
	elements.bioText.textContent = 'Nagot gick fel nar vi hamtade profilen.';
	console.error('Error fetching player profile:', error);
}

/*
	Utility function to return a fallback value if the main value is null, undefined or empty
*/
function withFallback(value, fallback) {
	return value || fallback;
}

/*
	Set the profile avatar image source and alt text using fallbacks if necessary
*/
function setProfileAvatar(elements, data) {
	elements.avatarImage.src = withFallback(data.avatar_url, '/static/img/profiles/default.jpg');
	elements.avatarImage.alt = withFallback(data.username, 'Player avatar');
}

/*
	Render the profile information rows based on data
*/
function renderProfileInfoRows(elements, data) {
	// Define the rows to display
	const rows = [
		['Username', withFallback(data.username, 'Unknown')],
		['Tag', withFallback(data.user_tag, 'N/A')],
		['Rank', withFallback(data.rank, 'N/A')],
		['Age Range', withFallback(data.age_range, 'N/A')],
		['Platform', withFallback(data.platform, 'N/A')],
		['Playtime', withFallback(data.playtime, 'N/A')],
		['Languages', withFallback(data.languages, 'N/A')],
	];

	// Loop over them and create info rows in the card/modal
	rows.forEach(([label, value]) => createInfoRow(elements.infoBox, label, value));
}

/*
	Render the favorite games as icons in the profile modal
*/
function renderProfileGames(gamePanel, games) {
	// If the games data is not an array, do not attempt to render
	if (!Array.isArray(games)) {
		return;
	}

	games.forEach(game => createGameIcon(gamePanel, game));
}

/*
	Open the profile modal for a given username.
	Fetches the profile from the API and renders it, showing loading state and handling errors
*/
function openProfile(username) {
	const elements = getProfileModalElements();
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

/*
	Close the profile modal and reset its content
*/
function closeProfile() {
	const elements = getProfileModalElements();
	if (!elements) {
		return;
	}

	hideProfileCard(elements.card);
}

/*
	Event listener for the escape key
*/
document.addEventListener('keydown', event => {
	if (event.key === 'Escape') {
		// Close any open profiles when the escape key is pressed
		closeProfile();
	}
});

/*
	Event listener for clicks
*/
document.addEventListener('click', event => {
	// Profile check: if the click is outside the profile card, close it
	// Get the profile elements
	const elements = getProfileModalElements();
	// If no elements or the card is hidden, do nothing
	if (!elements || elements.card.classList.contains('hidden')) {
		// TODO: If adding more modals, this logic should be updated
		return;
	}

	if (event.target === elements.card) {
		closeProfile();
	}
});

/*
	Event listeners for filter buttons (toggles the "on" class for visual state)
*/
document.querySelectorAll('.filter-btn').forEach(btn => {
	// TODO: Trigger actual filtering logic (call the API with filter parameters)
	btn.addEventListener('click', () => btn.classList.toggle('on'));
});