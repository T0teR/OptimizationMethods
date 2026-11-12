const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, ImageRun } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };

function cell(text, opts = {}) {
  const { bold = false, width = 1500, fill = null, align = AlignmentType.LEFT, fontSize = 18 } = opts;
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({ text: String(text), bold, size: fontSize, font: "Times New Roman" })]
    })]
  });
}
function p(text, opts = {}) {
  const { bold = false, italic = false, size = 24, center = false, spacing = 160, indent = 0 } = opts;
  return new Paragraph({
    alignment: center ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
    spacing: { after: spacing },
    indent: indent ? { firstLine: indent } : undefined,
    children: [new TextRun({ text, bold, italics: italic, size, font: "Times New Roman" })]
  });
}
function h(text, level = 1) {
  return new Paragraph({
    heading: level === 1 ? HeadingLevel.HEADING_1 : HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 160 },
    children: [new TextRun({ text, bold: true, size: level === 1 ? 28 : 26, font: "Times New Roman" })]
  });
}
function formula(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 100, after: 100 },
    children: [new TextRun({ text, italics: true, size: 22, font: "Times New Roman" })]
  });
}

const imgPath = "/home/workdir/artifacts/lab2/figures/network_flows.png";
let imgBuffer = null;
try { imgBuffer = fs.readFileSync(imgPath); } catch (e) {}

