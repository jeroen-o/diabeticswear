#!/usr/bin/env python3
"""Genereert de statische site van Diabeticswear uit tools/content.json.

Gebruik:  python3 tools/build.py
De gegenereerde HTML wordt mee gecommit; de site zelf heeft geen build-step nodig.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://diabeticswear.com/"
C = json.load(open(os.path.join(ROOT, "tools", "content.json"), encoding="utf-8"))
PRODUCTS = C["products"]
BY = {p["slug"]: p for p in PRODUCTS}
CATS = C["cats"]
MAIL = "info@diabeticswear.com"
TEL, TEL_LINK = "+31 6 10022060", "tel:+31610022060"
ADDR = "De Wel 14-16, 3871 MV Hoevelaken"
e = html.escape

CATLABEL = {"tshirts": "T-shirts", "hemden": "Hemden", "sportlegging": "Sportlegging", "bikershorts": "Bikershorts",
            "rokken": "Sport rok", "sokken": "Compressiesokken", "patches": "Patch pleisters", "accessoires": "Accessoires"}
CATPAGE = {"tshirts": "diabetes-t-shirts-insulinepomp", "hemden": "diabetes-hemden-insulinepomp",
           "sportlegging": "diabetes-2-pocket-sportlegging", "bikershorts": "diabetes-2-pocket-bikershort-sporten",
           "rokken": "diabetes-2-pocket-bikershort-sporten", "sokken": "diabetes-compressiesokken",
           "patches": "productpagina-patch-pleisters", "accessoires": "producten-kleding-accessoires-overig"}


def eur(v):
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "€ " + s


def img(base, R, sm=False):
    return f"{R}assets/img/p/{base}{'-sm' if sm else ''}.webp"


# ---------------------------------------------------------------- layout

def head(R, path, title, desc, extra="", og_img=None):
    canon = DOMAIN + path
    og = og_img or "assets/img/p/diabetes-2-pocket-sportlegging-1.webp"
    return f"""<!doctype html>
<html lang="nl" data-root="{R}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Diabeticswear">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}{og}">
<meta name="theme-color" content="#2BAA92">
<link rel="icon" href="{R}assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{R}assets/img/logo-dw.png">
<link rel="stylesheet" href="{R}assets/css/style.css">
{extra}</head>
<body>
<a class="skip" href="#main">Naar de inhoud</a>
"""


NAV = [
    ("Home", "", None),
    ("Kleding", "diabetes-kleding-insulinepomp/", [
        ("T-shirts", "diabetes-t-shirts-insulinepomp/"), ("Hemden", "diabetes-hemden-insulinepomp/"),
        ("Sportlegging", "diabetes-2-pocket-sportlegging/"), ("Bikershorts & sport rok", "diabetes-2-pocket-bikershort-sporten/"),
        ("Compressiesokken", "diabetes-compressiesokken/"), ("Combi deal", "product/sportlegging-bikershort-insulinepomp/"),
        ("Alle kleding", "diabetes-kleding-insulinepomp/")]),
    ("Patch pleisters", "productpagina-patch-pleisters/", None),
    ("Accessoires", "producten-kleding-accessoires-overig/", None),
    ("Alle producten", "winkel/", None),
    ("Over ons", "over-ons/", None),
    ("Contact", "contact/", None),
]


def logo(R):
    return (f'<a class="logo" href="{R}" aria-label="Diabeticswear, naar de homepage">'
            f'<span class="logo-mark" aria-hidden="true"></span><span>Diabetics<b>Wear</b></span></a>')


def header(R, active):
    items = []
    for label, href, sub in NAV:
        if label == "Home":
            continue
        cur = ' aria-current="page"' if active == href else ""
        if sub:
            subs = "".join(f'<a href="{R}{h}">{e(l)}</a>' for l, h in sub)
            items.append(f'<div class="has-sub"><a href="{R}{href}"{cur}>{label}</a><div class="sub">{subs}</div></div>')
        else:
            items.append(f'<a href="{R}{href}"{cur}>{label}</a>')
    return f"""<div class="topbar"><span>Gratis verzending in NL vanaf € 30</span><span>Levering in 2-3 werkdagen</span><span>14 dagen retour</span></div>
<header class="header">
  <div class="container">
    {logo(R)}
    <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    <nav class="nav" id="nav" aria-label="Hoofdmenu">
      {"".join(items)}
    </nav>
    <button class="cart-btn" aria-label="Winkelmand openen"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 7h12l-1 13H7z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg><span class="label">Mand</span><span class="cart-count">0</span></button>
  </div>
</header>
"""


def footer(R):
    return f"""<footer class="footer">
  <div class="container">
    <div class="cols">
      <div>
        {logo(R)}
        <p>Kleding met slimme pompzakjes en een discrete slangdoorvoer, en accessoires die het leven met diabetes makkelijker maken.</p>
      </div>
      <div><h4>Shop</h4><ul>
        <li><a href="{R}diabetes-t-shirts-insulinepomp/">T-shirts</a></li>
        <li><a href="{R}diabetes-hemden-insulinepomp/">Hemden</a></li>
        <li><a href="{R}diabetes-2-pocket-sportlegging/">Sportlegging</a></li>
        <li><a href="{R}diabetes-2-pocket-bikershort-sporten/">Bikershorts &amp; sport rok</a></li>
        <li><a href="{R}diabetes-compressiesokken/">Compressiesokken</a></li>
        <li><a href="{R}productpagina-patch-pleisters/">Patch pleisters</a></li>
        <li><a href="{R}producten-kleding-accessoires-overig/">Accessoires</a></li>
      </ul></div>
      <div><h4>Service</h4><ul>
        <li><a href="{R}veelgestelde-vragen/">Veelgestelde vragen</a></li>
        <li><a href="{R}terugbetaalde-retourneringen/">Retourbeleid</a></li>
        <li><a href="{R}over-ons/">Over ons</a></li>
        <li><a href="{R}contact/">Contact</a></li>
      </ul></div>
      <div><h4>Contact</h4><ul>
        <li><a href="mailto:{MAIL}">{MAIL}</a></li>
        <li><a href="{TEL_LINK}">{TEL}</a></li>
        <li>De Wel 14-16<br>3871 MV Hoevelaken</li>
        <li>Reactie binnen 24 uur</li>
      </ul></div>
    </div>
    <div class="bottom">
      <span>© 2026 Diabeticswear · KvK 91840376 · BTW NL004919866B33<br>Freestyle Libre, Dexcom en Omnipod zijn merken van hun respectievelijke eigenaren; Diabeticswear is hier niet aan gelieerd.</span>
      <span><a href="{R}algemene-voorwaarden/">Algemene voorwaarden</a> · <a href="{R}privacybeleid/">Privacy</a> · <a href="{R}terugbetaalde-retourneringen/">Retourbeleid</a></span>
    </div>
  </div>
