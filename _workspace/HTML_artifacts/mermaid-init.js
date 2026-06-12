/* =====================================================================
   agentic-research · загрузчик Mermaid + тёплая тема.
   ---------------------------------------------------------------------
   В артефакте с диаграммой подключи ОДНОЙ строкой перед </body>:
       <script src="mermaid-init.js"></script>
   и пиши схему как:
       <pre class="mermaid">flowchart TD
         A[Заявка] --> B[Оплата]</pre>

   Тема (цвета, крупный шрифт, тёмный режим) живёт здесь — в файлах-ответах
   её настраивать не нужно. Масштаб «по ширине рамки» включён через
   useMaxWidth + .mermaid в styles.css.
   ===================================================================== */
import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs')
  .then(({ default: mermaid }) => {
    const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    const light = {
      background: '#fcfaf6',
      primaryColor: '#f1e3d8', primaryBorderColor: '#bd6a44', primaryTextColor: '#2c2823',
      secondaryColor: '#f3efe9', secondaryBorderColor: '#cdbfb2', secondaryTextColor: '#2c2823',
      tertiaryColor: '#faf6f0', tertiaryBorderColor: '#e4ded6',
      mainBkg: '#f1e3d8', nodeBorder: '#bd6a44', clusterBkg: '#f7f0ea', clusterBorder: '#e4ded6',
      lineColor: '#a4988a', textColor: '#2c2823', titleColor: '#2c2823', edgeLabelBackground: '#fcfaf6',
    };
    const darkv = {
      background: '#211f1c',
      primaryColor: '#34302a', primaryBorderColor: '#d99a6f', primaryTextColor: '#e9e4dc',
      secondaryColor: '#2a2723', secondaryBorderColor: '#4a443c', secondaryTextColor: '#e9e4dc',
      tertiaryColor: '#26231f', tertiaryBorderColor: '#3a352f',
      mainBkg: '#34302a', nodeBorder: '#d99a6f', clusterBkg: '#2a2723', clusterBorder: '#3a352f',
      lineColor: '#8a8175', textColor: '#e9e4dc', titleColor: '#e9e4dc', edgeLabelBackground: '#211f1c',
    };

    mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      themeVariables: Object.assign({
        fontFamily: 'ui-sans-serif, -apple-system, "SF Pro Text", system-ui, sans-serif',
        fontSize: '16px',
      }, dark ? darkv : light),
      flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis',
                   padding: 14, nodeSpacing: 40, rankSpacing: 50 },
      sequence: { useMaxWidth: true },
      gantt: { useMaxWidth: true },
      pie: { useMaxWidth: true },
    });

    mermaid.run();
  })
  .catch((e) => console.warn('Mermaid не загрузился (вероятно, офлайн):', e));
