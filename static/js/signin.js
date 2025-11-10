// Mobile Menu Toggle
const menuToggle = document.getElementById("menuToggle")
const mobileNav = document.getElementById("mobileNav")

if (menuToggle) {
  menuToggle.addEventListener("click", () => {
    mobileNav.classList.toggle("active")
  })
}

// Password Toggle
const passwordToggle = document.getElementById("passwordToggle")
const passwordInput = document.getElementById("password")

if (passwordToggle && passwordInput) {
  passwordToggle.addEventListener("click", (e) => {
    e.preventDefault()
    const isPassword = passwordInput.type === "password"
    passwordInput.type = isPassword ? "text" : "password"
    passwordToggle.textContent = isPassword ? "Hide" : "Show"
  })
}

// Form Submission
const signupForm = document.getElementById("signupForm")
if (signupForm) {
  signupForm.addEventListener("submit", (e) => {
    e.preventDefault()
    const formData = new FormData(signupForm)
    console.log("Sign Up Data:", Object.fromEntries(formData))
    alert("Account created successfully! (Demo)")
    signupForm.reset()
  })
}

const signinForm = document.getElementById("signinForm")
if (signinForm) {
  signinForm.addEventListener("submit", (e) => {
    e.preventDefault()
    const formData = new FormData(signinForm)
    console.log("Sign In Data:", Object.fromEntries(formData))
    alert("Signed in successfully! (Demo)")
  })
}