</footer>
<aside class="drawer" id="drawer" aria-label="Winkelmand">
  <header><h2>Winkelmand</h2><button class="close" data-close-drawer aria-label="Sluiten">×</button></header>
  <div class="drawer-items" id="d-items"></div>
  <footer>
    <div class="row"><span>Subtotaal</span><span id="d-sub">€ 0,00</span></div>
    <div class="row"><span>Verzenden naar <label class="sr-only" for="d-country">Land</label><select id="d-country"><option value="NL">Nederland</option><option value="BE">België</option></select></span><span id="d-ship">Gratis</span></div>
    <div class="ship-bar"><span id="d-shipfill"></span></div>
    <small id="d-shipmsg"></small>
    <div class="total" style="margin-top:.8rem"><span>Totaal</span><span id="d-total">€ 0,00</span></div>
    <button class="btn btn-primary btn-block" id="d-checkout">Bestelling afronden</button>
  </footer>
</aside>
<div class="drawer-bg" id="drawer-bg"></div>
<dialog class="modal" id="checkout-dlg" aria-labelledby="co-title"><div class="inner">
  <header><h2 id="co-title" style="margin:0">Bestelling afronden</h2><button class="close" style="background:none;border:0;font-size:1.6rem;cursor:pointer" data-close aria-label="Sluiten">×</button></header>
  <form class="form" id="co-form">
    <p class="small" style="margin:0">Vul je gegevens in. Je bestelling gaat als e-mail naar {MAIL}; je ontvangt daarna de betaalinstructies.</p>
    <div class="two"><label>Naam *<input name="naam" required autocomplete="name"></label><label>E-mail *<input name="email" type="email" required autocomplete="email"></label></div>
    <div class="two"><label>Telefoon<input name="tel" type="tel" autocomplete="tel"></label><label>Land<select name="land" id="co-country"><option value="NL">Nederland</option><option value="BE">België</option></select></label></div>
    <label>Straat en huisnummer *<input name="adres" required autocomplete="street-address"></label>
    <div class="two"><label>Postcode *<input name="postcode" required autocomplete="postal-code"></label><label>Plaats *<input name="plaats" required autocomplete="address-level2"></label></div>
    <label>Voorkeur betaling<select name="betaling"><option>iDEAL</option><option>Bancontact</option><option>Klarna</option><option>Overboeking</option></select></label>
    <label>Opmerking<textarea name="opmerking" rows="3" style="min-height:80px"></textarea></label>
    <button class="btn btn-primary" type="submit">Bestelling versturen via e-mail</button>
    <p class="small" style="margin:0">Door te bestellen ga je akkoord met de <a href="{R}algemene-voorwaarden/">algemene voorwaarden</a>. We gebruiken je gegevens alleen voor je bestelling (<a href="{R}privacybeleid/">privacybeleid</a>).</p>
  </form>
  <div id="co-done" hidden>
    <p><strong>Je e-mailprogramma is geopend met je bestelling.</strong> Verstuur de e-mail om je bestelling te plaatsen. Opende er niets? Mail je bestelling dan naar <a href="mailto:{MAIL}">{MAIL}</a>.</p>
    <button class="btn btn-primary" id="co-clear" type="button">Verstuurd, winkelmand legen</button>
  </div>
