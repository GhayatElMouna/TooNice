// Carousel functionality
let currentSlide = 0
const slides = document.querySelectorAll(".carousel-slide")
const indicators = document.querySelectorAll(".indicator")
const totalSlides = slides.length
let autoPlayInterval

function goToSlide(index) {
  slides.forEach((slide) => slide.classList.remove("active"))
  indicators.forEach((indicator) => indicator.classList.remove("active"))

  currentSlide = index
  slides[currentSlide].classList.add("active")
  indicators[currentSlide].classList.add("active")

  resetAutoPlay()
}

function nextSlide() {
  goToSlide((currentSlide + 1) % totalSlides)
}

function prevSlide() {
  goToSlide((currentSlide - 1 + totalSlides) % totalSlides)
}

function autoPlay() {
  autoPlayInterval = setInterval(() => {
    nextSlide()
  }, 5000)
}

function resetAutoPlay() {
  clearInterval(autoPlayInterval)
  autoPlay()
}

// Event listeners for carousel buttons
const nextBtn = document.getElementById("nextBtn")
const prevBtn = document.getElementById("prevBtn")
if (nextBtn) nextBtn.addEventListener("click", nextSlide)
if (prevBtn) prevBtn.addEventListener("click", prevSlide)

// Mobile menu toggle
const menuToggle = document.querySelector(".menu-toggle")
const mobileNav = document.getElementById("mobileNav")

if (menuToggle && mobileNav) {
  menuToggle.addEventListener("click", () => {
    mobileNav.classList.toggle("active")
  })
}

// Close mobile menu when clicking a link
const mobileLinks = document.querySelectorAll(".nav-link-mobile")
mobileLinks.forEach((link) => {
  link.addEventListener("click", () => {
    mobileNav.classList.remove("active")
  })
})

// Initialize carousel
goToSlide(0)


// Mobile dropdown for events
document.querySelectorAll('.mobile-dropdown-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        btn.parentElement.classList.toggle('open');
    });
});

