/**
 * Fits the decorative iPhone body to the window and exposes the result as
 * --screen-w, which css/styles.css uses to size .device (and, from that,
 * the bezel, buttons and Dynamic Island via calc()).
 *
 * On an actual phone the mock-up chrome is pointless (the browser already
 * gives you a real device edge), so it's hidden via the .is-bare class and
 * the screen is sized to fill the real viewport instead.
 */
(function () {
  "use strict";

  var root = document.documentElement;
  var controls = document.getElementById("controls");

  // Must match --device-width / --device-height in css/styles.css.
  var DEVICE_W = 2868;
  var DEVICE_H = 1420;
  var SCREEN_RATIO_H = DEVICE_H / DEVICE_W;

  // Must match the 0.017 bezel fraction used in .iphone's padding.
  var BEZEL_FRAC = 0.017;
  var BODY_WIDTH_FACTOR = 1 + 2 * BEZEL_FRAC;
  var BODY_HEIGHT_FACTOR = SCREEN_RATIO_H + 2 * BEZEL_FRAC;

  // How much smaller than "as large as technically fits" to render the
  // mock-up, so it doesn't look cramped against the window edges.
  var PHONE_SIZE = 0.85;
  var MIN_SCREEN_W = 200;

  function isRealPhone() {
    var coarse = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;
    return coarse && Math.min(window.innerWidth, window.innerHeight) < 600;
  }

  function fit() {
    var w = window.innerWidth;
    var h = window.innerHeight;
    var screenW;

    if (isRealPhone()) {
      root.classList.add("is-bare");
      // No bezel on a real phone: fit the screen content directly.
      screenW = Math.min(w, (h * DEVICE_W) / DEVICE_H);
    } else {
      root.classList.remove("is-bare");
      var controlsH = controls ? controls.offsetHeight + 28 + 30 : 0;
      var byWidth = (w - 32) / BODY_WIDTH_FACTOR;
      var byHeight = (h - controlsH - 40) / BODY_HEIGHT_FACTOR;
      screenW = Math.max(MIN_SCREEN_W, Math.min(byWidth, byHeight) * PHONE_SIZE);
    }

    root.style.setProperty("--screen-w", screenW.toFixed(2) + "px");
  }

  fit();
  window.addEventListener("resize", fit);
  window.addEventListener("orientationchange", function () {
    window.setTimeout(fit, 100);
  });
})();