</div></dialog>
<dialog class="modal lightbox" id="lightbox" aria-label="Afbeelding vergroot"><button class="close" style="border:0;font-size:1.5rem;cursor:pointer" data-close aria-label="Sluiten">×</button><img alt=""></dialog>
<script src="{R}assets/js/catalog.js"></script>
<script src="{R}assets/js/main.js"></script>
</body>
</html>
"""


def page(path, title, desc, body, active=None, extra="", og=None):
    depth = path.count("/")
    R = "../" * depth
    out = head(R, path, title, desc, extra, og) + header(R, active if active is not None else path) + \
        f'<main id="main">\n{body(R)}\n</main>\n' + footer(R)
    fp = os.path.join(ROOT, path, "index.html") if path else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(out)
    PAGES.append(path)


PAGES = []


# ---------------------------------------------------------------- componenten

def price_html(p):
    if p.get("variants"):
        return f'<span class="from">vanaf</span> {eur(p["variants"][0][1])}'
    if p.get("compare"):
        return f'<s>{eur(p["compare"])}</s>{eur(p["price"])}'
    return eur(p["price"])


def card(p, R, order=0):
    alt = e(p["name"])
    second = f'<img class="alt" src="{img(p["imgs"][1], R, True)}" alt="" loading="lazy" width="600" height="600">' if len(p["imgs"]) > 1 else ""
    tag = f'<span class="tag">{e(p["tag"])}</span>' if p.get("tag") else ""
    cols = p.get("colors", [])
    dots = '<div class="dots">' + "".join(f'<i style="background:{c[1]}" title="{e(c[0])}"></i>' for c in cols) + "</div>" if len(cols) > 1 else ""
    cats = p["cat"] + (" kleding" if p["group"] in ("sport", "shirts", "sokken") else "")
    price = p["variants"][0][1] if p.get("variants") else p["price"]
    return (f'<a class="card" href="{R}product/{p["slug"]}/" data-cats="{cats}" data-price="{price}" data-order="{order}">'
            f'<div class="card-media"><img src="{img(p["imgs"][0], R, True)}" alt="{alt}" loading="lazy" width="600" height="600">{second}{tag}</div>'
            f'<div class="card-body"><small>{CATLABEL[p["cat"]]}</small><h3>{alt}</h3>{dots}<span class="price">{price_html(p)}</span></div></a>')


def grid(ps, R, gid=""):
    return f'<div class="grid"{f" id={gid}" if gid else ""}>' + "".join(card(p, R, i) for i, p in enumerate(ps)) + "</div>"


def hero_small(eyebrow, title, text, R):
    return (f'<section class="hero small"><div class="container"><div><span class="eyebrow">{e(eyebrow)}</span>'
            f'<h1>{e(title)}</h1>{f"<p class=lead>{text}</p>" if text else ""}</div></div></section>')


def crumbs(R, items):
    out = [f'<a href="{R}">Home</a>'] + [f'<a href="{R}{h}">{e(l)}</a>' if h is not None else e(l) for l, h in items]
    return f'<nav class="crumbs container" aria-label="Kruimelpad">{" / ".join(out)}</nav>'


def faq_html(items):
    return "".join(f'<details><summary>{e(q)}</summary><p>{linkify(e(a))}</p></details>' for q, a in items)


def linkify(t):
    return t.replace(MAIL, f'<a href="mailto:{MAIL}">{MAIL}</a>')


def reviews_html(rs, single=False):
    out = "".join(f'<blockquote class="review" style="margin:0"><p>“{e(txt)}”</p><footer>{e(name)} · over {e(prod)}</footer></blockquote>'
                  for name, prod, txt, _ in rs)
    return f'<div class="reviews"{" style=grid-template-columns:1fr" if single else ""}>{out}</div>'


USP_ICON = {
    "move": '<circle cx="13" cy="4" r="2"/><path d="m7 21 3-6 3 3v3"/><path d="M6 12l3-4 4 1 3 3h3"/>',
    "shield": '<path d="M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7z"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/>',
    "truck": '<path d="M3 7h13v10H3z"/><path d="M16 10h3l2 3v4h-5"/><circle cx="7" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>',
    "return": '<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
}


def usp(i, t, d):
    return (f'<div class="usp"><div class="usp-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{USP_ICON[i]}</svg></div><div><h3>{t}</h3><p>{d}</p></div></div>')


def usps_service():
    return '<div class="container usps">' + usp("truck", "Gratis verzending", "In NL vanaf € 30, naar België vanaf € 75") + \
        usp("shield", "Discreet verpakt", "Levering binnen 2-3 werkdagen") + usp("return", "14 dagen retour", "Ruilen of retourneren binnen 14 dagen") + \
        usp("chat", "Reactie binnen 24 uur", "Vragen? Mail of bel ons gerust") + "</div>"


def usps_values():
    return '<div class="usps">' + usp("move", "Bewegingsvrijheid", "Sporten, werken of ontspannen: je pomp blijft veilig op zijn plek.") + \
        usp("shield", "Geen loshangende slang", "Het gaatje in de zak houdt de infuusslang netjes weg.") + \
        usp("eye", "Discreet", "De slang is weggewerkt, voor een onopvallende look.") + \
        usp("heart", "Kwaliteit", "Elk kledingstuk wordt zorgvuldig getest op comfort en duurzaamheid.") + "</div>"


def perks():
    return ('<ul class="perks"><li>Gratis verzending in NL vanaf € 30, naar België vanaf € 75</li>'
            '<li>Levering binnen 2-3 werkdagen</li><li>14 dagen retourneren</li>'
            f'<li>Vragen? Reactie binnen 24 uur via <a href="mailto:{MAIL}">{MAIL}</a></li></ul>')


def newsletter_contact(R):
    return f"""<div class="container" style="margin-top:4rem">
  <div class="newsletter">
    <div><h2 style="margin-bottom:.3rem">Twijfel je over je maat of pomp?</h2><p style="margin:0;opacity:.9">Stuur ons je gebruikelijke maat of het type insulinepomp. We denken mee en reageren binnen 24 uur.</p></div>
    <div style="display:flex;gap:.5rem;flex-wrap:wrap"><a class="btn btn-light" href="{R}contact/">Neem contact op</a><a class="btn btn-ghost" href="mailto:{MAIL}">{MAIL}</a></div>
  </div>
