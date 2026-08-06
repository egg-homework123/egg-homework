// Service Worker 已废弃 - 改用服务器端 Cache-Control: no-cache
// 此文件仅用于注销旧版 SW
self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    Promise.all([
      // 删除所有缓存
      caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k)))),
      // 注销自己
      self.registration.unregister()
    ]).then(() => self.clients.claim())
  );
});

// 所有请求直接走网络，不拦截
self.addEventListener('fetch', event => {
  // 不调用 event.respondWith，让浏览器走默认行为
});