const children = [
  new Paragraph({ spacing: { after: 400 }, children: [] }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: [new TextRun({ text: "ЛАБОРАТОРНАЯ РАБОТА № 2", bold: true, size: 32, font: "Times New Roman" })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 400 },
    children: [new TextRun({ text: "по дисциплине «Методы оптимизации»", size: 26, font: "Times New Roman" })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 100 },
    children: [new TextRun({ text: "Тема: транзитная транспортная задача", size: 24, font: "Times New Roman" })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 600 },
    children: [new TextRun({ text: "с промежуточными складами (хабами). Вариант 2", size: 24, font: "Times New Roman" })]
  }),
  new Paragraph({
    alignment: AlignmentType.RIGHT, spacing: { after: 60 },
    children: [new TextRun({ text: "Выполнила: Лабузова Екатерина", size: 24, font: "Times New Roman" })]
  }),
  new Paragraph({
    alignment: AlignmentType.RIGHT, spacing: { after: 60 },
    children: [new TextRun({ text: "Группа: Б24-527", size: 24, font: "Times New Roman" })]
  }),
  new Paragraph({
    alignment: AlignmentType.RIGHT, spacing: { after: 400 },
    children: [new TextRun({ text: "Seed: 10213", size: 24, font: "Times New Roman" })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Москва, 2026", size: 24, font: "Times New Roman" })]
  }),
  new Paragraph({ spacing: { after: 400 }, children: [] }),

  h("1. Цель и содержание"),
  p("Цель — построить и решить сетевую LP-модель транзитных перевозок, проверить балансы независимо от солвера, провести сценарный анализ и интерпретировать двойственные оценки. Дополнительно выполнены два задания со звёздочкой: целочисленные потоки (LP vs MILP) и двойственная интерпретация с проверкой сильной двойственности.", { indent: 720 }),

  h("2. Индивидуализация и сеть"),
  p("Параметры: N = 13, Q = 2, Y = 26 → V = 2, seed = 10213. Вариант 2: транзитная транспортная задача, 3 источника, 2 хаба, 5 потребителей.", { indent: 720 }),
  p("Узлы: источники S1–S3 (предложение), хабы H1–H2 (чистый транзит: вход = выход), потребители C1–C5 (спрос). Дуги: все S→H, все H→C и несколько прямых S→C с более высокой стоимостью. На всех дугах заданы пропускные способности. Задача закрытая: сумма предложений равна сумме спросов.", { indent: 720 }),

  new Paragraph({
    spacing: { before: 160, after: 100 },
    children: [new TextRun({ text: "Таблица 1. Узлы (фрагмент после генерации)", bold: true, size: 20, font: "Times New Roman" })]
  }),
  new Table({
    width: { size: 7000, type: WidthType.DXA },
    columnWidths: [1500, 1800, 1800, 1800],
    rows: [
      new TableRow({ children: [
        cell("Узел", { bold: true, width: 1500, fill: "D9E2F3", align: AlignmentType.CENTER }),
        cell("Тип", { bold: true, width: 1800, fill: "D9E2F3", align: AlignmentType.CENTER }),
        cell("Supply", { bold: true, width: 1800, fill: "D9E2F3", align: AlignmentType.CENTER }),
        cell("Demand", { bold: true, width: 1800, fill: "D9E2F3", align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [cell("S1", { width: 1500 }), cell("source", { width: 1800 }), cell("40.97", { width: 1800, align: AlignmentType.CENTER }), cell("0", { width: 1800, align: AlignmentType.CENTER })] }),
      new TableRow({ children: [cell("S2", { width: 1500 }), cell("source", { width: 1800 }), cell("34.03", { width: 1800, align: AlignmentType.CENTER }), cell("0", { width: 1800, align: AlignmentType.CENTER })] }),
      new TableRow({ children: [cell("S3", { width: 1500 }), cell("source", { width: 1800 }), cell("28.52", { width: 1800, align: AlignmentType.CENTER }), cell("0", { width: 1800, align: AlignmentType.CENTER })] }),
      new TableRow({ children: [cell("H1/H2", { width: 1500 }), cell("hub", { width: 1800 }), cell("0", { width: 1800, align: AlignmentType.CENTER }), cell("0", { width: 1800, align: AlignmentType.CENTER })] }),
      new TableRow({ children: [cell("C1…C5", { width: 1500 }), cell("consumer", { width: 1800 }), cell("0", { width: 1800, align: AlignmentType.CENTER }), cell("сумма 103.52", { width: 1800, align: AlignmentType.CENTER })] }),
    ]
  }),

  h("3. Математическая модель"),
  p("Переменные: x_e ≥ 0 — поток по дуге e. Параметры: c_e — стоимость единицы потока, u_e — пропускная способность, a_i — предложение источника, b_j — спрос потребителя.", { indent: 720 }),
  formula("min Σ_e c_e x_e"),
  p("Ограничения:", { indent: 720 }),
  formula("Σ_{e: start(e)=s} x_e = a_s    (источники)"),
  formula("Σ_{e: end(e)=c} x_e = b_c    (потребители)"),
  formula("Σ_{e: end(e)=h} x_e − Σ_{e: start(e)=h} x_e = 0    (хабы)"),
  formula("0 ≤ x_e ≤ u_e"),
  p("Линейность следует из аддитивности стоимостей и балансов. Упрощающие допущения: постоянные тарифы и ёмкости, отсутствие задержек и неделимости груза в базовой модели, хабы без собственного спроса/предложения.", { indent: 720 }),

  h("4. Реализация и решение HiGHS"),
  p("Модель собрана в Python, решена scipy.optimize.linprog(method='highs'). Зависимости зафиксированы в requirements.txt. Статус базового запуска: Optimal. Лог сохранён в solver_log.txt.", { indent: 720 }),
  p("Минимальная стоимость: 709.236865. Основные потоки идут через хабы; прямые дорогие дуги в оптимуме не используются. Самая загруженная дуга: S1→H1 (≈40.97).", { indent: 720 }),

  h("5. Независимая проверка"),
  p("Для каждого узла отдельно пересчитаны вход и выход по найденному вектору потоков (NumPy, без объекта солвера). Для источников outflow = supply, для потребителей inflow = demand, для хабов inflow = outflow. Все балансы выполнены с допуском 1e-6. Пропускные способности не нарушены. Пересчёт целевой функции совпадает с результатом HiGHS.", { indent: 720 }),

  h("6. Визуализация сети"),
  p("Схема построена в NetworkX: зелёные — источники, оранжевые — хабы, синие — потребители. Толщина дуг пропорциональна потоку; подписи — величина потока.", { indent: 720 }),
];

if (imgBuffer) {
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 120 },
    children: [new ImageRun({ type: "png", data: imgBuffer, transformation: { width: 480, height: 300 }, altText: { title: "network", description: "flows", name: "net" } })]
  }));
}

