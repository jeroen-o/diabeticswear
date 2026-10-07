#!/usr/bin/env python3
"""Genereert de statische site van Diabeticswear uit tools/content.json.

Gebruik:  python3 tools/build.py
De gegenereerde HTML wordt mee gecommit; de site zelf heeft geen build-step nodig.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from i18n import (BASE, CATLABEL as CATLABEL_I, COLORS, HTML_LANG, IN_LANG, JS, LANG_NAME, LANGS, OG_LOCALE, PATHS,  # noqa: E402
                  SPEC_KEYS, SPEC_VALUES, UI)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://diabeticswear.com/"
# Zoekmachines buiten de deur houden (preview/testfase). Zet op False zodra de site live mag in Google.
NOINDEX = True
NOINDEX_ROBOTS = "noindex, nofollow"
C = json.load(open(os.path.join(ROOT, "tools", "content.json"), encoding="utf-8"))
PRODUCTS = C["products"]
for _p in PRODUCTS:
    _p["id"] = _p["slug"]
BY = {p["slug"]: p for p in PRODUCTS}
CATS = C["cats"]
KB = json.load(open(os.path.join(ROOT, "tools", "kennisbank.json"), encoding="utf-8"))
SIZE_TABLE = [("Lengte (zijde 1)", [70, 73, 75, 77, 80, 81]), ("Breedte (zijde 2)", [50, 51, 52, 53, 55, 56]),
              ("Zakje breedte (zijde 3)", [11.7] * 6), ("Zakje hoogte (zijde 4)", [13.8] * 6)]
SIZE_COLS = ["XS", "S", "M", "L", "XL", "XXL"]
MAIL = "info@diabeticswear.com"
TEL, TEL_LINK = "+31 6 10022060", "tel:+31610022060"
ADDR = "De Wel 14-16, 3871 MV Hoevelaken"
e = html.escape
LANG = "nl"          # taal van de pagina die nu gebouwd wordt
LOC = {l: json.load(open(os.path.join(ROOT, "tools", f"content-{l}.json"), encoding="utf-8")) for l in ("en", "de")}
CRUMB_ARIA = {"nl": "Kruimelpad", "en": "Breadcrumb", "de": "Brotkrümelnavigation"}
NAV_ARIA = {"nl": "Hoofdmenu", "en": "Main menu", "de": "Hauptmenü"}


def U(k):
    return UI[LANG][k]

CATLABEL = {"tshirts": "T-shirts", "hemden": "Hemden", "sportlegging": "Sportlegging", "bikershorts": "Bikershorts",
            "rokken": "Sport rok", "sokken": "Compressiesokken", "patches": "Patch pleisters", "accessoires": "Accessoires"}
CATPAGE = {"tshirts": "diabetes-t-shirts-insulinepomp", "hemden": "diabetes-hemden-insulinepomp",
           "sportlegging": "diabetes-2-pocket-sportlegging", "bikershorts": "diabetes-2-pocket-bikershort-sporten",
           "rokken": "diabetes-2-pocket-bikershort-sporten", "sokken": "diabetes-compressiesokken",
           "patches": "productpagina-patch-pleisters", "accessoires": "producten-kleding-accessoires-overig"}


def eur(v, lang=None):
    lang = lang or LANG
    if lang == "en":
        return f"€{v:,.2f}"
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €" if lang == "de" else "€ " + s


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


def hreflang_links(path, alts):
    alts = alts or {LANG: path}
    out = "".join(f'<link rel="alternate" hreflang="{l}" href="{DOMAIN}{alts[l]}">\n' for l in LANGS if l in alts)
    return out + f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}{alts.get("nl", path)}">\n'


def head(R, path, title, desc, extra="", og_img=None, og_type="website", preload=None, product=None,
         robots="index,follow,max-image-preview:large,max-snippet:-1", alts=None):
    canon = DOMAIN + path
    if NOINDEX:
        robots = NOINDEX_ROBOTS
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
<html lang="{HTML_LANG[LANG]}" data-root="{R}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon}">
{hreflang_links(path, alts)}<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="{OG_LOCALE[LANG]}">
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
<a class="skip" href="#main">{U("skip")}</a>
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
    return (f'<a class="logo" href="{R}{BASE[LANG]}" aria-label="{U("logo_aria")}">'
            f'<span class="logo-mark" aria-hidden="true"></span><span>Diabetics<b>Wear</b></span></a>')


def lang_switch(R, alts):
    alts = alts or {}
    out = []
    for l in LANGS:
        href = R + alts.get(l, PATHS[l]["home"])
        cur = ' aria-current="true"' if l == LANG else ""
        out.append(f'<a href="{href}" hreflang="{l}" lang="{l}"{cur} title="{LANG_NAME[l]}">{l.upper()}</a>')
    return f'<div class="lang-switch" role="group" aria-label="{U("lang_label")}">' + "".join(out) + "</div>"


def nav_items():
    if LANG == "nl":
        return NAV
    out = []
    for label, key in LOC[LANG]["nav"]:
        k, _, h = key.partition("#")
        out.append((label, PATHS[LANG][k] + (f"#{h}" if h else ""), None))
    return [("Home", "", None)] + out


def header(R, active, alts=None):
    items = []
    for label, href, sub in nav_items():
        if label == "Home":
            continue
        cur = ' aria-current="page"' if active == href else ""
        if sub:
            subs = "".join(f'<a href="{R}{h}">{e(l)}</a>' for l, h in sub)
            items.append(f'<div class="has-sub"><a href="{R}{href}"{cur}>{label}</a><div class="sub">{subs}</div></div>')
        else:
            items.append(f'<a href="{R}{href}"{cur}>{label}</a>')
    tb = "".join(f"<span>{t}</span>" for t in U("topbar"))
    return f"""<div class="topbar">{tb}</div>
<header class="header">
  <div class="container">
    {logo(R)}
    <button class="menu-btn" aria-label="{U("menu")}" aria-expanded="false" aria-controls="nav"><svg aria-hidden="true" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    <nav class="nav" id="nav" aria-label="{NAV_ARIA[LANG]}">
      {"".join(items)}
      {lang_switch(R, alts)}
    </nav>
    <button class="cart-btn"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 7h12l-1 13H7z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg><span class="label">{U("cart")}</span><span class="cart-count">0</span><span class="sr-only">{U("cart_sr")}</span></button>
  </div>
