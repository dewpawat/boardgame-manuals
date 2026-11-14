#!/usr/bin/env python3
"""ตรวจคู่มือบอร์ดเกมตามกฎใน README.md

ใช้:
  python tools/check_manual.py games/wingspan.html      ตรวจเล่มเดียว (ใช้กับเล่มใหม่)
  python tools/check_manual.py --all                    ตรวจทุกเล่ม + index.html

ERROR = ต้องแก้ก่อนเผยแพร่ · WARN = ไม่ตรงมาตรฐานเล่มต้นแบบ ควรแก้ · INFO = แจ้งให้ทราบ (ไม่นับ)
exit code = 1 ถ้ามี ERROR (หรือมี WARN เมื่อใช้ --strict)
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES_DIR = ROOT / "games"
INDEX = ROOT / "index.html"

REQUIRED_SECTIONS = ["summary", "box", "setup", "turn", "end", "faq", "glossary"]
SHELF_STYLE_BITS = ["#5f3c1f", "position:fixed", "z-index:50", "body{padding-bottom:72px}"]
ALLOWED_EXTERNAL_LOAD = ("https://fonts.googleapis.com", "https://fonts.gstatic.com")
FILE_RE = re.compile(r"^[0-9a-z]+(_[0-9a-z]+)*\.html$")


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []          # (href, attrs)
        self.loads = []          # (tag, url) ที่โหลดอัตโนมัติ
        self.sections = []       # id ของ <section> ตามลำดับ
        self.toc_links = []
        self.in_toc = False
        self.toc_depth = 0
        self.tags = {}
        self.classes = {}
        self.scripts = []
        self._in_script = False
        self._buf = []
        self.title = ""
        self._in_title = False
        self.h1_has_span = False
        self._in_h1 = False
        self.eyebrow = ""
        self._in_eyebrow = False
        self.footer_text = ""
        self._in_footer = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags[tag] = self.tags.get(tag, 0) + 1
        for c in (a.get("class") or "").split():
            self.classes[c] = self.classes.get(c, 0) + 1
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and a.get("href") is not None:
            self.hrefs.append((a["href"], a))
            if self.in_toc and a["href"].startswith("#"):
                self.toc_links.append(a["href"][1:])
        if tag in ("script", "img", "iframe", "embed", "object", "audio", "video", "source") and a.get("src"):
            self.loads.append((tag, a["src"]))
        if tag == "link" and a.get("href"):
            self.loads.append(("link", a["href"]))
        if tag == "section" and a.get("id"):
            self.sections.append(a["id"])
        if tag == "nav" and "toc" in (a.get("class") or "").split():
            self.in_toc = True
        if tag == "script":
            self._in_script = True
            self._buf = []
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self._in_h1 = True
        if tag == "span" and self._in_h1:
            self.h1_has_span = True
        if "eyebrow" in (a.get("class") or "").split():
            self._in_eyebrow = True
        if tag == "footer":
            self._in_footer = True

    def handle_endtag(self, tag):
        if tag == "nav":
            self.in_toc = False
        if tag == "script" and self._in_script:
            self.scripts.append("".join(self._buf))
            self._in_script = False
        if tag == "title":
            self._in_title = False
        if tag == "h1":
            self._in_h1 = False
        if tag == "div":
            self._in_eyebrow = False
        if tag == "footer":
            self._in_footer = False

    def handle_data(self, data):
        if self._in_script:
            self._buf.append(data)
        if self._in_title:
            self.title += data
        if self._in_eyebrow:
            self.eyebrow += data
        if self._in_footer:
            self.footer_text += data


def node_check(scripts, errs):
    node = shutil.which("node")
    if not node:
        return
    for i, js in enumerate(scripts):
        if not js.strip():
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(js)
            name = fh.name
        try:
            r = subprocess.run([node, "--check", name], capture_output=True, text=True, encoding="utf-8")
            if r.returncode != 0:
                msg = (r.stderr or "").strip().splitlines()
                errs.append(f"JavaScript ก้อนที่ {i + 1} มี syntax error: {' | '.join(msg[-3:])}")
        finally:
            Path(name).unlink(missing_ok=True)


def check_manual(path: Path):
    errs, warns, infos = [], [], []
    text = path.read_text(encoding="utf-8")
    p = Collector()
    p.feed(text)

    # ชื่อไฟล์
    if not FILE_RE.match(path.name):
        errs.append(f"ชื่อไฟล์ต้องเป็น snake_case ตัวเล็ก เช่น 7_wonders_architects.html (ตอนนี้: {path.name})")

    # placeholder ที่ยังไม่ได้แทน
    left = re.findall(r"\{\{[^}]*\}\}", text)
    if left:
        errs.append(f"ยังเหลือ placeholder {{{{...}}}} {len(left)} จุด เช่น {left[0]}")
    if "<!-- TODO" in text:
        errs.append("ยังเหลือคอมเมนต์ <!-- TODO ... --> ให้ทำตามแล้วลบออก")

    # title / h1 / eyebrow
    title = p.title.strip()
    if not title:
        errs.append("ไม่มี <title>")
    else:
        if not title.endswith("ฉบับไทย"):
            warns.append(f'<title> ควรเป็น "ชื่อเกมภาษาอังกฤษ ฉบับไทย" (ตอนนี้: {title})')
        if not re.match(r"^[0-9A-Za-z]", title):
            warns.append(f"<title> ควรขึ้นต้นด้วยชื่อเกมภาษาอังกฤษ (ตอนนี้: {title})")
    if p.tags.get("h1", 0) != 1:
        errs.append(f"ต้องมี <h1> 1 อัน (เจอ {p.tags.get('h1', 0)})")
    elif not p.h1_has_span:
        warns.append("h1 ควรมี <span> ชื่อไทย · คำอธิบายสั้น ๆ อยู่ข้างใน")
    if not p.eyebrow.strip().startswith("คู่มือภาษาไทย ·"):
        warns.append('eyebrow ควรขึ้นต้นด้วย "คู่มือภาษาไทย · ..."')
    elif "อิงคู่มือ" not in p.eyebrow:
        warns.append('eyebrow ควรลงท้ายด้วย "อิงคู่มือทางการ (สำนักพิมพ์)"')

    # ปุ่ม shelf-home
    shelf = [a for h, a in p.hrefs if "shelf-home" in (a.get("class") or "").split()]
    if len(shelf) != 1:
        errs.append(f"ต้องมีปุ่ม a.shelf-home 1 ปุ่ม (เจอ {len(shelf)})")
    elif shelf[0].get("href") != "../index.html":
        errs.append(f'a.shelf-home ต้องลิงก์ไป "../index.html" (ตอนนี้: {shelf[0].get("href")})')
    for bit in SHELF_STYLE_BITS:
        if bit not in text:
            errs.append(f"CSS ของ .shelf-home ไม่ครบ ขาด {bit} (คัดลอก snippet จาก template)")

    # กฎ CSS
    if re.search(r"\.steps\s+li\b", text):
        errs.append('CSS ใช้ ".steps li" ต้องเป็น ".steps>li"')
    if "prefers-color-scheme: dark" not in text and "prefers-color-scheme:dark" not in text:
        warns.append("ไม่มีสีโหมดมืด (@media prefers-color-scheme: dark)")
    if ':root[data-theme="dark"]' not in text:
        warns.append(':root[data-theme="dark"] ไม่มี (ใช้ชุดสีเดียวกับโหมดมืด)')

    # ห้ามโหลด/ส่งข้อมูลภายนอก
    if "claude.ai" in text:
        errs.append("มีลิงก์ claude.ai เหลืออยู่ ให้ใช้ path แบบ relative")
    for tag, url in p.loads:
        if url.startswith(("http://", "https://", "//")) and not url.startswith(ALLOWED_EXTERNAL_LOAD):
            errs.append(f"โหลดไฟล์ภายนอกไม่ได้ ({tag}: {url}) ใช้ได้แค่ Google Fonts")
    for tag in ("iframe", "form", "embed", "object"):
        if p.tags.get(tag):
            errs.append(f"ห้ามใช้ <{tag}>")
    for pat, name in [(r"\bfetch\s*\(", "fetch()"), (r"XMLHttpRequest", "XMLHttpRequest"),
                      (r"sendBeacon", "sendBeacon"), (r"new\s+WebSocket", "WebSocket"),
                      (r"\beval\s*\(", "eval()"), (r"document\.write", "document.write")]:
        if any(re.search(pat, s) for s in p.scripts):
            errs.append(f"สคริปต์ใช้ {name} ไม่ได้")
    for s in p.scripts:
        if "localStorage" in s and "try" not in s:
            errs.append("ใช้ localStorage ต้องครอบด้วย try/catch")

    # id ซ้ำ + ลิงก์ภายในหน้า
    seen, dup = set(), set()
    for i in p.ids:
        (dup if i in seen else seen).add(i)
    if dup:
        errs.append(f"id ซ้ำกัน: {', '.join(sorted(dup))}")
    for h, _ in p.hrefs:
        if h.startswith("#") and len(h) > 1 and h[1:] not in seen:
            errs.append(f"ลิงก์ {h} ไม่มี id ปลายทาง")

    # โครงหัวข้อ
    missing = [s for s in REQUIRED_SECTIONS if s not in p.sections]
    if missing:
        warns.append(f"ไม่มีหัวข้อมาตรฐาน: {', '.join(missing)} (โครงเล่มต้นแบบ)")
    order = [s for s in p.sections if s in REQUIRED_SECTIONS]
    if order != [s for s in REQUIRED_SECTIONS if s in order]:
        warns.append(f"ลำดับหัวข้อไม่ตรงเล่มต้นแบบ: {' → '.join(order)}")
    if not p.classes.get("toc"):
        errs.append("ไม่มีสารบัญด้านข้าง (nav.toc)")
    else:
        not_in_toc = [s for s in p.sections if s not in p.toc_links]
        if not_in_toc:
            warns.append(f"หัวข้อที่ไม่อยู่ในสารบัญ: {', '.join(not_in_toc)}")
    if not p.classes.get("formula"):
        warns.append("ไม่มีแถบสูตรแต้ม (.formula) ในสรุป 1 นาที")
    if p.classes.get("en", 0) < 10:
        warns.append(f'ชื่ออังกฤษตามคู่มือทางการ (<span class="en">) น้อยไป: {p.classes.get("en", 0)} จุด (เล่มต้นแบบมี ~28)')
    if p.classes.get("figure", 0) < 3 and p.tags.get("svg", 0) < 5:
        warns.append("ภาพประกอบ SVG น้อยไป (ควรมีภาพในกติกาสำคัญทุกเรื่อง)")
    if p.tags.get("details", 0) < 6:
        warns.append(f"ข้อที่ชอบเถียงกันมี {p.tags.get('details', 0)} ข้อ (ควรอย่างน้อย 6)")
    if "steps" not in p.classes:
        warns.append("ไม่มีขั้นตอนแบบ .steps (เตรียมเกม / ในตาของคุณ)")

    # footer แหล่งที่มา
    if not p.tags.get("footer"):
        errs.append("ไม่มี footer แหล่งที่มา")
    else:
        if "คู่มือในกล่อง" not in text:
            warns.append('ไม่มีประโยค "ถ้ากล่องพิมพ์ต่างจากคู่มือนี้ ให้ยึดคู่มือในกล่อง"')
        foot = text[text.rfind("<footer"):]
        if len(re.findall(r'href="https?://', foot)) < 1 and "แหล่ง" not in p.footer_text:
            warns.append("footer ไม่มีลิงก์แหล่งที่มา")

    if "unverified" in p.classes or "ยังไม่ยืนยัน" in text:
        infos.append("มีข้อมูลที่ติดป้ายยังไม่ยืนยัน (ต้องบอกผู้ใช้ และตรวจเพิ่มถ้าทำได้)")

    node_check(p.scripts, errs)
    return errs, warns, infos


def parse_games():
    """ดึง GAMES/CATS/ART ออกจาก index.html แบบหยาบ ๆ"""
    text = INDEX.read_text(encoding="utf-8")
    games = re.findall(r'\{id:"([^"]+)",name:"([^"]+)".*?url:"([^"]+)",cat:"([^"]+)"(.*?)art:"([^"]+)"\}', text, re.S)
    cats = re.findall(r'\{id:"([^"]+)",name:"[^"]+",en:"[^"]+"\}', text)
    art_block = text[text.find("var ART={"):text.find("};", text.find("var ART={"))]
    arts = re.findall(r"^\s*([a-z0-9_]+):'<svg", art_block, re.M)
    return text, games, cats, arts


def check_index():
    errs, warns = [], []
    text, games, cats, arts = parse_games()
    files = {f.name for f in GAMES_DIR.glob("*.html")}
    linked = set()
    ids = set()
    for gid, name, url, cat, body, art in games:
        if gid in ids:
            errs.append(f"GAMES id ซ้ำ: {gid}")
        ids.add(gid)
        if not url.startswith("games/"):
            errs.append(f"{name}: url ต้องเป็น games/<ไฟล์>.html (ตอนนี้: {url})")
        else:
            fn = url[len("games/"):]
            linked.add(fn)
            if fn not in files:
                errs.append(f"{name}: ไม่มีไฟล์ {url}")
        if cat not in cats:
            errs.append(f"{name}: หมวด {cat} ไม่มีใน CATS")
        if art not in arts:
            errs.append(f"{name}: ภาพ {art} ไม่มีใน ART")
        for field in ("min:", "max:", "t:", "tmax:", "parts:", "exp:", "rules:", "score:", "extra:", "tools:", "c:", "c2:", "hl:"):
            if field not in body:
                errs.append(f"{name}: GAMES ขาดฟิลด์ {field[:-1]}")
        m = re.search(r'added:"([^"]*)"', body)
        if m and not re.match(r"^\d{4}-\d{2}-\d{2}$", m.group(1)):
            errs.append(f"{name}: added ต้องเป็น YYYY-MM-DD")
    for fn in sorted(files - linked):
        errs.append(f"games/{fn} ยังไม่มีในชั้น (GAMES)")
    if "claude.ai/artifact" in text:
        errs.append("index.html ยังมีลิงก์ claude.ai/artifact")
    return errs, warns, len(games)


def report(label, errs, warns, infos=()):
    status = "OK" if not errs and not warns else ("ERROR" if errs else "WARN")
    print(f"[{status}] {label}")
    for e in errs:
        print(f"   ERROR  {e}")
    for w in warns:
        print(f"   WARN   {w}")
    for i in infos:
        print(f"   INFO   {i}")


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    strict = "--strict" in argv
    args = [a for a in argv if not a.startswith("--")]
    targets = [Path(a) for a in args] if args else []
    if "--all" in argv or not targets:
        targets = sorted(GAMES_DIR.glob("*.html"))
    total_e = total_w = 0
    for t in targets:
        e, w, i = check_manual(t.resolve())
        report(t.name, e, w, i)
        total_e += len(e)
        total_w += len(w)
    e, w, n = check_index()
    report(f"index.html (ชั้น {n} เล่ม)", e, w)
    total_e += len(e)
    total_w += len(w)
    print(f"\nสรุป: ERROR {total_e} · WARN {total_w}")
    return 1 if total_e or (strict and total_w) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
