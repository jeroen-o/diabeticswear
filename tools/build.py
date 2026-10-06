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
KB = json.load(open(os.path.join(ROOT, "tools", "kennisbank.json"), encoding="utf-8"))
SIZE_TABLE = [("Lengte (zijde 1)", [70, 73, 75, 77, 80, 81]), ("Breedte (zijde 2)", [50, 51, 52, 53, 55, 56]),
              ("Zakje breedte (zijde 3)", [12] * 6), ("Zakje hoogte (zijde 4)", [14] * 6)]
SIZE_COLS = ["XS", "S", "M", "L", "XL", "XXL"]
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


def srcset(base, R):
    return f'srcset="{R}assets/img/p/{base}-sm.webp 600w, {R}assets/img/p/{base}.webp 1200w"'


def img(base, R, sm=False):
    return f"{R}assets/img/p/{base}{'-sm' if sm else ''}.webp"


# ---------------------------------------------------------------- layout

ORG_ID = DOMAIN + "#organisatie"
SITE_ID = DOMAIN + "#website"
LASTMOD = "2026-10-06"


def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>\n'


def head(R, path, title, desc, extra="", og_img=None, og_type="website", preload=None, product=None,
         robots="index,follow,max-image-preview:large,max-snippet:-1"):
    canon = DOMAIN + path
    og = og_img or "assets/img/p/diabetes-2-pocket-sportlegging-1.webp"
    pre = ""
    if preload:
        src = preload if preload.endswith(".webp") else f"assets/img/p/{preload}.webp"
        sset = "" if preload.endswith(".webp") else f' imagesrcset="{R}assets/img/p/{preload}-sm.webp 600w, {R}assets/img/p/{preload}.webp 1200w" imagesizes="(max-width:900px) 100vw, 600px"'
        pre = f'<link rel="preload" as="image" href="{R}{src}"{sset} fetchpriority="high">\n'
    prod = ""
    if product:
        prod = (f'<meta property="product:price:amount" content="{product[0]:.2f}">\n'
                f'<meta property="product:price:currency" content="EUR">\n'
                f'<meta property="product:brand" content="Diabeticswear">\n')
    return f"""<!doctype html>
<html lang="nl" data-root="{R}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="nl" href="{canon}">
<link rel="alternate" hreflang="x-default" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="nl_NL">
<meta property="og:site_name" content="Diabeticswear">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="1200">
<meta property="og:image:alt" content="{e(title)}">
{prod}<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2BAA92">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="{R}favicon.ico" sizes="48x48">
<link rel="icon" href="{R}assets/img/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="{R}assets/img/apple-touch-icon.png">
<link rel="manifest" href="{R}site.webmanifest">
<link rel="sitemap" type="application/xml" href="{R}sitemap.xml">
{pre}<link rel="stylesheet" href="{R}assets/css/style.css">
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
    ("Kennisbank", "kennisbank/", None),
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
    <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav"><svg aria-hidden="true" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    <nav class="nav" id="nav" aria-label="Hoofdmenu">
      {"".join(items)}
    </nav>
    <button class="cart-btn"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 7h12l-1 13H7z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg><span class="label">Mand</span><span class="cart-count">0</span><span class="sr-only"> artikelen in winkelmand</span></button>
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
      <div><h2 class="fh">Shop</h2><ul>
        <li><a href="{R}diabetes-t-shirts-insulinepomp/">T-shirts</a></li>
        <li><a href="{R}diabetes-hemden-insulinepomp/">Hemden</a></li>
        <li><a href="{R}diabetes-2-pocket-sportlegging/">Sportlegging</a></li>
        <li><a href="{R}diabetes-2-pocket-bikershort-sporten/">Bikershorts &amp; sport rok</a></li>
        <li><a href="{R}diabetes-compressiesokken/">Compressiesokken</a></li>
        <li><a href="{R}productpagina-patch-pleisters/">Patch pleisters</a></li>
        <li><a href="{R}producten-kleding-accessoires-overig/">Accessoires</a></li>
      </ul></div>
      <div><h2 class="fh">Service</h2><ul>
        <li><a href="{R}veelgestelde-vragen/">Veelgestelde vragen</a></li>
        <li><a href="{R}kennisbank/">Kennisbank</a></li>
        <li><a href="{R}kennisbank/maatgids-diabetes-kleding/">Maatgids</a></li>
        <li><a href="{R}terugbetaalde-retourneringen/">Retourbeleid</a></li>
        <li><a href="{R}over-ons/">Over ons</a></li>
        <li><a href="{R}contact/">Contact</a></li>
      </ul></div>
      <div><h2 class="fh">Contact</h2><ul>
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


def page(path, title, desc, body, active=None, extra="", og=None, **kw):
    depth = path.count("/")
    R = "../" * depth
    out = head(R, path, title, desc, extra, og, **kw) + header(R, active if active is not None else path) + \
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


def card(p, R, order=0, eager=False):
    alt = e(p["name"])
    second = f'<img class="alt" src="{img(p["imgs"][1], R, True)}" {srcset(p["imgs"][1], R)} sizes="(max-width:520px) 100vw, (max-width:1000px) 50vw, 280px" alt="" loading="lazy" width="600" height="600">' if len(p["imgs"]) > 1 else ""
    tag = f'<span class="tag">{e(p["tag"])}</span>' if p.get("tag") else ""
    cols = p.get("colors", [])
    dots = '<div class="dots">' + "".join(f'<i style="background:{c[1]}" title="{e(c[0])}"></i>' for c in cols) + "</div>" if len(cols) > 1 else ""
    cats = p["cat"] + (" kleding" if p["group"] in ("sport", "shirts", "sokken") else "")
    price = p["variants"][0][1] if p.get("variants") else p["price"]
    return (f'<a class="card" href="{R}product/{p["slug"]}/" data-cats="{cats}" data-price="{price}" data-order="{order}">'
            f'<div class="card-media"><img src="{img(p["imgs"][0], R, True)}" {srcset(p["imgs"][0], R)} sizes="(max-width:520px) 100vw, (max-width:1000px) 50vw, 280px" alt="{alt}" {"" if eager else 'loading="lazy" '}width="600" height="600">{second}{tag}</div>'
            f'<div class="card-body"><small>{CATLABEL[p["cat"]]}</small><h3>{alt}</h3>{dots}<span class="price">{price_html(p)}</span></div></a>')


def grid(ps, R, gid="", eager=0, title=None):
    return (f'<h2 class="sr-only">{e(title)}</h2>' if title else "") + f'<div class="grid"{f" id={gid}" if gid else ""}>' + "".join(card(p, R, i, i < eager) for i, p in enumerate(ps)) + "</div>"


def collection_ld(path, name, desc, ps, trail):
    items = [{"@type": "ListItem", "position": i + 1, "url": f'{DOMAIN}product/{p["slug"]}/', "name": p["name"]} for i, p in enumerate(ps)]
    crumbs_l = [{"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN}] + \
        [{"@type": "ListItem", "position": i + 2, "name": n, "item": DOMAIN + h} for i, (n, h) in enumerate(trail)]
    return ld({"@context": "https://schema.org", "@type": "CollectionPage", "@id": DOMAIN + path, "url": DOMAIN + path, "name": name,
               "description": desc, "inLanguage": "nl-NL", "isPartOf": {"@id": SITE_ID},
               "mainEntity": {"@type": "ItemList", "numberOfItems": len(ps), "itemListElement": items}}) + \
        ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs_l})


def hero_small(eyebrow, title, text, R):
    return (f'<section class="hero hero-sub"><div class="container"><div><span class="eyebrow">{e(eyebrow)}</span>'
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
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{USP_ICON[i]}</svg></div><div><h2 class="uh">{t}</h2><p>{d}</p></div></div>')


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
    org = {"@context": "https://schema.org", "@graph": [
        {"@type": ["Organization", "OnlineStore"], "@id": ORG_ID, "name": "Diabeticswear", "url": DOMAIN,
         "logo": {"@type": "ImageObject", "url": DOMAIN + "assets/img/logo-dw.png", "width": 192, "height": 192},
         "image": DOMAIN + "assets/img/p/diabetes-2-pocket-sportlegging-1.webp",
         "description": "Webshop voor kleding met pompzakjes en slangdoorvoer voor mensen met een insulinepomp, transparante patch pleisters voor CGM-sensoren en pods, en accessoires.",
         "email": MAIL, "telephone": "+31610022060", "vatID": "NL004919866B33",
         "identifier": {"@type": "PropertyValue", "propertyID": "KvK", "value": "91840376"},
         "address": {"@type": "PostalAddress", "streetAddress": "De Wel 14-16", "postalCode": "3871 MV",
                     "addressLocality": "Hoevelaken", "addressCountry": "NL"},
         "areaServed": ["NL", "BE"],
         "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "email": MAIL, "telephone": "+31610022060",
                          "availableLanguage": ["nl"], "areaServed": ["NL", "BE"]},
         "hasMerchantReturnPolicy": RETURN_POLICY,
         "knowsAbout": ["kleding voor insulinepomp", "diabetes kleding", "patch pleisters voor CGM-sensoren", "insulinepomp dragen tijdens sporten"]},
        {"@type": "WebSite", "@id": SITE_ID, "url": DOMAIN, "name": "Diabeticswear", "inLanguage": "nl-NL", "publisher": {"@id": ORG_ID}}]}

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
      <img class="h1" src="{img("diabetes-2-pocket-sportlegging-1", R)}" alt="" width="1200" height="1200" fetchpriority="high">
      <img class="h2" src="{img("patch-pleister-freestyle-libre-2-1", R, True)}" {srcset("patch-pleister-freestyle-libre-2-1", R)} sizes="(max-width:860px) 45vw, 240px" alt="" width="600" height="600">
      <img class="h3" src="{img("diabetes-v-hals-t-shirt-3", R, True)}" {srcset("diabetes-v-hals-t-shirt-3", R)} sizes="(max-width:860px) 45vw, 260px" alt="" width="600" height="600">
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

<section class="bg-white" id="kennisbank">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">Kennisbank</span><h2>Tips voor elke dag</h2></div><a class="btn btn-primary" href="{R}kennisbank/">Alle artikelen</a></div>
    {kb_grid([a for a in KB["articles"] if a["slug"] in ("insulinepomp-dragen-tijdens-sporten", "sensor-laat-los-tips", "slapen-met-een-insulinepomp", "maatgids-diabetes-kleding")], R)}
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
         body, extra=ld(org), preload="assets/img/p/diabetes-2-pocket-sportlegging-1.webp")


SHOP_ORDER = ["diabetes-2-pocket-sportlegging", "diabetes-2-pocket-bikershort", "sportlegging-bikershort-insulinepomp", "2-pocket-sport-rok-voor-diabetes",
              "diabetes-v-hals-t-shirt", "diabetes-ronde-hals-t-shirt", "diabetes-v-hals-hemd", "diabetes-ronde-hals-hemd",
              "patch-pleister-freestyle-libre-2", "patch-pleisters-dexcom-g6-40-stuks", "patch-pleisters-dexcom-g7-40-stuks", "patch-pleisters-omnipod-50-125-stuks",
              "compressiesokken-kort", "compressiesokken-lang", "insuline-organizer"]


def build_shop():
    chips = [("alle", "Alles"), ("kleding", "Kleding"), ("tshirts", "T-shirts"), ("hemden", "Hemden"), ("sportlegging", "Sportlegging"),
             ("bikershorts", "Bikershorts"), ("rokken", "Sport rok"), ("sokken", "Sokken"), ("patches", "Patch pleisters"), ("accessoires", "Accessoires")]

    def body(R):
        ch = "".join(f'<button class="chip" type="button" data-cat="{k}" aria-pressed="false">{l}</button>' for k, l in chips)
        return (crumbs(R, [("Alle producten", None)]) + hero_small("Winkel", "Alle producten", "Kleding met pompzakjes, patch pleisters en accessoires voor het leven met diabetes.", R) +
                f'<section><div class="container"><div class="filters" role="group" aria-label="Filter op categorie">{ch}'
                f'<label class="sr-only" for="sort">Sorteren</label><select id="sort"><option value="std">Aanbevolen</option><option value="laag">Prijs: laag naar hoog</option><option value="hoog">Prijs: hoog naar laag</option></select></div>'
                f'<p class="small" id="shop-count" style="margin:-.6rem 0 1rem"></p>' + grid([BY[s] for s in SHOP_ORDER], R, "shop-grid", eager=4, title="Alle producten") + '</div></section>' +
                f'<section class="bg-white" style="padding:2.5rem 0">{usps_service()}</section>')
    desc = "Alle producten van Diabeticswear: t-shirts, hemden, sportleggings en bikershorts met pompzakjes, compressiesokken, patch pleisters en accessoires."
    page("winkel/", "Alle producten voor insulinepomp-gebruikers | Diabeticswear", desc, body,
         extra=collection_ld("winkel/", "Alle producten", desc, [BY[s] for s in SHOP_ORDER], [("Alle producten", "winkel/")]))


def build_category(c):
    ps = [p for p in PRODUCTS if p["cat"] in c["cats"]]
    ps.sort(key=lambda p: SHOP_ORDER.index(p["slug"]))

    def body(R):
        out = crumbs(R, [(c["name"], None)]) + hero_small(c["name"], c["h1"], e(c["intro"]), R)
        out += f'<section><div class="container">{grid(ps, R, eager=4, title=c["name"])}</div></section>'
        if c.get("body"):
            bl = "".join(f"<li>{e(b)}</li>" for b in c.get("bullets", []))
            out += f'<section class="bg-white"><div class="container faq"><h2>Over onze {e(c["name"].lower())}</h2>'
            out += "".join(f"<p>{e(p)}</p>" for p in c["body"]) + (f'<ul class="checklist">{bl}</ul>' if bl else "") + "</div></section>"
        if c.get("faq"):
            out += f'<section><div class="container faq"><div style="text-align:center;margin-bottom:2rem"><span class="eyebrow">FAQ</span><h2>Veelgestelde vragen</h2></div>{faq_html(c["faq"])}</div></section>'
        return out + newsletter_contact(R)
    extra = collection_ld(c["slug"] + "/", c["h1"], c["intro"], ps, [(c["name"], c["slug"] + "/")])
    if c.get("faq"):
        extra += ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]]})
    page(c["slug"] + "/", f'{c["h1"]} | Diabeticswear', c["intro"], body, extra=extra)


RETURN_POLICY = {"@type": "MerchantReturnPolicy", "applicableCountry": ["NL", "BE"],
                 "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow", "merchantReturnDays": 14,
                 "returnMethod": "https://schema.org/ReturnByMail", "returnFees": "https://schema.org/ReturnShippingFees",
                 "url": DOMAIN + "terugbetaalde-retourneringen/"}

SHIP_QA = ("Wat zijn de verzendkosten en levertijd?",
           "Binnen Nederland is verzending gratis vanaf € 30 (anders € 4,25), naar België vanaf € 75 (anders € 5,25). "
           "We streven ernaar je bestelling binnen 2-3 werkdagen te leveren.")
RETURN_QA = ("Kan ik dit product retourneren?",
             "Ja, binnen 14 dagen na ontvangst, ongebruikt en in de originele verpakking. De retourkosten zijn voor eigen rekening, "
             "tenzij het product defect of verkeerd geleverd is.")


def product_faq(p):
    spec = dict((k.lower(), v) for k, v in p["specs"])
    zak = spec.get("afmetingen zakjes", "")
    if p["group"] == "shirts":
        qa = [("Past mijn insulinepomp in de zakjes?", f"De twee zakjes aan de voorkant zijn {zak} en sluiten met klittenband. Ze passen de meest gangbare insulinepompen. Twijfel je? Mail het type pomp naar {MAIL}."),
              ("Hoe loopt de infuusslang?", "Aan de binnenkant zitten twee stevig afgewerkte gaatjes. Daardoor leid je de slang onder het shirt naar je pomp, zonder dat er iets loshangt."),
              ("Welke maat moet ik kiezen?", "De t-shirts en hemden vallen groot uit. We adviseren een maat kleiner te bestellen dan normaal. Bekijk de maattabel op deze pagina."),
              ("Van welk materiaal is het gemaakt?", f"{spec.get('materiaal', '100% katoen')}: zacht, ademend en geschikt voor dagelijks gebruik, ook 's nachts.")]
    elif p["group"] == "sport":
        qa = [("Past mijn insulinepomp in de zakken?", "De twee zijzakken zijn diep genoeg voor de meest gangbare insulinepompen en houden je pomp stabiel op zijn plek." + (f" De zakjes zijn {zak}." if zak else "") + f" Twijfel je? Mail het type pomp naar {MAIL}."),
              ("Hoe loopt de infuusslang?", "Aan de binnenkant van de zak zit een discreet gaatje. Daardoor voer je de infuusslang netjes door, zodat hij niet loshangt of blijft haken."),
              ("Van welk materiaal is het gemaakt?", f"{spec.get('materiaal', '90% polyester, 10% elastaan')}: lichtgewicht, ademend, sneldrogend en elastisch."),
              ("Welke maten zijn er?", "Maat S, M, L en XL.")]
    elif p["group"] == "patches":
        fit = spec.get("geschikt voor", "")
        qa = [(f"Voor welke sensor of pod is deze pleister?", f"Deze patch pleister is gemaakt voor de {fit}. Afmetingen: {spec.get('afmetingen', '')}. De uitsparing laat je sensor of pod vrij."),
              ("Is de pleister waterbestendig?", "Ja, de pleister is water- en zweetbestendig en geschikt voor sporten, douchen en zwemmen."),
              ("Hoe gebruik ik de pleister?", "Plak de pleister over de rand van je sensor of pod op schone, droge huid. Gebruik een nieuwe pleister bij elke wissel."),
              ("Hoeveel pleisters zitten er in een verpakking?", spec.get("aantal", "") + ".")]
    elif p["group"] == "sokken":
        qa = [("Welke maat hebben de sokken?", "De sokken zijn unisex en passen maat 37-48."),
              ("Wat is er anders aan deze sokken?", "Ze hebben een losse pasvorm, lichte compressie en een naadloze, niet-knellende manchet."),
              ("Van welk materiaal zijn ze gemaakt?", spec.get("materiaal", "") + "."),
              ("Zijn deze sokken een medisch hulpmiddel?", "Nee. Heb je klachten aan je voeten, overleg dan met je arts of podotherapeut welke sokken voor jou geschikt zijn.")]
    else:
        qa = [("Wat past er in de Insuline Organizer?", "Eén insulinepen en vijf naalden, in twee ronde openingen van 2 cm doorsnee."),
              ("Hoe groot is de organizer?", "16,5 cm hoog, 4,8 cm breed en 2,8 cm diep: past in een tas, broekzak of jaszak."),
              ("Van welk materiaal is hij gemaakt?", "PLA, een bioplastic uit hernieuwbare grondstoffen. Niet te lang in de zon of bij hoge temperaturen bewaren.")]
    return qa + [SHIP_QA, RETURN_QA]


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
    shipping = [
        {"@type": "OfferShippingDetails",
         "shippingRate": {"@type": "MonetaryAmount", "value": 4.25 if p["price"] < 30 else 0, "currency": "EUR"},
         "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "NL"},
         "deliveryTime": {"@type": "ShippingDeliveryTime",
                          "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 1, "unitCode": "DAY"},
                          "transitTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 2, "unitCode": "DAY"}}},
        {"@type": "OfferShippingDetails",
         "shippingRate": {"@type": "MonetaryAmount", "value": 5.25 if p["price"] < 75 else 0, "currency": "EUR"},
         "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "BE"},
         "deliveryTime": {"@type": "ShippingDeliveryTime",
                          "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 1, "unitCode": "DAY"},
                          "transitTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 3, "unitCode": "DAY"}}}]
    offer_base = {"priceCurrency": "EUR", "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition",
                  "url": DOMAIN + path, "seller": {"@id": ORG_ID}, "shippingDetails": shipping, "hasMerchantReturnPolicy": RETURN_POLICY}
    if variants:
        offers = [dict(offer_base, **{"@type": "Offer", "name": v[0], "price": f"{v[1]:.2f}", "sku": f'{p["slug"]}-{v[0].split()[0]}'}) for v in variants]
    else:
        offers = dict(offer_base, **{"@type": "Offer", "price": f'{p["price"]:.2f}'})
    spec = dict((k.lower(), v) for k, v in p["specs"])
    ld_prod = {"@context": "https://schema.org", "@type": "Product", "@id": DOMAIN + path + "#product", "name": p["name"],
               "description": p["seo_desc"], "sku": p["slug"], "category": CATLABEL[p["cat"]], "url": DOMAIN + path,
               "image": [f"{DOMAIN}assets/img/p/{b}.webp" for b in imgs], "brand": {"@type": "Brand", "name": "Diabeticswear"},
               "manufacturer": {"@id": ORG_ID}, "offers": offers}
    if colors:
        ld_prod["color"] = ", ".join(c[0] for c in colors)
    if sizes:
        ld_prod["size"] = ", ".join(sizes)
    if "materiaal" in spec:
        ld_prod["material"] = spec["materiaal"]
    if p["group"] in ("sport", "shirts", "sokken"):
        ld_prod["audience"] = {"@type": "PeopleAudience", "healthCondition": {"@type": "MedicalCondition", "name": "Diabetes"}}
    ld_prod["additionalProperty"] = [{"@type": "PropertyValue", "name": k, "value": v} for k, v in p["specs"]]
    crumbs_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
        {"@type": "ListItem", "position": 2, "name": CATLABEL[p["cat"]], "item": DOMAIN + CATPAGE[p["cat"]] + "/"},
        {"@type": "ListItem", "position": 3, "name": p["name"], "item": DOMAIN + path}]}
    pfaq = product_faq(p)
    PAGE_IMGS[path] = imgs
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
            tabs.append(("size", "Maattabel", f'<p>De maten zijn plat gemeten in centimeters. De t-shirts en hemden vallen groot uit: bestel bij twijfel een maat kleiner. <a href="{R}kennisbank/maatgids-diabetes-kleding/">Bekijk de maatgids</a>.</p>' + size_table_html() +
                         f'<div class="sizechart" data-zoom="{img(imgs[p["sizechart"] - 1], R)}" role="button" tabindex="0" aria-label="Maattabel vergroten">'
                         f'<img src="{img(imgs[p["sizechart"] - 1], R)}" alt="Maattabel {alt}" loading="lazy" width="1200" height="1200"></div>'))
        tabs.append(("ship", "Verzenden &amp; retour",
                     f'<p><strong>Levering:</strong> we streven ernaar je bestelling binnen 2-3 werkdagen te bezorgen.</p>'
                     f'<p><strong>Nederland:</strong> gratis vanaf € 30, daaronder € 4,25.</p><p><strong>België:</strong> gratis vanaf € 75, daaronder € 5,25.</p>'
                     f'<p><strong>Retour:</strong> binnen 14 dagen na ontvangst, ongebruikt en in de originele verpakking. Retourkosten zijn voor eigen rekening, tenzij het product defect of verkeerd geleverd is. '
                     f'<a href="{R}terugbetaalde-retourneringen/">Lees ons retourbeleid</a>.</p>'))
        tabbar = "".join(f'<button role="tab" aria-selected="{str(i == 0).lower()}" aria-controls="t-{k}" id="tab-{k}">{l}</button>' for i, (k, l, _) in enumerate(tabs))
        panels = "".join(f'<div class="tabpanel" role="tabpanel" id="t-{k}" aria-labelledby="tab-{k}"{" hidden" if i else ""}><h2 class="sr-only">{l}</h2>{c}</div>' for i, (k, l, c) in enumerate(tabs))
        rel = related(p)
        nav_btns = (f'<button class="gnav prev" data-d="-1" aria-label="Vorige afbeelding">‹</button><button class="gnav next" data-d="1" aria-label="Volgende afbeelding">›</button>' if len(imgs) > 1 else "")
        return f"""<main class="container">
  {crumbs(R, [(CATLABEL[p["cat"]], CATPAGE[p["cat"]] + "/"), (p["name"], None)]).replace('class="crumbs container"', 'class="crumbs"')}
  <div class="pdp">
    <div>
      <div class="gallery-main" id="gmain" role="button" tabindex="0" aria-label="Afbeelding vergroten">
        {f'<span class="tag">{e(p["tag"])}</span>' if p.get("tag") else ""}
        <img src="{img(imgs[0], R)}" {srcset(imgs[0], R)} sizes="(max-width:900px) 100vw, 600px" alt="{alt}" width="1200" height="1200" fetchpriority="high">{nav_btns}
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

  <section class="faq-mini" aria-labelledby="pfaq-title"><div class="section-head"><div><span class="eyebrow">Vragen</span><h2 id="pfaq-title">Veelgestelde vragen over dit product</h2></div></div><div class="faq" style="max-width:none">{faq_html(pfaq)}</div></section>

  {f'<section style="padding-top:1rem"><div class="section-head"><div><span class="eyebrow">Recensies</span><h2>Wat klanten zeggen</h2></div></div>{reviews_html(rv)}</section>' if rv else ""}

  <section style="padding-top:2rem">
    <div class="section-head"><div><span class="eyebrow">Maak het compleet</span><h2>Bekijk ook</h2></div></div>
    {grid(rel, R)}
  </section>