children.push(
  h("7. Сценарный анализ"),
  p("Обязательные сценарии:", { indent: 720 }),
  new Table({
    width: { size: 8500, type: WidthType.DXA },
    columnWidths: [2800, 2000, 2200, 1500],
    rows: [
      new TableRow({ children: [
        cell("Сценарий", { bold: true, width: 2800, fill: "D9E2F3", align: AlignmentType.CENTER }),
        cell("Статус", { bold: true, width: 2000, fill: "D9E2F3", align: AlignmentType.CENTER }),
        cell("Стоимость", { bold: true, width: 2200, fill: "D9E2F3", align: AlignmentType.CENTER }),
        cell("Изм.", { bold: true, width: 1500, fill: "D9E2F3", align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("Базовый", { width: 2800 }), cell("Optimal", { width: 2000, align: AlignmentType.CENTER }),
        cell("709.24", { width: 2200, align: AlignmentType.CENTER }), cell("—", { width: 1500, align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("Отказ S1→H1", { width: 2800 }), cell("Optimal", { width: 2000, align: AlignmentType.CENTER }),
        cell("847.83", { width: 2200, align: AlignmentType.CENTER }), cell("+19.5%", { width: 1500, align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        cell("Спрос +20%", { width: 2800 }), cell("Infeasible", { width: 2000, align: AlignmentType.CENTER }),
        cell("—", { width: 2200, align: AlignmentType.CENTER }), cell("—", { width: 1500, align: AlignmentType.CENTER }),
      ]}),
    ]
  }),
  p("При отказе самой загруженной дуги поток перераспределяется на более дорогие маршруты, стоимость растёт примерно на 19.5%. При увеличении всех спросов на 20% при неизменных предложениях задача становится несовместной — суммарного supply не хватает.", { indent: 720 }),

  h("8. Жадная эвристика"),
  p("Эвристика: перечисляем все пути S→C (прямые и через один хаб), сортируем по стоимости пути, жадно насыщаем с учётом остатков supply/demand и остаточных ёмкостей. На данной сети жадный план совпал с оптимумом (зазор 0%). Это не гарантия для произвольной сети, но для текущих данных жадность оказалась достаточной.", { indent: 720 }),

  h("9. Узкие места и теневые цены"),
  p("Узкое место базового плана — дуга S1→H1 (почти полное использование относительно потока с S1). Теневые цены (маргиналы балансовых ограничений) интерпретируются как потенциалы узлов. Разница потенциалов связана с целесообразностью использования дуги. Прямая и двойственная цели совпадают с точностью порядка 1e-13, что подтверждает сильную двойственность.", { indent: 720 }),

  h("10. Задание со звёздочкой: целочисленные потоки"),
  p("Потоки и правые части округлены до целых; решена LP-релаксация и MILP (все переменные integer) через scipy.optimize.milp / HiGHS. На данной размерности оба решения совпали: стоимость 712.721, интегральный зазор 0%. Непрерывное решение после округления данных уже оказалось целочисленным, поэтому ветвление не потребовалось. На больших или более жёстких ёмкостях зазор может появиться.", { indent: 720 }),

  h("11. Задание со звёздочкой: двойственная интерпретация"),
  p("Выписаны потенциалы всех узлов. Для используемых дуг вида H→C приведённые стоимости обнуляются (условие дополняющей нежёсткости). Равенство cᵀx = bᵀπ выполнено численно. Экономический смысл: потенциал источника отражает «ценность» дополнительной единицы предложения в этом узле; потенциал потребителя — ценность удовлетворения дополнительного спроса.", { indent: 720 }),

  h("12. Практическая реализуемость"),
  p("Модель учебная: тарифы и ёмкости синтетические, нет окон времени, неделимости рейсов в базовой постановке (кроме задания со звёздочкой), нет отказов и стохастики. Для практики потребовались бы целочисленные рейсы, динамика и надёжность дуг. Тем не менее постановка корректно демонстрирует сетевое LP, балансы и чувствительность.", { indent: 720 }),

  h("13. Выводы"),
  p("Построена и решена транзитная транспортная LP-модель (3 источника, 2 хаба, 5 потребителей). HiGHS нашёл оптимум со стоимостью 709.24. Независимая проверка балансов и ёмкостей пройдена. Отказ ключевой дуги удорожает план на ~19.5%; рост спроса на 20% делает модель несовместной. Жадная эвристика на этих данных совпала с оптимумом. Выполнены два задания со звёздочкой: сравнение LP/MILP (зазор 0%) и двойственный анализ с проверкой сильной двойственности.", { indent: 720 }),
);

const doc = new Document({
  styles: {
    default: { document: { styles: [{ id: "Normal", run: { font: "Times New Roman", size: 24 } }] } },
  },
  sections: [{
    properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 850 } } },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "Лабораторная работа № 2 — Методы оптимизации", size: 18, italics: true, font: "Times New Roman", color: "666666" })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "— ", size: 20, font: "Times New Roman" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 20, font: "Times New Roman" }),
            new TextRun({ text: " —", size: 20, font: "Times New Roman" }),
          ]
        })]
      })
    },
    children,
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/home/workdir/artifacts/lab2/Лаба2_МО_отчёт.docx", buf);
  console.log("OK: Лаба2_МО_отчёт.docx");
}).catch(e => { console.error(e); process.exit(1); });
