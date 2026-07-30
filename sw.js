const CACHE = "ccse-a57ed379b19f";
const ASSETS = ["./", "./ccse.html", "./manifest.webmanifest", "./icon-180.png", "./icon-512.png"];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(names => Promise.all(names.filter(n => n !== CACHE).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

// Serve from cache so the app opens with no network at all, then refresh in the
// background so the next launch has the newest build.
self.addEventListener("fetch", event => {
  const request = event.request;
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const cached = await cache.match(request, { ignoreSearch: true });
    // Refresh in the background even when the cache answers, but swallow failures:
    // being offline is the expected state here, not an error worth surfacing.
    const update = fetch(request)
      .then(response => {
        if (response && response.ok) cache.put(request, response.clone());
        return response;
      })
      .catch(() => null);
    return cached || (await update) || (await cache.match("./ccse.html"));
  })());
});
