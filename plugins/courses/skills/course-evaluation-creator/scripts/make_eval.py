"""Genera, por cada evaluación de una especificación: versión alumno (.docx), versión docente (.docx)
y script de Google Forms (.gs). Cada evaluación suma 20 puntos.

Uso:   python scripts/make_eval.py <especificacion.py> <carpeta_salida> [clave ...]
Ej.:   python scripts/make_eval.py assets/ejemplo-especificacion-RED-201.py ./salida L1 EF

El archivo de especificación debe definir CURSO (texto) y SPECS (dict clave -> evaluación); véase
assets/ejemplo-especificacion-RED-201.py. Requiere: pip install python-docx
Después de generar los .docx, cree su Markdown equivalente con scripts/docx2md.py.
"""
import datetime
import importlib.util
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

CURSO = ""
SPECS = {}


def cargar_especificacion(ruta):
    """Carga CURSO y SPECS desde un archivo .py de especificación."""
    global CURSO, SPECS
    spec = importlib.util.spec_from_file_location("especificacion_eval", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    CURSO, SPECS = mod.CURSO, mod.SPECS

RED = RGBColor(0xB9, 0x1C, 0x1C)
LET = "ABCD"


def fmt(n):
    return str(n).replace(".", ",") if isinstance(n, float) and n != int(n) else str(int(n))


def shade_par(p, fill):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def shade_cell(c, fill):
    tcPr = c._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def totales(sp):
    t = dict(simple=len(sp["simple"]), vf=len(sp["vf"]), comp=len(sp["comp"]), mult=sp["mult"]["pts"], casos=sum(c["pts"] for c in sp["casos"]))
    tot = t["simple"] + t["vf"] + t["comp"] + t["mult"] + t["casos"]
    assert tot == 20, (sp["code"], t, tot)
    return t, tot


def numerar(sp):
    """Asigna número consecutivo a cada pregunta; devuelve lista (sección, objeto, número)."""
    n = 0
    out = []
    for key in ("simple", "vf", "comp"):
        for q in sp[key]:
            n += 1; q["n"] = n
    n += 1; sp["mult"]["n"] = n
    for c in sp["casos"]:
        n += 1; c["n"] = n
    return n


def build_docx(sp, docente, path):
    t, tot = totales(sp)
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    for name, size in (("Heading 1", 15), ("Heading 2", 12)):
        h = doc.styles[name]; h.font.name = "Calibri"; h.font.size = Pt(size); h.font.bold = True; h.font.color.rgb = RED
        h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

    def par(text, bold=False, indent=0, italic=False):
        p = doc.add_paragraph()
        if indent:
            p.paragraph_format.left_indent = Pt(indent)
        r = p.add_run(text); r.bold = bold; r.italic = italic
        return p

    def callout(prefix, text, fill="E3F3E5"):
        p = doc.add_paragraph(); shade_par(p, fill)
        p.paragraph_format.left_indent = Pt(14)
        p.add_run(prefix + " ").bold = True
        p.add_run(text)

    def table(rows, header=None):
        tb = doc.add_table(rows=len(rows) + (1 if header else 0), cols=len(rows[0]))
        tb.style = "Table Grid"
        ri = 0
        if header:
            for j, hdr in enumerate(header):
                c = tb.rows[0].cells[j]; c.text = ""
                rr = c.paragraphs[0].add_run(hdr); rr.bold = True; rr.font.color.rgb = RGBColor(255, 255, 255)
                shade_cell(c, "B91C1C")
            ri = 1
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                c = tb.rows[ri + i].cells[j]; c.text = ""
                rr = c.paragraphs[0].add_run(str(v))
                if j == 0 and not header:
                    rr.bold = True; shade_cell(c, "F3E3E3")
        doc.add_paragraph()

    tt = doc.add_paragraph(); tt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = tt.add_run("EVALUACIÓN"); r.bold = True; r.font.size = Pt(22); r.font.color.rgb = RED
    s2 = doc.add_paragraph(); s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s2.add_run(sp["titulo"]).bold = True
    s3 = doc.add_paragraph(); s3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s3.add_run("Versión docente (con clave de respuestas)" if docente else "Versión alumno").italic = True

    info = [("Curso", CURSO), ("Lección", sp["leccion"]), ("Código", sp["code"]), ("Tipo", sp["tipo"]),
            ("Tiempo asignado", f"{sp['minutos']} minutos"), ("Puntaje total", f"{tot} puntos"), ("Modo", "Individual"),
            ("Recursos permitidos", sp["recursos"])]
    if not docente:
        info += [("Nombre del alumno", "______________________________"), ("Fecha", "____ / ____ / ________")]
    table(info)

    doc.add_heading("Instrucciones generales", level=1)
    par(f"Esta evaluación tiene {tot} puntos y debe resolverse de forma individual en {sp['minutos']} minutos. "
        f"Recursos permitidos: {sp['recursos']}. Lea cada pregunta completa antes de responder. Responda con "
        "claridad y use la sintaxis exacta de los comandos de Redis cuando se pida. Versión de referencia: Redis 8.0.3.")

    n_total = numerar(sp)

    # A. Selección simple
    doc.add_heading(f"Sección A: Selección simple ({t['simple']} pts)", level=1)
    par("Marque la única respuesta correcta. Cada pregunta vale 1 punto.", italic=True)
    for q in sp["simple"]:
        par(f"{q['n']}. {q['q']}", bold=True)
        for i, o in enumerate(q["opts"]):
            par(f"{LET[i]}) {o}", indent=18)
        if docente:
            callout("✔ Respuesta correcta:", f"{LET[q['ok']]}) {q['opts'][q['ok']]} — Nivel Bloom: {q['bloom']}")

    # B. Verdadero / Falso
    doc.add_heading(f"Sección B: Verdadero o falso ({t['vf']} pts)", level=1)
    par("Indique si el enunciado es verdadero (V) o falso (F). Cada pregunta vale 1 punto.", italic=True)
    for q in sp["vf"]:
        par(f"{q['n']}. {q['q']}    ( V )   ( F )", bold=True)
        if docente:
            callout("✔ Respuesta:", f"{'V' if q['ans'] else 'F'} — Justificación: {q['just']} — Nivel Bloom: {q['bloom']}")

    # C. Completar
    doc.add_heading(f"Sección C: Completar espacios ({t['comp']} pts)", level=1)
    par("Escriba la palabra o el comando que completa la oración. Cada pregunta vale 1 punto.", italic=True)
    for q in sp["comp"]:
        par(f"{q['n']}. {q['q']}", bold=True)
        if docente:
            extra = f" (también se acepta: {', '.join(q['alt'])})" if q["alt"] else ""
            callout("✔ Respuesta esperada:", f"{q['ans']}{extra} — Nivel Bloom: {q['bloom']}")

    # D. Selección múltiple
    m = sp["mult"]
    doc.add_heading(f"Sección D: Selección múltiple ({m['pts']} pts)", level=1)
    par(f"{m['n']}. {m['q']} (Seleccione todas las que apliquen) — {m['pts']} pts", bold=True)
    for i, o in enumerate(m["opts"]):
        par(f"☐ {LET[i]}) {o}", indent=18)
    if docente:
        corr = ", ".join(LET[i] for i in m["oks"])
        callout("✔ Respuestas correctas:", f"{corr} — Puntaje parcial: +1 por cada opción correcta marcada y −1 por cada incorrecta, "
                f"con un mínimo de 0 — Nivel Bloom: {m['bloom']}")

    # E. Casos
    doc.add_heading(f"Sección E: Caso práctico ({t['casos']} pts)", level=1)
    for c in sp["casos"]:
        par(f"{c['n']}. CASO: {c['texto']}", bold=True)
        for k, p in enumerate(c["preguntas"], 1):
            par(f"{c['n']}.{k} {p}", indent=18)
            if not docente:
                for _ in range(3):
                    par("______________________________________________________________________", indent=18)
        par(f"Puntaje total del caso: {c['pts']} pts" + (" — Nivel Bloom: Analizar / Evaluar" if docente else ""), italic=True)
        if docente:
            doc.add_heading("Puntos esperados en la respuesta", level=2)
            for e in c["esperados"]:
                doc.add_paragraph(e, style="List Bullet")
            doc.add_heading(f"Rúbrica del caso {c['n']} (1 punto por criterio)", level=2)
            table([[r[0], r[1], r[2], r[3], r[4]] for r in c["rubrica"]],
                  header=["Criterio", "Excelente (1)", "Bueno (0,75)", "Regular (0,5)", "Insuficiente (0,25 o 0)"])

    # Tabla de puntuación
    doc.add_heading("Tabla de puntuación (uso del docente)", level=1)
    filas = [("A. Selección simple", t["simple"], ""), ("B. Verdadero o falso", t["vf"], ""), ("C. Completar espacios", t["comp"], ""),
             ("D. Selección múltiple", t["mult"], ""), ("E. Caso práctico", t["casos"], ""), ("TOTAL", tot, "")]
    table(filas, header=["Sección", "Puntaje máximo", "Puntaje obtenido"])

    if docente:
        doc.add_heading("Niveles de desempeño", level=1)
        table([("18-20", "Sobresaliente", "Domina todos los objetivos"), ("14-17", "Satisfactorio", "Logra los objetivos principales"),
               ("11-13", "En proceso", "Logra objetivos básicos"), ("0-10", "Insuficiente", "No logra los objetivos mínimos")],
              header=["Puntaje", "Nivel", "Descripción"])
        doc.add_heading("Cobertura de objetivos", level=1)
        filas = []
        todas = [(q["n"], q["o"]) for k in ("simple", "vf", "comp") for q in sp[k]] + [(m["n"], m["o"])] + [(c["n"], c["o"]) for c in sp["casos"]]
        for key, texto in sp["obj"]:
            nums = [str(n) for n, o in todas if key in o]
            filas.append((("Objetivo " if not key.startswith("L") else "") + key, texto, ", ".join(nums)))
        table(filas, header=["Referencia", "Objetivo o contenido", "Preguntas"])
        doc.add_heading("Notas para el docente", level=1)
        for nota in ("Las preguntas de completar espacios admiten las variantes indicadas en la clave; acepte mayúsculas y minúsculas.",
                     "Los casos prácticos se califican con la rúbrica; el puntaje de cada criterio es acumulable hasta el máximo del caso.",
                     "Las respuestas se basan en lo medido en los laboratorios con Redis 8.0.3; los números exactos pueden variar entre ejecuciones."):
            doc.add_paragraph(nota, style="List Bullet")

    f = doc.sections[0].footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f.add_run(f"{sp['code']} · {'Versión docente' if docente else 'Versión alumno'} · {datetime.date.today().strftime('%d/%m/%Y')}").font.size = Pt(9)
    doc.save(path)


def js(s):
    return json.dumps(s, ensure_ascii=False)


def build_gs(sp, path):
    t, tot = totales(sp)
    numerar(sp)
    L = []
    a = L.append
    a(f"// {sp['code']} — Script de Google Apps Script que crea el formulario de la evaluación.")
    a("// Uso: abrir script.google.com > Nuevo proyecto > pegar este archivo > ejecutar crearEvaluacion().")
    a("// Notas: las preguntas de completar espacios y los casos prácticos requieren calificación manual")
    a("// (Apps Script no permite fijar la respuesta correcta de un texto corto). En la selección múltiple,")
    a("// el formulario califica todo o nada; el puntaje parcial se puede activar a mano en el formulario.")
    a("function crearEvaluacion() {")
    a(f"  var form = FormApp.create({js(sp['titulo'] + ' — ' + sp['code'])});")
    desc = (f"{sp['leccion']}. Tipo: {sp['tipo']}. Tiempo: {sp['minutos']} minutos. Puntaje total: {tot} puntos. "
            f"Recursos: {sp['recursos']}. Lea cada pregunta completa antes de responder.")
    a(f"  form.setDescription({js(desc)});")
    a("  form.setIsQuiz(true);")
    a("  form.setCollectEmail(true);")
    a("  form.setLimitOneResponsePerUser(true);")
    a("")
    a(f"  form.addSectionHeaderItem().setTitle({js('SECCIÓN A: SELECCIÓN SIMPLE')}).setHelpText({js('Seleccione la única respuesta correcta. Cada pregunta vale 1 punto.')});")
    for q in sp["simple"]:
        v = f"q{q['n']}"
        a(f"  var {v} = form.addMultipleChoiceItem();")
        ch = ", ".join(f"{v}.createChoice({js(LET[i] + ') ' + o)}, {'true' if i == q['ok'] else 'false'})" for i, o in enumerate(q["opts"]))
        a(f"  {v}.setTitle({js(str(q['n']) + '. ' + q['q'])}).setChoices([{ch}]).setRequired(true).setPoints(1);")
    a("")
    a(f"  form.addSectionHeaderItem().setTitle({js('SECCIÓN B: VERDADERO O FALSO')}).setHelpText({js('Cada pregunta vale 1 punto.')});")
    for q in sp["vf"]:
        v = f"q{q['n']}"
        a(f"  var {v} = form.addMultipleChoiceItem();")
        a(f"  {v}.setTitle({js(str(q['n']) + '. ' + q['q'])}).setChoices([{v}.createChoice('Verdadero', {'true' if q['ans'] else 'false'}), "
          f"{v}.createChoice('Falso', {'false' if q['ans'] else 'true'})]).setRequired(true).setPoints(1)"
          f".setFeedbackForCorrect(FormApp.createFeedback().setText({js(q['just'])}).build())"
          f".setFeedbackForIncorrect(FormApp.createFeedback().setText({js(q['just'])}).build());")
    a("")
    a(f"  form.addSectionHeaderItem().setTitle({js('SECCIÓN C: COMPLETAR ESPACIOS')}).setHelpText({js('Escriba la palabra o el comando que completa la oración. Cada pregunta vale 1 punto (calificación manual).')});")
    for q in sp["comp"]:
        v = f"q{q['n']}"
        extra = f" (también: {', '.join(q['alt'])})" if q["alt"] else ""
        a(f"  // Clave: {q['ans']}{extra}")
        a(f"  var {v} = form.addTextItem();")
        a(f"  {v}.setTitle({js(str(q['n']) + '. ' + q['q'])}).setRequired(true).setPoints(1);")
    a("")
    m = sp["mult"]
    a(f"  form.addSectionHeaderItem().setTitle({js('SECCIÓN D: SELECCIÓN MÚLTIPLE')}).setHelpText({js('Seleccione todas las que apliquen.')});")
    v = f"q{m['n']}"
    a(f"  var {v} = form.addCheckboxItem();")
    ch = ", ".join(f"{v}.createChoice({js(LET[i] + ') ' + o)}, {'true' if i in m['oks'] else 'false'})" for i, o in enumerate(m["opts"]))
    a(f"  {v}.setTitle({js(str(m['n']) + '. ' + m['q'] + ' (Seleccione todas las que apliquen)')}).setChoices([{ch}]).setRequired(true).setPoints({m['pts']});")
    a("")
    a(f"  form.addSectionHeaderItem().setTitle({js('SECCIÓN E: CASO PRÁCTICO')}).setHelpText({js('Se evalúa con rúbrica (calificación manual).')});")
    for c in sp["casos"]:
        a(f"  form.addSectionHeaderItem().setTitle({js('CASO ' + str(c['n']))}).setHelpText({js(c['texto'])});")
        por = c["pts"] / len(c["preguntas"])
        for k, p in enumerate(c["preguntas"], 1):
            v = f"q{c['n']}_{k}"
            a(f"  var {v} = form.addParagraphTextItem();")
            a(f"  {v}.setTitle({js(str(c['n']) + '.' + str(k) + ' ' + p)}).setHelpText({js('Puntaje: ' + fmt(por) + ' pts — se evaluará con rúbrica.')}).setRequired(true).setPoints({por});")
    a("")
    a("  form.setConfirmationMessage('Tu evaluación ha sido enviada correctamente.');")
    a("  Logger.log('Formulario creado: ' + form.getPublishedUrl());")
    a("  Logger.log('URL de edición: ' + form.getEditUrl());")
    a("}")
    Path(path).write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


UNIDADES = {"Milisegundos", "Microsegundos", "Segundos", "Nanosegundos"}


def orden_logico(opts):
    """Opciones con orden propio (números, unidades, 'Ambos/Ninguno') que no deben reordenarse."""
    if all(o.strip().isdigit() for o in opts):
        return True
    if set(opts) == UNIDADES or any(o.startswith("Ambos") for o in opts):
        return True
    return False


def equilibrar(sp):
    """Reubica la opción correcta de forma determinista para repartir A, B, C y D."""
    objetivo = [1, 3, 0, 2, 3, 1, 0, 2]
    k = 0
    for q in sp["simple"]:
        if orden_logico(q["opts"]):
            continue
        correcta = q["opts"][q["ok"]]
        resto = [o for i, o in enumerate(q["opts"]) if i != q["ok"]]
        pos = objetivo[k % len(objetivo)]
        resto.insert(pos, correcta)
        q["opts"], q["ok"] = resto, pos
        k += 1


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cargar_especificacion(sys.argv[1])
    root = Path(sys.argv[2])
    claves = sys.argv[3:] or list(SPECS)
    for k in claves:
        sp = SPECS[k]
        equilibrar(sp)
        print(k, "letras correctas (sel. simple):", "".join(LET[q["ok"]] for q in sp["simple"]))
        d = root / sp["folder"]
        d.mkdir(parents=True, exist_ok=True)
        build_docx(sp, False, d / f"{sp['code']}-eval-alumno.docx")
        build_docx(sp, True, d / f"{sp['code']}-eval-docente.docx")
        build_gs(sp, d / f"{sp['code']}-evaluacion-forms.gs")
        print(k, "->", d.name, "(20 pts)")
