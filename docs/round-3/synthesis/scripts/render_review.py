"""Render the report and make numbered contact sheets for human visual review.

Images are deliberately intermediate; validation.json records the reviewed PDF
hash. This script does not itself certify layout quality.
"""
from pathlib import Path
import re
import subprocess
from PIL import Image, ImageOps, ImageDraw
from pypdf import PdfReader

HERE = Path(__file__).resolve().parents[1]
QA = HERE / '.qa'
QA.mkdir(exist_ok=True)
subprocess.run(['pdftoppm', '-r', '85', '-png', str(HERE / 'unified-report.pdf'),
                str(QA / 'round3-page')], check=True, capture_output=True)
page_count = len(PdfReader(HERE / 'unified-report.pdf').pages)
pages = sorted((p for p in QA.iterdir() if re.fullmatch(r'round3-page-\d+\.png', p.name)
                and 1 <= int(p.stem.rsplit('-', 1)[1]) <= page_count),
               key=lambda p: int(p.stem.rsplit('-', 1)[1]))
if len(pages) != page_count:
    raise RuntimeError('Rendered page inventory differs from current PDF')
for offset in range(0, len(pages), 6):
    sheet = Image.new('RGB', (920, 1830), '#d8dde1')
    draw = ImageDraw.Draw(sheet)
    for slot, path in enumerate(pages[offset:offset + 6]):
        page = Image.open(path).convert('RGB')
        page.thumbnail((440, 570))
        x, y = 10 + (slot % 2) * 460, 30 + (slot // 2) * 605
        sheet.paste(page, (x, y))
        draw.text((x, y - 20), f'PDF page {offset + slot + 1}', fill='black')
    sheet.save(QA / f'contact-{offset // 6 + 1:02d}.png')
print(f'Rendered {len(pages)} pages and {(len(pages) + 5) // 6} contact sheets.')
