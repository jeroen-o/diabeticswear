/* DiabeticsWear — winkelmand, navigatie en productpagina (geen externe afhankelijkheden) */
(function () {
  "use strict";

  var ROOT = document.documentElement.getAttribute("data-root") || "";
  var FREE_SHIPPING = 50;
  var eur = new Intl.NumberFormat("nl-NL", { style: "currency", currency: "EUR" });

  /* ---------- Legging-illustratie (SVG) ---------- */
  function leggingSVG(color, view, accent) {
    color = color || "#1F2726";
    accent = accent || "#7DC59A";
    var bg = '<rect width="400" height="400" fill="#2BAA92"/>' +
      '<ellipse cx="200" cy="378" rx="110" ry="9" fill="#145F52" opacity=".35"/>';
    var legs = '<path d="M128 98 L272 98 L285 232 L270 362 L222 362 L207 178 L193 178 L178 362 L130 362 L115 232 Z" fill="' + color + '"/>';
    var band = '<rect x="124" y="58" width="152" height="44" rx="10" fill="' + color + '"/>' +
      '<rect x="124" y="58" width="152" height="44" rx="10" fill="#fff" opacity=".07"/>' +
      '<path d="M128 100 H272" stroke="#fff" stroke-opacity=".18" stroke-width="2"/>';
    var seams = '<path d="M200 102 V178" stroke="#fff" stroke-opacity=".12" stroke-width="2"/>';
    var pocket = function (x, flip) {
      var d = flip
        ? "M" + x + " 128 h-30 l-4 70 h30 z"
        : "M" + x + " 128 h30 l4 70 h-30 z";
      return '<path d="' + d + '" fill="#fff" fill-opacity=".1" stroke="' + accent + '" stroke-width="3" stroke-linejoin="round"/>' +
        '<path d="' + (flip ? "M" + x + " 136 h-31" : "M" + x + " 136 h31") + '" stroke="' + accent + '" stroke-width="5"/>';
    };
    var body;
    if (view === "side") {
      body = '<path d="M168 58 h70 a8 8 0 0 1 8 8 v34 l10 132 -14 130 h-48 l-6-130 -26-132 v-34 a8 8 0 0 1 8-8z" fill="' + color + '"/>' +
        '<path d="M176 128 h56 l3 82 h-56 z" fill="#fff" fill-opacity=".1" stroke="' + accent + '" stroke-width="3"/>' +
        '<path d="M176 138 h57" stroke="' + accent + '" stroke-width="5"/>' +
        '<rect x="188" y="150" width="34" height="48" rx="8" fill="#F3F2EE" opacity=".9"/>' +
        '<circle cx="205" cy="166" r="7" fill="' + accent + '"/>';
    } else if (view === "pocket") {
      body = '<rect x="70" y="70" width="260" height="260" rx="22" fill="' + color + '"/>' +
        '<path d="M110 120 h180 l8 170 h-196 z" fill="#fff" fill-opacity=".08" stroke="' + accent + '" stroke-width="5" stroke-linejoin="round"/>' +
        '<path d="M110 142 h182" stroke="' + accent + '" stroke-width="10"/>' +
        '<rect x="150" y="168" width="100" height="98" rx="18" fill="#F3F2EE"/>' +
        '<rect x="170" y="184" width="60" height="40" rx="8" fill="#A3C8E6"/>' +
        '<circle cx="200" cy="246" r="8" fill="' + accent + '"/>';
    } else if (view === "back") {
      body = legs + band + seams +
        '<path d="M140 110 q60 30 120 0" stroke="#fff" stroke-opacity=".14" stroke-width="2" fill="none"/>' +
        '<rect x="178" y="68" width="44" height="22" rx="6" fill="none" stroke="' + accent + '" stroke-width="3"/>';
    } else {
      body = legs + band + seams + pocket(118, false) + pocket(282, true) +
        '<path d="M150 80 q50 10 100 0" stroke="' + accent + '" stroke-width="3" fill="none" opacity=".8"/>';
    }
    return '<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Illustratie diabetes 2-pocket sportlegging">' + bg + body + "</svg>";
  }
  window.DW = { leggingSVG: leggingSVG };

  /* ---------- Productcatalogus (prijzen = placeholder, aanpassen) ---------- */
  var PRODUCTS = {
    legging: { name: "Diabetes 2-pocket sportlegging", price: 49.95, svg: true },
    "patch-rond": { name: "Overpatch rond (10 st.)", price: 12.95, img: "assets/img/patch-rond-libre.webp" },
    "patch-pod": { name: "Overpatch pomp/pod (10 st.)", price: 14.95, img: "assets/img/patch-omnipod.webp" },
    "patch-ovaal": { name: "Overpatch ovaal (10 st.)", price: 13.95, img: "assets/img/patch-ovaal.webp" },
    "patch-ei": { name: "Overpatch ei-vorm (10 st.)", price: 13.95, img: "assets/img/patch-ei.webp" }
  };

  /* ---------- Winkelmand (sessionStorage, valt terug op geheugen) ---------- */
  var memCart = [];
  function load() {
    try { var s = sessionStorage.getItem("dw-cart"); return s ? JSON.parse(s) : memCart; }
    catch (e) { return memCart; }
  }
  function save(c) {
    memCart = c;
    try { sessionStorage.setItem("dw-cart", JSON.stringify(c)); } catch (e) { /* in-memory */ }
  }
  var cart = load();

  function addToCart(id, opts, qty, color) {
    var key = id + "|" + (opts || "");
    var line = cart.filter(function (l) { return l.key === key; })[0];
    if (line) line.qty += qty; else cart.push({ key: key, id: id, opts: opts || "", qty: qty, color: color });
    save(cart); render(); openDrawer();
  }
  window.DW.addToCart = addToCart;

  function thumbFor(line) {
    var p = PRODUCTS[line.id];
    if (p.svg) return leggingSVG(line.color, "front");
    return '<img src="' + ROOT + p.img + '" alt="">';
  }

  function render() {
    var count = cart.reduce(function (n, l) { return n + l.qty; }, 0);
    var total = cart.reduce(function (n, l) { return n + l.qty * PRODUCTS[l.id].price; }, 0);
    document.querySelectorAll(".cart-count").forEach(function (el) { el.textContent = count; });
    var list = document.getElementById("drawer-items");
    if (!list) return;
    if (!cart.length) {
      list.innerHTML = '<p class="empty">Je winkelmand is nog leeg.</p>';
    } else {
      list.innerHTML = cart.map(function (l, i) {
        var p = PRODUCTS[l.id];
        return '<div class="drawer-item"><div class="thumb">' + thumbFor(l) + '</div><div><strong>' + p.name + '</strong>' +
          (l.opts ? '<small>' + l.opts + '</small>' : "") + '<small>' + l.qty + ' × ' + eur.format(p.price) + '</small>' +
          '<button class="rm" data-rm="' + i + '">Verwijderen</button></div><strong>' + eur.format(p.price * l.qty) + '</strong></div>';
      }).join("");
    }
    document.getElementById("drawer-total").textContent = eur.format(total);
    var rest = Math.max(0, FREE_SHIPPING - total);
    document.getElementById("ship-msg").textContent = rest > 0
      ? "Nog " + eur.format(rest) + " tot gratis verzending"
      : "Je bestelling wordt gratis verzonden";
    document.getElementById("ship-fill").style.width = Math.min(100, total / FREE_SHIPPING * 100) + "%";
  }

  var drawer = document.getElementById("drawer");
  var drawerBg = document.getElementById("drawer-bg");
  function openDrawer() { if (drawer) { drawer.classList.add("open"); drawerBg.classList.add("open"); } }
  function closeDrawer() { if (drawer) { drawer.classList.remove("open"); drawerBg.classList.remove("open"); } }

  document.addEventListener("click", function (e) {
    var t = e.target;
    if (t.closest(".cart-btn")) { openDrawer(); }
    else if (t.closest("[data-close-drawer]") || t === drawerBg) { closeDrawer(); }
    else if (t.dataset && t.dataset.rm !== undefined) { cart.splice(+t.dataset.rm, 1); save(cart); render(); }
    else if (t.closest("[data-quick-add]")) {
      e.preventDefault();
      addToCart(t.closest("[data-quick-add]").dataset.quickAdd, "", 1);
    }
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDrawer(); });

  var checkout = document.getElementById("checkout");
  if (checkout) checkout.addEventListener("click", function () {
    alert("Demo-winkel: koppel hier je betaalprovider (bijv. Mollie of WooCommerce-checkout).");
  });

  /* ---------- Mobiel menu ---------- */
  var menuBtn = document.querySelector(".menu-btn");
  var nav = document.querySelector(".nav");
  if (menuBtn) menuBtn.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", open);
  });

  /* ---------- Legging-illustraties in kaarten ---------- */
  document.querySelectorAll("[data-legging]").forEach(function (el) {
    el.innerHTML = leggingSVG(el.dataset.color, el.dataset.legging);
  });

  /* ---------- Nieuwsbrief ---------- */
  document.querySelectorAll("form[data-newsletter]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      f.innerHTML = "<p><strong>Bedankt!</strong> Je staat op de lijst.</p>";
    });
  });

  render();
})();