</header>
"""


NL_FOOT_SHOP = [("T-shirts", "diabetes-t-shirts-insulinepomp/"), ("Hemden", "diabetes-hemden-insulinepomp/"),
                ("Sportlegging", "diabetes-2-pocket-sportlegging/"), ("Bikershorts &amp; sport rok", "diabetes-2-pocket-bikershort-sporten/"),
                ("Compressiesokken", "diabetes-compressiesokken/"), ("Patch pleisters", "productpagina-patch-pleisters/"),
                ("Accessoires", "producten-kleding-accessoires-overig/")]
NL_FOOT_SERVICE = [("Veelgestelde vragen", "veelgestelde-vragen/"), ("Kennisbank", "kennisbank/"), ("Maatgids", "kennisbank/maatgids-diabetes-kleding/"),
                   ("Retourbeleid", "terugbetaalde-retourneringen/"), ("Over ons", "over-ons/"), ("Contact", "contact/")]


def foot_links(kind):
    if LANG == "nl":
        return NL_FOOT_SHOP if kind == "shop" else NL_FOOT_SERVICE
    out = []
    for label, key in LOC[LANG]["footer_" + kind]:
        k, _, h = key.partition("#")
        out.append((e(label), PATHS[LANG][k] + (f"#{h}" if h else "")))
    return out


def footer(R):
    shop = "\n".join(f'        <li><a href="{R}{h}">{l}</a></li>' for l, h in foot_links("shop"))
    serv = "\n".join(f'        <li><a href="{R}{h}">{l}</a></li>' for l, h in foot_links("service"))
    lg, note = U("legal"), U("legal_note")
    legal = (f'<a href="{R}algemene-voorwaarden/">{lg[0]}</a> · <a href="{R}privacybeleid/">{lg[1]}</a> · '
             f'<a href="{R}terugbetaalde-retourneringen/">{lg[2]}</a>{note}')
    nl_opt = f'<option value="NL">{U("nl")}</option><option value="BE">{U("be")}</option>'
    return f"""<footer class="footer">
  <div class="container">
    <div class="cols">
      <div>
        {logo(R)}
        <p>{U("tagline")}</p>
      </div>
      <div><h2 class="fh">{U("f_shop")}</h2><ul>
{shop}
      </ul></div>
      <div><h2 class="fh">{U("f_service")}</h2><ul>
{serv}
      </ul></div>
      <div><h2 class="fh">{U("f_contact")}</h2><ul>
        <li><a href="mailto:{MAIL}">{MAIL}</a></li>
        <li><a href="{TEL_LINK}">{TEL}</a></li>
        <li>De Wel 14-16<br>3871 MV Hoevelaken</li>
        <li>{U("reply24")}</li>
      </ul></div>
    </div>
    <div class="bottom">
      <span>© 2026 Diabeticswear · KvK 91840376 · BTW NL004919866B33<br>{U("trademark")}</span>
      <span>{legal}</span>
    </div>
  </div>
</footer>
<aside class="drawer" id="drawer" aria-label="{U("drawer")}">
  <header><h2>{U("drawer")}</h2><button class="close" data-close-drawer aria-label="{U("close")}">×</button></header>
  <div class="drawer-items" id="d-items"></div>
  <footer>
    <div class="row"><span>{U("subtotal")}</span><span id="d-sub">{eur(0)}</span></div>
    <div class="row"><span>{U("ship_to")} <label class="sr-only" for="d-country">{U("country")}</label><select id="d-country">{nl_opt}</select></span><span id="d-ship">{U("free")}</span></div>
    <div class="ship-bar"><span id="d-shipfill"></span></div>
    <small id="d-shipmsg"></small>
    <div class="total" style="margin-top:.8rem"><span>{U("total")}</span><span id="d-total">{eur(0)}</span></div>
    <button class="btn btn-primary btn-block" id="d-checkout">{U("checkout")}</button>
  </footer>
</aside>
<div class="drawer-bg" id="drawer-bg"></div>
<dialog class="modal" id="checkout-dlg" aria-labelledby="co-title"><div class="inner">
  <header><h2 id="co-title" style="margin:0">{U("checkout")}</h2><button class="close" style="background:none;border:0;font-size:1.6rem;cursor:pointer" data-close aria-label="{U("close")}">×</button></header>
  <form class="form" id="co-form">
    <p class="small" style="margin:0">{U("co_intro").format(mail=MAIL)}</p>
    <div class="two"><label>{U("f_name")} *<input name="naam" required autocomplete="name"></label><label>{U("f_email")} *<input name="email" type="email" required autocomplete="email"></label></div>
    <div class="two"><label>{U("f_tel")}<input name="tel" type="tel" autocomplete="tel"></label><label>{U("country")}<select name="land" id="co-country">{nl_opt}</select></label></div>
    <label>{U("f_street")} *<input name="adres" required autocomplete="street-address"></label>
    <div class="two"><label>{U("f_zip")} *<input name="postcode" required autocomplete="postal-code"></label><label>{U("f_city")} *<input name="plaats" required autocomplete="address-level2"></label></div>
    <label>{U("f_pay")}<select name="betaling"><option>iDEAL</option><option>Bancontact</option><option>Klarna</option><option>{U("f_transfer")}</option></select></label>
    <label>{U("f_note")}<textarea name="opmerking" rows="3" style="min-height:80px"></textarea></label>
    <button class="btn btn-primary" type="submit">{U("co_submit")}</button>
    <p class="small" style="margin:0">{U("co_agree").format(av=R + "algemene-voorwaarden/", pr=R + "privacybeleid/")}</p>
  </form>
  <div id="co-done" hidden>
    <p>{U("co_done").format(mail=MAIL)}</p>
    <button class="btn btn-primary" id="co-clear" type="button">{U("co_clear")}</button>
  </div>
