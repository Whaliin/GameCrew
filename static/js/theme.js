/* ============================================================
   theme.js - Appearance settings (loaded on every page).

   Reads user preferences from localStorage and applies them
   immediately by overriding CSS variables and setting data-*
   attributes on <html>. Loaded synchronously in <head> BEFORE
   the stylesheet so we don't get a flash of the default.
   ============================================================ */
(function () {
	'use strict';

	const STORAGE_KEY = 'gamecrew:appearance';

	const ACCENT_COLORS = {
		cyan:   { color: '#00F0FF', glow: 'rgba(0, 240, 255, %A)' },
		purple: { color: '#9D00FF', glow: 'rgba(157, 0, 255, %A)' },
		pink:   { color: '#FF0090', glow: 'rgba(255, 0, 144, %A)' },
		green:  { color: '#00FF88', glow: 'rgba(0, 255, 136, %A)' },
		orange: { color: '#FF8C00', glow: 'rgba(255, 140, 0, %A)' },
	};

	const DEFAULTS = {
		accent: 'cyan',
		language: 'en',
		'reduce-motion': false,
		'high-contrast': false,
		'hide-grid': false,
	};

	function read() {
		try {
			const raw = localStorage.getItem(STORAGE_KEY);
			const parsed = raw ? JSON.parse(raw) : {};
			return Object.assign({}, DEFAULTS, parsed);
		} catch (e) {
			return Object.assign({}, DEFAULTS);
		}
	}

	function write(state) {
		try {
			localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
		} catch (e) { /* ignore */ }
	}

	function applyAccent(accentName) {
		const root = document.documentElement;
		const accent = ACCENT_COLORS[accentName] || ACCENT_COLORS.cyan;
		root.style.setProperty('--cyan', accent.color);
		root.style.setProperty('--glow-cyan', '0 0 18px ' + accent.glow.replace('%A', '.35'));
		root.style.setProperty('--glow-cyan-strong', '0 0 24px ' + accent.glow.replace('%A', '.55'));
		root.dataset.themeAccent = accentName;
	}

	function applyToggle(name, value) {
		// e.g. data-reduce-motion="true" / "false"
		document.documentElement.setAttribute('data-' + name, value ? 'true' : 'false');
	}

	function applyAll(state) {
		applyAccent(state.accent);
		applyToggle('reduce-motion', state['reduce-motion']);
		applyToggle('high-contrast', state['high-contrast']);
		applyToggle('hide-grid', state['hide-grid']);
		document.documentElement.lang = state.language || 'en';
	}

	// Apply immediately so there's no flash of default theme
	const state = read();
	applyAll(state);

	// Public API for settings.html
	window.GameCrewTheme = {
		get: read,
		set: function (key, value) {
			const current = read();
			current[key] = value;
			write(current);
			applyAll(current);
		},
		reset: function () {
			write(Object.assign({}, DEFAULTS));
			applyAll(DEFAULTS);
		},
	};
})();