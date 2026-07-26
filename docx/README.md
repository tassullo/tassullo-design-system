# Relazioni Word (Python / python-docx)

Fonte unica dello stile Tassullo per i documenti Word generati dalle app
(relazioni tecniche, perizie, report) — l'equivalente di `theme.css` ma per
`python-docx` invece che per il browser.

Contiene:
- **`tassullo_report.py`** — helper deterministici (nessun LLM) per generare
  relazioni a partire dal template: `aggiungi_titolo`/`aggiungi_corpo`,
  `sostituisci_token`, `inserisci_tabella`/`inserisci_immagine`/`inserisci_paragrafi`,
  costanti di colore e tipografia. Metodo "template + token": la prosa fissa
  vive nel `.docx`, l'export cambia solo i campi variabili.
- **`templates/relazione_tassullo_base.docx`** — il template Word (testata con
  logo, piè `tassullo.it` + numero pagina, font Arial, A4).

## Palette (allineata a tassullo.it, v1.1)

| Costante | Hex | Uso |
|---|---|---|
| `NERO` | `#141414` | testo principale (nero brand, non `#000` puro) |
| `ACCENTO` | `#F4AC3D` | arancio brand — filetti/tocchi d'accento (es. sotto i titoli §1) |
| `ACCENTO_INK` | `#B45309` | arancio leggibile come testo su fondo chiaro |
| `HDR_FILL` | `#141414` | sfondo intestazione tabelle (nero, testo bianco sopra) |
| `BLU` / `VERDE` / `ROSSO` | storici | accenti informativi/esito, **non** legati al brand — usati da moduli specifici (es. analisi prezzo) che li adottano volutamente come propria identità |

## Copertina: elemento indipendente e opzionale

Il template contiene una copertina (testata "Spett.le:", logo, luogo/data,
"Cantiere:", "Oggetto:") ma **non è obbligatoria**: è un elemento a parte,
non incollato al corpo della relazione, con due punti d'ingresso distinti:

- **`documento_base()`** — template completo CON copertina. I campi della
  copertina sono prosa segnaposto (non `{{TOKEN}}`): pensata per essere
  compilata a mano in Word quando serve una lettera di accompagnamento
  intestata a un destinatario. Nessun export automatico oggi la usa da sola;
  è usata solo per costruire template derivati (es. lo script che genera il
  template dell'antiribaltamento).
- **`documento_base_senza_cover()`** — stesso layout (testata/piè, A4, font)
  MA senza copertina: `pulisci_corpo()` svuota il corpo mantenendo le
  proprietà di sezione. **È lo standard per ogni export generato da codice**:
  tutti gli export attuali (proposta, manuale di calcolo, condizioni d'uso,
  caso di prova, analisi prezzo) partono da qui.

Se una relazione ha bisogno di una copertina compilata con dati reali (non a
mano), la strada è tokenizzare i campi della copertina (`{{DESTINATARIO}}`,
`{{CANTIERE}}`, `{{OGGETTO}}`, `{{LUOGO_DATA}}`) così `sostituisci_token` può
riempirli come già fa per testata/piè — non ancora fatto, da valutare quando
serve davvero un caso d'uso concreto.

## Perché non è un pacchetto pip (a differenza di `@tassullo/theme` su npm)

SuperTM builda ed esegue i test su Python 3.12 in CI, ma il deploy verso Azure
App Service installa le dipendenze così (vedi `.github/workflows/deploy.yml`):

```bash
pip install --only-binary :all: --target=".python_packages/lib/site-packages" -r requirements.txt
```

`--only-binary :all:` rifiuta qualsiasi pacchetto senza wheel precompilato —
un pacchetto installato da `git+https://...` non ne ha uno (va costruito da
sorgente) e romperebbe il deploy. Finché questo vincolo resta, la propagazione
per Python è **manuale**, non `npm update`:

1. Modifica `tassullo_report.py` (e/o il template) qui.
2. Ricopia i due file nell'app: `cp docx/tassullo_report.py <app>/relazione_tassullo.py`
   e `cp docx/templates/relazione_tassullo_base.docx <app>/templates/`.
3. Rigenera un documento di prova e verifica i colori (vedi test in fondo).

Se in futuro un'app costruisse le proprie wheel in CI (o si passasse a un
registry privato), si potrebbe rivalutare il pacchetto pip.

## Usarlo in una nuova app

1. Copia `tassullo_report.py` nel repo dell'app (es. come `relazione_tassullo.py`
   nel root, o in un modulo dedicato secondo le convenzioni dell'app).
2. Copia `templates/relazione_tassullo_base.docx` nella cartella template
   dell'app; aggiorna `TEMPLATE_DIR`/`TEMPLATE_BASE` se il percorso cambia.
3. Genera un documento:
   ```python
   import tassullo_report as RT
   doc = RT.documento_base_senza_cover()
   RT.aggiungi_titolo(doc, "1. Descrizione dell'intervento", livello=1)
   RT.aggiungi_corpo(doc, "Testo della relazione…")
   doc.save("relazione.docx")
   ```
4. Se l'app ha un logo/dominio diverso da Tassullo: il logo vive come immagine
   nel `.docx` (testata/piè), non nei token Python — va sostituito nel template
   stesso (Word: Inserisci > Intestazione), non ricreato da zero.

## Nota sul font

Il template usa **Arial** (non Replicall come il CSS): Word non garantisce il
rendering di font non di sistema senza incorporarli nel file, e Arial è lo
standard già validato per la stampa/firma dei documenti Tassullo. Non cambiare
font nel template senza verificarne la resa in stampa.