</main>
<div class="sticky-buy" id="sticky-buy"><strong>{alt}<br><span class="js-price">{eur(start)}</span></strong><button class="btn btn-primary" id="sticky-add" type="button">In winkelmand</button></div>
<script type="application/json" id="pdata">{json.dumps(pdata, ensure_ascii=False)}</script>"""
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pfaq]}
    page_raw(path, p["seo_title"], p["seo_desc"], body, active=CATPAGE[p["cat"]] + "/", extra=ld(ld_prod) + ld(crumbs_ld) + ld(faq_ld),
             og=f"assets/img/p/{imgs[0]}.webp", og_type="product", preload=imgs[0],
             product=(variants[0][1] if variants else p["price"],))


def page_raw(path, title, desc, body, active=None, extra="", og=None, **kw):
    """Zoals page(), maar de body levert zelf het <main>-element."""
    depth = path.count("/")
    R = "../" * depth
    out = head(R, path, title, desc, extra, og, **kw) + header(R, active) + \
        body(R).replace("<main class=\"container\">", '<main class="container" id="main">', 1) + "\n" + footer(R)
    fp = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(out)
    PAGES.append(path)


def size_table_html():
    head_ = "".join(f"<th scope='col'>{c}</th>" for c in SIZE_COLS)
    rows = "".join(f"<tr><th scope='row'>{e(n)}</th>" + "".join(f"<td>{v}</td>" for v in vals) + "</tr>" for n, vals in SIZE_TABLE)
    return f'<div class="table-wrap"><table><caption class="sr-only">Maattabel t-shirts en hemden in centimeters</caption><thead><tr><th scope="col">Maat (cm)</th>{head_}</tr></thead><tbody>{rows}</tbody></table></div>'


def md_links(t, R):
    """[tekst](pad) -> interne link; e-mailadres -> mailto."""
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{R}{m.group(2)}">{m.group(1)}</a>', t)
    return t


def kb_card(a, R):
    return (f'<a class="card" href="{R}kennisbank/{a["slug"]}/"><div class="card-media"><img src="{img(a["img"], R, True)}" {srcset(a["img"], R)} '
            f'sizes="(max-width:520px) 100vw, (max-width:1000px) 50vw, 280px" alt="" loading="lazy" width="600" height="600"></div>'
            f'<div class="card-body"><small>Kennisbank</small><h3>{e(a["title"])}</h3><p class="small" style="margin:.3rem 0 0">{e(a["desc"])}</p></div></a>')


def kb_grid(arts, R):
    return '<div class="grid">' + "".join(kb_card(a, R) for a in arts) + "</div>"


def build_kb_index():
    arts = KB["articles"]
    desc = "Praktische tips over leven met een insulinepomp of CGM-sensor: sporten, slapen, zwemmen, op reis, sensor die loslaat en de juiste maat kleding."

    def body(R):
        return crumbs(R, [("Kennisbank", None)]) + hero_small("Kennisbank", "Tips voor leven met je insulinepomp en sensor", e(desc), R) + \
            f'<section><div class="container"><h2 class="sr-only">Artikelen</h2>{kb_grid(arts, R)}</div></section>' + newsletter_contact(R)
    items = [{"@type": "ListItem", "position": i + 1, "url": f'{DOMAIN}kennisbank/{a["slug"]}/', "name": a["title"]} for i, a in enumerate(arts)]
    extra = ld({"@context": "https://schema.org", "@type": "CollectionPage", "url": DOMAIN + "kennisbank/", "name": "Kennisbank", "description": desc,
                "inLanguage": "nl-NL", "isPartOf": {"@id": SITE_ID}, "mainEntity": {"@type": "ItemList", "itemListElement": items}}) + \
        ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
            {"@type": "ListItem", "position": 2, "name": "Kennisbank", "item": DOMAIN + "kennisbank/"}]})
    page("kennisbank/", "Kennisbank: tips voor insulinepomp en sensor | Diabeticswear", desc, body, extra=extra)


def build_kb_article(a):
    path = f'kennisbank/{a["slug"]}/'
    others = [x for x in KB["articles"] if x["slug"] != a["slug"]][:3]

    def body(R):
        out = []
        for kind, val in a["blocks"]:
            if kind == "h2":
                out.append(f"<h2>{e(val)}</h2>")
            elif kind == "p":
                out.append(f"<p>{md_links(e(val), R)}</p>")
            elif kind == "ul":
                out.append("<ul class='checklist'>" + "".join(f"<li>{md_links(e(x), R)}</li>" for x in val) + "</ul>")
            elif kind == "sizetable":
                out.append(size_table_html())
        rel = [BY[s] for s in a["related"]]
        return crumbs(R, [("Kennisbank", "kennisbank/"), (a["title"], None)]) + hero_small("Kennisbank", a["title"], e(a["intro"]), R) + f"""
