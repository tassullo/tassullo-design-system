# Integrazione col Design System Tassullo

> Blocco da inserire nel piano di sviluppo di ogni nuova app dello studio.
> È autosufficiente: contiene tutto il contesto necessario, anche per chi
> non conosce la storia del progetto.

## Contesto

Le app dello studio Tassullo (la prima è "Studio Tassullo" / SuperTM) condividono
un unico stile grafico, allineato al sito istituzionale tassullo.it — nero `#141414`,
superfici chiare su neutri caldi, accento arancio `#F4AC3D` con testo scuro —
centralizzato nel pacchetto npm **`@tassullo/theme`**,
che vive nel repo GitHub pubblico:

**https://github.com/tassullo/tassullo-design-system**

Il pacchetto contiene:
- `theme.css` — tutti i design token come variabili CSS: colori (brand, superfici,
  testo, sidebar, stati semantici success/danger/warn/info), tipografia, raggi,
  ombre, spaziatura. È la **fonte unica**: nessuna app deve averne una copia.
- `components.css` — le classi dei componenti ricorrenti (`.btn`, `.chip`,
  `.badge`, `.card`, `.input`, `.alert`, `.table`, `.sidebar`, `.skel`),
  costruite solo sui token. Si importa: **non si copia**. Fino alla v1.1.0
  queste ricette esistevano solo come testo nella style guide, e le app che le
  hanno ricopiate sono divergite — per questo ora sono un CSS vero.
- `stylelint-config.cjs` — la config che verifica in CI la regola "solo
  variabili": senza un controllo automatico la regola si perde in poche
  settimane.
- `styleguide.html` — style guide visiva: palette con i nomi delle variabili e
  demo dei componenti. Le demo **caricano i CSS veri del pacchetto**, quindi non
  possono divergere da ciò che usano le app. Aprirla nel browser.

Non esiste un registry npm: il pacchetto si installa direttamente dal repo git.

## Task di setup (fase iniziale del progetto, ~10 minuti)

1. Scaffold dell'app con **Vite + React + TypeScript** (stesso stack di SuperTM:
   le ricette della style guide valgono identiche).
2. Installare il tema **prima di scrivere la prima pagina**:
   ```bash
   npm install github:tassullo/tassullo-design-system
   ```
3. Nel CSS globale (`src/index.css`), come **prime righe** — prima i token,
   poi i componenti:
   ```css
   @import '@tassullo/theme/theme.css';
   @import '@tassullo/theme/components.css';
   ```
   seguite dal reset di base:
   ```css
   * { box-sizing: border-box; }
   body {
     margin: 0;
     font-family: var(--font-family);
     background: var(--color-page-bg);
     color: var(--color-text);
   }
   ```
4. Eliminare i CSS demo del template Vite (`App.css` e gli stili di esempio
   in `index.css`), che altrimenti inquinano lo stile.
5. Se l'app si usa **in campo** (schermo piccolo, guanti), nell'`index.html`:
   ```html
   <body data-density="touch">
   ```
   I bersagli passano a >=48px. Le app desktop dense non mettono l'attributo.
6. Attivare il lint dello stile, in `frontend/.stylelintrc.cjs`:
   ```js
   module.exports = {
     extends: '@tassullo/theme/stylelint-config',
     ignoreFiles: ['dist/**', 'node_modules/**'],
   }
   ```
   più uno script `lint:css` che lancia `stylelint` sui CSS di `src/`, e uno
   step che lo esegue nel job frontend del workflow di test. Unica dipendenza:
   `stylelint` (nessun plugin).
7. Verificare: la pagina vuota deve avere sfondo `#F6F6F4` e font di sistema.

## Regole da inserire nel CLAUDE.md della nuova app

Copiare queste righe tal quali — servono a mantenere l'aggancio nel tempo,
non solo al setup:

```markdown
## Stile e design system

- I design token (colori, tipografia, raggi, ombre, spaziatura) e le classi dei
  componenti vivono nel pacchetto condiviso `@tassullo/theme`
  (https://github.com/tassullo/tassullo-design-system).
- Nei CSS di pagine e componenti usare SOLO le variabili
  (`var(--color-accent)`, `var(--radius-lg)`, `var(--shadow-md)`, …):
  MAI hex, ombre o raggi hardcodati. E MAI fallback tipo
  `var(--color-accent, #d4892b)`: il token è sempre definito, e il fallback
  congela la palette vecchia.
- Nuovi token si aggiungono SOLO nel repo tassullo-design-system, mai qui.
- Per i componenti ricorrenti usare le classi di `components.css`
  (`.btn`, `.chip`, `.badge`, `.card`, `.input`, `.link`, `.alert`,
  `.table`, `.sidebar`, `.skel`): non riscriverle e non copiarle in un
  CSS di pagina.
- Il nome dice la funzione, non l'aspetto: `.badge` è un'etichetta che si
  legge, `.chip` è un filtro che si clicca. Chiamare "chip" o "pill" una
  targhetta statica è il modo più veloce per ritrovarsi a riscriverla —
  in Studio è successo 23 volte.
  Se serve una variante che il pacchetto non ha, costruirla SOPRA la classe
  condivisa, non al posto suo.
- `npm run lint:css` deve passare: è la regola qui sopra resa eseguibile.
- Per aggiornare il tema: `npm update @tassullo/theme` + commit del lockfile.
```

## Manutenzione ricorrente (voce di piano)

A ogni modifica di stile concordata:
1. si modifica `theme.css` nel repo `tassullo-design-system` (version bump + push);
2. in ogni app collegata: `npm update @tassullo/theme` e commit di `package-lock.json`.

Le app che rispettano la regola "solo variabili" si aggiornano senza toccare
altro codice.

## Se l'app avrà un'identità visiva diversa

Non toccare il pacchetto: dopo l'import, ridefinire solo i token brand in un
blocco locale dell'app:

```css
:root {
  --color-accent: /* nuovo colore */;
  --color-accent-hover: /* … */;
  --color-accent-light: /* … */;
  --color-accent-border: /* … */;
}
```

Superfici, tipografia e componenti restano coerenti con il resto delle app.

## Note tecniche

- Il repo è pubblico apposta: i CI (es. GitHub Actions che fanno `npm ci`)
  lo installano senza token. Non renderlo privato senza prima configurare
  un PAT nei CI di tutte le app collegate.
- Il lockfile aggancia la dipendenza a un commit preciso: le app non si
  aggiornano da sole a ogni push del tema, ma solo con `npm update`.

## Se l'app genera anche documenti Word (relazioni, perizie, report)

Lo stesso design system copre anche i documenti Word generati in Python con
`python-docx`, nella cartella `docx/` del repo (vedi `docx/README.md` per il
dettaglio completo). A differenza del tema CSS, **non è un pacchetto pip**:
se l'app builda/deploya con un vincolo tipo `pip install --only-binary :all:`
(niente wheel da sorgente — controllare il workflow di deploy dell'app),
un pacchetto installato da `git+https://...` romperebbe il deploy perché non
ha un wheel precompilato. La propagazione è quindi manuale, per copia di file:

1. Copia `docx/tassullo_report.py` nel repo dell'app (es. come
   `relazione_tassullo.py` nel root, o dove convenzionalmente vivono i moduli
   di export).
2. Copia `docx/templates/relazione_tassullo_base.docx` nella cartella
   template dell'app.
3. Genera un documento di prova e verifica i colori (nero `#141414` per il
   testo, sfondo tabella nero, filetto arancio `#F4AC3D` sotto i titoli §1):
   ```python
   import relazione_tassullo as RT
   doc = RT.documento_base_senza_cover()
   RT.aggiungi_titolo(doc, "1. Descrizione dell'intervento", livello=1)
   doc.save("prova.docx")
   ```

Se in futuro l'app costruisse le proprie wheel in CI (o si usasse un registry
privato), si potrebbe rivalutare un pacchetto pip installabile da git, come
già avviene per il tema CSS via npm.
