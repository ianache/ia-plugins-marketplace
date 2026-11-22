"""Convierte un .docx generado por los skills de curso a un .md equivalente.

Uso: python -I docx2md.py <entrada.docx> [salida.md]
Por defecto escribe <entrada>.md junto al .docx.
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


def fill_of(el):
    """Color de sombreado (w:shd) de un párrafo o celda, o None."""
    shd = el.find('.//' + qn('w:shd'))
    return shd.get(qn('w:fill')) if shd is not None else None


def is_mono(p):
    runs = [r for r in p.runs if r.text.strip()]
    return bool(runs) and all((r.font.name or '').lower() in ('consolas', 'courier new') for r in runs)


def esc_cell(t):
    return t.replace('|', '\\|').replace('\n', '<br>').strip()


def table_md(t):
    rows = [[esc_cell(c.text) if '\n' not in c.text else '<br>'.join(
        esc_cell(pp.text) for pp in c.paragraphs if pp.text.strip()) for c in r.cells] for r in t.rows]
    header = fill_of(t.rows[0].cells[0]._tc) == 'B91C1C'
    if not header:
        rows.insert(0, ['Campo', 'Valor'] if len(rows[0]) == 2 else [''] * len(rows[0]))
    n = len(rows[0])
    out = ['| ' + ' | '.join(rows[0]) + ' |', '| ' + ' | '.join(['---'] * n) + ' |']
    out += ['| ' + ' | '.join(r) + ' |' for r in rows[1:]]
    return out


def convert(src):
    doc = Document(src)
    out, code = [], []

    def flush_code():
        if code:
            if out and out[-1] != '':
                out.append('')
            out.extend(['```', *code, '```', ''])
            code.clear()

    for child in doc.element.body.iterchildren():
        if child.tag == qn('w:tbl'):
            flush_code()
            out.extend(table_md(Table(child, doc)))
            out.append('')
            continue
        if child.tag != qn('w:p'):
            continue
        p = Paragraph(child, doc)
        text = p.text.strip()
        style = p.style.name if p.style is not None else ''
        if is_mono(p):
            code.append(p.text.rstrip())
            continue
        flush_code()
        if not text or re.fullmatch(r'_+', text):
            continue  # párrafos vacíos y líneas de respuesta (solo guiones bajos)
        if style.startswith('Heading'):
            level = int(re.sub(r'\D', '', style) or 1)
            out.extend(['#' * (level + 1) + ' ' + text, ''])
        elif p.alignment is not None and int(p.alignment) == 1:  # centrado → título
            bold = any(r.bold for r in p.runs)
            first = not any(l.startswith('# ') for l in out)
            out.extend([('# ' + text.capitalize() if first and text.isupper() else
                         ('**' + text + '**' if bold else text)), ''])
        elif style.startswith('List Bullet'):
            out.append('- ' + text)
        elif fill_of(child) and fill_of(child) != 'EEEEEE':
            bold = [r.text for r in p.runs if r.bold]
            if bold:
                prefix = bold[0].strip()
                body = text[len(prefix):].strip() if text.startswith(prefix) else text
                out.extend([f'> **{prefix}** {body}', ''])
            else:
                out.extend(['> ' + text, ''])
        elif re.match(r'^\d+\.\s', text):
            out.append(text)
        else:
            if out and re.match(r'^(- |\d+\. )', out[-1]):
                out.append('')
            out.extend([('**' + text + '**') if all(r.bold for r in p.runs if r.text.strip()) else text, ''])
    flush_code()

    # pie de página
    foot = ' '.join(p.text.strip() for s in doc.sections for p in s.footer.paragraphs if p.text.strip())
    if foot:
        out.extend(['---', '', '*' + foot + '*'])

    # normaliza: una línea en blanco tras listas y sin blancos dobles
    md, prev_blank = [], False
    for i, l in enumerate(out):
        if l == '':
            if prev_blank:
                continue
            prev_blank = True
        else:
            if md and re.match(r'^(- |\d+\. )', md[-1]) and not re.match(r'^(- |\d+\. |```| )', l) and not prev_blank:
                md.append('')
            prev_blank = False
        md.append(l)
    return '\n'.join(md).strip() + '\n'


if __name__ == '__main__':
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix('.md')
    dst.write_text(convert(src), encoding='utf-8', newline='\n')
    print(dst)
