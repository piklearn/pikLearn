/*!
 * theme.js — پیک‌لرن
 * Vanilla JS only. No dependencies.
 *
 * Responsibilities:
 *   1. Apply the saved theme (or default to "dark") as early as possible,
 *      so this file must be included in <head> WITHOUT `defer`/`async`
 *      to avoid a flash of the wrong theme.
 *   2. Wire up the .theme-toggle button once the DOM is ready.
 *   3. Drive a subtle, lag-free cursor glow using requestAnimationFrame
 *      interpolation. All colors/opacity for the glow live in CSS
 *      variables (see style.css) — this file only ever moves it.
 */

(function () {
  "use strict";

  var STORAGE_KEY = "piklearn-theme";
  var root = document.documentElement;

  /* ---------------------------------------------------------------------
   * 1. Apply saved theme immediately (runs the instant this script parses)
   * ------------------------------------------------------------------- */
  function getPreferredTheme() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved === "light" || saved === "dark") return saved;
    } catch (e) {
      /* localStorage unavailable (privacy mode, etc.) — fall through */
    }
    return "dark"; // dark is the product default, regardless of OS setting
  }

  function applyTheme(theme) {
    root.setAttribute("data-bs-theme", theme);
  }

  applyTheme(getPreferredTheme());

  /* ---------------------------------------------------------------------
   * 2. Toggle button + persistence
   * ------------------------------------------------------------------- */
  function setTheme(theme) {
    applyTheme(theme);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      /* ignore write errors */
    }
    var btn = document.getElementById("themeToggle");
    if (btn) {
      btn.setAttribute("aria-pressed", theme === "light" ? "true" : "false");
    }
  }

  function initToggle() {
    var btn = document.getElementById("themeToggle");
    if (!btn) return;

    btn.setAttribute(
      "aria-pressed",
      root.getAttribute("data-bs-theme") === "light" ? "true" : "false"
    );

    btn.addEventListener("click", function () {
      var current = root.getAttribute("data-bs-theme") === "light" ? "light" : "dark";
      setTheme(current === "light" ? "dark" : "light");
    });
  }

  /* ---------------------------------------------------------------------
   * 3. Cursor glow — smooth trailing dot, never blocks clicks
   * ------------------------------------------------------------------- */
  function initCursorGlow() {
    // Skip entirely on touch/coarse-pointer devices — no mouse to follow.
    if (window.matchMedia && window.matchMedia("(hover: none), (pointer: coarse)").matches) {
      return;
    }
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    var glow = document.getElementById("cursor-glow");
    if (!glow) return;

    var targetX = window.innerWidth / 2;
    var targetY = window.innerHeight / 2;
    var currentX = targetX;
    var currentY = targetY;
    var hasMoved = false;
    var rafId = null;

    function onPointerMove(e) {
      targetX = e.clientX;
      targetY = e.clientY;
      if (!hasMoved) {
        hasMoved = true;
        glow.classList.add("is-visible");
      }
    }

    function onPointerLeave() {
      glow.classList.remove("is-visible");
    }

    function tick() {
      // Lerp toward the target — smooth, no perceptible lag, no overshoot.
      var ease = 0.16;
      currentX += (targetX - currentX) * ease;
      currentY += (targetY - currentY) * ease;

      glow.style.setProperty("--gx", currentX.toFixed(1) + "px");
      glow.style.setProperty("--gy", currentY.toFixed(1) + "px");

      rafId = requestAnimationFrame(tick);
    }

    document.addEventListener("pointermove", onPointerMove, { passive: true });
    document.addEventListener("pointerleave", onPointerLeave, { passive: true });
    document.addEventListener("mouseleave", onPointerLeave, { passive: true });

    rafId = requestAnimationFrame(tick);

    // Clean up if the page is being torn down (SPA-style navigation safety).
    window.addEventListener("pagehide", function () {
      if (rafId) cancelAnimationFrame(rafId);
    });
  }

  /* ---------------------------------------------------------------------
   * Boot
   * ------------------------------------------------------------------- */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initToggle();
      initCursorGlow();
    });
  } else {
    initToggle();
    initCursorGlow();
  }
})();
