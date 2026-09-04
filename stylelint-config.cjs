/* ════════════════════════════════════════════════════════════════
   TASSULLO DESIGN SYSTEM — config stylelint condivisa (v1.2.0)

   Rende eseguibile la regola "nei CSS d'app solo variabili, mai
   valori hardcodati". Sta qui e non nei repo delle app perché
   anche l'anti-deriva deve essere ancorata alla fonte unica: si
   cambia in un posto solo e vale ovunque.

   Uso, in <app>/frontend/.stylelintrc.cjs:
     module.exports = {
       extends: '@tassullo/theme/stylelint-config',
       ignoreFiles: ['dist/**', 'node_modules/**'],
     }
   e in package.json uno script "lint:css" che lancia stylelint
   sui CSS di src/.

   Serve solo stylelint come devDependency: nessun plugin.
   ════════════════════════════════════════════════════════════════ */

module.exports = {
  rules: {
    /* Nessun colore esadecimale: esiste un token per ogni colore
       del brand. Se manca, si aggiunge a theme.css — non qui. */
    'color-no-hex': [
      true,
      {
        message:
          'Colore hardcodato: usa un token di @tassullo/theme (es. var(--color-accent)). Se il colore non esiste, aggiungilo a theme.css nel design system.',
      },
    ],

    /* Niente rgb()/hsl() al volo. Per il velo delle modali c'è
       var(--color-overlay); per le ombre var(--shadow-*). */
    'function-disallowed-list': [
      ['rgb', 'rgba', 'hsl', 'hsla'],
      {
        message:
          'Colore hardcodato: usa un token (var(--color-overlay) per i veli, var(--shadow-md) per le ombre).',
      },
    ],

    /* I fallback var(--x, #hex) congelano la palette vecchia: nel
       2026 in Studio c'erano 186 fallback che dicevano ancora
       l'arancio pre-v1.1.0, e uno diceva testo bianco dove il token
       vale nero. I token sono sempre definiti: il fallback non
       serve, e mente. */
    'declaration-property-value-disallowed-list': [
      { '/.*/': [/var\(\s*--[^,)]+\s*,/] },
      {
        message:
          'Fallback nel var(): scrivi var(--token) senza valore di riserva — il token è sempre definito da theme.css.',
      },
    ],
  },
}
