// sw.js
self.addEventListener('push', function(event) {
   let data = {};
   if (event.data) {
     data = event.data.json();
   }
   const title = data.title || "Default Title";
   const options = {
     body: data.body || "Default body",
     data: data.url || "/"
   };
   event.waitUntil(
     self.registration.showNotification(title, options)
   );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
