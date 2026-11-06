"""Chạy test case của Test Report BT3 và in đủ TÁM CỘT (để chụp ảnh / chạy lại tại chỗ khi giảng viên chọn).

  python -m scripts.run_tc TC-05          chạy một test case
  python -m scripts.run_tc --all          chạy cả 12 test case, in bảng tóm tắt
  python -m scripts.run_tc --report       sinh lại docs/test-report.md từ lịch sử chạy THẬT (docs/test-runs.jsonl)

Mỗi lần chạy được ghi thêm một dòng vào docs/test-runs.jsonl (thời điểm, máy, kết quả thực tế, PASS/FAIL),
nên Test Report luôn phản ánh kết quả chạy thật, kể cả lần FAIL trước khi sửa bug.
"""
import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.tc_bt3 import BY_ID, CASES, execute  # noqa: E402

RUNS = ROOT / "docs" / "test-runs.jsonl"
GREEN, RED, BOLD, END = "\033[92m", "\033[91m", "\033[1m", "\033[0m"
if os.name == "nt":
    os.system("")                                   # bật màu ANSI trong cmd Windows


def run_one(case, quiet=False):
    actual, ok = execute(case)
    stamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    RUNS.parent.mkdir(exist_ok=True)
    with RUNS.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"id": case.id, "at": stamp, "host": platform.node(), "actual": actual,
                            "result": "PASS" if ok else "FAIL"}, ensure_ascii=False) + "\n")
    if not quiet:
        verdict = f"{GREEN}{BOLD}PASS{END}" if ok else f"{RED}{BOLD}FAIL{END}"
        print(f"\n{BOLD}$ python -m scripts.run_tc {case.id}{END}      ({stamp} · máy {platform.node()})")
        print("=" * 100)
        print(f"1. Mã               : {case.id} – {case.ten}  [{case.loai}]")
        print(f"2. Tiền điều kiện   : {case.tien_dk}")
        print("3. Các bước         : " + "\n                     ".join(f"{i}. {b}" for i, b in enumerate(case.cac_buoc, 1)))
        print(f"4. Dữ liệu thử      : {case.du_lieu}")
        print(f"5. Kết quả mong đợi : {case.mong_doi}")
        print(f"6. Mức ưu tiên      : {case.uu_tien}")
        print(f"7. Kết quả thực tế  : {actual}")
        print(f"8. PASS / FAIL      : {verdict}")
        print("=" * 100)
    return ok, actual


def history():
    if not RUNS.exists():
        return {}
    h = {}
    for line in RUNS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            h.setdefault(r["id"], []).append(r)
    return h


def write_report():
    h = history()
    lines = ["# Test Report – Luồng L4 (track SE)", "",
             "Sinh tự động bởi `python -m scripts.run_tc --report` từ lịch sử chạy THẬT `docs/test-runs.jsonl`.",
             "Chạy lại một test case: `python -m scripts.run_tc TC-xx` (resetDb trước mỗi test case, database riêng `smartcrm_test`).", "",
             "| 1. Mã | 2. Tiền điều kiện | 3. Các bước | 4. Dữ liệu thử | 5. Kết quả mong đợi | 6. Ưu tiên | 7. Kết quả thực tế | 8. PASS/FAIL |",
             "|---|---|---|---|---|---|---|---|"]
    for c in CASES:
        runs = h.get(c.id, [])
        if not runs:
            actual, verdict = "(chưa chạy)", "–"
        else:
            last = runs[-1]
            fails = [r for r in runs if r["result"] == "FAIL"]
            actual = f'{last["actual"]} ({last["at"]})'
            verdict = f'**{last["result"]}**'
            if fails and last["result"] == "PASS":
                actual = f'Lần đầu ({fails[0]["at"]}): {fails[0]["actual"]} → FAIL, xem Bug Log. Sau khi sửa: {actual}'
                verdict = "FAIL → **PASS**"
        steps = "<br>".join(f"{i}. {b}" for i, b in enumerate(c.cac_buoc, 1))
        lines.append(f"| **{c.id}**<br>{c.loai}<br>{c.ten} | {c.tien_dk} | {steps} | {c.du_lieu} | {c.mong_doi} | {c.uu_tien} | "
                     f"{actual}<br>Ảnh: `docs/screenshots/{c.id}.png` | {verdict} |")
    last = [h[c.id][-1]["result"] for c in CASES if c.id in h]
    lines += ["", f"**Tổng hợp lần chạy gần nhất:** {last.count('PASS')} PASS · {last.count('FAIL')} FAIL / {len(CASES)} test case.",
              "", "Đủ năm loại: luồng đúng ×4 (TC-01 – TC-04) · giá trị biên ×2 hai bên ranh giới 15 phút (TC-05, TC-06) · "
              "dữ liệu sai ×3 (TC-07 – TC-09) · bảo mật ×2 (TC-10, TC-11) · tái lập ×1 (TC-12)."]
    out = ROOT / "docs" / "test-report.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Đã ghi {out.relative_to(ROOT)}")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    if argv[0] == "--report":
        write_report(); return 0
    if argv[0] == "--all":
        res = [(c, *run_one(c, quiet=True)) for c in CASES]
        print(f"\n{BOLD}$ python -m scripts.run_tc --all{END}      ({datetime.now():%d/%m/%Y %H:%M:%S})")
        for c, ok, actual in res:
            print(f"  {c.id}  {(GREEN + 'PASS' if ok else RED + 'FAIL') + END}  {c.loai:<14} {actual[:80]}")
        n = sum(ok for _, ok, _ in res)
        print(f"{BOLD}{n}/{len(res)} PASS{END}")
        return 0 if n == len(res) else 1
    case = BY_ID.get(argv[0].upper())
    if case is None:
        print(f"Không có test case {argv[0]}. Có: {', '.join(BY_ID)}"); return 2
    ok, _ = run_one(case)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
