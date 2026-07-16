document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".ship-card").forEach((card) => {
    const link = card.querySelector(".ship-detail-link");
    if (!link) return;

    card.addEventListener("dblclick", () => {
      window.location.href = link.href;
    });
  });
});