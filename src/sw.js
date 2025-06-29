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

//self.addEventListener('notificationclick', function(event) {
//   const url = `https://localhost:5000${event.notification.data?.url}`;  //event.notification.data?.url || '/';
//   event.notification.close();

//   event.waitUntil(
//     clients.openWindow(url)
//   );
// });

self.addEventListener('notificationclick', function(event) {
 // event.notification.close(); // Close the notification

  event.waitUntil(
    clients.matchAll({ type: 'window' }).then(function(clientList) {
      for (var i = 0; i < clientList.length; i++) {
        var client = clientList[i];
        if (client.url === '/' && 'focus' in client) {
          return client.focus(); // Bring existing window to focus
        }
      }
      if (clients.openWindow) {
        return clients.openWindow('/'); // Open a new window
      }
    })
  );
});