</div>"""


# ---------------------------------------------------------------- pagina's

def build_home():
    feat = [BY[s] for s in ("patch-pleister-freestyle-libre-2", "diabetes-2-pocket-sportlegging", "diabetes-2-pocket-bikershort", "diabetes-v-hals-t-shirt")]
    patches = [p for p in PRODUCTS if p["cat"] == "patches"]
    ld = json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": "Diabeticswear", "url": DOMAIN,
                     "email": MAIL, "telephone": "+31610022060",
                     "address": {"@type": "PostalAddress", "streetAddress": "De Wel 14-16", "postalCode": "3871 MV",
                                 "addressLocality": "Hoevelaken", "addressCountry": "NL"}}, ensure_ascii=False)

    def body(R):
        reviews = C["reviews"]
        return f"""<section class="hero">
  <div class="container">
    <div>
      <span class="eyebrow">De diabetesshop voor insulinepomp-gebruikers</span>
      <h1>Vrij bewegen met je insulinepomp.</h1>
      <p class="lead">Kleding met slimme pompzakjes en een discrete slangdoorvoer, en transparante patch pleisters die je sensor of pod extra houvast geven.</p>
      <div class="hero-actions">
        <a class="btn btn-light" href="{R}winkel/">Bekijk alle producten</a>
        <a class="btn btn-ghost" href="{R}productpagina-patch-pleisters/">Shop patch pleisters</a>
      </div>
      <div class="hero-badges"><span>2 zakjes voor je pomp</span><span>Gaatje voor de infuusslang</span><span>14 dagen retour</span></div>
    </div>
    <div class="hero-visual" aria-hidden="true">
      <img class="h1" src="{img("diabetes-2-pocket-sportlegging-1", R)}" alt="">
      <img class="h2" src="{img("patch-pleister-freestyle-libre-2-1", R, True)}" alt="">
      <img class="h3" src="{img("diabetes-v-hals-t-shirt-3", R, True)}" alt="">
    </div>
  </div>
</section>

<section class="bg-white" style="padding:2.5rem 0">
  {usps_service()}
</section>

<section id="kleding">
  <div class="container">
    <div class="section-head">
      <div><span class="eyebrow">Categorieën</span><h2>Vind wat bij jou past</h2></div>
      <p>Van t-shirts en sportkleding met pompzakjes tot patch pleisters voor je sensor.</p>
    </div>
    <div class="cats">
      <a class="cat cat-1" href="{R}diabetes-2-pocket-sportlegging/"><span class="stripe"></span><small>Legging, bikershort, rok</small><h3>Sportkleding</h3></a>
      <a class="cat cat-2" href="{R}diabetes-t-shirts-insulinepomp/"><span class="stripe"></span><small>Met 2 pompzakjes</small><h3>T-shirts &amp; hemden</h3></a>
      <a class="cat cat-3" href="{R}productpagina-patch-pleisters/"><span class="stripe"></span><small>Libre, Dexcom, Omnipod</small><h3>Patch pleisters</h3></a>
      <a class="cat cat-4" href="{R}diabetes-compressiesokken/"><span class="stripe"></span><small>Sokken &amp; organizer</small><h3>Overig</h3></a>
    </div>
  </div>
</section>

<section class="bg-white">
  <div class="container">
    <div class="section-head">
      <div><span class="eyebrow">Populair</span><h2>Onze bestsellers</h2></div>
      <a class="btn btn-primary" href="{R}winkel/">Bekijk alles</a>
    </div>
    {grid(feat, R)}
  </div>
</section>

<section>
  <div class="container split">
    <div class="split-visual" style="padding:0;overflow:hidden"><img src="{img("diabetes-2-pocket-sportlegging-3", R)}" alt="Sportlegging met insulinepomp in de zijzak" loading="lazy" width="1200" height="1200"></div>
    <div>
      <span class="eyebrow">Zo werkt het</span>
      <h2>Je pomp in het zakje, de slang erdoor</h2>
      <p>Al onze kleding heeft geïntegreerde zakjes waarin je je insulinepomp stevig opbergt. Via het discrete gaatje aan de binnenkant van de zak loopt de infuusslang netjes naar je pomp. Zo hangt er niets los.</p>
      <ul class="checklist">
        <li>2 zakjes: kies zelf links of rechts</li>
        <li>Stevig afgewerkt gaatje voor de infuusslang</li>
        <li>Zakjes ook handig voor je telefoon of sleutels</li>
        <li>T-shirts en hemden met klittenbandsluiting</li>
      </ul>
      <a class="btn btn-primary" href="{R}diabetes-kleding-insulinepomp/">Bekijk alle kleding</a>
    </div>
  </div>
</section>

<section id="patches" class="bg-white">
  <div class="container">
    <div class="section-head">
      <div><span class="eyebrow">Patch pleisters</span><h2>Extra houvast voor je sensor</h2></div>
      <p>Transparante, waterbestendige patch pleisters met een uitsparing voor je sensor of pod.</p>
    </div>
    {grid(patches, R)}
  </div>
</section>

<section>
  <div class="container split">
    <div>
      <span class="eyebrow">Combi deal</span>
      <h2>Sportlegging + bikershort voor {eur(48.95)}</h2>
      <p>De 2-Pocket Sportlegging en de 2-Pocket Bikershort samen, in plaats van {eur(51.90)}. Voor intensieve workouts én warme dagen of onder een jurk.</p>
      <a class="btn btn-primary" href="{R}product/sportlegging-bikershort-insulinepomp/">Bekijk de combi deal</a>
    </div>
    <div class="split-visual" style="padding:0;overflow:hidden"><img src="{img("sportlegging-bikershort-insulinepomp-1", R)}" alt="Combi deal sportlegging en bikershort" loading="lazy" width="1200" height="1200"></div>
  </div>
</section>

<section class="bg-white" id="recensies">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Recensies</span><h2>Wat klanten zeggen</h2></div><p>Echte ervaringen, ook de verbeterpunten.</p></div>
    {reviews_html(reviews)}
  </div>
</section>

<section id="faq">
  <div class="container faq">
    <div style="text-align:center;margin-bottom:2rem"><span class="eyebrow">FAQ</span><h2>Veelgestelde vragen</h2></div>
    {faq_html([C["faq"][1][1][1], C["faq"][1][1][0], C["faq"][2][1][0], C["faq"][2][1][1], C["faq"][3][1][1]])}
    <p style="text-align:center;margin-top:1.4rem"><a class="btn btn-primary" href="{R}veelgestelde-vragen/">Alle vragen</a></p>
  </div>