</div></dialog>
<dialog class="modal lightbox" id="lightbox" aria-label="{U("lightbox")}"><button class="close" style="border:0;font-size:1.5rem;cursor:pointer" data-close aria-label="{U("close")}">×</button><img alt=""></dialog>
<script src="{R}assets/js/catalog{"" if LANG == "nl" else "-" + LANG}.js"></script>
<script src="{R}assets/js/main.js"></script>
</body>
</html>
"""


def page(path, title, desc, body, active=None, extra="", og=None, alts=None, **kw):
    depth = path.count("/")
    R = "../" * depth
    out = head(R, path, title, desc, extra, og, alts=alts, **kw) + header(R, active if active is not None else path, alts) + \
        f'<main id="main">\n{body(R)}\n</main>\n' + footer(R)
    fp = os.path.join(ROOT, path, "index.html") if path else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(out)
    PAGES.append(path)


PAGES = []


def purl(p):
    return f'{BASE[LANG]}product/{p["slug"]}/'


def catlabel(cat):
    return CATLABEL_I[LANG][cat]


def catpage(cat):
    return CATPAGE[cat] + "/" if LANG == "nl" else PATHS[LANG]["shop"] + "#" + cat


# ---------------------------------------------------------------- componenten

def price_html(p):
    if p.get("variants"):
        return f'<span class="from">{U("from")}</span> {eur(p["variants"][0][1])}'
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
    return (f'<a class="card" href="{R}{purl(p)}" data-cats="{cats}" data-price="{price}" data-order="{order}">'
            f'<div class="card-media"><img src="{img(p["imgs"][0], R, True)}" {srcset(p["imgs"][0], R)} sizes="(max-width:520px) 100vw, (max-width:1000px) 50vw, 280px" alt="{alt}" {"" if eager else 'loading="lazy" '}width="600" height="600">{second}{tag}</div>'
            f'<div class="card-body"><small>{catlabel(p["cat"])}</small><h3>{alt}</h3>{dots}<span class="price">{price_html(p)}</span></div></a>')


def grid(ps, R, gid="", eager=0, title=None):
    return (f'<h2 class="sr-only">{e(title)}</h2>' if title else "") + f'<div class="grid"{f" id={gid}" if gid else ""}>' + "".join(card(p, R, i, i < eager) for i, p in enumerate(ps)) + "</div>"


def collection_ld(path, name, desc, ps, trail):
    items = [{"@type": "ListItem", "position": i + 1, "url": DOMAIN + purl(p), "name": p["name"]} for i, p in enumerate(ps)]
    crumbs_l = [{"@type": "ListItem", "position": 1, "name": U("home"), "item": DOMAIN + BASE[LANG]}] + \
        [{"@type": "ListItem", "position": i + 2, "name": n, "item": DOMAIN + h} for i, (n, h) in enumerate(trail)]
    return ld({"@context": "https://schema.org", "@type": "CollectionPage", "@id": DOMAIN + path, "url": DOMAIN + path, "name": name,
               "description": desc, "inLanguage": IN_LANG[LANG], "isPartOf": {"@id": SITE_ID},
               "mainEntity": {"@type": "ItemList", "numberOfItems": len(ps), "itemListElement": items}}) + \
        ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs_l})


def hero_small(eyebrow, title, text, R):
    return (f'<section class="hero hero-sub"><div class="container"><div><span class="eyebrow">{e(eyebrow)}</span>'
            f'<h1>{e(title)}</h1>{f"<p class=lead>{text}</p>" if text else ""}</div></div></section>')


def crumbs(R, items):
    out = [f'<a href="{R}{BASE[LANG]}">{U("home")}</a>'] + [f'<a href="{R}{h}">{e(l)}</a>' if h is not None else e(l) for l, h in items]
    return f'<nav class="crumbs container" aria-label="{CRUMB_ARIA[LANG]}">{" / ".join(out)}</nav>'


def faq_html(items):
    return "".join(f'<details><summary>{e(q)}</summary><p>{linkify(e(a))}</p></details>' for q, a in items)


def linkify(t):
    return t.replace(MAIL, f'<a href="mailto:{MAIL}">{MAIL}</a>')


def reviews_html(rs, single=False):
    out = "".join(f'<blockquote class="review" style="margin:0"><p>“{e(txt)}”</p><footer>{e(name)} · {U("review_about")} {e(prod)}{U("translated")}</footer></blockquote>'
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
    return '<div class="container usps">' + "".join(usp(i, t, d) for i, t, d in U("usps")) + "</div>"


def usps_values():
    return '<div class="usps">' + usp("move", "Bewegingsvrijheid", "Sporten, werken of ontspannen: je pomp blijft veilig op zijn plek.") + \
        usp("shield", "Geen loshangende slang", "Het gaatje in de zak houdt de infuusslang netjes weg.") + \
        usp("eye", "Discreet", "De slang is weggewerkt, voor een onopvallende look.") + \
        usp("heart", "Kwaliteit", "Elk kledingstuk wordt zorgvuldig getest op comfort en duurzaamheid.") + "</div>"


def perks():
    return '<ul class="perks">' + "".join(f"<li>{x.format(mail=MAIL)}</li>" for x in U("perks")) + "</ul>"


def newsletter_contact(R):
    return f"""<div class="container" style="margin-top:4rem">
  <div class="newsletter">
    <div><h2 style="margin-bottom:.3rem">{U("nc_title")}</h2><p style="margin:0;opacity:.9">{U("nc_text")}</p></div>
    <div style="display:flex;gap:.5rem;flex-wrap:wrap"><a class="btn btn-light" href="{R}{PATHS[LANG]["contact"]}">{U("nc_btn")}</a><a class="btn btn-ghost" href="mailto:{MAIL}">{MAIL}</a></div>
  </div>
