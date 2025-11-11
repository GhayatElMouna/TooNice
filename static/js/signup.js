// Password visibility toggle
const passwordInput = document.getElementById("password")
const passwordToggle = document.getElementById("passwordToggle")

if (passwordToggle) {
  passwordToggle.addEventListener("click", (e) => {
    e.preventDefault()
    const type = passwordInput.getAttribute("type") === "password" ? "text" : "password"
    passwordInput.setAttribute("type", type)
    passwordToggle.textContent = type === "password" ? "Show" : "Hide"
  })
}
document.getElementById('confirmPasswordToggle').addEventListener('click', function () {
        const confirmField = document.getElementById('confirmPassword');
        if (confirmField.type === 'password') {
            confirmField.type = 'text';
            this.textContent = 'Hide';
        } else {
            confirmField.type = 'password';
            this.textContent = 'Show';
        }
    });

// Form submission
const signupForm = document.getElementById("signupForm")
if (signupForm) {
  signupForm.addEventListener("submit", (e) => {
    e.preventDefault()
    const formData = new FormData(signupForm)
    console.log("Form submitted with data:", Object.fromEntries(formData))
    alert("Account created successfully!")
    signupForm.reset()
  })
}
