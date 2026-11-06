"""Điền link commit vào docs/bug-log.md: thay {{COMMIT:BUG-xx}} bằng link tới commit có message chứa "(BUG-xx)".
Chạy SAU khi đã commit và push các bản sửa:  python -m scripts.fill_bug_links"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment"
SPECIAL = {"BUG-07": "khoa phien ban requirements"}       # commit sửa C6 làm trước khi có quy ước (BUG-xx)


def main():
    log = subprocess.run(["git", "log", "--all", "--format=%H%x09%s"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8").stdout.splitlines()
    path = ROOT / "docs" / "bug-log.md"
    text = path.read_text(encoding="utf-8")
    for bug in sorted(set(re.findall(r"\{\{COMMIT:(BUG-\d+)\}\}", text))):
        key = SPECIAL.get(bug, f"({bug})")
        hits = [line.split("\t", 1)[0] for line in log if key in line.split("\t", 1)[-1]]
        if not hits:
            print(f"  ✗ {bug}: chưa thấy commit có message chứa '{key}' – commit bản sửa trước rồi chạy lại")
            continue
        sha = hits[0]
        text = text.replace(f"{{{{COMMIT:{bug}}}}}", f"[{sha[:7]}]({REPO}/commit/{sha})")
        print(f"  ✓ {bug}: {REPO}/commit/{sha}")
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
