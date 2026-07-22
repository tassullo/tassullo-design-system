# Tassullo Design System

Fonte unica dello stile visivo delle app Tassullo: **`theme.css`** contiene tutti
i design token (colori, tipografia, raggi, ombre, spaziatura) come variabili CSS.
**`styleguide.html`** è la style guide visiva: palette click-to-copy e ricette CSS
dei componenti (bottoni, chip, badge, card, input, alert, sidebar, tabelle, skeleton).
Aprila nel browser per consultarla.

## Usarlo in un'app

```bash
npm install github:tassullo/tassullo-design-system
```

Nel CSS globale, come prima riga:

```css
@import '@tassullo/theme/theme.css';
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

- **Studio Tassullo (SuperTM)** — `frontend/` importa il tema da questo pacchetto.