<section class="bg-white"><div class="container faq">
  <article class="prose">
    <p class="small">Laatst bijgewerkt: <time datetime="{LASTMOD}">6 oktober 2026</time> · Door het team van Diabeticswear</p>
    <img src="{img(a["img"], R)}" {srcset(a["img"], R)} sizes="(max-width:860px) 100vw, 760px" alt="" width="1200" height="1200" style="border-radius:var(--radius);aspect-ratio:16/9;object-fit:cover;width:100%;background:var(--teal);margin:0 0 1.5rem">
    {"".join(out)}
    <div class="advice" role="note"><strong>Let op:</strong> {e(KB["disclaimer"])}</div>
  </article>
  <h2 style="margin-top:2.5rem">Veelgestelde vragen</h2>
  {faq_html(a["faq"])}
</div></section>
<section><div class="container">
  <div class="section-head"><div><span class="eyebrow">Handig bij dit onderwerp</span><h2>Producten</h2></div></div>
  {grid(rel, R)}
</div></section>
<section class="bg-white"><div class="container">
  <div class="section-head"><div><span class="eyebrow">Kennisbank</span><h2>Lees ook</h2></div><a class="btn btn-primary" href="{R}kennisbank/">Alle artikelen</a></div>
  {kb_grid(others, R)}