</section>
{newsletter_contact(R)}"""
    page("", "De diabetesshop voor insulinepomp gebruikers | Diabeticswear",
         "Kleding met pompzakjes en discrete slangdoorvoer, en transparante patch pleisters voor je sensor. Gratis verzending in NL vanaf € 30.",
         body, extra=f'<script type="application/ld+json">{ld}</script>\n')


SHOP_ORDER = ["diabetes-2-pocket-sportlegging", "diabetes-2-pocket-bikershort", "sportlegging-bikershort-insulinepomp", "2-pocket-sport-rok-voor-diabetes",
              "diabetes-v-hals-t-shirt", "diabetes-ronde-hals-t-shirt", "diabetes-v-hals-hemd", "diabetes-ronde-hals-hemd",
              "patch-pleister-freestyle-libre-2", "patch-pleisters-dexcom-g6-40-stuks", "patch-pleisters-dexcom-g7-40-stuks", "patch-pleisters-omnipod-50-125-stuks",
              "compressiesokken-kort", "compressiesokken-lang", "insuline-organizer"]


def build_shop():
    chips = [("alle", "Alles"), ("kleding", "Kleding"), ("tshirts", "T-shirts"), ("hemden", "Hemden"), ("sportlegging", "Sportlegging"),
             ("bikershorts", "Bikershorts"), ("rokken", "Sport rok"), ("sokken", "Sokken"), ("patches", "Patch pleisters"), ("accessoires", "Accessoires")]

    def body(R):
        ch = "".join(f'<button class="chip" type="button" data-cat="{k}" aria-pressed="false">{l}</button>' for k, l in chips)
        return (hero_small("Winkel", "Alle producten", "Kleding met pompzakjes, patch pleisters en accessoires voor het leven met diabetes.", R) +
                f'<section><div class="container"><div class="filters" role="group" aria-label="Filter op categorie">{ch}'
                f'<label class="sr-only" for="sort">Sorteren</label><select id="sort"><option value="std">Aanbevolen</option><option value="laag">Prijs: laag naar hoog</option><option value="hoog">Prijs: hoog naar laag</option></select></div>'
                f'<p class="small" id="shop-count" style="margin:-.6rem 0 1rem"></p>' + grid([BY[s] for s in SHOP_ORDER], R, "shop-grid") + '</div></section>' +
                f'<section class="bg-white" style="padding:2.5rem 0">{usps_service()}</section>')
    page("winkel/", "Alle producten | Diabeticswear", "Bekijk alle producten van Diabeticswear: t-shirts, hemden, sportleggings en bikershorts met pompzakjes, compressiesokken, patch pleisters en accessoires.", body)


def build_category(c):
    ps = [p for p in PRODUCTS if p["cat"] in c["cats"]]
    ps.sort(key=lambda p: SHOP_ORDER.index(p["slug"]))

    def body(R):
        out = hero_small(c["name"], c["h1"], e(c["intro"]), R)
        out += f'<section><div class="container">{grid(ps, R)}</div></section>'
        if c.get("body"):
            bl = "".join(f"<li>{e(b)}</li>" for b in c.get("bullets", []))
            out += f'<section class="bg-white"><div class="container faq"><h2>Over onze {e(c["name"].lower())}</h2>'
            out += "".join(f"<p>{e(p)}</p>" for p in c["body"]) + (f'<ul class="checklist">{bl}</ul>' if bl else "") + "</div></section>"
        if c.get("faq"):
            out += f'<section><div class="container faq"><div style="text-align:center;margin-bottom:2rem"><span class="eyebrow">FAQ</span><h2>Veelgestelde vragen</h2></div>{faq_html(c["faq"])}</div></section>'
        return out + newsletter_contact(R)
    page(c["slug"] + "/", f'{c["h1"]} | Diabeticswear', c["intro"], body)


def related(p):
    same = [q for q in PRODUCTS if q["group"] == p["group"] and q["slug"] != p["slug"]]
    rest = [q for q in PRODUCTS if q["group"] != p["group"] and q.get("tag")]
    return (same + rest)[:4]


def build_product(p):
    path = f'product/{p["slug"]}/'
    imgs = p["imgs"]
    sizes, colors, variants = p.get("sizes", []), p.get("colors", []), p.get("variants", [])
    rules = p.get("rules", {})
    pdata = {"slug": p["slug"], "price": p["price"], "imgs": imgs, "sizes": sizes, "colors": [c[0] for c in colors],
             "rules": rules, "variants": variants, "colorLabel": p.get("color_label", "Kleur")}
    offers = {"@type": "Offer", "priceCurrency": "EUR", "price": f'{p["price"]:.2f}', "url": DOMAIN + path}
    if variants:
        offers = {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": f"{variants[0][1]:.2f}", "highPrice": f"{variants[-1][1]:.2f}", "offerCount": len(variants)}
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p["meta"],
          "image": [f"{DOMAIN}assets/img/p/{b}.webp" for b in imgs], "brand": {"@type": "Brand", "name": "Diabeticswear"}, "offers": offers}
    crumbs_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
        {"@type": "ListItem", "position": 2, "name": CATLABEL[p["cat"]], "item": DOMAIN + CATPAGE[p["cat"]] + "/"},
        {"@type": "ListItem", "position": 3, "name": p["name"]}]}
    rv = [r for r in C["reviews"] if r[3] == p["group"]]
    if p["group"] == "sport":
        rv = [r for r in C["reviews"] if "Bikershort" in r[1]]

    def body(R):
        alt = e(p["name"])
        start = variants[0][1] if variants else p["price"]
        thumbs = "".join(f'<button type="button" aria-current="{str(i == 0).lower()}" aria-label="Afbeelding {i + 1}"><img src="{img(b, R, True)}" alt="" width="600" height="600" loading="lazy"></button>' for i, b in enumerate(imgs))
        compare = f'<s>{eur(p["compare"])}</s>' if p.get("compare") else ""
        save = f'<span class="save">Bespaar {eur(p["compare"] - p["price"])}</span>' if p.get("compare") else ""
        hl = "".join(f'<div class="hl"><strong>{e(u)}</strong></div>' for u in p.get("usp", []))
        opts = ""
        if variants:
            vb = "".join(f'<button type="button" class="size" data-variant="{i}" aria-pressed="false">{e(v[0])} · {eur(v[1])}</button>' for i, v in enumerate(variants))
            opts += f'<div class="opt"><div class="opt-label"><span>Aantal stuks</span></div><div class="sizes">{vb}</div>' + \
                    (f'<p class="hint">{linkify(e(p["variant_note"]))}</p>' if p.get("variant_note") else "") + "</div>"
        if len(colors) > 1:
            cb = "".join(f'<button type="button" class="swatch" data-color="{e(c[0])}" aria-pressed="false" aria-label="{e(c[0])}" title="{e(c[0])}" style="background:{c[1]}"></button>' for c in colors)
            opts += f'<div class="opt"><div class="opt-label"><span>{e(p.get("color_label", "Kleur"))}: <span id="sel-color" style="font-weight:600"></span></span></div><div class="swatches">{cb}</div></div>'
        elif colors:
            opts += f'<div class="opt"><div class="opt-label"><span>Kleur: <span style="font-weight:600">{e(colors[0][0])}</span></span></div></div>'
        if len(sizes) > 1:
            sb = "".join(f'<button type="button" class="size" data-size="{s}" aria-pressed="false">{s}</button>' for s in sizes)
            chart = f'<button type="button" data-zoom="{img(imgs[p["sizechart"] - 1], R)}" aria-label="Maattabel {alt}">Maattabel</button>' if p.get("sizechart") else ""
            rule_txt = " ".join(f"{s} alleen in {c.lower()}." for s, c in rules.items())
            opts += (f'<div class="opt"><div class="opt-label"><span>Maat: <span id="sel-size" style="font-weight:600"></span></span>{chart}</div><div class="sizes">{sb}</div>'
                     + (f'<p class="hint">{rule_txt}</p>' if rule_txt else "") + "</div>")
        elif sizes:
            opts += f'<div class="opt"><div class="opt-label"><span>Maat: <span style="font-weight:600">{e(sizes[0])} (unisex)</span></span></div></div>'
        note = f'<div class="advice"><strong>Let op:</strong> deze producten vallen groot uit. We adviseren een maat kleiner te bestellen dan normaal. Bekijk de maattabel of <a href="mailto:{MAIL}">vraag ons om advies</a>.</div>' if p.get("note") else ""

        prose = []
        for kind, val in p["body"]:
            if kind == "p":
                prose.append(f"<p>{linkify(e(val))}</p>")
            elif kind == "h3":
                prose.append(f"<h3>{e(val)}</h3>")
            else:
                prose.append("<ul class='checklist'>" + "".join(f"<li>{e(x)}</li>" for x in val) + "</ul>")
        specs = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in p["specs"])
        tabs = [("desc", "Beschrijving", f'<div class="prose">{"".join(prose)}</div>')]
        if specs:
            tabs.append(("specs", "Specificaties", f'<div class="table-wrap"><table>{specs}</table></div>'))
        if p.get("sizechart"):
            tabs.append(("size", "Maattabel", f'<p>De maten zijn in centimeters. De t-shirts en hemden vallen groot uit: bestel bij twijfel een maat kleiner.</p>'
                         f'<div class="sizechart" data-zoom="{img(imgs[p["sizechart"] - 1], R)}" role="button" tabindex="0" aria-label="Maattabel vergroten">'
                         f'<img src="{img(imgs[p["sizechart"] - 1], R)}" alt="Maattabel {alt}" loading="lazy" width="1200" height="1200"></div>'))
        tabs.append(("ship", "Verzenden &amp; retour",
                     f'<p><strong>Levering:</strong> we streven ernaar je bestelling binnen 2-3 werkdagen te bezorgen.</p>'
                     f'<p><strong>Nederland:</strong> gratis vanaf € 30, daaronder € 4,25.</p><p><strong>België:</strong> gratis vanaf € 75, daaronder € 5,25.</p>'
                     f'<p><strong>Retour:</strong> binnen 14 dagen na ontvangst, ongebruikt en in de originele verpakking. Retourkosten zijn voor eigen rekening, tenzij het product defect of verkeerd geleverd is. '
                     f'<a href="{R}terugbetaalde-retourneringen/">Lees ons retourbeleid</a>.</p>'))
        tabbar = "".join(f'<button role="tab" aria-selected="{str(i == 0).lower()}" aria-controls="t-{k}" id="tab-{k}">{l}</button>' for i, (k, l, _) in enumerate(tabs))
        panels = "".join(f'<div class="tabpanel" role="tabpanel" id="t-{k}" aria-labelledby="tab-{k}"{" hidden" if i else ""}>{c}</div>' for i, (k, l, c) in enumerate(tabs))
        rel = related(p)
        nav_btns = (f'<button class="gnav prev" data-d="-1" aria-label="Vorige afbeelding">‹</button><button class="gnav next" data-d="1" aria-label="Volgende afbeelding">›</button>' if len(imgs) > 1 else "")
        return f"""<main class="container">
  {crumbs(R, [(CATLABEL[p["cat"]], CATPAGE[p["cat"]] + "/"), (p["name"], None)]).replace('class="crumbs container"', 'class="crumbs"')}
  <div class="pdp">
    <div>
      <div class="gallery-main" id="gmain" role="button" tabindex="0" aria-label="Afbeelding vergroten">
        {f'<span class="tag">{e(p["tag"])}</span>' if p.get("tag") else ""}
        <img src="{img(imgs[0], R)}" alt="{alt}" width="1200" height="1200">{nav_btns}
      </div>
      <div class="thumbs" id="thumbs">{thumbs if len(imgs) > 1 else ""}</div>
    </div>
    <div class="pdp-info">
      <span class="eyebrow">{CATLABEL[p["cat"]]}</span>
      <h1 style="font-size:clamp(1.8rem,3.4vw,2.6rem)">{alt}</h1>
      <div class="pdp-price">{compare}<span class="js-price">{eur(start)}</span> <small>incl. btw</small>{save}</div>
      <p style="color:var(--muted)">{e(p["meta"])}</p>
      <div class="highlights">{hl}</div>
      {opts}{note}
      <div class="buy-row">
        <div class="qty"><button type="button" id="qmin" aria-label="Minder">−</button><input id="qty" value="1" inputmode="numeric" aria-label="Aantal"><button type="button" id="qplus" aria-label="Meer">+</button></div>
        <button class="btn btn-primary" id="add" type="button">In winkelmand</button>
      </div>
      <p class="notice" id="msg" role="status"></p>
      {perks()}
    </div>
  </div>

  <div class="tabs" role="tablist">{tabbar}</div>
  {panels}

  {f'<section style="padding-top:1rem"><div class="section-head"><div><span class="eyebrow">Recensies</span><h2>Wat klanten zeggen</h2></div></div>{reviews_html(rv)}</section>' if rv else ""}

  <section style="padding-top:2rem">
    <div class="section-head"><div><span class="eyebrow">Maak het compleet</span><h2>Bekijk ook</h2></div></div>
    {grid(rel, R)}
  </section>
