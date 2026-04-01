// ─── Mobile Menu ───────────────────────────────────────────────────────────
const mobileMenuBtn = document.querySelector(".mobile-menu-btn");
const navUl = document.querySelector("nav ul");

if (mobileMenuBtn && navUl) {
  mobileMenuBtn.addEventListener("click", () => {
    const isOpen = navUl.classList.toggle("mobile-open");
    mobileMenuBtn.setAttribute("aria-expanded", isOpen);
  });

  // Close menu when a nav link is clicked
  navUl.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navUl.classList.remove("mobile-open");
      mobileMenuBtn.setAttribute("aria-expanded", false);
    });
  });

  // Close menu on resize back to desktop
  window.addEventListener("resize", () => {
    if (window.innerWidth > 992) {
      navUl.classList.remove("mobile-open");
      mobileMenuBtn.setAttribute("aria-expanded", false);
    }
  });
}

// ─── Testimonial Slider (only if present on page) ──────────────────────────
const slider = document.getElementById("testimonials-slider");
const dots = document.querySelectorAll(".slider-dot");

if (slider && dots.length > 0) {
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

  setInterval(() => {
    currentSlide = (currentSlide + 1) % dots.length;
    showSlide(currentSlide);
  }, 5000);
}

// ─── Modal Handling (only if modals exist on page) ─────────────────────────
const loginBtn = document.getElementById("login-btn");
const signupBtn = document.getElementById("signup-btn");
const loginModal = document.getElementById("login-modal");
const signupModal = document.getElementById("signup-modal");
const closeModals = document.querySelectorAll(".close-modal");
const switchToSignup = document.getElementById("switch-to-signup");
const switchToLogin = document.getElementById("switch-to-login");

if (loginBtn && loginModal) {
  loginBtn.addEventListener("click", () => {
    loginModal.style.display = "flex";
    document.body.style.overflow = "hidden";
  });
}

if (signupBtn && signupModal) {
  signupBtn.addEventListener("click", () => {
    signupModal.style.display = "flex";
    document.body.style.overflow = "hidden";
  });
}

closeModals.forEach((btn) => {
  btn.addEventListener("click", () => {
    if (loginModal) loginModal.style.display = "none";
    if (signupModal) signupModal.style.display = "none";
    document.body.style.overflow = "auto";
  });
});

if (switchToSignup && loginModal && signupModal) {
  switchToSignup.addEventListener("click", (e) => {
    e.preventDefault();
    loginModal.style.display = "none";
    signupModal.style.display = "flex";
  });
}

if (switchToLogin && loginModal && signupModal) {
  switchToLogin.addEventListener("click", (e) => {
    e.preventDefault();
    signupModal.style.display = "none";
    loginModal.style.display = "flex";
  });
}

window.addEventListener("click", (e) => {
  if (loginModal && e.target === loginModal) {
    loginModal.style.display = "none";
    document.body.style.overflow = "auto";
  }
  if (signupModal && e.target === signupModal) {
    signupModal.style.display = "none";
    document.body.style.overflow = "auto";
  }
});

const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");

if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (loginModal) {
      loginModal.style.display = "none";
      document.body.style.overflow = "auto";
    }
  });
}

if (signupForm) {
  signupForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (signupModal) {
      signupModal.style.display = "none";
      document.body.style.overflow = "auto";
    }
  });
}
