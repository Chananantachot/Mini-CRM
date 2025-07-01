// sw.js
self.addEventListener('push', function(event) {
  const data = JSON.parse(event.data?.text()); 

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/static/icon.png', 
      badge: '/static/badge.png', 
      data: { url: data.url } 
    })
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data?.url)
  );
});

self.addEventListener("notificationclose", function(event) {
  console.log('notification close');
})

