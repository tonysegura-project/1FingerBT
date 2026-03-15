const CACHE_NAME = '1fingerbt-v1';
const urlsToCache = [
  '/',
  '/login',
  '/signup'
];

// Install the service worker and cache basic files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Serve files from cache when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});