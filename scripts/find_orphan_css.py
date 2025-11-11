#!/usr/bin/env python3
"""
Find orphan CSS classes defined in styles.css that aren't used in the project HTML/JS/PY files.
Writes a report to orphan_css_report.txt in the repo root and prints results to stdout.
"""
import os
import re
import sys

root = os.getcwd()
css_path = os.path.join(root, 'styles.css')
if not os.path.exists(css_path):
    print('ERROR: styles.css not found at', css_path, file=sys.stderr)
    sys.exit(1)

with open(css_path, encoding='utf-8') as f:
    css = f.read()

# Find selector blocks (text before '{')
sel_blocks = re.findall(r'([^{]+){', css)
classes = set()
for blk in sel_blocks:
    parts = blk.split(',')
    for p in parts:
        p = p.strip()
        for m in re.finditer(r'\.([a-zA-Z0-9_-]+)', p):
            classes.add(m.group(1))

# Search files for usage
used = set()
for dirpath, dirnames, filenames in os.walk(root):
    # skip .git and node_modules
    if '.git' in dirpath.split(os.sep) or 'node_modules' in dirpath.split(os.sep):
        continue
    for fname in filenames:
        if not fname.lower().endswith(('.html', '.htm', '.js', '.py')):
            continue
        path = os.path.join(dirpath, fname)
        try:
            txt = open(path, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for cls in list(classes):
            # crude but practical checks
            # 1) class="... cls ..." or class='... cls ...'
            if re.search(r'class=[\"\'][^\"\']*\b' + re.escape(cls) + r'\b', txt):
                used.add(cls)
                continue
            # 2) className = '...cls...' or className="..."
            if re.search(r'className\s*=\s*[\"\'][^\"\']*\b' + re.escape(cls) + r'\b', txt):
                used.add(cls)
                continue
            # 3) JS usage: document.querySelector('.cls' or " .cls") or $('.cls')
            if re.search(r"[\.\'$]" + re.escape(cls) + r"\b", txt):
                # this matches more cases; we'll mark as used conservatively
                used.add(cls)
                continue

orphan = sorted(classes - used)
print('Classes defined in styles.css:', len(classes))
print('Detected orphan classes:', len(orphan))
if orphan:
    print('\nOrphan classes:')
    for c in orphan:
        print('-', c)

report_path = os.path.join(root, 'orphan_css_report.txt')
with open(report_path, 'w', encoding='utf-8') as outf:
    outf.write('Classes defined in styles.css: {}\n'.format(len(classes)))
    outf.write('Detected orphan classes: {}\n\n'.format(len(orphan)))
    for c in orphan:
        outf.write(c + '\n')

print('\nReport written to', report_path)