</div>"""


# ---------------------------------------------------------------- talen

TAGS = {"en": {"Bestseller": "Bestseller", "Combi deal": "Combo deal", "Nieuw": "New"},
        "de": {"Bestseller": "Bestseller", "Combi deal": "Kombi-Angebot", "Nieuw": "Neu"}}


def tr_value(v, lang):
    if lang == "nl" or not v:
        return v
    if v.startswith("Zie label"):
        return {"en": "See label in the item", "de": "Siehe Etikett im Artikel"}[lang]
    for a, b in SPEC_VALUES[lang]:
        if not a.startswith("Zie label"):
            v = v.replace(a, b)
    return v


def localize(p, lang):
    L = LOC[lang]["products"][p["slug"]]
    q = dict(p)
    q.update(id=p["slug"], slug=L["slug"], name=L["name"], seo_title=L["seo_title"], seo_desc=L["seo_desc"], meta=L["seo_desc"],
             usp=L["usp"], body=L["body"])
    q.pop("color_label", None)
    if L.get("color_label"):
        q["color_label"] = L["color_label"]
    if p.get("variants"):
        q["variants"] = [[lab, v[1]] for lab, v in zip(L["variants"], p["variants"])]
        q["variant_note"] = L.get("variant_note", "")
    q["colors"] = [[COLORS[lang][n], h] for n, h in p.get("colors", [])]
    q["rules"] = {sz: COLORS[lang][c] for sz, c in p.get("rules", {}).items()}
    q["specs"] = [[SPEC_KEYS[lang].get(k, k), tr_value(v, lang)] for k, v in p["specs"]]
    if p.get("tag"):
        q["tag"] = TAGS[lang][p["tag"]]
    return q


LP = {"nl": BY}
for _l in ("en", "de"):
    LP[_l] = {p["slug"]: localize(p, _l) for p in PRODUCTS}


def prod_alts(pid):
    return {l: f'{BASE[l]}product/{LP[l][pid]["slug"]}/' for l in LANGS}


def static_alts(key):
    return {l: PATHS[l][key] for l in LANGS}


def reviews_loc():
    if LANG == "nl":
        return C["reviews"]
    L = LOC[LANG]
    return [(r[0], L["review_products"][i], L["reviews"][i], r[3]) for i, r in enumerate(C["reviews"])]


def webpage_ld(path, name, typ="WebPage"):
    return ld({"@context": "https://schema.org", "@type": typ, "url": DOMAIN + path, "name": name, "inLanguage": IN_LANG[LANG],
               "isPartOf": {"@id": SITE_ID}, "about": {"@id": ORG_ID}})


def build_home_i18n():
    H = LOC[LANG]["home"]
    P_ = LP[LANG]
    feat = [P_[x] for x in ("patch-pleister-freestyle-libre-2", "diabetes-2-pocket-sportlegging", "diabetes-2-pocket-bikershort", "diabetes-v-hals-t-shirt")]
    patches = [P_[x["slug"]] for x in PRODUCTS if x["cat"] == "patches"]
    combo = P_["sportlegging-bikershort-insulinepomp"]
    F = LOC[LANG]["faq"]
    picks = [F[1][1][0], F[1][1][1], F[2][1][1], F[2][1][2], F[3][1][1]]
    shop = PATHS[LANG]["shop"]

    def body(R):
        badges = "".join(f"<span>{e(b)}</span>" for b in H["badges"])
        cats = "".join(f'<a class="cat cat-{i + 1}" href="{R}{shop}#{k}"><span class="stripe"></span><small>{e(sm)}</small><h3>{e(t)}</h3></a>'
                       for i, (sm, t, k) in enumerate(H["cats"]))
        how = "".join(f"<li>{e(x)}</li>" for x in H["how_list"])
        return f"""<section class="hero">
  <div class="container">
    <div>
      <span class="eyebrow">{e(H["eyebrow"])}</span>
      <h1>{e(H["h1"])}</h1>
      <p class="lead">{e(H["lead"])}</p>
      <div class="hero-actions">
        <a class="btn btn-light" href="{R}{shop}">{e(H["btn1"])}</a>
        <a class="btn btn-ghost" href="{R}{shop}#patches">{e(H["btn2"])}</a>
      </div>
      <div class="hero-badges">{badges}</div>
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
<section>
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">{e(H["cats_eyebrow"])}</span><h2>{e(H["cats_title"])}</h2></div><p>{e(H["cats_text"])}</p></div>
    <div class="cats">{cats}</div>
  </div>
</section>
<section class="bg-white">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">{e(H["best_eyebrow"])}</span><h2>{e(H["best_title"])}</h2></div><a class="btn btn-primary" href="{R}{shop}">{e(H["view_all"])}</a></div>
    {grid(feat, R)}
  </div>
</section>
<section>
  <div class="container split">
    <div class="split-visual" style="padding:0;overflow:hidden"><img src="{img("diabetes-2-pocket-sportlegging-3", R)}" alt="" loading="lazy" width="1200" height="1200"></div>
    <div>
      <span class="eyebrow">{e(H["how_eyebrow"])}</span>
      <h2>{e(H["how_title"])}</h2>
      <p>{e(H["how_text"])}</p>
      <ul class="checklist">{how}</ul>
      <a class="btn btn-primary" href="{R}{shop}#kleding">{e(H["view_all"])}</a>
    </div>
  </div>
</section>
<section class="bg-white">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">{e(H["patch_eyebrow"])}</span><h2>{e(H["patch_title"])}</h2></div><p>{e(H["patch_text"])}</p></div>
    {grid(patches, R)}
  </div>
</section>
<section>
  <div class="container split">
    <div>
      <span class="eyebrow">{e(H["combo_eyebrow"])}</span>
      <h2>{e(H["combo_title"].format(p=eur(48.95)))}</h2>
      <p>{e(H["combo_text"].format(c=eur(51.90)))}</p>
      <a class="btn btn-primary" href="{R}{purl(combo)}">{e(H["combo_btn"])}</a>
    </div>
    <div class="split-visual" style="padding:0;overflow:hidden"><img src="{img("sportlegging-bikershort-insulinepomp-1", R)}" alt="" loading="lazy" width="1200" height="1200"></div>
  </div>
</section>
<section class="bg-white">
  <div class="container">
    <div class="section-head"><div><span class="eyebrow">{e(H["rev_eyebrow"])}</span><h2>{e(H["rev_title"])}</h2></div><p>{e(H["rev_text"])}</p></div>
    {reviews_html(reviews_loc())}
  </div>
