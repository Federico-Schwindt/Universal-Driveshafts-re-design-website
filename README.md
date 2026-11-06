# Universal Driveshafts · Rediseño de la tienda

Nuevo diseño de la tienda de [Universal Driveshafts](https://dev.udshafts.com) (repuestos de cardanes y cardanes completos, Odessa, Florida). Empieza por el **home**. Es un diseño nuevo sobre **el mismo backend Laravel**: los mismos controladores, servicios, carrito, checkout con Stripe, envíos, cuentas mayoristas y asistente. Solo cambia la capa de presentación (Blade, CSS y JS).

**Vista previa:** https://federico-schwindt.github.io/Universal-Driveshafts-re-design-website/

La vista previa es una exportación estática del home renderizado por la app real. El buscador por vehículo y la búsqueda usan el catálogo en vivo de dev.udshafts.com. El resto de los enlaces abren la tienda actual, y "Agregar al carrito" muestra un aviso, porque la vista previa no tiene servidor.

## Qué hay en el home

- **Barra superior** con la cuenta regresiva real del envío en el día (`CartService::cutoffToday()`), envío gratis desde el mínimo configurado y el teléfono de un técnico.
- **Header orientado a la búsqueda**: buscador grande con resultados en vivo (`/api/search`), con foto, número de parte, precio y botón de agregar. También un menú de categorías con los conteos reales, cuenta, favoritos y carrito (abre el panel lateral existente).
- **Hero con consola de 3 caminos**: por vehículo (marca, año y modelo con la API del buscador, solo combinaciones reales), por número de parte (Spicer, Neapco, OE o UDS) y armado a medida (lleva al builder online).
- **Franja de confianza**: calificación de Google (desde Ajustes), piezas en stock, cardanes por vehículo, corte de las 2 pm ET y "desde 2018".
- **Comprar por componente**: 4 grupos con fotos reales y las categorías con sus conteos.
- **Más vendidos** con "Agregar" directo por SKU (`/quick-order/add`, el mismo endpoint del buscador actual).
- **Tres caminos al cardán correcto**: por vehículo, premade y builder.
- **Comprar por serie de cruceta** (1310 a 1550, 7290, 3R) con las medidas reales, enlazando a `/series/{serie}`.
- **Banda del builder** y **cuentas mayoristas** con los niveles reales de `B2bAccounts`: Bronze 5 %, Silver 8 % y Gold 10 %.
- **Botón flotante "Ask a tech"** (WhatsApp y teléfono), promesa de servicio, newsletter y footer.

Todo con `__()` para las traducciones existentes (en, es, fr, zh, ja). El SEO es el del layout actual: overrides de Admin → SEO, `noindex` fuera de producción y canonical sobre `APP_URL`.

## Rendimiento (Lighthouse 12, perfil móvil, vista previa)

| Rendimiento | Accesibilidad | Buenas prácticas | LCP | TBT | CLS |
|---|---|---|---|---|---|
| 95 | 100 | 100 | 2,9 s | 0 ms | 0 |

Una sola hoja de estilos de unos 50 KB (unos 10 KB comprimida), unos 16 KB de JavaScript sin dependencias, fotos en AVIF y WebP con tamaños para celular y escritorio, y fuentes propias con `font-display: swap`.

## Cómo instalarlo en la app Laravel

Ya está listo como PR en borrador en la app: [Federico-Schwindt/UniversalDriveshaftsLARAVEL#2](https://github.com/Federico-Schwindt/UniversalDriveshaftsLARAVEL/pull/2) (rama `redesign/home`). También se puede copiar a mano:

La carpeta `laravel/` tiene las mismas rutas que la app. Copiá su contenido sobre la raíz del proyecto:

```bash
cp -r laravel/* /ruta/a/UniversalDriveshaftsLARAVEL/
php artisan view:clear
```

Archivos nuevos o reemplazados:

- `resources/views/home.blade.php` (reemplaza al home actual, que sigue en el historial de git)
- `resources/views/layouts/store.blade.php` (layout nuevo, por ahora solo lo usa el home)
- `resources/views/partials/store/{header,footer,lang}.blade.php`
- `public/css/store.css`, `public/js/store.js`
- `public/fonts/store/` (Barlow Semi Condensed 600 y 700)
- `public/img/store/` (fotos optimizadas)

No toca rutas, controladores, servicios ni la base de datos. Reutiliza `partials/cart-drawer`, `partials/schema`, `partials/analytics`, `partials/assistant`, `public/js/cart-drawer.js` y el componente `<x-icon>`.

Mientras se migran las demás páginas, el home usa el layout nuevo y el resto sigue con `layouts/app`.

## Fotos

Solo fotos reales, sin imágenes generadas con IA (como pide la regla del dueño en `PtiDewatermark`):

- El camión del hero, el taller, el depósito, las piezas, los tubos y la soldadura son fotos que ya estaban en `public/img/photos` y `public/img/hero`.
- La Jeep Gladiator de la tarjeta "por vehículo" viene de la web.
- Las fotos de producto son las del catálogo, tal como las sirve la tienda, con la marca de agua de UDS que pidió el dueño.

## Regenerar la vista previa

Con la app corriendo en local (`php artisan serve`):

```bash
python3 scripts/export_preview.py --app http://127.0.0.1:8000 --laravel /ruta/a/UniversalDriveshaftsLARAVEL
```

Cada push a `main` publica la carpeta `preview/` en GitHub Pages (`.github/workflows/pages.yml`).
