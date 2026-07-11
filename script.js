const navToggle = document.querySelector(".nav-toggle");
const siteNav = document.querySelector(".site-nav");
const navItems = document.querySelectorAll(".nav-item");

function closeAllPanels(except) {
  navItems.forEach((item) => {
    if (item === except) return;
    item.classList.remove("is-open");
    item.querySelector(".nav-link")?.setAttribute("aria-expanded", "false");
  });
}

function closeMobileNav() {
  siteNav?.classList.remove("is-open");
  navToggle?.setAttribute("aria-expanded", "false");
  closeAllPanels();
}

navToggle?.addEventListener("click", () => {
  const isOpen = siteNav.classList.toggle("is-open");
  navToggle.setAttribute("aria-expanded", String(isOpen));
  if (!isOpen) closeAllPanels();
});

navItems.forEach((item) => {
  const link = item.querySelector(".nav-link");
  link?.addEventListener("click", (event) => {
    event.stopPropagation();
    const isOpen = item.classList.toggle("is-open");
    link.setAttribute("aria-expanded", String(isOpen));
    closeAllPanels(isOpen ? item : undefined);
  });
});

document.addEventListener("click", (event) => {
  if (!(event.target instanceof Element) || !event.target.closest(".nav-item")) {
    closeAllPanels();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeAllPanels();
});

siteNav?.querySelectorAll(".nav-panel a, .nav-link--plain").forEach((link) => {
  link.addEventListener("click", closeMobileNav);
});