</main>
<div class="sticky-buy" id="sticky-buy"><strong>{alt}<br><span class="js-price">{eur(start)}</span></strong><button class="btn btn-primary" id="sticky-add" type="button">In winkelmand</button></div>
<script type="application/json" id="pdata">{json.dumps(pdata, ensure_ascii=False)}</script>"""
    extra = (f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'
             f'<script type="application/ld+json">{json.dumps(crumbs_ld, ensure_ascii=False)}</script>\n')
    page_raw(path, f'{p["title"]} | Diabeticswear', p["meta"], body, active=CATPAGE[p["cat"]] + "/", extra=extra, og=f"assets/img/p/{imgs[0]}.webp")


def page_raw(path, title, desc, body, active=None, extra="", og=None):
    """Zoals page(), maar de body levert zelf het <main>-element."""
    depth = path.count("/")
    R = "../" * depth
    out = head(R, path, title, desc, extra, og).replace('href="#main"', 'href="#main"') + header(R, active) + \
        body(R).replace("<main class=\"container\">", '<main class="container" id="main">', 1) + "\n" + footer(R)
    fp = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(out)
    PAGES.append(path)


def build_about():
    def body(R):
        return hero_small("Over ons", "Kleding die rekening houdt met je insulinepomp", "", R) + f"""
