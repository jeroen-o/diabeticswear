# diabeticswear

Statische website voor [diabeticswear.com](https://diabeticswear.com): kleding en overpatches voor mensen met diabetes.

- Geen build-step, geen externe API's of fonts: open `index.html` direct in de browser.
- Productpagina: `product/diabetes-2-pocket-sportlegging/` (zelfde pad als de huidige WooCommerce-URL, zodat links blijven werken).
- Winkelmand is een demo (sessionStorage met in-memory fallback). Koppel bij livegang een betaalprovider/checkout in `assets/js/main.js` (`#checkout`).
- Prijzen staan in `assets/js/main.js` (`PRODUCTS`) en in de HTML; dit zijn placeholders.

## Kleuren

| Token | Hex | Gebruik |
|---|---|---|
| `--teal` | `#2BAA92` | Hoofdkleur, achtergrond productfoto's |
| `--teal-deep` | `#145F52` | Topbar, prijzen, accenten |
| `--cream` | `#F3F2EE` | Pagina-achtergrond (patchkleur) |
| `--mint` | `#7DC59A` | Accent (groene strook) |
| `--sky` | `#A3C8E6` | Accent (blauwe strook) |
| `--slate` | `#B6C4CD` | Accent (grijsblauwe strook) |

## Hosting via GitHub Pages

`CNAME` bevat `diabeticswear.com`. Zet Pages aan (Settings → Pages → branch `main`, map `/`) en wijs DNS naar GitHub Pages (A-records 185.199.108–111.153, `www` CNAME naar `jeroen-o.github.io`).
