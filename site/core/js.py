# -*- coding: utf-8 -*-
"""
The site's only JavaScript: the language transition and the theme switch.

THEME_KEY is declared once here and interpolated into both consumers -- the
blocking bootstrap that shell.py inlines in <head>, and the deferred
site.js -- so the two can never disagree about where the preference lives.
"""

THEME_KEY = "arjuanfelipe:theme"

# Inlined in <head>, before the stylesheet paints, so a stored preference is
# applied to <html> in the same tick the document is parsed. Deferring this to
# site.js would repaint the page from dark to light in front of the reader.
THEME_BOOTSTRAP_JS = (
    '(()=>{try{var t=localStorage.getItem("' + THEME_KEY + '");'
    'if(t==="light"||t==="dark")document.documentElement.dataset.theme=t;}'
    'catch(e){}})();'
)

SITE_JS = r'''(() => {
  const KEY = "arjuanfelipe:language-scroll-y";
  const TRANSITION_KEY = "arjuanfelipe:language-transition";
  const links = document.querySelectorAll("[data-language-switch]");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  for (const link of links) {
    link.addEventListener("click", (event) => {
      try {
        sessionStorage.setItem(KEY, String(window.scrollY));
        sessionStorage.setItem(TRANSITION_KEY, "1");
      } catch (_) {}

      if (reduceMotion) return;
      event.preventDefault();
      document.documentElement.classList.add("site-language-leaving");
      window.setTimeout(() => { window.location.href = link.href; }, 130);
    });
  }

  let saved = null;
  let arriving = false;
  try {
    saved = sessionStorage.getItem(KEY);
    if (saved !== null) sessionStorage.removeItem(KEY);
    arriving = sessionStorage.getItem(TRANSITION_KEY) === "1";
    if (arriving) sessionStorage.removeItem(TRANSITION_KEY);
  } catch (_) {}

  if (arriving && !reduceMotion) {
    document.documentElement.classList.add("site-language-arriving");
  }

  if (saved !== null) {
    const y = Number(saved);
    if (Number.isFinite(y)) {
      requestAnimationFrame(() => requestAnimationFrame(() => {
        window.scrollTo(0, y);
        document.documentElement.classList.remove("site-language-arriving");
      }));
    }
  } else if (arriving) {
    requestAnimationFrame(() =>
      document.documentElement.classList.remove("site-language-arriving"));
  }

  // ---------------------------------------------------------------- theme --
  // The document already carries a resolved data-theme: "dark" from the
  // server, or the stored preference applied by the <head> bootstrap. This
  // only keeps the control in sync with it and writes new choices down.
  const THEME_KEY = "@@THEME_KEY@@";
  const root = document.documentElement;
  const buttons = document.querySelectorAll("[data-theme-set]");
  const themeColor = document.querySelector('meta[name="theme-color"]');

  const applyTheme = (theme) => {
    root.dataset.theme = theme;
    for (const button of buttons) {
      button.setAttribute("aria-pressed",
        String(button.dataset.themeSet === theme));
    }
    // The browser chrome colour is read back from the token layer rather than
    // duplicated here, so the palette stays defined in exactly one place.
    if (themeColor) {
      const bg = getComputedStyle(root).getPropertyValue("--wds-bg").trim();
      if (bg) themeColor.setAttribute("content", bg);
    }
  };

  applyTheme(root.dataset.theme === "light" ? "light" : "dark");

  for (const button of buttons) {
    button.addEventListener("click", () => {
      const theme = button.dataset.themeSet;
      applyTheme(theme);
      try { localStorage.setItem(THEME_KEY, theme); } catch (_) {}
    });
  }

  // ----------------------------------------------------------------- back --
  // The "Back" control on /applications/ is a real link to Home, so it works
  // with no script and on a direct visit. When there IS a same-origin page
  // to go back to, step back to it instead of pushing Home onto the stack.
  for (const el of document.querySelectorAll("[data-back]")) {
    el.addEventListener("click", (event) => {
      let sameOrigin = false;
      try {
        sameOrigin = document.referrer !== "" &&
          new URL(document.referrer).origin === window.location.origin;
      } catch (_) {}
      if (sameOrigin && window.history.length > 1) {
        event.preventDefault();
        window.history.back();
      }
    });
  }
})();
'''.replace("@@THEME_KEY@@", THEME_KEY)
