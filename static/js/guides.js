(() => {
  document.querySelectorAll('[data-guide-open]').forEach(link => {
    const dialog = document.getElementById(link.dataset.guideOpen);
    link.addEventListener('click', event => {
      event.preventDefault();
      dialog.showModal();
      document.body.classList.add('guide-is-open');
    });
    dialog.addEventListener('close', () => {
      document.body.classList.remove('guide-is-open');
      link.focus();
    });
    dialog.addEventListener('click', event => {
      if (event.target === dialog) {
        const r = dialog.getBoundingClientRect();
        if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
      }
    });
    const pages = [...dialog.querySelectorAll('.guide-pages figure')];
    const previous = dialog.querySelector('[data-guide-prev]');
    const next = dialog.querySelector('[data-guide-next]');
    let index = 0;
    function show(n) {
      index = Math.max(0, Math.min(n, pages.length - 1));
      pages.forEach((page, i) => { page.hidden = i !== index; });
      dialog.querySelector('[data-guide-count]').textContent = `${index + 1} / ${pages.length}`;
      dialog.querySelector('[data-guide-full]').href = pages[index].querySelector('img').src;
      previous.disabled = index === 0;
      next.disabled = index === pages.length - 1;
    }
    previous.addEventListener('click', () => show(index - 1));
    next.addEventListener('click', () => show(index + 1));
    dialog.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault(); show(index + (event.key === 'ArrowRight' ? 1 : -1));
      }
    });
    let start;
    const surface = dialog.querySelector('.guide-pages');
    surface.addEventListener('touchstart', event => { start = event.changedTouches[0]; }, {passive:true});
    surface.addEventListener('touchend', event => {
      if (!start) return;
      const end = event.changedTouches[0];
      const dx = end.clientX - start.clientX;
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(end.clientY - start.clientY)) show(index + (dx < 0 ? 1 : -1));
      start = null;
    }, {passive:true});
    show(0);
  });
})();
