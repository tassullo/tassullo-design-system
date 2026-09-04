# Tassullo Design System

Fonte unica dello stile visivo delle app Tassullo, su due medium:

- **Web** — due CSS installabili via npm:
  - `theme.css`: i design token (colori, tipografia, raggi, ombre, spaziatura)
    come variabili CSS;
  - `components.css`: le ricette dei componenti ricorrenti (bottoni, chip,
    badge, card, input, alert, sidebar, tabelle, skeleton), costruite solo sui
    token.

  `styleguide.html` è la style guide visiva: palette click-to-copy e demo dei
  componenti. **Le demo caricano i due CSS veri del pacchetto**, quindi mostrano
  esattamente ciò che le app importano e non possono divergere. Aprila nel
  browser per consultarla.
- **Lint** — `stylelint-config.cjs`: la config condivisa che verifica in CI la
  regola "solo variabili, mai valori hardcodati".
- **Documenti Word** — cartella `docx/`: modulo `python-docx` + template per
  generare relazioni tecniche nello stesso brand. Vedi `docx/README.md`
  (propagazione manuale, non pip — spiegato lì il perché).

## Usarlo in un'app (stile web)

```bash
npm install github:tassullo/tassullo-design-system
```

Nel CSS globale, come prime righe — prima i token, poi i componenti:

```css
@import '@tassullo/theme/theme.css';
@import '@tassullo/theme/components.css';
```

Reset di base consigliato:

```css
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--font-family);
  background: var(--color-page-bg);
  color: var(--color-text);
}
```

Da lì in poi, nei CSS dell'app si usano **solo le variabili** (`var(--color-accent)`,
`var(--radius-lg)`, `var(--shadow-md)`, …) — mai valori hardcodati.

### Densità

Le ricette sono in taglia desktop compatta. Un'app usata in campo (schermo
piccolo, guanti) attiva i bersagli da 48px con un attributo nell'`index.html`:

```html
<body data-density="touch">
```

Non serve altro: `components.css` contiene entrambe le densità.

### Tenere la regola nel tempo

La regola "solo variabili" si verifica in CI con la config condivisa. In
`frontend/.stylelintrc.cjs`:

```js
module.exports = {
  extends: '@tassullo/theme/stylelint-config',
  ignoreFiles: ['dist/**', 'node_modules/**'],
}
```

più uno script `lint:css` che lancia `stylelint` sui CSS di `src/`, e uno step
che lo esegue nel workflow di test. Serve solo `stylelint` come devDependency:
nessun plugin.

## Aggiornare lo stile (propagazione)

1. Modifica `theme.css` in questo repo (e la style guide se serve).
2. Alza la `version` in `package.json` e committa/pusha.
3. In ogni app: `npm update @tassullo/theme` (il lockfile si aggancia al nuovo commit).

Le app che usano solo le variabili si aggiornano senza toccare altro codice.

## Ribrandizzare un'app mantenendo l'impianto

Dopo l'import del tema, ridefinisci solo i token brand nell'app:

```css
:root {
  --color-accent: /* nuovo colore */;
  --color-accent-hover: /* … */;
}
```

Tutto il resto (superfici, tipografia, componenti) segue automaticamente.

## App collegate

- **Studio Tassullo (SuperTM)** — github.com/tassullo/studio, `frontend/`.
- **Officina** — github.com/tassullo/officina, `frontend/`. Usa
  `data-density="touch"`: è l'app di campo.
