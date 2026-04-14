document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById("imageModal");
    const img = document.getElementById("profileTrigger");
    const modalImg = document.getElementById("img01");
    const closeBtn = document.getElementById("closeModal");

    if (img) {
        // Open Popup
        img.onclick = function() {
            modal.style.display = "flex";
            modalImg.src = this.src;
        }
    }

    if (closeBtn) {
        // Close Popup
        closeBtn.onclick = function() {
            modal.style.display = "none";
        }
    }

    // Isara kapag clinick ang itim na background
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // Isara gamit ang Escape Key
    document.addEventListener('keydown', function(e) {
        if (e.key === "Escape") {
            modal.style.display = "none";
        }
    });
});