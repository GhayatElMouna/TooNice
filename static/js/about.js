// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Mobile Menu Toggle
const menuToggle = document.getElementById('menuToggle');
const mobileNav = document.getElementById('mobileNav');

if (menuToggle) {
    menuToggle.addEventListener('click', () => {
        mobileNav.classList.toggle('active');
    });
}

// Close menu when link is clicked
document.querySelectorAll('.nav-link-mobile').forEach(link => {
    link.addEventListener('click', () => {
        mobileNav.classList.remove('active');
    });
});

// Smooth scroll for internal links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Counter animation for stats
function animateCounters() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(element => {
        const target = element.textContent;
        const isVisible = element.getBoundingClientRect().top < window.innerHeight;
        
        if (isVisible && !element.classList.contains('animated')) {
            element.classList.add('animated');
            // Add animation logic here if needed
        }
    });
}

window.addEventListener('scroll', animateCounters);

// Intersection Observer for all fade-in elements
document.querySelectorAll('.fade-in, .fade-in-up, .slide-in-left, .slide-in-right').forEach(element => {
    observer.observe(element);
});
