(() => {
  const scene = document.querySelector('.scene');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  function reveal() {
    scene.classList.add('is-ready');
  }
  if (document.readyState === 'complete') reveal();
  else window.addEventListener('load', reveal, { once: true });
  document.querySelectorAll('.card').forEach((card) => {
    card.addEventListener('pointermove', (event) => {
      if (reduced.matches || !fine.matches) return;
      const box = card.getBoundingClientRect();
      card.style.setProperty('--spot-x', `${event.clientX - box.left}px`);
      card.style.setProperty('--spot-y', `${event.clientY - box.top}px`);
    });
    card.addEventListener('pointerleave', () => {
      card.style.removeProperty('--spot-x');
      card.style.removeProperty('--spot-y');
    });
  });
})();
