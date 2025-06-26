// sw.js

self.addEventListener('push', function(event) {
  const data = event.data?.text() || '🔔 You have a new notification!';

  event.waitUntil(
    self.registration.showNotification('XYZ-MiNi CRM Reminder', {
      body: data,
      icon: '/static/icon.png', // optional
      badge: '/static/badge.png', // optional
      data: { url: '/' } // you can customize this
    })
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
