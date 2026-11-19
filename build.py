# ტესტების ბიბლიოთეკის ბილდი (მხოლოდ სტანდარტული ბიბლიოთეკა).
#   python3 build.py   → index.html + <კურსი>/<ტესტი>/index.html რეპოს root-ში (GitHub Pages ამას აჩვენებს)
#
# courses/<კურსი>/course.json          {"title", "order"} — ერთი კურსი = ერთი ჩანართი მთავარ გვერდზე
# courses/<კურსი>/<NN-slug>/test.html   თავად ტესტი (ერთი თვითკმარი HTML)
# courses/<კურსი>/<NN-slug>/test.json   {"title", "badge"?, "topics": [...], "duration", "questions", "points"}
import json, pathlib, shutil

ROOT = pathlib.Path(__file__).parent
COURSES = ROOT / 'courses'
GENERATED = ROOT / '.generated'   # folders build.py created — only these are ever deleted

# clean previous output
if GENERATED.exists():
    for name in GENERATED.read_text().split():
        d = ROOT / name
        if d.is_dir() and d.name not in ('courses', 'engine', '.git'):
            shutil.rmtree(d)

catalog, created = [], []
for cdir in sorted(p for p in COURSES.iterdir() if (p / 'course.json').exists()):
    meta = json.loads((cdir / 'course.json').read_text())
    tests = []
    for tdir in sorted(p for p in cdir.iterdir() if (p / 'test.html').exists()):
        t = json.loads((tdir / 'test.json').read_text())
        out = ROOT / cdir.name / tdir.name
        out.mkdir(parents=True, exist_ok=True)
        shutil.copy(tdir / 'test.html', out / 'index.html')
        tests.append({'slug': tdir.name, 'num': tdir.name.split('-')[0], **t})
    catalog.append({'slug': cdir.name, 'title': meta['title'], 'order': meta.get('order', 99), 'tests': tests})
    if tests:
        created.append(cdir.name)

catalog.sort(key=lambda c: c['order'])
page = (ROOT / 'engine' / 'index.html').read_text().replace('/*CATALOG*/[]', json.dumps(catalog, ensure_ascii=False))
(ROOT / 'index.html').write_text(page)
GENERATED.write_text('\n'.join(created) + '\n')

n = sum(len(c['tests']) for c in catalog)
print(f'✓ {n} ტესტი, {len(catalog)} კურსი → index.html')
