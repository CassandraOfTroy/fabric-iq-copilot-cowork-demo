"""Convert markdown files to Word (.docx) with proper table formatting AND live hyperlinks.

Usage:
    python scripts/md_to_docx.py <input.md> [output.docx]   # single file
    python scripts/md_to_docx.py                            # batch: outputs/recommendations -> .../docx

Inline formatting supported:
  - [text](url)        → real, clickable Word hyperlink (blue, underlined)
  - **bold**           → bold run
  - `code`             → monospace run
Hyperlinks render correctly inside paragraphs, bullets, numbered lists,
blockquotes, and table cells.
"""
import re
import sys
import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.opc.constants import RELATIONSHIP_TYPE as RT


# ---------- inline rendering helpers ----------

# Matches [text](url), **bold**, `code` and *italic* in a single pass. Order matters:
# we try links first (so `**foo**` inside link text is preserved as text), then bold, code and italic.
_INLINE_RE = re.compile(
    r'(\[(?P<ltext>[^\]]+)\]\((?P<url>[^)]+)\))'      # [text](url)
    r'|(\*\*(?P<bold>[^*]+)\*\*)'                       # **bold**
    r'|(`(?P<code>[^`]+)`)'                             # `code`
    r'|((?<![\w*])\*(?![\s*])(?P<ital>[^*]+?)(?<![\s*])\*(?![\w*]))'  # *italic* (may contain links/bold-free text)
)

# Directory of the markdown file being converted: relative links to other .md files are pointed at their
# sibling .docx when it exists, so the Word documents link to each other instead of to markdown.
_CURRENT_MD_DIR = None


def _resolve_url(url):
    if _CURRENT_MD_DIR is None or re.match(r'^[a-z][a-z0-9+.-]*:', url, re.I) or url.startswith('#'):
        return url
    path, _, anchor = url.partition('#')
    if path.lower().endswith('.md'):
        docx_rel = path[:-3] + '.docx'
        if os.path.exists(os.path.join(_CURRENT_MD_DIR, docx_rel)):
            return docx_rel
    return url


