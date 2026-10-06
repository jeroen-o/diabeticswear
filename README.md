# diabeticswear

Statische website voor [diabeticswear.com](https://diabeticswear.com): kleding met pompzakjes, patch pleisters en accessoires voor mensen met diabetes.

- Geen externe API's, fonts of frameworks. De gegenereerde HTML staat in de repo; de site werkt direct op GitHub Pages.
- Bron van alle teksten, prijzen en varianten: `tools/content.json`. Na een wijziging: `python3 tools/build.py`.
- Productfoto's: `assets/img/p/` (webp, 1200 px en `-sm` 600 px), omgezet uit de WooCommerce-export.
- URL's zijn gelijk aan de oude WooCommerce-site (`/product/<slug>/`, categoriepagina's, `/contact/` enz.).
- Winkelmand: sessionStorage met in-memory fallback. **Afrekenen gaat via een bestelaanvraag per e-mail** (mailto naar info@diabeticswear.com); er is nog geen online betaling gekoppeld.
- Contactformulier: opent het e-mailprogramma van de bezoeker (mailto).

## SEO en GEO

- Per pagina: unieke titel (max. 60 tekens) en omschrijving, canonical naar `https://diabeticswear.com/…`, `robots`, `hreflang`, Open Graph en Twitter-card.
- Structured data (JSON-LD): Organization/OnlineStore + WebSite (home), Product met prijs, voorraad, verzendkosten NL/BE en retourbeleid, BreadcrumbList, CollectionPage/ItemList, FAQPage, AboutPage, ContactPage.
- `sitemap.xml` met afbeeldingen, `robots.txt` (zoekmachines en AI-crawlers toegestaan) en `llms.txt` met een feitelijke samenvatting voor AI-assistenten.
- Oude WooCommerce-URL's in andere talen (`/en/…`, `/de/…` enz.) verwijzen door naar de Nederlandse pagina.
- Snelheid: preload en `fetchpriority` voor de hoofdafbeelding, `srcset` (600/1200 px), lazy loading onder de vouw, vaste afmetingen tegen layout shift.
- Lighthouse (lokaal, mobiel en desktop): performance, best practices en SEO 100; toegankelijkheid 96-97 (alleen kleurcontrast wit op teal).

Zolang het domein nog niet naar GitHub Pages wijst, verwijzen de canonicals naar diabeticswear.com; de preview op github.io concurreert daardoor niet met de live shop.

## Kleuren

| Token | Hex | Gebruik |
|---|---|---|
| `--teal` | `#2BAA92` | Hoofdkleur |
| `--teal-deep` | `#145F52` | Topbar, prijzen |
| `--cream` | `#F3F2EE` | Pagina-achtergrond |
| `--mint` | `#7DC59A` | Accent |
| `--sky` | `#A3C8E6` | Accent |
| `--slate` | `#B6C4CD` | Accent |

## Live

GitHub Pages vanaf `main` (root): https://jeroen-o.github.io/diabeticswear/

Eigen domein: voeg een `CNAME`-bestand met `diabeticswear.com` toe en wijs de DNS naar GitHub Pages (A-records 185.199.108–111.153, `www` CNAME naar `jeroen-o.github.io`). Let op: daarmee gaat de huidige WooCommerce-shop offline.
