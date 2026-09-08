from pathlib import Path
import json
import re
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[2]
source = root / 'tmp/research-4d-20260908/report-source.md'
text = source.read_text(encoding='utf-8')
lines = text.splitlines()
errors = []
headings = [(i + 1, line) for i, line in enumerate(lines) if line.startswith('#')]
if sum(line.startswith('# ') for line in lines) != 1:
    errors.append('Expected one H1')
sections = re.findall(r'^## (\d+)\.', text, re.M)
if sections != [str(i) for i in range(1, 13)]:
    errors.append(f'Unexpected sections: {sections}')
for i, line in enumerate(lines):
    if line.startswith('#') and i + 1 < len(lines) and lines[i + 1].strip():
        errors.append(f'Heading lacks following blank line at {i+1}')
table_sizes = []
i = 0
while i < len(lines):
    if lines[i].startswith('|'):
        start = i
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            rows.append(lines[i])
            i += 1
        sizes = [len(row.split('|')) - 2 for row in rows]
        if len(set(sizes)) != 1:
            errors.append(f'Inconsistent table columns at line {start+1}: {sizes}')
        table_sizes.append({'line': start+1, 'rows': len(rows), 'columns': sizes[0]})
    else:
        i += 1
links = re.findall(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', text)
for label, url in links:
    parsed = urlparse(url)
    if not label.strip() or parsed.scheme not in ('http', 'https') or not parsed.netloc:
        errors.append(f'Invalid Markdown URL: {label}: {url}')
for bad in ['delta-flow.github.io', 'https://d4rt.github.io/', '\ufffd', '\ue200', 'turn68view', 'TODO:']:
    if bad in text:
        errors.append(f'Unexpected stale/internal marker: {bad}')
if not ('没有实际运行模型' in text and '未执行浏览器排版检查' in text):
    errors.append('Missing verification limitations')
ledger = json.loads((source.parent / 'claim-source-ledger.json').read_text(encoding='utf-8'))
required = ['title', 'author_or_publisher', 'publication_or_update', 'url', 'supported_claims', 'confidence_and_access']
for row in ledger['records']:
    if any(not row.get(k) for k in required):
        errors.append(f'Missing provenance for {row.get("id")}')
result = {'characters': len(text), 'lines': len(lines), 'headings': len(headings), 'tables': table_sizes,
          'links': len(links), 'unique_urls': len({u for _, u in links}), 'ledger_records': len(ledger['records']),
          'structural_errors': errors, 'visual_qa': 'Not performed; Markdown deliverable, disclosed in report',
          'link_qa': 'Syntax and corrected known URLs; critical sources checked through research, no universal live-link test'}
(source.parent / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
target = root / 'docs/papers/streaming_4d_tracking_research_2026.md'
if target.exists():
    raise RuntimeError(f'Refusing to overwrite an existing public note: {target}')
target.write_text(text, encoding='utf-8')
assert target.read_text(encoding='utf-8') == text
print(f'Published Markdown note: {target} ({target.stat().st_size} bytes)')