def _add_hyperlink(paragraph, url, text):
    """Insert a real Word hyperlink (blue + underlined) into the paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    # Blue color
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0563C1')
    rPr.append(color)

    # Underline
    underline = OxmlElement('w:u')
    underline.set(qn('w:val'), 'single')
    rPr.append(underline)

    # Font size
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), '20')  # 10pt = 20 half-points
    rPr.append(sz)

    new_run.append(rPr)

    t = OxmlElement('w:t')
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    new_run.append(t)

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink


def _add_inline(paragraph, text, base_size=Pt(10), base_bold=False, base_italic=False):
    """Render markdown inline formatting (links / bold / code / italic) into a paragraph."""
    if text is None:
        return
    pos = 0
    for m in _INLINE_RE.finditer(text):
        # plain text before the match
        if m.start() > pos:
            run = paragraph.add_run(text[pos:m.start()])
            run.font.size = base_size
            run.bold = base_bold or None
            run.italic = base_italic or None

        if m.group('url'):
            _add_hyperlink(paragraph, _resolve_url(m.group('url').strip()), m.group('ltext'))
        elif m.group('bold') is not None:
            _add_inline(paragraph, m.group('bold'), base_size, True, base_italic)
        elif m.group('code') is not None:
            run = paragraph.add_run(m.group('code'))
            run.font.name = 'Consolas'
            run.font.size = Pt(max(8, base_size.pt - 1))
        elif m.group('ital') is not None:
            _add_inline(paragraph, m.group('ital'), base_size, base_bold, True)
        pos = m.end()

    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        run.font.size = base_size
        run.bold = base_bold or None
        run.italic = base_italic or None


def parse_md_to_docx(md_path, docx_path):
    global _CURRENT_MD_DIR
    _CURRENT_MD_DIR = os.path.dirname(os.path.abspath(md_path))
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(10)

    # Adjust margins for wider tables
    for section in doc.sections:
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Standalone image: ![alt](path)
        img_match = re.fullmatch(r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)', line.strip())
        if img_match:
            src = img_match.group('src')
            img_path = src if os.path.isabs(src) else os.path.join(os.path.dirname(os.path.abspath(md_path)), src)
            if os.path.exists(img_path):
                doc.add_picture(img_path, width=Inches(6.6))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                print(f"  WARNING: image not found, skipped: {img_path}")
            i += 1
            continue

        # Headings
        if line.startswith('# '):
            p = doc.add_heading(line[2:].strip(), level=1)
            i += 1
            continue
        if line.startswith('## '):
            doc.add_heading(line[3:].strip(), level=2)
            i += 1
            continue
        if line.startswith('### '):
            doc.add_heading(line[4:].strip(), level=3)
            i += 1
            continue
        if line.startswith('#### '):
            doc.add_heading(line[5:].strip(), level=4)
            i += 1
            continue

        # Horizontal rule
        if line.strip() in ('---', '***', '___'):
            p = doc.add_paragraph()
            p.add_run('─' * 80).font.color.rgb = RGBColor(180, 180, 180)
            i += 1
            continue

        # Table detection
        if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
            table_lines = []
            while i < len(lines) and '|' in lines[i].strip():
                stripped = lines[i].strip()
                if stripped and not all(c in '-| :' for c in stripped):
                    cells = [c.strip() for c in stripped.split('|')]
                    # Remove ONLY the leading/trailing empty edge cells produced by
                    # the outer pipes. Interior empty cells must be preserved so that
                    # columns stay aligned (e.g. a table with a blank top-left corner).
                    if cells and cells[0] == '':
                        cells = cells[1:]
                    if cells and cells[-1] == '':
                        cells = cells[:-1]
                    table_lines.append(cells)
                i += 1

            if table_lines:
                num_cols = len(table_lines[0])
                table = doc.add_table(rows=len(table_lines), cols=num_cols)
                table.style = 'Light Grid Accent 1'
                table.alignment = WD_TABLE_ALIGNMENT.LEFT

                for row_idx, row_data in enumerate(table_lines):
                    for col_idx in range(min(len(row_data), num_cols)):
                        cell = table.cell(row_idx, col_idx)
                        cell.text = ''
                        p = cell.paragraphs[0]
                        _add_inline(
                            p,
                            row_data[col_idx],
                            base_size=Pt(9),
                            base_bold=(row_idx == 0),
                        )

                doc.add_paragraph()  # spacing after table
            continue

        # Code blocks
        if line.strip().startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i].rstrip('\n'))
                i += 1
            i += 1  # skip closing ```
            if code_lines:
                p = doc.add_paragraph()
                p.style = doc.styles['Normal']
                p.paragraph_format.left_indent = Inches(0.3)
                run = p.add_run('\n'.join(code_lines))
                run.font.name = 'Consolas'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(40, 40, 40)
            continue

        # Blockquotes
        if line.startswith('>'):
            text = line.lstrip('>').strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            _add_inline(p, text, base_size=Pt(10))
            for r in p.runs:
                r.italic = True
                r.font.color.rgb = RGBColor(80, 80, 80)
            i += 1
            continue

        # Bullet points
        if line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            p = doc.add_paragraph(style='List Bullet')
            _add_inline(p, text, base_size=Pt(10))
            i += 1
            continue

        # Numbered list
        # Render the literal number from the source instead of Word's built-in
        # "List Number" style, which auto-continues across the whole document
        # (e.g. section 2 would start at 9 instead of 1).
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            number = m.group(1)
            text = m.group(2).strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.tab_stops.add_tab_stop(Inches(0.25))
            run = p.add_run(f"{number}.\t")
            run.font.size = Pt(10)
            _add_inline(p, text, base_size=Pt(10))
            i += 1
            continue

        # Regular paragraph
        text = line.strip()
        if text:
            p = doc.add_paragraph()
            _add_inline(p, text, base_size=Pt(10))
        i += 1

    doc.save(docx_path)
    print(f"  ✓ {os.path.basename(docx_path)}")


if __name__ == '__main__':
    # Console may be cp1252 on Windows; avoid UnicodeEncodeError on status glyphs.
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

    if len(sys.argv) >= 2:
        md_path = sys.argv[1]
        if len(sys.argv) >= 3:
            docx_path = sys.argv[2]
        else:
            docx_path = os.path.splitext(md_path)[0] + '.docx'
        parent = os.path.dirname(os.path.abspath(docx_path))
        os.makedirs(parent, exist_ok=True)
        print(f"Converting {os.path.basename(md_path)} to Word (.docx)...\n")
        parse_md_to_docx(md_path, docx_path)
        sys.exit(0)

    input_dir = 'outputs/recommendations'
    output_dir = 'outputs/recommendations/docx'
    os.makedirs(output_dir, exist_ok=True)

    md_files = [f for f in os.listdir(input_dir) if f.endswith('.md') and f != 'README.md']
    print(f"Converting {len(md_files)} markdown files to Word (.docx)...\n")

    for md_file in sorted(md_files):
        md_path = os.path.join(input_dir, md_file)
        docx_name = md_file.replace('.md', '.docx')
        docx_path = os.path.join(output_dir, docx_name)
        try:
            parse_md_to_docx(md_path, docx_path)
        except Exception as e:
            print(f"  ✗ {md_file}: {e}")

    print(f"\nDone! Files saved to: {output_dir}/")
