const GAMES = {
  cs2:      { name: "Counter-Strike 2",  img: "https://media.steampowered.com/apps/csgo/blog/images/fb_image.png?v=6" },
  lol:      { name: "League of Legends", img: "https://cmsassets.rgpub.io/sanity/images/dsfx7636/news/565197caf987af4e4da307df6e2b235a28714736-837x469.jpg?accountingTag=LoL" },
  valorant: { name: "Valorant",          img: "https://i.pcmag.com/imagery/reviews/05mFypQIoSDkooz9qdATJ54-1..v1586539963.png" },
  arc:      { name: "ARC Raiders",       img: "https://static.wikia.nocookie.net/arc-raiders/images/a/a0/Logo.webp/revision/latest?cb=20251105003659" },
  mobile:   { name: "Mobile Legends",    img: "https://www.exitlag.com/blog/wp-content/uploads/2025/01/MLBB_-everything-you-need-to-know-about-heroes-and-gameplay.webp" },
};

function goHome() {
  document.getElementById('page-spel').classList.remove('active');
  document.getElementById('page-hem').classList.add('active');
}

function goGame(id) {
  const g = GAMES[id];
  document.getElementById('spel-img').src          = g.img;
  document.getElementById('spel-img').alt          = g.name;
  document.getElementById('spel-namn').textContent = g.name;

  document.querySelectorAll('#spel-nav .nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.game === id);
  });

  document.getElementById('page-hem').classList.remove('active');
  document.getElementById('page-spel').classList.add('active');
  window.scrollTo({ top: 0 });
}

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => btn.classList.toggle('on'));
});