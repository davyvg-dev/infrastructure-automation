/*
 * Klantkraan chat widget loader.
 *
 * A client pastes ONE line on their own site:
 *   <script src="https://<client>.klantkraan.nl/widget.js" defer
 *           data-label="Chat" data-color="#ffb84d" data-position="right"></script>
 *
 * This script runs on the client's page but only touches the DOM: it injects a floating
 * bubble and, on first open, an <iframe> pointing back at OUR origin (derived from this
 * script's own src). The chat itself lives inside that iframe, so its fetch('/chat') and
 * fetch('/config') stay same-origin -> no CORS, no API key exposed in the client's page.
 * The whole widget lives in a shadow root so the host site's CSS can't leak in.
 */
(function () {
  "use strict";
  if (window.__klantkraanWidget) return; // idempotent if the tag is included twice
  window.__klantkraanWidget = true;

  var script =
    document.currentScript ||
    (function () {
      var all = document.getElementsByTagName("script");
      for (var i = all.length - 1; i >= 0; i--) {
        if (/widget\.js(\?|$)/.test(all[i].src)) return all[i];
      }
      return null;
    })();

  var origin = "";
  try {
    origin = new URL(script.src).origin;
  } catch (e) {
    // Can't resolve our own origin -> can't safely load the iframe; bail quietly.
    return;
  }

  var ds = (script && script.dataset) || {};
  // Brand default: Klantkraan sodium-amber bubble with petrol-dark icon. A client
  // can still override both via data-color / data-ink to match their own site.
  var color = ds.color || "#ffb84d";
  var ink = ds.ink || "#0f1c1e";
  var label = ds.label || "Chat";
  var side = ds.position === "left" ? "left" : "right";
  var frameSrc = origin + "/?embed=1";

  var CHAT_ICON =
    '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="' + ink + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7A8.38 8.38 0 0 1 4 11.5 8.38 8.38 0 0 1 12.5 3 8.38 8.38 0 0 1 21 11.5z"/></svg>';
  var CLOSE_ICON =
    '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="' + ink + '" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>';

  function build() {
    var host = document.createElement("div");
    host.id = "klantkraan-widget";
    document.body.appendChild(host);
    var root = host.attachShadow ? host.attachShadow({ mode: "open" }) : host;

    var style = document.createElement("style");
    style.textContent = [
      ":host{all:initial}",
      ".kk-bubble,.kk-panel{position:fixed;z-index:2147483000;" + side + ":20px}",
      ".kk-bubble{bottom:20px;width:60px;height:60px;border:0;border-radius:50%;",
      "background:" + color + ";cursor:pointer;box-shadow:0 6px 24px rgba(0,0,0,.28);",
      "display:flex;align-items:center;justify-content:center;padding:0;transition:transform .15s ease}",
      ".kk-bubble:hover{transform:scale(1.06)}",
      ".kk-panel{bottom:92px;width:min(400px,calc(100vw - 40px));height:min(640px,calc(100vh - 120px));",
      "border:0;border-radius:16px;overflow:hidden;background:#0f1c1e;",
      "box-shadow:0 16px 48px rgba(0,0,0,.28);opacity:0;transform:translateY(12px) scale(.98);",
      "pointer-events:none;transition:opacity .18s ease,transform .18s ease}",
      ".kk-panel.kk-open{opacity:1;transform:none;pointer-events:auto}",
      ".kk-frame{width:100%;height:100%;border:0;display:block}",
      "@media (max-width:480px){.kk-panel{width:calc(100vw - 24px);height:calc(100vh - 96px);" + side + ":12px}}",
    ].join("");
    root.appendChild(style);

    var panel = document.createElement("div");
    panel.className = "kk-panel";
    root.appendChild(panel);

    var bubble = document.createElement("button");
    bubble.className = "kk-bubble";
    bubble.type = "button";
    bubble.setAttribute("aria-label", label);
    bubble.setAttribute("aria-expanded", "false");
    bubble.innerHTML = CHAT_ICON;
    root.appendChild(bubble);

    var frame = null;
    var open = false;

    function setOpen(next) {
      open = next;
      if (open && !frame) {
        frame = document.createElement("iframe");
        frame.className = "kk-frame";
        frame.title = label;
        frame.src = frameSrc;
        panel.appendChild(frame);
      }
      panel.classList.toggle("kk-open", open);
      bubble.innerHTML = open ? CLOSE_ICON : CHAT_ICON;
      bubble.setAttribute("aria-expanded", open ? "true" : "false");
    }

    bubble.addEventListener("click", function () {
      setOpen(!open);
    });

    // The embedded page posts {type:'klantkraan-widget', action:'close'} to collapse itself.
    window.addEventListener("message", function (e) {
      if (e.origin !== origin) return;
      var d = e.data;
      if (d && d.type === "klantkraan-widget" && d.action === "close") setOpen(false);
    });
  }

  if (document.body) build();
  else document.addEventListener("DOMContentLoaded", build);
})();
