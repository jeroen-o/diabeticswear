# diabeticswear

Statische website voor [diabeticswear.com](https://diabeticswear.com): kleding met pompzakjes, patch pleisters en accessoires voor mensen met diabetes.

- Geen externe API's, fonts of frameworks. De gegenereerde HTML staat in de repo; de site werkt direct op GitHub Pages.
- Bron van alle teksten, prijzen en varianten: `tools/content.json`. Na een wijziging: `python3 tools/build.py`.
- Productfoto's: `assets/img/p/` (webp, 1200 px en `-sm` 600 px), omgezet uit de WooCommerce-export.
- URL's zijn gelijk aan de oude WooCommerce-site (`/product/<slug>/`, categoriepagina's, `/contact/` enz.).
- Winkelmand: sessionStorage met in-memory fallback. **Afrekenen gaat via een bestelaanvraag per e-mail** (mailto naar info@diabeticswear.com); er is nog geen online betaling gekoppeld.
- Contactformulier: opent het e-mailprogramma van de bezoeker (mailto).

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
