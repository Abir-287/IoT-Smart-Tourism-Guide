// VAPID public key
const publicVapidKey = "BGjxb3k5mQ-Dja55KpKtONI8qbyQf5GFcsv14HBsu7WnxL41AsVJE1dkZ8BcSxD3JpZ7ucdDwD7KGJnbGuraTXc";

// Convert base64 string to Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

// Subscribe user to push notifications
async function subscribeUser() {
    if ('serviceWorker' in navigator) {
        const register = await navigator.serviceWorker.register('/static/scripts/service-worker.js');
        const subscription = await register.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
        });

        // Send subscription to server
        await fetch('/subscribe', {
            method: 'POST',
            body: JSON.stringify(subscription),
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log("User subscribed to notifications!");
    } else {
        console.error("Service workers are not supported in this browser.");
    }
}

// Call the function to subscribe user
subscribeUser();

// Add button hover effect after DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".btn");
    buttons.forEach(btn => {
        btn.addEventListener("mouseenter", () => btn.classList.add("btn-outline-light"));
        btn.addEventListener("mouseleave", () => btn.classList.remove("btn-outline-light"));
    });
});