</section>
<section>
  <div class="container faq">
    <div style="text-align:center;margin-bottom:2rem"><span class="eyebrow">{e(H["faq_eyebrow"])}</span><h2>{e(H["faq_title"])}</h2></div>
    {faq_html(picks)}
    <p style="text-align:center;margin-top:1.4rem"><a class="btn btn-primary" href="{R}{PATHS[LANG]["faq"]}">{e(H["faq_btn"])}</a></p>
  </div>
</section>
{newsletter_contact(R)}"""
    path = PATHS[LANG]["home"]
    page(path, H["title"], H["desc"], body, alts=static_alts("home"), extra=webpage_ld(path, H["title"]),
         preload="assets/img/p/diabetes-2-pocket-sportlegging-1.webp")


def build_shop_i18n():
    S = LOC[LANG]["shop"]
    ps = [LP[LANG][x] for x in SHOP_ORDER]
    path = PATHS[LANG]["shop"]

    def body(R):
        ch = "".join(f'<button class="chip" type="button" data-cat="{k}" aria-pressed="false">{e(l)}</button>' for k, l in S["chips"])
        so = S["sort"]
        return (crumbs(R, [(S["h1"], None)]) + hero_small(S["eyebrow"], S["h1"], e(S["lead"]), R) +
                f'<section><div class="container"><div class="filters" role="group" aria-label="{e(S["filter_label"])}">{ch}'
                f'<label class="sr-only" for="sort">{e(S["sort_label"])}</label><select id="sort"><option value="std">{so[0]}</option><option value="laag">{so[1]}</option><option value="hoog">{so[2]}</option></select></div>'
                f'<p class="small" id="shop-count" style="margin:-.6rem 0 1rem"></p>' + grid(ps, R, "shop-grid", eager=4, title=S["h1"]) + '</div></section>' +
                f'<section class="bg-white" style="padding:2.5rem 0">{usps_service()}</section>')
    page(path, S["title"], S["desc"], body, alts=static_alts("shop"), extra=collection_ld(path, S["h1"], S["desc"], ps, [(S["h1"], path)]))


def build_faq_i18n():
    Fp = LOC[LANG]["faqpage"]
    F = LOC[LANG]["faq"]
    path = PATHS[LANG]["faq"]
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": IN_LANG[LANG], "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for _, items in F for q, a in items]}

    def body(R):
        groups = "".join(f'<div class="faq-group"><h2>{e(g)}</h2>{faq_html(items)}</div>' for g, items in F)
        return hero_small(Fp["eyebrow"], Fp["h1"], e(Fp["lead"]), R) + f'<section><div class="container faq">{groups}</div></section>' + newsletter_contact(R)
    page(path, Fp["title"], Fp["desc"], body, alts=static_alts("faq"), extra=ld(faq_ld))


def build_about_i18n():
    A = LOC[LANG]["about"]
    path = PATHS[LANG]["about"]

    def body(R):
        vals = '<div class="usps">' + "".join(usp(i, e(t), e(d)) for i, t, d in A["values"]) + "</div>"
        return hero_small(A["eyebrow"], A["h1"], "", R) + f"""
<section class="bg-white"><div class="container split">
  <div>
    <span class="eyebrow">{e(A["m_eyebrow"])}</span>
    <h2>{e(A["m_title"])}</h2>
    <p>{e(A["m1"])}</p>
    <p>{e(A["m2"])}</p>
    <a class="btn btn-primary" href="{R}{PATHS[LANG]["shop"]}">{e(A["btn"])}</a>
  </div>
  <div class="split-visual" style="padding:0;overflow:hidden"><img src="{img("diabetes-v-hals-hemd-3", R)}" alt="" loading="lazy" width="1200" height="1200"></div>
</div></section>
<section><div class="container">
  <div class="section-head"><div><span class="eyebrow">{e(A["v_eyebrow"])}</span><h2>{e(A["v_title"])}</h2></div></div>
  {vals}
</div></section>
<section class="bg-white"><div class="container">
  <div class="section-head"><div><span class="eyebrow">{U("r_eyebrow")}</span><h2>{U("r_title")}</h2></div></div>
  {reviews_html(reviews_loc()[:3])}
</div></section>
{newsletter_contact(R)}"""
    page(path, A["title"], A["desc"], body, alts=static_alts("about"), extra=webpage_ld(path, A["title"], "AboutPage"))


def build_contact_i18n():
    K = LOC[LANG]["contact"]
    path = PATHS[LANG]["contact"]

    def body(R):
        subj = "".join(f"<option>{e(x)}</option>" for x in K["subjects"])
        return hero_small(K["eyebrow"], K["h1"], e(K["lead"]), R) + f"""
<section><div class="container contact-grid">
  <div class="page-card">
    <h2>{e(K["details"])}</h2>
    <ul class="contact-list">
      <li><strong>{e(K["email"])}</strong><br><a href="mailto:{MAIL}">{MAIL}</a></li>
      <li><strong>{e(K["phone"])}</strong><br><a href="{TEL_LINK}">{TEL}</a></li>
      <li><strong>{e(K["address"])}</strong><br>Diabeticswear<br>De Wel 14-16<br>3871 MV Hoevelaken<br>{"Netherlands" if LANG == "en" else "Niederlande"}</li>
    </ul>
    <p class="small" style="margin:1.4rem 0 0">KvK 91840376 · BTW NL004919866B33</p>
  </div>
  <div class="page-card">
    <h2>{e(K["form_title"])}</h2>
    <form class="form" id="contact-form">
      <div class="two"><label>{U("f_name")} *<input name="naam" required autocomplete="name"></label><label>{U("f_email")} *<input name="email" type="email" required autocomplete="email"></label></div>
      <div class="two"><label>{U("f_tel")}<input name="tel" type="tel" autocomplete="tel"></label><label>{e(K["subject"])}<select name="onderwerp">{subj}</select></label></div>
      <label>{e(K["message"])} *<textarea name="bericht" required></textarea></label>
      <button class="btn btn-primary" type="submit">{e(K["send"])}</button>
      <p class="small" id="contact-done" hidden>{K["done"]}</p>
      <p class="small" style="margin:0">{e(K["note"])}</p>
    </form>
  </div>
