import os
import glob
import datetime

INDEX_FILE = os.path.join('docs', 'index.md')
INDEX_HEADER = \
"""
# Knocking's personal notebook

Notebook: https://cydknocking.github.io/notes/

This is Knockning's personal notebook.

这里是Knocking的个人笔记本.

Please "Ctrl+F5" to update newest notes.
"""

_exclude_list = [INDEX_FILE,]

files = glob.glob('docs/**/*.md', recursive=True)
files = [f for f in files if f not in _exclude_list]
files = sorted(files, key=lambda t: -os.stat(t).st_mtime) # descending modification time

# write recent updated files to index.md
files = files[:5]
with open(INDEX_FILE, 'w') as handle:
    handle.write(INDEX_HEADER)
    for file in files:
        name = os.path.basename(file)
        modified = os.path.getmtime(file)
        
        handle.write(f'- [{name}]({os.path.relpath(file, "docs").replace(".md", "/")}) <div style="text-align: right">{datetime.datetime.fromtimestamp(modified)}</div>\n')