/* --- UTILITY FUNCTIONS --- */
/*
	Utility function to return a fallback value if the main value is null, undefined or empty
*/
function withFallback(value, fallback) {
	return value || fallback;
}

/* --- NAVIGATION FUNCTIONS --- */
/*
	Set the page location to the index/home page
*/
function goHome() {
  	window.location.href = '/';
}

/*
	Set the page location to a specific game id
*/
function goGame(id) {
  	window.location.href = `/game/${id}`;
}

/*
	Set the page location to the login page
*/
function goLogin() {
  	window.location.href = '/login';
}

/*
	Set the page location to the registration page
*/
function goRegister() {
  	window.location.href = '/register';
}

/*
	Set the page location to a specific user's profile page
*/
function goProfile(username) {
  	window.location.href = `/profile/${username}`;
}

/* --- API FUNCTIONS --- */
/*
	Fetch the player profile data from the API for a given username
	Returns a promise that resolves to the profile data in JSON format
*/
async function fetchProfile(username) {
	const response = await fetch(`/api/players/${username}`);
	if (!response.ok) {
		throw new Error('Network response was not ok');
	}
	return response.json();
}

/*
	Add user to friends list (placeholder)
*/
async function addFriend(username) {
	// TODO: How do we implement this?
	// Where do we store the currently logged in user data?
	alert("Funktion inte implementerad");
}

/* --- NAVIGATION SCROLLING --- */
/*
	Scroll the games navigation track left or right based on the direction parameter
*/
function scrollNavGames(direction) {
	// direction: -1 for left, 1 for right
	const track = document.getElementById('nav-games-track');
	// if track is null or undefined do nothing 
  	if (!track) {
    	return;
  	}

  	// scroll by 80% of the track width or a minimum of 220px, whichever is greater
	// calculate the distance to scroll
  	const distance = Math.max(track.clientWidth * 0.8, 220);
	// scroll the element
  	track.scrollBy({ left: distance * direction, behavior: 'smooth' });
}

/* --- PROFILE CARD LOGIC --- */
/*
	Creates an info row element with a label and value, and appends it to the given infobox element
	Used when rendering the profile cards
*/
function createInfoRow(infobox, label, value) {
	// Create a new div element for the info row
	const row = document.createElement('div');
	// Set the class for styling
	row.className = 'info-row';
	// Set the inner HTML to include the label and value with classes for styling
	row.innerHTML = `<span class="lbl">${label}</span><span class="val">${value}</span>`;
	// Append the new row to the passed infobox element
	infobox.appendChild(row);
}

/*
	Creates a game icon element (link with image) and append it to the given game panel element
	Used when rendering the profile cards to show favorite games
*/
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
function getProfileCardElements() {
	// Get the main card element
	const card = document.getElementById('profile-card');

	// If the card doesn't exist on the page, return null
	// This allows us to null check and return when we are on a page without the profile cards
	if (!card) {
		return null;
	}

	// Find all of the relevant child elements within the card
	const profilePanel = card.getElementsByClassName('profile-panel')[0];
	const loading = card.querySelector('#profile-loading');
	const infoBox = card.getElementsByClassName('info-box')[0];
	const gamePanel = card.getElementsByClassName('games-panel')[0];
	const avatarImage = profilePanel.querySelector('.profile-avatar img');
	const bioText = infoBox.querySelector('.bio-text');
	const profileButtons = profilePanel.querySelector('.profile-buttons');

	return { card, loading, infoBox, gamePanel, avatarImage, bioText, profileButtons: profileButtons };
}

/*
	Show the profile card modal and display the "loading" state while fetching profile data
*/
function showProfileCard(card, loading) {
	// Remove the "hidden" class
	card.classList.remove('hidden');
	// Set the aria-hidden attribute (useful for screen readers and accessibility)
	card.setAttribute('aria-hidden', 'false');
	// Add a class to the body to prevent background scrolling when the modal is open
	document.body.classList.add('modal-open');
	// Set the display of the loading element to block to show it
	loading.style.display = 'block';
}