<section class="bg-white"><div class="container split">
  <div>
    <span class="eyebrow">Onze missie</span>
    <h2>Onbezorgd leven met diabetes</h2>
    <p>Wij bij Diabeticswear dromen van een wereld waarin mensen met diabetes onbezorgd kunnen leven, zonder dat hun insulinepomp een belemmering vormt in hun dagelijks leven. Onze kleding is speciaal ontworpen om hen deze vrijheid te geven.</p>
    <p>Bij Diabeticswear geloven we dat iedereen het verdient om zich vrij en zelfverzekerd te voelen, ongeacht de uitdagingen die diabetes met zich mee kan brengen. Daarom blijven we innoveren en streven we naar de hoogste kwaliteit in alles wat we doen.</p>
    <a class="btn btn-primary" href="{R}winkel/">Bekijk onze producten</a>
  </div>
  <div class="split-visual" style="padding:0;overflow:hidden"><img src="{img("diabetes-v-hals-hemd-3", R)}" alt="Diabetes hemd met insulinepomp in het zakje" loading="lazy" width="1200" height="1200"></div>
</div></section>
<section><div class="container">
  <div class="section-head"><div><span class="eyebrow">Waar we voor staan</span><h2>Onze uitgangspunten</h2></div></div>
  {usps_values()}
</div></section>
<section class="bg-white" id="recensies"><div class="container">
  <div class="section-head"><div><span class="eyebrow">Recensies</span><h2>Wat klanten zeggen</h2></div></div>
  {reviews_html(C["reviews"][:3])}
</div></section>
{newsletter_contact(R)}"""
    page("over-ons/", "Over ons | Diabeticswear", "Diabeticswear ontwerpt kleding waarmee mensen met diabetes hun insulinepomp veilig, comfortabel en discreet dragen.", body)


def build_faq():
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for _, items in C["faq"] for q, a in items]}

    def body(R):
        groups = "".join(f'<div class="faq-group"><h2>{e(g)}</h2>{faq_html(items)}</div>' for g, items in C["faq"])
        return hero_small("FAQ", "Veelgestelde vragen", "Staat je vraag er niet tussen? Neem contact op, we reageren binnen 24 uur.", R) + \
            f'<section><div class="container faq">{groups}</div></section>' + newsletter_contact(R)
    page("veelgestelde-vragen/", "Veelgestelde vragen | Diabeticswear", "Antwoorden op vragen over maten, pompzakjes, verzending, betalen en retourneren bij Diabeticswear.",
         body, extra=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')


def build_contact():
    def body(R):
        return hero_small("Contact", "Neem contact op", "Heb je vragen over een product of kun je jouw maat niet vinden? We streven ernaar je vraag binnen 24 uur te beantwoorden.", R) + f"""
