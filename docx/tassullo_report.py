"""Modulo STANDARD per le relazioni Word in stile Tassullo.

FONTE UNICA di questo modulo per tutte le app dello studio (mirror del ruolo di
theme.css per il CSS). Le app lo usano copiando questo file + il template
templates/relazione_tassullo_base.docx nel proprio repo (vedi docx/README.md
in questo stesso repo per il perché non è un pacchetto pip installabile da
git, e come propagare una modifica).

Questo è lo stile ufficiale ("Relazione layout vuoto") da riusare in TUTTE le
esportazioni di relazioni dell'app. Fornisce:

* il percorso del template base (`TEMPLATE_BASE`) con testata (logo Tassullo),
  piè di pagina (`tassullo.it` + numero pagina), font Arial e impostazione A4;
* costanti tipografiche coerenti con il layout Tassullo;
* helper deterministici (nessun LLM) per riempire un template a token:
  - `sostituisci_token`      → rimpiazza i segnaposto `{{...}}` (anche nei textbox
                               della cover e in testata/piè di pagina);
  - `inserisci_tabella`      → sostituisce un paragrafo-ancora con una tabella;
  - `inserisci_immagine`     → sostituisce un paragrafo-ancora con un'immagine;
  - `inserisci_paragrafi`    → sostituisce un paragrafo-ancora con testo/elenco;
  - `aggiungi_titolo`/`aggiungi_corpo` → paragrafi con lo stile Tassullo.

Metodo "template + token": la prosa fissa vive nel .docx, l'export cambia solo i
campi variabili → costo in token ~0.
"""
from __future__ import annotations

import os
from typing import Iterable, Optional, Sequence

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

# ── Percorsi ──────────────────────────────────────────────────────────────────
# I template sono versionati in `templates/` alla radice del repo (la cartella
# `esportazioni/` è .gitignore e non arriverebbe in produzione).
_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(_DIR, "templates")
TEMPLATE_BASE = os.path.join(TEMPLATE_DIR, "relazione_tassullo_base.docx")

# ── Tipografia Tassullo (mezzi-punti come nel docx: sz=28 → 14pt) ─────────────
FONT = "Arial"
SZ_H1 = 28      # titolo di sezione  "1. …"           (14 pt, bold)
SZ_H2 = 24      # sottosezione       "3.1 …"          (12 pt, bold)
SZ_H3 = 20      # sotto-sottosezione "3.1.1 …"        (10 pt, bold)
SZ_BODY = 20    # corpo                                (10 pt)
SZ_SMALL = 16   # note                                 (8 pt)
NERO = RGBColor(0x14, 0x14, 0x14)   # nero brand (tassullo.it), non #000 puro
GRIGIO = RGBColor(0x55, 0x55, 0x55)
BLU = RGBColor(0x1F, 0x4E, 0x79)    # accento informativo storico (non brand): usato da voce_analisi_export.py
VERDE = RGBColor(0x1B, 0x7F, 0x3B)
ROSSO = RGBColor(0xB3, 0x26, 0x1E)
ACCENTO = RGBColor(0xF4, 0xAC, 0x3D)      # arancio brand tassullo.it — tocchi d'accento (rule, evidenze)
ACCENTO_INK = RGBColor(0xB4, 0x53, 0x09)  # arancio leggibile come testo su fondo chiaro
ACCENTO_HEX = "F4AC3D"
HDR_FILL = "141414"   # intestazione tabelle — nero brand (era il blu #1F4E79)

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


# ── Caricamento ───────────────────────────────────────────────────────────────
def documento_base() -> Document:
    """Apre il template base (stile Tassullo, cover/testata/piè inclusi)."""
    return Document(TEMPLATE_BASE)


def documento_da_template(nome_file: str) -> Document:
    """Apre un template specifico dalla cartella `templates/`."""
    return Document(os.path.join(TEMPLATE_DIR, nome_file))


def pulisci_corpo(doc: Document) -> None:
    """Svuota il corpo del documento mantenendo le proprietà di sezione (A4,
    margini) e testata/piè di pagina. Utile per partire dal layout Tassullo
    SENZA la copertina e senza i contenuti segnaposto del template."""
    body = doc.element.body
    for child in list(body):
        if child.tag == qn("w:sectPr"):
            continue  # ultimo figlio: proprietà di sezione (header/footer, A4)
        body.remove(child)


