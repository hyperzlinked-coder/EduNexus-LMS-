/**
 * EduNexus Dashboard Utilities
 * Handles auto-logout and Live Clock
 */

// --- 1. Auto Logout Logic ---
let timeoutTimer;
const logoutUrl = "/logout/"; // Fallback URL if dynamic URL fails

function resetTimer() {
    clearTimeout(timeoutTimer);
    // Timer set for 60 seconds (1 minute)
    timeoutTimer = setTimeout(() => {
        // Redirect to logout. Note: Ensure this matches your URL path
        window.location.href = window.location.origin + "/logout/";
    }, 600000);
}

// Initialize listeners for user activity
window.onload = resetTimer;
document.onmousemove = resetTimer;
document.onkeypress = resetTimer;
document.onclick = resetTimer;
document.onscroll = resetTimer;

// --- 2. Live Clock Logic ---
function updateLiveClock() {
    const clockElement = document.getElementById('real-time-clock');
    if (!clockElement) return; // Exit if element doesn't exist on page

    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    
    let timeString = now.toLocaleDateString('en-US', options);
    timeString = timeString.replace(',', ' |');
    clockElement.textContent = timeString;
}

// Start clock
if (document.getElementById('real-time-clock')) {
    updateLiveClock();
    setInterval(updateLiveClock, 1000);
}