</div></section>"""
    art = {"@context": "https://schema.org", "@type": "Article", "@id": DOMAIN + path + "#artikel", "headline": a["title"], "description": a["desc"],
           "image": [f'{DOMAIN}assets/img/p/{a["img"]}.webp'], "datePublished": LASTMOD, "dateModified": LASTMOD, "inLanguage": "nl-NL",
           "author": {"@type": "Organization", "name": "Diabeticswear", "url": DOMAIN}, "publisher": {"@id": ORG_ID},
           "mainEntityOfPage": DOMAIN + path, "isPartOf": {"@id": SITE_ID}}
    crumbs_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN},
        {"@type": "ListItem", "position": 2, "name": "Kennisbank", "item": DOMAIN + "kennisbank/"},
        {"@type": "ListItem", "position": 3, "name": a["title"], "item": DOMAIN + path}]}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": x}} for q, x in a["faq"]]}
    PAGE_IMGS[path] = [a["img"]]
    page(path, a["seo_title"], a["desc"], body, active="kennisbank/", extra=ld(art) + ld(crumbs_ld) + ld(faq_ld),
         og=f'assets/img/p/{a["img"]}.webp', og_type="article")


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
    page("over-ons/", "Over ons | Diabeticswear", "Diabeticswear ontwerpt kleding waarmee mensen met diabetes hun insulinepomp veilig, comfortabel en discreet dragen.", body,
         extra=ld({"@context": "https://schema.org", "@type": "AboutPage", "url": DOMAIN + "over-ons/", "name": "Over Diabeticswear",
                   "inLanguage": "nl-NL", "isPartOf": {"@id": SITE_ID}, "about": {"@id": ORG_ID}}))


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
    page("contact/", "Contact | Diabeticswear", "Neem contact op met Diabeticswear via info@diabeticswear.com of +31 6 10022060. We reageren binnen 24 uur.", body,
         extra=ld({"@context": "https://schema.org", "@type": "ContactPage", "url": DOMAIN + "contact/", "name": "Contact met Diabeticswear",
                   "inLanguage": "nl-NL", "isPartOf": {"@id": SITE_ID}, "about": {"@id": ORG_ID}}))


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


LEGAL_DESC = {
    "algemene-voorwaarden": "Algemene voorwaarden van Diabeticswear: bestellen, prijzen, levering, herroepingsrecht, garantie en klachten.",
    "privacybeleid": "Privacybeleid van Diabeticswear: welke gegevens we verzamelen, waarvoor we ze gebruiken en welke rechten je hebt.",
    "terugbetaalde-retourneringen": "Retourbeleid van Diabeticswear: binnen 14 dagen retourneren, ruilen en terugbetaling binnen 5 werkdagen.",
}


def build_legal(slug, d):
    t, h = legal_html(d["text"])

    def body(R):
        return hero_small("Informatie", d["title"], "", R) + f'<section><div class="container faq"><article class="page-card">{h}</article></div></section>'
    page(slug + "/", f'{d["title"]} | Diabeticswear', LEGAL_DESC.get(slug, f'{d["title"]} van Diabeticswear.'), body)


def build_redirect(path, target):
    """Meta-refresh met 0 seconden: Google behandelt dit als permanente doorverwijzing."""
    depth = path.count("/")
    R = "../" * depth
    fp = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(
        f'<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>Doorverwijzen naar Diabeticswear</title><link rel="canonical" href="{DOMAIN}{target}">'
        f'<meta http-equiv="refresh" content="0; url={R}{target}"></head>'
        f'<body><p><a href="{R}{target}">Ga naar de nieuwe pagina</a></p></body></html>')
    REDIRECTS.append(path)


REDIRECTS = []


def old_target(url):
    """Koppelt een oude anderstalige WooCommerce-URL aan de Nederlandse productpagina."""
    u = url.lower()
    is_v = any(k in u for k in ("v-neck", "v-hals", "col-en-v", "col-v-", "v-ausschnitt", "cuello-en-v", "v-ringad", "scollo-a-v"))
    if any(k in u for k in ("socks", "socken", "chaussettes", "calze", "calcetines", "strumpor")):
        return "product/compressiesokken-lang/" if any(k in u for k in ("long", "lang", "lunghe", "largos")) else "product/compressiesokken-kort/"
    if "dexcom-g6" in u:
        return "product/patch-pleisters-dexcom-g6-40-stuks/"
    if "dexcom-g7" in u:
        return "product/patch-pleisters-dexcom-g7-40-stuks/"
    if "omnipod" in u:
        return "product/patch-pleisters-omnipod-50-125-stuks/"
    if "libre" in u:
        return "product/patch-pleister-freestyle-libre-2/"
    biker, legging = "biker" in u, any(k in u for k in ("legging", "sportlegging"))
    if biker and legging:
        return "product/sportlegging-bikershort-insulinepomp/"
    if biker:
        return "product/diabetes-2-pocket-bikershort/"
    if legging:
        return "product/diabetes-2-pocket-sportlegging/"
    if re.search(r"(?<!pocke)t-shirt", u) or ("camiseta" in u and "sin-mangas" not in u):
        return "product/diabetes-v-hals-t-shirt/" if is_v else "product/diabetes-ronde-hals-t-shirt/"
    if any(k in u for k in ("hemd", "shirt", "chemise", "canottiera", "skjorta", "sin-mangas")):
        return "product/diabetes-v-hals-hemd/" if is_v else "product/diabetes-ronde-hals-hemd/"
    return "winkel/"


def build_404():
    body = lambda R: hero_small("404", "Pagina niet gevonden", f'Deze pagina bestaat niet (meer). <a style="color:#fff" href="{R}winkel/">Bekijk alle producten</a>.', R)
    # GitHub Pages serveert 404.html op elk pad: daarom absolute paden.
    out = head("/", "404.html", "Pagina niet gevonden | Diabeticswear", "Pagina niet gevonden.", robots="noindex,follow") + \
        header("/", None) + f'<main id="main">{body("/")}</main>' + footer("/")
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(out)


def build_catalog():
    cat = {p["slug"]: {"name": p["name"], "price": p["price"], "img": f'assets/img/p/{p["imgs"][0]}-sm.webp'} for p in PRODUCTS}
    open(os.path.join(ROOT, "assets", "js", "catalog.js"), "w", encoding="utf-8").write(
        "/* Gegenereerd door tools/build.py, niet handmatig aanpassen. */\nwindow.DW_CATALOG=" + json.dumps(cat, ensure_ascii=False) + ";\n")


PAGE_IMGS = {}


def build_sitemap():
    def entry(p):
        imgs = "".join(f"<image:image><image:loc>{DOMAIN}assets/img/p/{i}.webp</image:loc></image:image>" for i in PAGE_IMGS.get(p, []))
        prio = "1.0" if p == "" else "0.9" if p.startswith("product/") or p == "winkel/" else "0.7" if p.startswith("kennisbank/") else "0.8" if p.count("/") == 1 and p.split("/")[0] in [c["slug"] for c in CATS] else "0.5"
        return f"<url><loc>{DOMAIN}{p}</loc><lastmod>{LASTMOD}</lastmod><priority>{prio}</priority>{imgs}</url>"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(entry(p) for p in PAGES) + "\n</urlset>\n")
    bots = ["Googlebot", "Bingbot", "Google-Extended", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
            "PerplexityBot", "Applebot", "Applebot-Extended"]
    robots = "# Diabeticswear: zoekmachines en AI-assistenten zijn welkom.\n" + \
        "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + "User-agent: *\nAllow: /\n\n" + f"Sitemap: {DOMAIN}sitemap.xml\n"
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(robots)


def build_llms():
    """llms.txt: beknopte, feitelijke samenvatting voor AI-assistenten (GEO)."""
    lines = ["# Diabeticswear", "",
             "> Nederlandse webshop voor mensen met diabetes die een insulinepomp of CGM-sensor dragen: kleding met twee pompzakjes en een gaatje voor de infuusslang, transparante patch pleisters voor sensoren en pods, compressiesokken en een insuline organizer.", "",
             f"- Bedrijf: Diabeticswear, {ADDR}. KvK 91840376, btw NL004919866B33.",
             f"- Contact: {MAIL}, {TEL}. Reactie binnen 24 uur.",
             "- Verzending: Nederland gratis vanaf € 30 (anders € 4,25), België gratis vanaf € 75 (anders € 5,25). Levering in 2-3 werkdagen.",
             "- Retour: binnen 14 dagen na ontvangst, retourkosten voor eigen rekening. Terugbetaling binnen 5 werkdagen.",
             "- Betalen: iDEAL, Bancontact, Klarna of overboeking.",
             "- T-shirts en hemden vallen groot uit: een maat kleiner bestellen dan normaal.", "",
             "## Producten", ""]
    for slug in SHOP_ORDER:
        p = BY[slug]
        price = f'vanaf {eur(p["variants"][0][1])}' if p.get("variants") else eur(p["price"])
        extra = []
        if p.get("sizes"):
            extra.append("maten " + "/".join(p["sizes"]))
        if p.get("colors"):
            extra.append("kleuren " + "/".join(c[0].lower() for c in p["colors"]))
        lines.append(f'- [{p["name"]}]({DOMAIN}product/{slug}/): {price}. {p["seo_desc"]}' + (f' ({"; ".join(extra)})' if extra else ""))
    lines += ["", "## Categorieën", ""] + [f'- [{c["h1"]}]({DOMAIN}{c["slug"]}/): {c["intro"]}' for c in CATS]
    lines += ["", "## Kennisbank", ""] + [f'- [{a["title"]}]({DOMAIN}kennisbank/{a["slug"]}/): {a["desc"]}' for a in KB["articles"]]
    lines += ["", "## Informatie", "",
              f"- [Veelgestelde vragen]({DOMAIN}veelgestelde-vragen/)", f"- [Over ons]({DOMAIN}over-ons/)", f"- [Contact]({DOMAIN}contact/)",
              f"- [Retourbeleid]({DOMAIN}terugbetaalde-retourneringen/)", f"- [Algemene voorwaarden]({DOMAIN}algemene-voorwaarden/)",
              f"- [Privacybeleid]({DOMAIN}privacybeleid/)", "",
              "Freestyle Libre, Dexcom en Omnipod zijn merken van hun respectievelijke eigenaren; Diabeticswear is hier niet aan gelieerd.", ""]
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines))


def build_manifest():
    m = {"name": "Diabeticswear", "short_name": "Diabeticswear", "lang": "nl", "start_url": "./", "display": "browser",
         "background_color": "#F3F2EE", "theme_color": "#2BAA92",
         "icons": [{"src": "assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                   {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}
    open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8").write(json.dumps(m, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    build_home()
    build_shop()
    for c in CATS:
        build_category(c)
    for p in PRODUCTS:
        build_product(p)
    build_kb_index()
    for a in KB["articles"]:
        build_kb_article(a)
    build_about()
    build_faq()
    build_contact()
    for slug, d in C["legal"].items():
        build_legal(slug, d)
    build_redirect("product/patch-pleister-freestyle-libre2/", "product/patch-pleister-freestyle-libre-2/")
    build_redirect("product/patch-pleisters-freestyle-libre-2-40-stycken/", "product/patch-pleister-freestyle-libre-2/")
    build_redirect("product/rundhals-2-taschen-t-shirt/", "product/diabetes-ronde-hals-t-shirt/")
    for lang in ("en", "de", "fr", "it", "es", "sv"):
        build_redirect(lang + "/", "")
    for u in C.get("old_urls", []):
        build_redirect(u, old_target(u))
    build_404()
    build_catalog()
    build_sitemap()
    build_llms()
    build_manifest()
    print(f"{len(PAGES)} pagina's, {len(REDIRECTS)} doorverwijzingen gegenereerd")
