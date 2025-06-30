// sw.js

self.addEventListener('push', function(event) {
  const data = JSON.parse(event.data?.text()); //|| '🔔 You have a new notification!';

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/static/icon.png', // optional
      badge: '/static/badge.png', // optional
      data: { url: data.url } // you can customize this
    })
  );
});

self.addEventListener('notificationclick', function(event) {
    console.log('Notification clicked! (inside service worker)'); // This should be the first thing
    event.notification.close(); // Good practice

    event.waitUntil(
      clients.openWindow(event.notification.data?.url)
    );
    clients.openWindow(event.notification.data?.url)
});

self.addEventListener("notificationclose", function(event) {
  console.log('notification close');
  // log send to server
});

