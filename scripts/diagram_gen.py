import os
from pathlib import Path
from graphviz import Digraph

DOC_MD = "docs/BLUEPRINT.md"
PNG_OUT = "docs/blueprint.png"

# 1. Scan folder & class
root = Path('.')
modules = {}
for folder, _, files in os.walk('colony'):
    for file in files:
        if file.endswith('.py'):
            mod = os.path.relpath(os.path.join(folder, file))
            modules.setdefault(folder, []).append(file)

def write_markdown():
    with open(DOC_MD, 'w') as f:
        f.write("# System Blueprint\n\n")
        for folder, files in modules.items():
            f.write(f"## {folder}\n")
            for file in files:
                f.write(f"- {file}\n")
    print(f"[DOC] Updated {DOC_MD}")

def write_png():
    dot = Digraph(comment='System Blueprint')
    for folder, files in modules.items():
        dot.node(folder, folder)
        for file in files:
            dot.node(file, file)
            dot.edge(folder, file)
    dot.render(PNG_OUT, view=False, format='png')
    print(f"[DOC] Generated {PNG_OUT}")

def main():
    write_markdown()
    try:
        write_png()
    except Exception as e:
        print(f"[WARN] PNG generation failed: {e}")

if __name__ == "__main__":
    main()