/*
	Hide the profile card modal and reset any dynamic content (prepare for next open)
*/
function hideProfileCard(card) {
	// Add the "hidden" class to hide the card
	card.classList.add('hidden');
	// Set the aria-hidden attribute to true to indicate it's hidden (for screen readers)
	card.setAttribute('aria-hidden', 'true');
	// Remove the "modal-open" class from the body to allow scrolling again
	document.body.classList.remove('modal-open');
}

/*
	Reset the profile card content to a clean state before loading new data
*/
function resetProfileCard(elements) {
	// Get all elements with info row class and remove them
	elements.infoBox.querySelectorAll('.info-row').forEach(row => row.remove());
	// Get all elements with game tile class and remove them
	elements.gamePanel.querySelectorAll('.game-tile').forEach(tile => tile.remove());
	// Remove bio text
	elements.bioText.textContent = '';
	// Reset avatar to default loading state
	elements.avatarImage.src = '/static/img/profiles/default.jpg';
	elements.avatarImage.alt = 'Loading...';
	// Show loading state
	elements.loading.textContent = 'Laddar profil...';
	elements.loading.style.display = 'block';
	// Remove any existing buttons in the profile buttons container
	elements.profileButtons.querySelectorAll('.action-button').forEach(btn => btn.remove());
}

function addActionButton(element, label, onClick) {
	// Create the button element
	const button = document.createElement('button');
	button.className = 'action-button';
	button.textContent = label;
	button.addEventListener('click', onClick);
	element.appendChild(button);
}

/*
	Render the fetched profile data into the modal
*/
function renderProfileData(elements, data) {
	// Set the avatar image
	setProfileAvatar(elements, data);
	// Create the info rows
	renderProfileInfoRows(elements, data);
	// Set the bio text
	elements.bioText.textContent = withFallback(data.bio, 'No bio available.');
	// Render the favorite games
	renderProfileGames(elements.gamePanel, data.games);
	// TODO: Add friend button
	addActionButton(elements.profileButtons, 'Lägg till som vän', () => addFriend(data.username));
	// Add the show profile button
	addActionButton(elements.profileButtons, 'Visa full profil', () => goProfile(data.username));
	// Hide the loading state
	elements.loading.style.display = 'none';
}

/*
	Render an error state in the profile modal if fetching data fails
*/
function renderProfileError(elements, username, error) {
	elements.loading.textContent = 'Kunde inte ladda profil. Försök igen.';
	createInfoRow(elements.infoBox, 'Username', username);
	elements.bioText.textContent = 'Något gick fel när vi hämtade profilen.';
	console.error('Error fetching player profile:', error);
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

	// For each game in the array, create a game icon element and append it to the game panel
	games.forEach(game => createGameIcon(gamePanel, game));
}

/*
	Open the profile modal for a given username.
	Fetches the profile from the API and renders it, showing loading state and handling errors
*/
function openProfile(username) {
	// Get the card elements
	const elements = getProfileCardElements();

	// If no elements found, return (for pages where the card doesn't exist)
	if (!elements) {
		return;
	}

	// Show the profile card with loading state and reset any previous content
	showProfileCard(elements.card, elements.loading);

	// Reset the profile card content
	resetProfileCard(elements);

	fetch(`/api/players/${username}`)
	.then(response => response.json())
	.then(data => renderProfileData(elements, data))
	.catch(error => renderProfileError(elements, username, error));
}

/*
	Close the profile card and reset its content
*/
function closeProfile() {
	// Get profile elements
	const elements = getProfileCardElements();

	// If no elements found, return
	if (!elements) {
		return;
	}

	// Hide the profile card
	hideProfileCard(elements.card);
}

/* --- EVENT LISTENERS --- */
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
	const elements = getProfileCardElements();
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