</div></section>"""
    page(path, K["title"], K["desc"], body, alts=static_alts("contact"), extra=webpage_ld(path, K["title"], "ContactPage"))


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
         body, extra=ld(org), preload="assets/img/p/diabetes-2-pocket-sportlegging-1.webp", alts=static_alts("home"))


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
    page("winkel/", "Alle producten voor insulinepomp-gebruikers | Diabeticswear", desc, body, alts=static_alts("shop"),
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


def product_faq_i18n(p):
    """Productvragen voor EN/DE uit de sjablonen in content-xx.json."""
    nl = BY[p["id"]]
    spec = dict((k.lower(), v) for k, v in nl["specs"])
    zak = tr_value(spec.get("afmetingen zakjes", ""), LANG)
    fill = {"zak": zak, "zakzin": (" " + {"en": "The pockets are {z}.", "de": "Die Taschen messen {z}."}[LANG].format(z=zak)) if zak else "",
            "material": tr_value(spec.get("materiaal", ""), LANG), "fit": spec.get("geschikt voor", ""),
            "dims": spec.get("afmetingen", ""), "count": tr_value(spec.get("aantal", ""), LANG), "mail": MAIL}
    qa = [(q, a.format(**fill)) for q, a in LOC[LANG]["pfaq"][p["group"]]]
    return qa + [tuple(U("ship_qa")), tuple(U("return_qa"))]


def product_faq(p):
    if LANG != "nl":
        return product_faq_i18n(p)
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
    return qa + [tuple(U("ship_qa")), tuple(U("return_qa"))]


def related(p):
    ps = [LP[LANG][x["slug"]] for x in PRODUCTS]
    same = [q for q in ps if q["group"] == p["group"] and q["id"] != p["id"]]
    rest = [q for q in ps if q["group"] != p["group"] and q.get("tag")]
    return (same + rest)[:4]


def build_product(p):
    path = purl(p)
    imgs = p["imgs"]
    sizes, colors, variants = p.get("sizes", []), p.get("colors", []), p.get("variants", [])
    rules = p.get("rules", {})
    pdata = {"slug": p["id"], "price": p["price"], "imgs": imgs, "sizes": sizes, "colors": [c[0] for c in colors],
             "rules": rules, "variants": variants, "colorLabel": p.get("color_label", U("color"))}
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
        offers = [dict(offer_base, **{"@type": "Offer", "name": v[0], "price": f"{v[1]:.2f}", "sku": f'{p["id"]}-{v[0].split()[0]}'}) for v in variants]
    else:
        offers = dict(offer_base, **{"@type": "Offer", "price": f'{p["price"]:.2f}'})
    spec = dict((k.lower(), v) for k, v in p["specs"])
    ld_prod = {"@context": "https://schema.org", "@type": "Product", "@id": DOMAIN + path + "#product", "name": p["name"],
               "description": p["seo_desc"], "sku": p["id"], "category": catlabel(p["cat"]), "url": DOMAIN + path, "inLanguage": IN_LANG[LANG],
               "image": [f"{DOMAIN}assets/img/p/{b}.webp" for b in imgs], "brand": {"@type": "Brand", "name": "Diabeticswear"},
               "manufacturer": {"@id": ORG_ID}, "offers": offers}
    if colors:
        ld_prod["color"] = ", ".join(c[0] for c in colors)
    if sizes:
        ld_prod["size"] = ", ".join(sizes)
    spec_nl = dict((k.lower(), v) for k, v in BY[p["id"]]["specs"])
    if "materiaal" in spec_nl:
        ld_prod["material"] = tr_value(spec_nl["materiaal"], LANG)
    if p["group"] in ("sport", "shirts", "sokken"):
        ld_prod["audience"] = {"@type": "PeopleAudience", "healthCondition": {"@type": "MedicalCondition", "name": "Diabetes"}}
    ld_prod["additionalProperty"] = [{"@type": "PropertyValue", "name": k, "value": v} for k, v in p["specs"]]
    crumbs_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": U("home"), "item": DOMAIN + BASE[LANG]},
        {"@type": "ListItem", "position": 2, "name": catlabel(p["cat"]), "item": DOMAIN + catpage(p["cat"])},
        {"@type": "ListItem", "position": 3, "name": p["name"], "item": DOMAIN + path}]}
    pfaq = product_faq(p)
    PAGE_IMGS[path] = imgs
    allrv = reviews_loc()
    rv = [r for r in allrv if r[3] == p["group"]]
    if p["group"] == "sport":
        rv = [allrv[i] for i, r in enumerate(C["reviews"]) if "Bikershort" in r[1]]

    def body(R):
        alt = e(p["name"])
        start = variants[0][1] if variants else p["price"]
        thumbs = "".join(f'<button type="button" aria-current="{str(i == 0).lower()}" aria-label="{U("img_n").format(n=i + 1)}"><img src="{img(b, R, True)}" alt="" width="600" height="600" loading="lazy"></button>' for i, b in enumerate(imgs))
        compare = f'<s>{eur(p["compare"])}</s>' if p.get("compare") else ""
        save = f'<span class="save">{U("save")} {eur(p["compare"] - p["price"])}</span>' if p.get("compare") else ""
        hl = "".join(f'<div class="hl"><strong>{e(u)}</strong></div>' for u in p.get("usp", []))
        opts = ""
        if variants:
            vb = "".join(f'<button type="button" class="size" data-variant="{i}" aria-pressed="false">{e(v[0])} · {eur(v[1])}</button>' for i, v in enumerate(variants))
            opts += f'<div class="opt"><div class="opt-label"><span>{U("qty_pieces")}</span></div><div class="sizes">{vb}</div>' + \
                    (f'<p class="hint">{linkify(e(p["variant_note"]))}</p>' if p.get("variant_note") else "") + "</div>"
        if len(colors) > 1:
            cb = "".join(f'<button type="button" class="swatch" data-color="{e(c[0])}" aria-pressed="false" aria-label="{e(c[0])}" title="{e(c[0])}" style="background:{c[1]}"></button>' for c in colors)
            opts += f'<div class="opt"><div class="opt-label"><span>{e(p.get("color_label", U("color")))}: <span id="sel-color" style="font-weight:600"></span></span></div><div class="swatches">{cb}</div></div>'
        elif colors:
            opts += f'<div class="opt"><div class="opt-label"><span>{U("color")}: <span style="font-weight:600">{e(colors[0][0])}</span></span></div></div>'
        if len(sizes) > 1:
            sb = "".join(f'<button type="button" class="size" data-size="{s}" aria-pressed="false">{s}</button>' for s in sizes)
            chart = f'<button type="button" data-zoom="{img(imgs[p["sizechart"] - 1], R)}" aria-label="{U("chart")} {alt}">{U("chart")}</button>' if p.get("sizechart") else ""
            rule_txt = " ".join(U("only_in").format(s=s, c=c.lower()) for s, c in rules.items())
            opts += (f'<div class="opt"><div class="opt-label"><span>{U("size")}: <span id="sel-size" style="font-weight:600"></span></span>{chart}</div><div class="sizes">{sb}</div>'
                     + (f'<p class="hint">{rule_txt}</p>' if rule_txt else "") + "</div>")
        elif sizes:
            opts += f'<div class="opt"><div class="opt-label"><span>{U("size")}: <span style="font-weight:600">{e(sizes[0])} {U("unisex")}</span></span></div></div>'
        note = f'<div class="advice">{U("note").format(mail=MAIL)}</div>' if p.get("note") else ""

        prose = []
        for kind, val in p["body"]:
            if kind == "p":
                prose.append(f"<p>{linkify(e(val))}</p>")
            elif kind == "h3":
                prose.append(f"<h3>{e(val)}</h3>")
            else:
                prose.append("<ul class='checklist'>" + "".join(f"<li>{e(x)}</li>" for x in val) + "</ul>")
        specs = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in p["specs"])
        tabs = [("desc", U("t_desc"), f'<div class="prose">{"".join(prose)}</div>')]
        if specs:
            tabs.append(("specs", U("t_specs"), f'<div class="table-wrap"><table>{specs}</table></div>'))
        if p.get("sizechart"):
            guide = f' <a href="{R}kennisbank/maatgids-diabetes-kleding/">{U("size_guide")}</a>.' if U("size_guide") else ""
            tabs.append(("size", U("t_size"), f'<p>{U("size_intro")}{guide}</p>' + size_table_html() +
                         f'<div class="sizechart" data-zoom="{img(imgs[p["sizechart"] - 1], R)}" role="button" tabindex="0" aria-label="{U("zoom_chart")}">'
                         f'<img src="{img(imgs[p["sizechart"] - 1], R)}" alt="{U("chart")} {alt}" loading="lazy" width="1200" height="1200"></div>'))
        tabs.append(("ship", U("t_ship"), U("ship_tab").format(ret=R + "terugbetaalde-retourneringen/")))
        tabbar = "".join(f'<button role="tab" aria-selected="{str(i == 0).lower()}" aria-controls="t-{k}" id="tab-{k}">{l}</button>' for i, (k, l, _) in enumerate(tabs))
        panels = "".join(f'<div class="tabpanel" role="tabpanel" id="t-{k}" aria-labelledby="tab-{k}"{" hidden" if i else ""}><h2 class="sr-only">{l}</h2>{c}</div>' for i, (k, l, c) in enumerate(tabs))
        rel = related(p)
        nav_btns = (f'<button class="gnav prev" data-d="-1" aria-label="{U("prev")}">‹</button><button class="gnav next" data-d="1" aria-label="{U("next")}">›</button>' if len(imgs) > 1 else "")
        return f"""<main class="container">
  {crumbs(R, [(catlabel(p["cat"]), catpage(p["cat"])), (p["name"], None)]).replace('class="crumbs container"', 'class="crumbs"')}
  <div class="pdp">
    <div>
      <div class="gallery-main" id="gmain" role="button" tabindex="0" aria-label="{U("zoom")}">
        {f'<span class="tag">{e(p["tag"])}</span>' if p.get("tag") else ""}
        <img src="{img(imgs[0], R)}" {srcset(imgs[0], R)} sizes="(max-width:900px) 100vw, 600px" alt="{alt}" width="1200" height="1200" fetchpriority="high">{nav_btns}
      </div>
      <div class="thumbs" id="thumbs">{thumbs if len(imgs) > 1 else ""}</div>
    </div>
    <div class="pdp-info">
      <span class="eyebrow">{catlabel(p["cat"])}</span>
      <h1 style="font-size:clamp(1.8rem,3.4vw,2.6rem)">{alt}</h1>
      <div class="pdp-price">{compare}<span class="js-price">{eur(start)}</span> <small>{U("incl_vat")}</small>{save}</div>
      <p style="color:var(--muted)">{e(p["meta"])}</p>
      <div class="highlights">{hl}</div>
      {opts}{note}
      <div class="buy-row">
        <div class="qty"><button type="button" id="qmin" aria-label="{U("less")}">−</button><input id="qty" value="1" inputmode="numeric" aria-label="{U("qty")}"><button type="button" id="qplus" aria-label="{U("more")}">+</button></div>
        <button class="btn btn-primary" id="add" type="button">{U("add")}</button>
      </div>
      <p class="notice" id="msg" role="status"></p>
      {perks()}
    </div>
  </div>

  <div class="tabs" role="tablist">{tabbar}</div>
  {panels}

  <section class="faq-mini" aria-labelledby="pfaq-title"><div class="section-head"><div><span class="eyebrow">{U("q_eyebrow")}</span><h2 id="pfaq-title">{U("q_title")}</h2></div></div><div class="faq" style="max-width:none">{faq_html(pfaq)}</div></section>

  {f'<section style="padding-top:1rem"><div class="section-head"><div><span class="eyebrow">{U("r_eyebrow")}</span><h2>{U("r_title")}</h2></div></div>{reviews_html(rv)}</section>' if rv else ""}

  <section style="padding-top:2rem">
    <div class="section-head"><div><span class="eyebrow">{U("rel_eyebrow")}</span><h2>{U("rel_title")}</h2></div></div>
    {grid(rel, R)}
  </section>