<section><div class="container contact-grid">
  <div class="page-card">
    <h2>Contactgegevens</h2>
    <ul class="contact-list">
      <li><strong>E-mail</strong><br><a href="mailto:{MAIL}">{MAIL}</a></li>
      <li><strong>Telefoon</strong><br><a href="{TEL_LINK}">{TEL}</a></li>
      <li><strong>Adres</strong><br>Diabeticswear<br>De Wel 14-16<br>3871 MV Hoevelaken</li>
    </ul>
    <p class="small" style="margin:1.4rem 0 0">KvK 91840376 · BTW NL004919866B33</p>
  </div>
  <div class="page-card">
    <h2>Stuur ons een bericht</h2>
    <form class="form" id="contact-form">
      <div class="two"><label>Naam *<input name="naam" required autocomplete="name"></label><label>E-mail *<input name="email" type="email" required autocomplete="email"></label></div>
      <div class="two"><label>Telefoonnummer<input name="tel" type="tel" autocomplete="tel"></label><label>Onderwerp<select name="onderwerp"><option>Vraag over een product</option><option>Advies over mijn maat</option><option>Past mijn pomp?</option><option>Mijn bestelling</option><option>Retour of ruilen</option><option>Anders</option></select></label></div>
      <label>Bericht *<textarea name="bericht" required></textarea></label>
      <button class="btn btn-primary" type="submit">Verzenden</button>
      <p class="small" id="contact-done" hidden><strong>Je e-mailprogramma is geopend met je bericht.</strong> Verstuur de e-mail om je vraag naar ons te sturen.</p>
      <p class="small" style="margin:0">Je bericht wordt via je eigen e-mailprogramma verstuurd. We gebruiken je gegevens alleen om je vraag te beantwoorden.</p>
    </form>
  </div>
</div></section>"""
    page("contact/", "Contact | Diabeticswear", "Neem contact op met Diabeticswear via info@diabeticswear.com of +31 6 10022060. We reageren binnen 24 uur.", body)


def legal_html(text):
    out, lst = [], []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    title = lines[0]
    for l in lines[1:]:
        heading = len(l) < 70 and not re.search(r"[.:;,!?]$", l) and ":" not in l[:40]
        if heading:
            if lst:
                out.append("<ul>" + "".join(lst) + "</ul>"); lst = []
            out.append(f"<h2>{e(l)}</h2>")
        elif re.match(r"^[^.]{2,40}: ", l) and len(l) < 260:
            k, v = l.split(":", 1)
            lst.append(f"<li><strong>{e(k)}:</strong>{linkify(e(v))}</li>")
        else:
            if lst:
                out.append("<ul>" + "".join(lst) + "</ul>"); lst = []
            out.append(f"<p>{linkify(e(l))}</p>")
    if lst:
        out.append("<ul>" + "".join(lst) + "</ul>")
    return title, "".join(out)


def build_legal(slug, d):
    t, h = legal_html(d["text"])

    def body(R):
        return hero_small("Informatie", d["title"], "", R) + f'<section><div class="container faq"><article class="page-card">{h}</article></div></section>'
    page(slug + "/", f'{d["title"]} | Diabeticswear', f'{d["title"]} van Diabeticswear.', body)


def build_redirect(path, target):
    depth = path.count("/")
    R = "../" * depth
    fp = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(
        f'<!doctype html><html lang="nl"><head><meta charset="utf-8"><title>Doorverwijzen…</title>'
        f'<link rel="canonical" href="{DOMAIN}{target}"><meta name="robots" content="noindex">'
        f'<meta http-equiv="refresh" content="0; url={R}{target}"></head>'
        f'<body><p><a href="{R}{target}">Ga naar de nieuwe pagina</a></p></body></html>')


def build_404():
    body = lambda R: hero_small("404", "Pagina niet gevonden", f'Deze pagina bestaat niet (meer). <a style="color:#fff" href="{R}winkel/">Bekijk alle producten</a>.', R)
    # GitHub Pages serveert 404.html op elk pad: daarom absolute paden.
    out = head("/", "404.html", "Pagina niet gevonden | Diabeticswear", "Pagina niet gevonden.").replace('data-root="/"', 'data-root="/"') + \
        header("/", None) + f'<main id="main">{body("/")}</main>' + footer("/")
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(out)


def build_catalog():
    cat = {p["slug"]: {"name": p["name"], "price": p["price"], "img": f'assets/img/p/{p["imgs"][0]}-sm.webp'} for p in PRODUCTS}
    open(os.path.join(ROOT, "assets", "js", "catalog.js"), "w", encoding="utf-8").write(
        "/* Gegenereerd door tools/build.py, niet handmatig aanpassen. */\nwindow.DW_CATALOG=" + json.dumps(cat, ensure_ascii=False) + ";\n")


def build_sitemap():
    urls = "".join(f"<url><loc>{DOMAIN}{p}</loc></url>" for p in PAGES)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}sitemap.xml\n")


if __name__ == "__main__":
    build_home()
    build_shop()
    for c in CATS:
        build_category(c)
    for p in PRODUCTS:
        build_product(p)
    build_about()
    build_faq()
    build_contact()
    for slug, d in C["legal"].items():
        build_legal(slug, d)
    build_redirect("product/patch-pleister-freestyle-libre2/", "product/patch-pleister-freestyle-libre-2/")
    build_404()
    build_catalog()
    build_sitemap()
    print(f"{len(PAGES)} pagina's gegenereerd")