def documento_base_senza_cover() -> Document:
    """Template base Tassullo (font Arial, A4, testata logo e piè `tassullo.it` +
    numero pagina) MA senza copertina/contenuti segnaposto: pronto per aggiungere
    solo le sezioni volute con gli helper `aggiungi_*` / `inserisci_*`."""
    doc = documento_base()
    pulisci_corpo(doc)
    return doc


def imposta_intestazione_corrente(doc: Document, testo: str) -> None:
    """Aggiorna il testo dell'intestazione running (pagine 2+) del documento,
    sostituendo il segnaposto del template."""
    for sec in doc.sections:
        paras = [p for p in sec.header.paragraphs if p.text.strip()]
        if not paras:
            continue
        ts = list(paras[0]._element.iter(qn("w:t")))
        if ts:
            ts[0].text = testo
            for t in ts[1:]:
                t.text = ""


# ── Run/paragrafi in stile Tassullo ───────────────────────────────────────────
def _styla_run(run, *, sz: int, bold: bool = False, color: RGBColor = NERO,
               italic: bool = False) -> None:
    run.font.name = FONT
    run.font.size = Pt(sz / 2)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    # forza il font anche per il complex-script
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(a), FONT)


def _bordo_inferiore(p, color_hex: str, *, sz: int = 6, space: int = 4) -> None:
    """Aggiunge un filetto (bottom border) al paragrafo — il tocco d'accento
    sotto i titoli di sezione principali."""
    pPr = p._p.get_or_add_pPr()
    pbdr = pPr.find(qn("w:pBdr"))
    if pbdr is None:
        pbdr = OxmlElement("w:pBdr")
        pPr.append(pbdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(sz))
    bottom.set(qn("w:space"), str(space))
    bottom.set(qn("w:color"), color_hex)
    pbdr.append(bottom)


def aggiungi_titolo(doc: Document, testo: str, livello: int = 1) -> "object":
    """Titolo di sezione con la resa del layout Tassullo (Arial bold nero).
    I titoli di livello 1 hanno un filetto d'accento arancio (brand) sotto."""
    sz = {1: SZ_H1, 2: SZ_H2, 3: SZ_H3}.get(livello, SZ_H3)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10 if livello == 1 else 6)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    _styla_run(p.add_run(testo), sz=sz, bold=True)
    if livello == 1:
        _bordo_inferiore(p, ACCENTO_HEX)
    return p


def aggiungi_corpo(doc: Document, testo: str, *, giustificato: bool = True,
                   grassetto: bool = False, color: RGBColor = NERO,
                   sz: int = SZ_BODY) -> "object":
    p = doc.add_paragraph()
    if giustificato:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(4)
    _styla_run(p.add_run(testo), sz=sz, bold=grassetto, color=color)
    return p


def aggiungi_elenco(doc: Document, voci: Iterable[str], *, sz: int = SZ_BODY) -> None:
    for v in voci:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Pt(14)
        p.paragraph_format.space_after = Pt(2)
        _styla_run(p.add_run("•  "), sz=sz)
        _styla_run(p.add_run(str(v)), sz=sz)


# ── Sostituzione token (cover/textbox/testata/piè inclusi) ────────────────────
def _parti_documento(doc: Document):
    """Elementi radice in cui cercare token: corpo + testate/piè di ogni sezione."""
    parti = [doc.element.body]
    for sec in doc.sections:
        for hf in (sec.header, sec.footer,
                   sec.first_page_header, sec.first_page_footer,
                   sec.even_page_header, sec.even_page_footer):
            try:
                parti.append(hf._element)
            except Exception:
                pass
    return parti


