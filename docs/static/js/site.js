(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var veil = document.getElementById("pageVeil");
  function samePageLink(a) {
    if (!a || !a.getAttribute) return false;
    if (a.target && a.target !== "_self") return false;
    if (a.hasAttribute("download")) return false;
    var href = a.getAttribute("href") || "";
    if (!href || href.charAt(0) === "#" || href.indexOf("mailto:") === 0 || href.indexOf("tel:") === 0) return false;
    if (href.indexOf("wa.me") !== -1 || href.indexOf("maps.google") !== -1 || href.indexOf("google.com/maps") !== -1) return false;
    var url;
    try { url = new URL(a.href, location.href); } catch (err) { return false; }
    if (url.origin !== location.origin) return false;
    return url.pathname + url.search !== location.pathname + location.search;
  }
  var nativeVT = false;
  try {
    nativeVT = !reduce && !!(document.startViewTransition) && CSS.supports("selector(::view-transition-old(root))");
  } catch (err) {
    nativeVT = false;
  }
  document.body.classList.add("is-entering");
  setTimeout(function () { document.body.classList.remove("is-entering"); }, 500);
  window.addEventListener("pageshow", function () {
    document.body.classList.remove("is-leaving");
    if (veil) veil.classList.remove("is-on");
  });
  if (!reduce && !nativeVT) {
    document.addEventListener("click", function (e) {
      if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
      var a = e.target.closest("a");
      if (!samePageLink(a)) return;
      e.preventDefault();
      document.body.classList.add("is-leaving");
      if (veil) veil.classList.add("is-on");
      var go = a.href;
      setTimeout(function () { location.href = go; }, 280);
    });
  }

  var bar = document.getElementById("progress");
  if (bar) {
    window.addEventListener("scroll", function () {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
    }, { passive: true });
  }

  var btn = document.getElementById("navToggle");
  var menu = document.getElementById("menu");
  if (btn && menu) {
    btn.addEventListener("click", function () {
      var open = menu.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var sky = document.querySelector(".magic-sky");
  if (sky && !reduce) {
    for (var n = 0; n < 22; n++) {
      var star = document.createElement("span");
      star.className = "star";
      star.style.left = Math.random() * 100 + "%";
      star.style.top = Math.random() * 100 + "%";
      star.style.animationDelay = (Math.random() * 3) + "s";
      star.style.transform = "scale(" + (0.5 + Math.random()) + ")";
      sky.appendChild(star);
    }
  }

  if (!reduce) {
    document.querySelectorAll(".hero, .section, .card, .service-row, .call-bar, .paper").forEach(function (el, idx) {
      el.classList.add("reveal");
      el.style.animationDelay = (Math.min(idx, 8) * 0.06) + "s";
    });
  }

  var canvas = document.getElementById("sparkles");
  if (canvas && canvas.getContext && !reduce) {
    var ctx = canvas.getContext("2d");
    var bits = [];
    var colors = ["#f5d21a", "#e23b3b", "#4aaae8", "#2f5cb0", "#ffffff"];
    function size() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    size();
    window.addEventListener("resize", size);
    function spawn(x, y, burst) {
      var count = burst ? 10 : 2;
      for (var i = 0; i < count; i++) {
        bits.push({
          x: x,
          y: y,
          vx: (Math.random() - 0.5) * (burst ? 4 : 1.2),
          vy: (Math.random() - 0.8) * (burst ? 4 : 1.4),
          life: 1,
          color: colors[(Math.random() * colors.length) | 0],
          r: 1.5 + Math.random() * 2.5
        });
      }
    }
    var last = 0;
    window.addEventListener("mousemove", function (e) {
      var now = Date.now();
      if (now - last < 30) return;
      last = now;
      spawn(e.clientX, e.clientY, false);
    });
    window.addEventListener("mousemove", function (e) {
      var cx = (e.clientX / window.innerWidth - 0.5) * 16;
      var cy = (e.clientY / window.innerHeight - 0.5) * 12;
      if (sky) sky.style.transform = "translate(" + cx + "px," + cy + "px)";
    });
    window.addEventListener("click", function (e) {
      spawn(e.clientX, e.clientY, true);
    });
    function tick() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (var i = bits.length - 1; i >= 0; i--) {
        var p = bits[i];
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.02;
        p.life -= 0.016;
        if (p.life <= 0) { bits.splice(i, 1); continue; }
        ctx.globalAlpha = Math.max(p.life, 0);
        ctx.fillStyle = p.color;
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.life * 6);
        ctx.beginPath();
        for (var s = 0; s < 5; s++) {
          ctx.lineTo(Math.cos((s * 4 * Math.PI) / 5) * p.r * 2, Math.sin((s * 4 * Math.PI) / 5) * p.r * 2);
        }
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      }
      ctx.globalAlpha = 1;
      requestAnimationFrame(tick);
    }
    tick();
  }

  document.querySelectorAll("[data-carousel]").forEach(function (root) {
    var imgs = root.querySelectorAll(".carousel-track img, .carousel-track .html-slide");
    var dotsWrap = root.querySelector("[data-dots]");
    if (!imgs.length) return;
    var i = 0;
    function show(n) {
      i = (n + imgs.length) % imgs.length;
      imgs.forEach(function (img, idx) { img.classList.toggle("is-on", idx === i); });
      if (dotsWrap) {
        dotsWrap.querySelectorAll("button").forEach(function (d, idx) {
          d.classList.toggle("is-on", idx === i);
        });
      }
    }
    if (dotsWrap) {
      imgs.forEach(function (_, idx) {
        var b = document.createElement("button");
        b.type = "button";
        b.setAttribute("aria-label", "Lámina " + (idx + 1));
        if (idx === 0) b.className = "is-on";
        b.addEventListener("click", function () { show(idx); });
        dotsWrap.appendChild(b);
      });
    }
    var prev = root.querySelector("[data-prev]");
    var next = root.querySelector("[data-next]");
    if (prev) prev.addEventListener("click", function () { show(i - 1); });
    if (next) next.addEventListener("click", function () { show(i + 1); });
    var startX = 0;
    root.addEventListener("touchstart", function (e) {
      startX = e.changedTouches[0].clientX;
    }, { passive: true });
    root.addEventListener("touchend", function (e) {
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1));
    });
    if (!reduce) {
      var timer = setInterval(function () { show(i + 1); }, 4200);
      root.addEventListener("mouseenter", function () { clearInterval(timer); });
      root.addEventListener("mouseleave", function () {
        timer = setInterval(function () { show(i + 1); }, 4200);
      });
    }
  });

  var waBtn = document.getElementById("waToggle");
  var waPanel = document.getElementById("waPanel");
  if (waBtn && waPanel) {
    waBtn.addEventListener("click", function () {
      var open = waPanel.hasAttribute("hidden");
      if (open) waPanel.removeAttribute("hidden");
      else waPanel.setAttribute("hidden", "");
    });
  }

  if (!reduce && window.matchMedia("(hover: hover)").matches) {
    document.querySelectorAll(".card, .hero-art").forEach(function (el) {
      el.addEventListener("mousemove", function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = "rotateY(" + (x * 10) + "deg) rotateX(" + (-y * 10) + "deg) translateY(-4px)";
      });
      el.addEventListener("mouseleave", function () { el.style.transform = ""; });
    });
  }
})();
