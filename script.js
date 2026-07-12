const navToggle = document.querySelector(".nav-toggle");
const menuOverlay = document.querySelector(".menu-overlay");
const menuPanel = document.querySelector(".menu-panel");
const menuClose = document.querySelector(".menu-close");
const menuItems = document.querySelectorAll(".menu-item.has-children");

function openMenu() {
  menuOverlay?.classList.add("is-open");
  navToggle?.setAttribute("aria-expanded", "true");
  document.body.style.overflow = "hidden";
}

function closeMenu() {
  menuOverlay?.classList.remove("is-open");
  navToggle?.setAttribute("aria-expanded", "false");
  document.body.style.overflow = "";
  menuItems.forEach((item) => {
    item.classList.remove("is-open");
    item.querySelector(".menu-expand")?.setAttribute("aria-expanded", "false");
  });
}

navToggle?.addEventListener("click", () => {
  if (menuOverlay?.classList.contains("is-open")) {
    closeMenu();
  } else {
    openMenu();
  }
});

menuClose?.addEventListener("click", closeMenu);

menuOverlay?.addEventListener("click", (event) => {
  if (!menuPanel?.contains(event.target)) closeMenu();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeMenu();
});

menuItems.forEach((item) => {
  const expandBtn = item.querySelector(".menu-expand");
  expandBtn?.addEventListener("click", () => {
    const isOpen = item.classList.toggle("is-open");
    expandBtn.setAttribute("aria-expanded", String(isOpen));
  });
});

document.querySelectorAll(".menu-panel a").forEach((link) => {
  link.addEventListener("click", closeMenu);
});

const subnavLinks = document.querySelectorAll(".page-subnav a");

if (subnavLinks.length) {
  const sections = [...subnavLinks]
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

  const setActive = (id) => {
    subnavLinks.forEach((link) => {
      link.classList.toggle("is-active", link.getAttribute("href") === `#${id}`);
    });
  };

  if (sections.length) {
    setActive(sections[0].id);

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActive(visible[0].target.id);
      },
      { rootMargin: "-140px 0px -60% 0px" }
    );

    sections.forEach((section) => observer.observe(section));
  }
}
