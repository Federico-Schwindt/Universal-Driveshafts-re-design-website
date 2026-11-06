#!/usr/bin/env python3
"""Export a static preview of the redesigned home for GitHub Pages.

Renders the page from a running copy of the Laravel app (the real Blade views, real config), then:
  * copies the redesign's assets next to it and makes their URLs relative (so it works under any sub-path),
  * points every other link, form and /media image at the live store (dev.udshafts.com by default),
  * sets window.UDS_API so the vehicle finder and the search use the store's public JSON endpoints (CORS *),
  * sets window.UDS_PREVIEW so add-to-cart shows a notice instead of posting to a server that is not there.

Usage:  python3 scripts/export_preview.py [--app http://127.0.0.1:8000] [--laravel PATH] [--store https://dev.udshafts.com]
"""
import argparse, os, re, shutil, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('--app', default='http://127.0.0.1:8000')
ap.add_argument('--laravel', default='/home/user/universaldriveshaftslaravel')
ap.add_argument('--store', default='https://dev.udshafts.com')
ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), '..', 'preview'))
a = ap.parse_args()
out = os.path.abspath(a.out)
pub = os.path.join(a.laravel, 'public')

html = urllib.request.urlopen(a.app + '/').read().decode('utf-8')

# 1) absolute app URLs -> root-relative
for base in ('http://localhost:8000', 'http://127.0.0.1:8000', a.app):
    html = html.replace(base + '/', '/').replace(base + '"', '/"').replace(base + '?', '/?')

# 2) the redesign's own assets become relative files of the preview
LOCAL = ('/css/store.css', '/css/st-shell.css', '/js/store.js', '/js/cart-drawer.js', '/fonts/', '/img/store/', '/img/uds-logo.webp', '/favicon', '/apple-touch-icon.png', '/img/og-default.jpg')
def rel(m):
    attr, url = m.group(1), m.group(2)
    if url.startswith(LOCAL):
        return f'{attr}"./{url[1:]}"'
    return f'{attr}"{a.store}{url}"'
html = re.sub(r'((?:href|src|action|content|data-src)=)"(/(?!/)[^"]*)"', rel, html)
def rel_srcset(m):
    parts = []
    for item in m.group(2).split(','):
        item = item.strip()
        if not item:
            continue
        url, *rest = item.split(' ')
        if url.startswith('/'):
            url = ('./' + url[1:]) if url.startswith(LOCAL) else a.store + url
        parts.append(' '.join([url] + rest))
    return f'{m.group(1)}"{", ".join(parts)}"'
html = re.sub(r'((?:srcset|imagesrcset)=)"([^"]*)"', rel_srcset, html)

# 3) runtime switches for the preview
html = html.replace('<script src="./js/store.js', '<script>window.UDS_API=' + repr(a.store) + ';window.UDS_PREVIEW=true;</script>\n<script src="./js/store.js', 1)
note = ('<div class="st-preview" role="note">Redesign preview of the Universal Driveshafts home. Finder and search use the live catalog; '
        f'other links open the current store at {a.store.replace("https://", "")}.</div>')
html = html.replace('<a class="st-skip"', note + '\n<a class="st-skip"', 1)

# 4) copy assets
if os.path.isdir(out):
    shutil.rmtree(out)
os.makedirs(out)
def cp(rel_path):
    src = os.path.join(pub, rel_path)
    dst = os.path.join(out, rel_path)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    elif os.path.exists(src):
        shutil.copy2(src, dst)
for f in ('css/store.css', 'css/st-shell.css', 'js/store.js', 'js/cart-drawer.js', 'fonts/store', 'fonts/hankengrotesk-var.woff2', 'fonts/ibmplexmono-500.woff2',
          'fonts/ibmplexmono-600.woff2', 'img/store', 'img/uds-logo.webp', 'favicon.svg', 'favicon.ico', 'apple-touch-icon.png', 'img/og-default.jpg'):
    cp(f)
for extra in ('css/st-shell.css',):
    path = os.path.join(out, extra)
    open(path, 'w').write(open(path).read().replace("url('/fonts/", "url('../fonts/"))
css = os.path.join(out, 'css/store.css')
s = open(css).read().replace("url('/fonts/", "url('../fonts/")
s += '\n.st-preview { background: #fff4d6; color: #5a4300; text-align: center; font-size: .82rem; padding: 7px 16px; border-bottom: 1px solid #f1d58a; }\n'
open(css, 'w').write(s)
open(os.path.join(out, 'index.html'), 'w').write(html)
open(os.path.join(out, '.nojekyll'), 'w').write('')
print('exported', out, len(html), 'bytes')
