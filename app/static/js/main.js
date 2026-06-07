document.addEventListener("DOMContentLoaded", function () {
    var header = document.querySelector(".site-header");
    if (!header) return;

    function updateHeader() {
        header.classList.toggle("is-scrolled", window.scrollY > 8);
    }

    window.addEventListener("scroll", updateHeader, { passive: true });
    updateHeader();
});