</main>
<div class="sticky-buy" id="sticky-buy"><strong>{alt}<br><span class="js-price">{eur(start)}</span></strong><button class="btn btn-primary" id="sticky-add" type="button">{U("add")}</button></div>
<script type="application/json" id="pdata">{json.dumps(pdata, ensure_ascii=False)}</script>"""
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pfaq]}
    page_raw(path, p["seo_title"], p["seo_desc"], body, active=catpage(p["cat"]), alts=prod_alts(p["id"]), extra=ld(ld_prod) + ld(crumbs_ld) + ld(faq_ld),
             og=f"assets/img/p/{imgs[0]}.webp", og_type="product", preload=imgs[0],
             product=(variants[0][1] if variants else p["price"],))


def page_raw(path, title, desc, body, active=None, extra="", og=None, alts=None, **kw):
    """Zoals page(), maar de body levert zelf het <main>-element."""
    depth = path.count("/")
    R = "../" * depth
    out = head(R, path, title, desc, extra, og, alts=alts, **kw) + header(R, active, alts) + \
        body(R).replace("<main class=\"container\">", '<main class="container" id="main">', 1) + "\n" + footer(R)
    fp = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(out)
    PAGES.append(path)


def num(v):
    """Getal in de notatie van de taal: 11,7 (nl/de) of 11.7 (en)."""
    t = f"{v:g}"
    return t if LANG == "en" else t.replace(".", ",")


def size_table_html():
    head_ = "".join(f"<th scope='col'>{c}</th>" for c in SIZE_COLS)
    rows = "".join(f"<tr><th scope='row'>{e(n)}</th>" + "".join(f"<td>{num(v)}</td>" for v in vals) + "</tr>"
                   for n, (_, vals) in zip(U("size_rows"), SIZE_TABLE))
    return f'<div class="table-wrap"><table><caption class="sr-only">{U("size_caption")}</caption><thead><tr><th scope="col">{U("size_head")}</th>{head_}</tr></thead><tbody>{rows}</tbody></table></div>'


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
    page("over-ons/", "Over ons | Diabeticswear", "Diabeticswear ontwerpt kleding waarmee mensen met diabetes hun insulinepomp veilig, comfortabel en discreet dragen.", body, alts=static_alts("about"),
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
         body, alts=static_alts("faq"), extra=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')


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
    page("contact/", "Contact | Diabeticswear", "Neem contact op met Diabeticswear via info@diabeticswear.com of +31 6 10022060. We reageren binnen 24 uur.", body, alts=static_alts("contact"),
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
        + (f'<meta name="robots" content="{NOINDEX_ROBOTS}">' if NOINDEX else "") +
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
    for lang in LANGS:
        cat = {p["slug"]: {"name": LP[lang][p["slug"]]["name"], "name_nl": p["name"], "price": p["price"],
                           "img": f'assets/img/p/{p["imgs"][0]}-sm.webp'} for p in PRODUCTS}
        fn = "catalog.js" if lang == "nl" else f"catalog-{lang}.js"
        open(os.path.join(ROOT, "assets", "js", fn), "w", encoding="utf-8").write(
            "/* Gegenereerd door tools/build.py, niet handmatig aanpassen. */\nwindow.DW_CATALOG=" + json.dumps(cat, ensure_ascii=False) +
            ";\nwindow.DW_I18N=" + json.dumps(dict(JS[lang], shopPath=PATHS[lang]["shop"]), ensure_ascii=False) + ";\n")


def lang_target(nl_target, lang):
    """Zet een Nederlands doel (product/<slug>/ of winkel/) om naar de pagina in een andere taal."""
    m = re.match(r"product/([^/]+)/$", nl_target)
    if m:
        return f'{BASE[lang]}product/{LP[lang][m.group(1)]["slug"]}/'
    return PATHS[lang]["shop"]


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
    if NOINDEX:
        # Crawlen blijft toegestaan, anders zien zoekmachines de noindex-tag niet.
        robots = ("# Testfase: alle pagina's hebben <meta name=\"robots\" content=\"noindex, nofollow\">.\n"
                  "# Crawlen blijft toegestaan zodat zoekmachines die tag kunnen lezen.\nUser-agent: *\nAllow: /\n")
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
    for lang, title in (("en", "English"), ("de", "Deutsch")):
        lines += [f"## {title}", "", f"- [{LOC[lang]['home']['title']}]({DOMAIN}{PATHS[lang]['home']})"]
        lines += [f'- [{LP[lang][x]["name"]}]({DOMAIN}{BASE[lang]}product/{LP[lang][x]["slug"]}/): {eur(LP[lang][x]["price"], lang)}' for x in SHOP_ORDER]
        lines += [""]
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
    for LANG in ("en", "de"):
        build_home_i18n()
        build_shop_i18n()
        for p in PRODUCTS:
            build_product(LP[LANG][p["slug"]])
        build_faq_i18n()
        build_about_i18n()
        build_contact_i18n()
    LANG = "nl"
    for slug, d in C["legal"].items():
        build_legal(slug, d)
    build_redirect("product/patch-pleister-freestyle-libre2/", "product/patch-pleister-freestyle-libre-2/")
    build_redirect("product/patch-pleisters-freestyle-libre-2-40-stycken/", "product/patch-pleister-freestyle-libre-2/")
    build_redirect("product/rundhals-2-taschen-t-shirt/", "product/diabetes-ronde-hals-t-shirt/")
    for lang in ("fr", "it", "es", "sv"):
        build_redirect(lang + "/", "en/")
    for u in C.get("old_urls", []):
        lang = u.split("/")[0]
        target = lang_target(old_target(u), lang if lang in ("en", "de") else "en")
        if target != u:
            build_redirect(u, target)
    build_404()
    build_catalog()
    build_sitemap()
    build_llms()
    build_manifest()
    print(f"{len(PAGES)} pagina's, {len(REDIRECTS)} doorverwijzingen gegenereerd")
