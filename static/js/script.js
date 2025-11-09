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
document.getElementById("nextBtn").addEventListener("click", nextSlide)
document.getElementById("prevBtn").addEventListener("click", prevSlide)

// Mobile menu toggle
const menuToggle = document.querySelector(".menu-toggle")
const mobileNav = document.getElementById("mobileNav")

menuToggle.addEventListener("click", () => {
  mobileNav.classList.toggle("active")
})

// Close mobile menu when clicking a link
const mobileLinks = document.querySelectorAll(".nav-link-mobile")
mobileLinks.forEach((link) => {
  link.addEventListener("click", () => {
    mobileNav.classList.remove("active")
  })
})

// Initialize carousel
goToSlide(0)
