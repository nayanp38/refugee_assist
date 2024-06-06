console.log('hello');

document.addEventListener("DOMContentLoaded", function() {
    var currentPath = window.location.pathname;
    console.log(currentPath);
    var navLinks = document.querySelectorAll(".nav-link");

    if (currentPath === '/') {
        navLinks.forEach(function(link) {
            if (link.textContent === 'Home') {
                link.classList.add('active');
            }
        });
    } else if (currentPath === '/about') {
        navLinks.forEach(function(link) {
            if (link.textContent === 'About') {
                link.classList.add('active');
            }
        });
    }

});
