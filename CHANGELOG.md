# Changelog

บันทึกการเพิ่มเกมและการแก้ไขชั้นคู่มือ เรียงใหม่ไปเก่า
รูปแบบ: `เพิ่ม` = เกมใหม่ขึ้นชั้น · `แก้` = แก้เนื้อหาคู่มือ · `ชั้น` = แก้หน้าชั้น/โครงเว็บ

## 2026-11-14 — เครื่องมือทำเล่มใหม่

- ชั้น: เพิ่ม `templates/manual.html` template คู่มือเล่มใหม่ โครงเดียวกับเล่มต้นแบบ Carcassonne (มีสมุดคะแนนที่ใช้ได้ทันที)
- ชั้น: เพิ่ม `templates/NEW_GAME_REQUEST.md` แบบฟอร์มสั่งทำเล่มใหม่
- ชั้น: เพิ่ม `tools/check_manual.py` สคริปต์ตรวจคู่มือตามกฎใน README (เล่มเก่า: ERROR 0 · WARN 71)
- ชั้น: เพิ่ม skill `/new-manual` ใน `.claude/skills/` ขั้นตอนทำเล่มใหม่ครบวงจร

## 2026-11-14 — ย้ายขึ้น GitHub

- ชั้น: ย้ายคู่มือทั้ง 25 เล่มจาก Artifact แยกลิงก์ มาไว้ใน repo นี้ (1 เกม 1 ไฟล์ใน `games/`)
- ชั้น: ตั้งชื่อไฟล์แบบ snake_case ตามชื่อเกมภาษาอังกฤษ
- ชั้น: เปลี่ยนลิงก์ในชั้นและปุ่ม "ชั้นคู่มือ" ของทุกเล่มเป็น path แบบ relative
- ชั้น: ย้ายกฎของชั้นคู่มือจากคอมเมนต์ใน `index.html` มาไว้ที่ `README.md`
- ลิงก์ Artifact เดิมของแต่ละเล่มยังเปิดได้ แต่จะไม่อัปเดตอีก ให้ใช้ลิงก์ชั้นคู่มือแทน

## 2026-11-14 — เกมที่ขึ้นชั้น

- เพิ่ม: Cascadia + Landmarks — การ์ดสัตว์ A–G, แลนด์มาร์ก A–L, กติกาเล่นเร็ว 5–6 คน
- เพิ่ม: Table Cooking (ฉบับแรก) — ตลาดเม็ดขาว เทียบกับฉบับ 2
- เพิ่ม: The Resistance: Avalon + Avalon X — แลนซ์ล็อต เอ็กซ์คาลิเบอร์ การ์ดพล็อต
- เพิ่ม: 7 Wonders Architects — พลังมหาสิ่งทั้ง 7
- เพิ่ม: Tacta — 5 แบบเล่น
- เพิ่ม: Bears vs Babies — ภาคหลัก
- เพิ่ม: Hues and Cues (สีสันบันเทิง) — กฎคำใบ้ภาษาไทย
- เพิ่ม: Coyote — โหมดร่วมมือ ขั้นเซียน
- เพิ่ม: Cat in the Box (Hobby Japan) — กติกา 2 คนและ 5 คน
- เพิ่ม: 6 nimmt! — 8 แบบเล่น ส่วนเสริมฉบับ 30 ปี
- เพิ่ม: Stool Pigeon (มาเฟียนกพิราบ) — แต้มตามคู่มือ PDF ทางการ

## ก่อนเริ่มบันทึกวันที่

เกมเหล่านี้ขึ้นชั้นก่อนจะมีฟิลด์ `added` จึงไม่มีวันที่แน่นอน

- เพิ่ม: Carcassonne Big Box — เกมหลัก + 11 ภาค (เล่มต้นแบบ)
- เพิ่ม: Forest Shuffle — เกมหลัก + 3 ภาค
- เพิ่ม: Happy Little Dinosaurs — ภาค 5–6 คน
- เพิ่ม: Twisted Cryptids — Ness is More
- เพิ่ม: Canvas — Reflections, Finishing Touches, KS Mini
- เพิ่ม: Sagrada — 5–6 Player, Passion
- เพิ่ม: Cryptid — โหมดปกติ + ขั้นสูง
- เพิ่ม: Exploding Kittens — 3 ภาค + Zombie Kittens
- เพิ่ม: Tower Up — เกมหลัก
- เพิ่ม: Azul: Master Chocolatier — 2 ตัวแปรในกล่อง
- เพิ่ม: Terraforming Mars — Prelude, Colonies
- เพิ่ม: Splendor — Cities of Splendor 4 โมดูล
- เพิ่ม: Monopoly — C1009 ฉบับอังกฤษ เทียบเกมเศรษฐีไทย
- เพิ่ม: Ticket to Ride: Europe — ฉบับครบรอบ 15 ปี 4 แบบการเล่น
