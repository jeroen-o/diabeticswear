/* Diabeticswear — navigatie, winkelmand, bestelaanvraag, shopfilters en productpagina.
   Geen externe afhankelijkheden. Catalogus komt uit assets/js/catalog.js (gegenereerd door tools/build.py). */
(function () {
  "use strict";

  var ROOT = document.documentElement.getAttribute("data-root") || "";
  var CAT = window.DW_CATALOG || {};
  var MAIL = "info@diabeticswear.com";
  var T = window.DW_I18N || {};
  var SHIP = { NL: { free: 30, cost: 4.25, label: T.nl || "Nederland", nl: "Nederland" }, BE: { free: 75, cost: 5.25, label: T.be || "België", nl: "België" } };
  var eur = new Intl.NumberFormat(T.locale || "nl-NL", { style: "currency", currency: "EUR" });
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- Opslag (sessionStorage met geheugen-fallback) ---------- */
  var mem = {};
  function get(k, d) { try { var v = sessionStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return k in mem ? mem[k] : d; } }
  function set(k, v) { mem[k] = v; try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* geheugen */ } }

  /* ---------- Melding bovenaan ---------- */
  var bar = $(".notice-bar");
  if (bar) {
    if (get("dw-notice", false)) bar.hidden = true;
    $(".notice-bar button").addEventListener("click", function () { bar.hidden = true; set("dw-notice", true); });
  }

  /* ---------- Mobiel menu ---------- */
  var nav = $(".nav"), navBg = $(".nav-bg"), menuBtn = $(".menu-btn");
  function navToggle(open) {
    nav.classList.toggle("open", open); if (navBg) navBg.classList.toggle("open", open);
    menuBtn.setAttribute("aria-expanded", open);
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () { navToggle(!nav.classList.contains("open")); });
    if (navBg) navBg.addEventListener("click", function () { navToggle(false); });
    if ($(".close-nav")) $(".close-nav").addEventListener("click", function () { navToggle(false); });
  }

  /* ---------- Toast ---------- */
  var toastEl;
  function toast(t) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "toast"; toastEl.setAttribute("role", "status"); document.body.appendChild(toastEl); }
    toastEl.textContent = t; toastEl.classList.add("show");
    clearTimeout(toastEl._t); toastEl._t = setTimeout(function () { toastEl.classList.remove("show"); }, 2600);
  }

  /* ---------- Winkelmand ---------- */
  var cart = get("dw-cart", []).filter(function (l) { return CAT[l.id]; });
  var country = get("dw-country", "NL");

  function totals() {
    var sub = cart.reduce(function (n, l) { return n + l.price * l.qty; }, 0);
    var s = SHIP[country];
    var ship = sub === 0 || sub >= s.free ? 0 : s.cost;
    return { sub: sub, ship: ship, total: sub + ship, rest: Math.max(0, s.free - sub), free: s.free };
  }

  function add(id, opts, qty, price) {
    var key = id + "|" + opts;
    var line = cart.filter(function (l) { return l.key === key; })[0];
    if (line) line.qty = Math.min(20, line.qty + qty);
    else cart.push({ key: key, id: id, opts: opts, qty: qty, price: price });
    set("dw-cart", cart); render(); openDrawer();
  }

  function render() {
    var count = cart.reduce(function (n, l) { return n + l.qty; }, 0);
    $$(".cart-count").forEach(function (e) { e.textContent = count; });
    var list = $("#d-items"); if (!list) return;
    if (!cart.length) {
      list.innerHTML = '<div class="empty"><p>' + T.empty + '</p><a class="btn btn-primary" href="' + ROOT + (T.shopPath || "winkel/") + '">' + T.viewAll + '</a></div>';
    } else {
      list.innerHTML = cart.map(function (l, i) {
        var p = CAT[l.id];
        return '<div class="drawer-item"><div class="thumb"><img src="' + ROOT + p.img + '" alt="" width="64" height="64"></div>' +
          '<div><strong>' + p.name + '</strong>' + (l.opts ? '<small>' + l.opts + '</small>' : "") +
          '<div class="lineqty"><button data-q="' + i + '" data-d="-1" aria-label="' + T.less + '">−</button><span>' + l.qty + '</span>' +
          '<button data-q="' + i + '" data-d="1" aria-label="' + T.more + '">+</button><button class="rm" data-rm="' + i + '">' + T.remove + '</button></div></div>' +
          '<strong>' + eur.format(l.price * l.qty) + '</strong></div>';
      }).join("");
    }
    var t = totals();
    $("#d-sub").textContent = eur.format(t.sub);
    $("#d-ship").textContent = t.ship ? eur.format(t.ship) : T.free;
    $("#d-total").textContent = eur.format(t.total);
    $("#d-country").value = country;
    var c = SHIP[country].label;
    $("#d-shipmsg").textContent = t.sub === 0 ? T.shipFrom.replace("{c}", c).replace("{a}", eur.format(t.free)) :
      t.rest > 0 ? T.shipRest.replace("{a}", eur.format(t.rest)).replace("{c}", c) : T.shipFree;
    $("#d-shipfill").style.width = Math.min(100, t.sub / t.free * 100) + "%";
    $("#d-checkout").disabled = !cart.length;
  }

  var drawer = $("#drawer"), drawerBg = $("#drawer-bg"), lastFocus;
  function openDrawer() { lastFocus = document.activeElement; drawer.classList.add("open"); drawerBg.classList.add("open"); $(".close", drawer).focus(); }
  function closeDrawer() { drawer.classList.remove("open"); drawerBg.classList.remove("open"); if (lastFocus) lastFocus.focus(); }

  document.addEventListener("click", function (e) {
    var t = e.target;
    if (t.closest(".cart-btn")) { openDrawer(); return; }
    if (t.closest("[data-close-drawer]") || t === drawerBg) { closeDrawer(); return; }
    if (t.dataset.rm !== undefined) { cart.splice(+t.dataset.rm, 1); set("dw-cart", cart); render(); return; }
    if (t.dataset.q !== undefined) {
      var l = cart[+t.dataset.q]; l.qty += +t.dataset.d;
      if (l.qty < 1) cart.splice(+t.dataset.q, 1);
      set("dw-cart", cart); render(); return;
    }
    var close = t.closest("[data-close]");
    if (close) { close.closest("dialog").close(); return; }
    if (t.tagName === "DIALOG") t.close();
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeDrawer(); if (nav) navToggle(false); } });
  var dc = $("#d-country");
  if (dc) dc.addEventListener("change", function () { country = dc.value; set("dw-country", country); render(); });

  /* ---------- Bestelaanvraag (via e-mail; nog geen online betaling) ---------- */
  var coDlg = $("#checkout-dlg");
  if (coDlg) {
    $("#d-checkout").addEventListener("click", function () {
      if (!cart.length) return;
      $("#co-country").value = country;
      closeDrawer(); coDlg.showModal();
    });
    $("#co-country").addEventListener("change", function () { country = this.value; set("dw-country", country); render(); });
    $("#co-form").addEventListener("submit", function (e) {
      e.preventDefault();
      var f = e.target, v = function (n) { return f.elements[n].value.trim(); };
      var t = totals();
      var lines = cart.map(function (l) { return "- " + l.qty + " x " + (CAT[l.id].name_nl || CAT[l.id].name) + (l.opts ? " (" + l.opts + ")" : "") + " = " + eur.format(l.price * l.qty); });
      var body = ["Bestelaanvraag via diabeticswear.com", "", "PRODUCTEN"].concat(lines).concat([
        "", "Subtotaal: " + eur.format(t.sub), "Verzendkosten (" + SHIP[country].nl + "): " + (t.ship ? eur.format(t.ship) : "gratis"), "Totaal: " + eur.format(t.total),
        "", "GEGEVENS", "Naam: " + v("naam"), "E-mail: " + v("email"), "Telefoon: " + v("tel"),
        "Adres: " + v("adres"), "Postcode en plaats: " + v("postcode") + " " + v("plaats"), "Land: " + SHIP[country].nl, "Taal website: " + document.documentElement.lang,
        "Voorkeur betaling: " + v("betaling"), "", "Opmerking: " + (v("opmerking") || "-")]).join("\n");
      window.location.href = "mailto:" + MAIL + "?subject=" + encodeURIComponent("Bestelaanvraag " + v("naam")) + "&body=" + encodeURIComponent(body);
      $("#co-done").hidden = false; f.hidden = true;
    });
    $("#co-clear").addEventListener("click", function () { cart = []; set("dw-cart", cart); render(); coDlg.close(); toast(T.thanks); });
  }

  /* ---------- Contactformulier (mailto) ---------- */
  var cf = $("#contact-form");
  if (cf) cf.addEventListener("submit", function (e) {
    e.preventDefault();
    var v = function (n) { return cf.elements[n].value.trim(); };
    var body = v("bericht") + "\n\n--\n" + v("naam") + "\n" + v("email") + (v("tel") ? "\n" + v("tel") : "");
    window.location.href = "mailto:" + MAIL + "?subject=" + encodeURIComponent((T.contactSubject || "Vraag via de website: ") + v("onderwerp")) + "&body=" + encodeURIComponent(body);
    $("#contact-done").hidden = false;
  });

  /* ---------- Shopfilters ---------- */
  var shop = $("#shop-grid");
  if (shop) {
    var chips = $$(".filters .chip"), sort = $("#sort");
    var cards = $$(".card", shop);
    var apply = function (cat) {
      chips.forEach(function (c) { c.setAttribute("aria-pressed", c.dataset.cat === cat); });
      cards.forEach(function (c) { c.hidden = cat !== "alle" && c.dataset.cats.split(" ").indexOf(cat) < 0; });
      $("#shop-count").textContent = cards.filter(function (c) { return !c.hidden; }).length + "";
      $("#shop-count").textContent = T.count.replace("{n}", $("#shop-count").textContent);
    };
    chips.forEach(function (c) { c.addEventListener("click", function () { apply(c.dataset.cat); history.replaceState(null, "", c.dataset.cat === "alle" ? location.pathname : "#" + c.dataset.cat); }); });
    sort.addEventListener("change", function () {
      var s = sort.value;
      cards.sort(function (a, b) {
        if (s === "laag") return a.dataset.price - b.dataset.price;
        if (s === "hoog") return b.dataset.price - a.dataset.price;
        return a.dataset.order - b.dataset.order;
      }).forEach(function (c) { shop.appendChild(c); });
    });
    var h = location.hash.slice(1);
    apply(chips.some(function (c) { return c.dataset.cat === h; }) ? h : "alle");
  }

  /* ---------- Tabs ---------- */
  var tabs = $$("[role=tab]");
  tabs.forEach(function (t) {
    t.addEventListener("click", function () {
      tabs.forEach(function (o) {
        o.setAttribute("aria-selected", o === t);
        document.getElementById(o.getAttribute("aria-controls")).hidden = o !== t;
      });
    });
  });
  $$("[data-tab]").forEach(function (a) {
    a.addEventListener("click", function (ev) { ev.preventDefault(); var t = document.getElementById(a.dataset.tab); t.click(); t.scrollIntoView({ behavior: "smooth", block: "start" }); });
  });

  /* ---------- Lightbox ---------- */
  var lb = $("#lightbox");
  function zoom(src, alt) { if (!lb) return; $("img", lb).src = src; $("img", lb).alt = alt || ""; lb.showModal(); }
  $$("[data-zoom]").forEach(function (el) {
    el.addEventListener("click", function () { zoom(el.dataset.zoom, el.getAttribute("aria-label")); });
    el.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); zoom(el.dataset.zoom, el.getAttribute("aria-label")); } });
  });

  /* ---------- Productpagina ---------- */
  var pd = $("#pdata");
  if (pd) {
    var P = JSON.parse(pd.textContent);
    var state = { img: 0, size: P.sizes.length === 1 ? P.sizes[0] : "", color: P.colors.length === 1 ? P.colors[0] : "", variant: P.variants.length ? 0 : -1 };
    var main = $("#gmain img"), thumbs = $$("#thumbs button");
    var show = function (i) {
      state.img = (i + P.imgs.length) % P.imgs.length;
      var b = ROOT + "assets/img/p/" + P.imgs[state.img];
      main.srcset = b + "-sm.webp 600w, " + b + ".webp 1200w";
      main.src = b + ".webp";
      thumbs.forEach(function (b, k) { b.setAttribute("aria-current", k === state.img); });
    };
    thumbs.forEach(function (b, k) { b.addEventListener("click", function () { show(k); }); });
    $$(".gnav").forEach(function (b) { b.addEventListener("click", function (e) { e.stopPropagation(); show(state.img + (+b.dataset.d)); }); });
    $("#gmain").addEventListener("click", function () { zoom(ROOT + "assets/img/p/" + P.imgs[state.img] + ".webp", main.alt); });
    var tx; $("#gmain").addEventListener("touchstart", function (e) { tx = e.touches[0].clientX; }, { passive: true });
    $("#gmain").addEventListener("touchend", function (e) { var d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 40) show(state.img + (d < 0 ? 1 : -1)); });

    var price = function () { return state.variant >= 0 ? P.variants[state.variant][1] : P.price; };
    var sync = function () {
      $$("[data-size]").forEach(function (b) {
        var need = P.rules[b.dataset.size];
        b.disabled = !!(need && state.color && state.color !== need);
        b.setAttribute("aria-pressed", b.dataset.size === state.size);
        b.title = b.disabled ? T.onlyIn.replace("{c}", need.toLowerCase()) : "";
      });
      $$("[data-color]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.color === state.color); });
      $$("[data-variant]").forEach(function (b) { b.setAttribute("aria-pressed", +b.dataset.variant === state.variant); });
      if ($("#sel-size")) $("#sel-size").textContent = state.size || T.chooseSize;
      if ($("#sel-color")) $("#sel-color").textContent = state.color || T.chooseColor;
      $$(".js-price").forEach(function (e) { e.textContent = eur.format(price()); });
    };
    $$("[data-size]").forEach(function (b) { b.addEventListener("click", function () { state.size = b.dataset.size; msg(""); sync(); }); });
    $$("[data-color]").forEach(function (b) {
      b.addEventListener("click", function () {
        state.color = b.dataset.color;
        var need = P.rules[state.size]; if (need && need !== state.color) state.size = "";
        msg(""); sync();
      });
    });
    $$("[data-variant]").forEach(function (b) { b.addEventListener("click", function () { state.variant = +b.dataset.variant; sync(); }); });

    var qty = $("#qty");
    var setQ = function (n) { qty.value = Math.max(1, Math.min(20, parseInt(n, 10) || 1)); };
    $("#qmin").addEventListener("click", function () { setQ(+qty.value - 1); });
    $("#qplus").addEventListener("click", function () { setQ(+qty.value + 1); });
    qty.addEventListener("change", function () { setQ(qty.value); });

    var m = $("#msg");
    function msg(t) { m.textContent = t; m.classList.toggle("err", !!t); }
    function buy() {
      if (P.colors.length > 1 && !state.color) { msg(T.pickColor); return; }
      if (P.sizes.length > 1 && !state.size) { msg(T.pickSize); return; }
      var o = [];
      if (P.colors.length > 1) o.push(P.colorLabel + ": " + state.color);
      if (P.sizes.length > 1) o.push(T.size + " " + state.size);
      if (state.variant >= 0) o.push(P.variants[state.variant][0]);
      add(P.slug, o.join(" · "), +qty.value, price());
      toast(T.added);
    }
    $("#add").addEventListener("click", buy);
    var sb = $("#sticky-buy");
    $("#sticky-add").addEventListener("click", function () {
      if ((P.sizes.length > 1 && !state.size) || (P.colors.length > 1 && !state.color)) { $("#add").scrollIntoView({ behavior: "smooth", block: "center" }); buy(); return; }
      buy();
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { sb.classList.toggle("show", !en[0].isIntersecting && en[0].boundingClientRect.top < 0); }).observe($("#add"));
    }
    sync();
  }

  render();
})();
