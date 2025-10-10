// Mobile Menu Toggle
const mobileMenuBtn = document.querySelector(".mobile-menu-btn");
const nav = document.querySelector("nav ul");

mobileMenuBtn.addEventListener("click", () => {
  nav.style.display = nav.style.display === "flex" ? "none" : "flex";
});

// Testimonial Slider
const slider = document.getElementById("testimonials-slider");
const dots = document.querySelectorAll(".slider-dot");
let currentSlide = 0;

function showSlide(index) {
  slider.scrollTo({
    left: slider.offsetWidth * index,
    behavior: "smooth",
  });

  dots.forEach((dot) => dot.classList.remove("active"));
  dots[index].classList.add("active");
  currentSlide = index;
}

dots.forEach((dot, index) => {
  dot.addEventListener("click", () => showSlide(index));
});

// Auto-advance slides every 5 seconds
setInterval(() => {
  currentSlide = (currentSlide + 1) % dots.length;
  showSlide(currentSlide);
}, 5000);

// Modal Handling
const loginBtn = document.getElementById("login-btn");
const signupBtn = document.getElementById("signup-btn");
const loginModal = document.getElementById("login-modal");
const signupModal = document.getElementById("signup-modal");
const closeModals = document.querySelectorAll(".close-modal");
const switchToSignup = document.getElementById("switch-to-signup");
const switchToLogin = document.getElementById("switch-to-login");

// Show login modal
loginBtn.addEventListener("click", () => {
  loginModal.style.display = "flex";
  document.body.style.overflow = "hidden";
});

// Show signup modal
signupBtn.addEventListener("click", () => {
  signupModal.style.display = "flex";
  document.body.style.overflow = "hidden";
});

// Close modals
closeModals.forEach((btn) => {
  btn.addEventListener("click", () => {
    loginModal.style.display = "none";
    signupModal.style.display = "none";
    document.body.style.overflow = "auto";
  });
});

// Switch between login and signup
switchToSignup.addEventListener("click", (e) => {
  e.preventDefault();
  loginModal.style.display = "none";
  signupModal.style.display = "flex";
});

switchToLogin.addEventListener("click", (e) => {
  e.preventDefault();
  signupModal.style.display = "none";
  loginModal.style.display = "flex";
});

// Close modal when clicking outside
window.addEventListener("click", (e) => {
  if (e.target === loginModal) {
    loginModal.style.display = "none";
    document.body.style.overflow = "auto";
  }
  if (e.target === signupModal) {
    signupModal.style.display = "none";
    document.body.style.overflow = "auto";
  }
});

// Form submission
document.getElementById("login-form").addEventListener("submit", (e) => {
  e.preventDefault();
  alert("Login functionality would be implemented here");
  loginModal.style.display = "none";
  document.body.style.overflow = "auto";
});

document.getElementById("signup-form").addEventListener("submit", (e) => {
  e.preventDefault();
  alert("Signup functionality would be implemented here");
  signupModal.style.display = "none";
  document.body.style.overflow = "auto";
});
