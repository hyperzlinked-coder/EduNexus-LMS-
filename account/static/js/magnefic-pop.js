/**
 * Profile Page Plugins Initialization
 * Handling Magnific Popup for Profile Picture Preview
 */
$(document).ready(function() {
    console.log("jQuery:", typeof $);

    if (typeof $ !== "undefined" && $.fn && $.fn.magnificPopup) {
        $('.image-popup-no-margins').magnificPopup({
            type: 'image',
            closeOnContentClick: true,
            closeBtnInside: false,
            fixedContentPos: true,
            mainClass: 'mfp-no-margins mfp-with-zoom',
            image: {
                verticalFit: true
            },
            zoom: {
                enabled: true,
                duration: 300
            }
        });
        console.log("Magnific Popup initialized successfully.");
    } else {
        console.error("Magnific Popup NOT loaded. Ensure jquery.magnific-popup.min.js is included.");
    }
});