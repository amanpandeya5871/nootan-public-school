import json
import pathlib
import re
import urllib.request

url = "https://forms.gle/nYG52cyhT2Jbdchs8"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    html = resp.read().decode("utf-8", "replace")
    final = resp.geturl()

root = pathlib.Path(__file__).resolve().parent
m = re.search(r"FB_PUBLIC_LOAD_DATA_\s*=\s*(.*?);\s*</script>", html, re.S)
mid = re.search(r"/forms/d/e/(1FAIpQLS[^/\"']+)", html)
formid = mid.group(1) if mid else ""
out = {"final_url": final, "formid": formid, "questions": []}
if m:
    data = json.loads(m.group(1))
    for q in data[1][1]:
        title = q[1]
        qtype = q[3]
        entries = []
        opts = []
        extra = []
        try:
            for block in q[4]:
                if isinstance(block, list) and block and isinstance(block[0], int):
                    entries.append(block[0])
                    extra.append(block)
                if isinstance(block, list) and len(block) > 1 and isinstance(block[1], list):
                    for opt in block[1]:
                        if isinstance(opt, list) and opt:
                            opts.append(str(opt[0]))
        except Exception:
            pass
        out["questions"].append(
            {"type": qtype, "entry": entries, "title": title, "options": opts, "raw4": extra}
        )
(root / "_hire_fields.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", len(out["questions"]), "formid", formid)
