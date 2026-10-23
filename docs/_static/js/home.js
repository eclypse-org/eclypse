(() => {
  const scene = document.querySelector('.scene');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  function reveal() {
    scene.classList.add('is-ready');
  }
  if (document.readyState === 'complete') reveal();
  else window.addEventListener('load', reveal, { once: true });
  const ambient = document.querySelector('.ambient');
  let pointerFrame = 0;
  function resetAtmosphere() {
    cancelAnimationFrame(pointerFrame);
    ambient.classList.remove('is-active');
    ambient.style.setProperty('--cloud-x', '0px');
    ambient.style.setProperty('--cloud-y', '0px');
  }
  window.addEventListener('pointermove', (event) => {
    if (reduced.matches || !fine.matches) return;
    cancelAnimationFrame(pointerFrame);
    pointerFrame = requestAnimationFrame(() => {
      ambient.style.setProperty('--pointer-x', `${event.clientX}px`);
      ambient.style.setProperty('--pointer-y', `${event.clientY}px`);
      ambient.style.setProperty('--cloud-x', `${(event.clientX / window.innerWidth - .5) * 36}px`);
      ambient.style.setProperty('--cloud-y', `${(event.clientY / window.innerHeight - .5) * 24}px`);
      ambient.classList.add('is-active');
    });
  }, { passive: true });
  document.documentElement.addEventListener('pointerleave', resetAtmosphere);
  window.addEventListener('blur', resetAtmosphere);
  reduced.addEventListener('change', resetAtmosphere);
  fine.addEventListener('change', resetAtmosphere);
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
  function startNetwork() {
    const canvas = document.querySelector('.ambient-network');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    let width = 0, height = 0, frame = 0, previousTime = 0;
    let nodes = [];
    let pointer = null;
    const canAnimate = () => !reduced.matches && fine.matches && !document.hidden;

    function draw(seconds) {
      ctx.clearRect(0, 0, width, height);
      for (const node of nodes) {
        node.x += node.vx * seconds;
        node.y += node.vy * seconds;
        if (pointer && seconds) {
          const dx = node.x - pointer.x, dy = node.y - pointer.y;
          const distance = Math.hypot(dx, dy);
          if (distance > 0 && distance < 115) {
            const push = (1 - distance / 115) * 22 * seconds;
            node.x += dx / distance * push;
            node.y += dy / distance * push;
          }
        }
        if (node.x < 0 || node.x > width) node.vx *= -1;
        if (node.y < 0 || node.y > height) node.vy *= -1;
        node.x = Math.max(0, Math.min(width, node.x));
        node.y = Math.max(0, Math.min(height, node.y));
      }
      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        const nearby = pointer && Math.hypot(a.x - pointer.x, a.y - pointer.y) < 180;
        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const distance = Math.hypot(a.x - b.x, a.y - b.y);
          if (distance >= 165) continue;
          const opacity = (1 - distance / 165) * (nearby ? .42 : .19);
          ctx.strokeStyle = nearby ? `rgba(255,158,71,${opacity})` : `rgba(191,192,192,${opacity})`;
          ctx.lineWidth = .7;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        }
        ctx.fillStyle = nearby ? 'rgba(255,183,121,.85)' : 'rgba(191,202,208,.58)';
        ctx.beginPath(); ctx.arc(a.x, a.y, a.radius, 0, Math.PI * 2); ctx.fill();
      }
    }
    function tick(time) {
      frame = 0;
      if (!canAnimate()) return;
      if (time - previousTime >= 1000 / 30) {
        draw(previousTime ? Math.min((time - previousTime) / 1000, .05) : 0);
        previousTime = time;
      }
      frame = requestAnimationFrame(tick);
    }
    function sync() {
      cancelAnimationFrame(frame);
      frame = 0; previousTime = 0; pointer = null;
      draw(0);
      if (canAnimate()) frame = requestAnimationFrame(tick);
    }
    function resize() {
      const oldWidth = width, oldHeight = height;
      width = window.innerWidth; height = window.innerHeight;
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      for (const node of nodes) {
        node.x *= width / oldWidth; node.y *= height / oldHeight;
      }
      // Bound pairwise link calculations even on very large displays.
      const count = Math.min(80, Math.max(24, Math.round(width * height / 16000)));
      nodes = nodes.slice(0, count);
      while (nodes.length < count) {
        const angle = Math.random() * Math.PI * 2, speed = 4 + Math.random() * 6;
        nodes.push({x:Math.random() * width, y:Math.random() * height,
          vx:Math.cos(angle) * speed, vy:Math.sin(angle) * speed,
          radius:.8 + Math.random() * .8});
      }
      sync();
    }
    window.addEventListener('pointermove', (event) => {
      if (canAnimate()) pointer = {x:event.clientX, y:event.clientY};
    }, {passive:true});
    document.documentElement.addEventListener('pointerleave', () => { pointer = null; });
    window.addEventListener('blur', () => { pointer = null; });
    window.addEventListener('resize', resize);
    document.addEventListener('visibilitychange', sync);
    reduced.addEventListener('change', sync); fine.addEventListener('change', sync);
    resize();
  }
  startNetwork();
})();