def sostituisci_token(doc: Document, mapping: dict[str, str]) -> None:
    """Rimpiazza i segnaposto `{{TOKEN}}` in tutto il documento.

    I token sono autorati come run singoli (una `w:t` = un token), quindi la
    sostituzione per-run è sufficiente e non altera la formattazione. In più,
    come rete di sicurezza, si gestisce anche il token spezzato su più run dello
    stesso paragrafo unendone il testo nel primo run.
    """
    def sub_text(s: str) -> str:
        for k, v in mapping.items():
            if k in s:
                s = s.replace(k, "" if v is None else str(v))
        return s

    for parte in _parti_documento(doc):
        # 1) sostituzione diretta per run
        for t in parte.iter(qn("w:t")):
            if t.text and "{{" in t.text:
                t.text = sub_text(t.text)
        # 2) fallback: token spezzato su più run in un paragrafo
        for p in parte.iter(qn("w:p")):
            runs_t = [t for t in p.iter(qn("w:t"))]
            joined = "".join(t.text or "" for t in runs_t)
            if "{{" in joined and any(k in joined for k in mapping):
                new = sub_text(joined)
                if new != joined and runs_t:
                    runs_t[0].text = new
                    for extra in runs_t[1:]:
                        extra.text = ""


# ── Ancore: trova il paragrafo il cui testo è esattamente l'ancora ────────────
def _trova_ancora(doc: Document, ancora: str):
    for p in doc.element.body.iter(qn("w:p")):
        txt = "".join(t.text or "" for t in p.iter(qn("w:t")))
        if txt.strip() == ancora:
            return p
    return None


def _shade(cell, fill_hex: str) -> None:
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), fill_hex)
    tcpr.append(shd)


def inserisci_tabella(doc: Document, ancora: str, righe: Sequence[Sequence[str]],
                      *, intestazione: bool = True,
                      colore_esito: Optional[dict[int, RGBColor]] = None) -> None:
    """Sostituisce il paragrafo-ancora con una tabella in stile Tassullo.

    `righe[0]` è l'intestazione (sfondo blu, testo bianco). `colore_esito` mappa
    l'indice di riga → colore del testo dell'ULTIMA colonna (per gli esiti).
    """
    anchor = _trova_ancora(doc, ancora)
    if anchor is None or not righe:
        return
    n_cols = max(len(r) for r in righe)
    table = doc.add_table(rows=0, cols=n_cols)
    table.style = "Table Grid"
    table.autofit = True
    for r, row in enumerate(righe):
        cells = table.add_row().cells
        for c in range(n_cols):
            testo = str(row[c]) if c < len(row) else ""
            cell = cells[c]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(testo)
            is_hdr = intestazione and r == 0
            col = NERO
            if colore_esito and r in colore_esito and c == n_cols - 1:
                col = colore_esito[r]
            _styla_run(
                run, sz=SZ_SMALL, bold=is_hdr,
                color=RGBColor(0xFF, 0xFF, 0xFF) if is_hdr else col,
            )
            if is_hdr:
                _shade(cell, HDR_FILL)
    # sposta la tabella al posto dell'ancora e rimuovi l'ancora
    anchor.addprevious(table._tbl)
    anchor.getparent().remove(anchor)


def inserisci_paragrafi(doc: Document, ancora: str, voci: Sequence[str],
                        *, elenco: bool = True) -> None:
    """Sostituisce il paragrafo-ancora con testo (elenco puntato o corpo)."""
    anchor = _trova_ancora(doc, ancora)
    if anchor is None:
        return
    for v in voci:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        if elenco:
            p.paragraph_format.left_indent = Pt(14)
            _styla_run(p.add_run("•  "), sz=SZ_BODY)
        _styla_run(p.add_run(str(v)), sz=SZ_BODY)
        anchor.addprevious(p._p)
    anchor.getparent().remove(anchor)


def inserisci_immagine(doc: Document, ancora: str, png_bytes: bytes,
                       *, larghezza_cm: float = 15.0) -> None:
    """Sostituisce il paragrafo-ancora con un'immagine PNG centrata."""
    import io
    from docx.shared import Cm
    anchor = _trova_ancora(doc, ancora)
    if anchor is None or not png_bytes:
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(io.BytesIO(png_bytes), width=Cm(larghezza_cm))
    anchor.addprevious(p._p)
    anchor.getparent().remove(anchor)


def rimuovi_ancore_residue(doc: Document, ancore: Iterable[str]) -> None:
    """Elimina eventuali paragrafi-ancora non riempiti (robustezza)."""
    for a in ancore:
        p = _trova_ancora(doc, a)
        if p is not None:
            p.getparent().remove(p)
