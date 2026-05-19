import { card, edge } from "./_helpers";

// Смысловой граф, а не карта файлов. Поток специально сделан ацикличным:
// факторы сходятся в качество и экономику, а петля роста показана как итог.

export default {
  id: "mavo-analysis",
  title: "Почему MAVO сработает",
  description: "Один поток успеха: спрос, студии, стандарт заказа, доверие и экономика",
  nodes: [
    card({
      id: "success",
      kind: "output",
      weight: 3,
      title: "MAVO становится успешным",
      kicker: "итоговая гипотеза",
      body: "Платформа приводит реальные оплаченные заказы студиям, клиент получает понятный путь к красивому физическому товару, а MAVO зарабатывает на каждом подтверждённом заказе.",
      bullets: ["оплаченный заказ", "прибыль", "масштабирование"]
    }),
    card({
      id: "chatPain",
      kind: "origin",
      weight: 2,
      title: "Текущий способ заказа хаотичен",
      kicker: "боль рынка",
      body: "Сейчас заказ часто живёт в переписке: клиент объясняет, студия уточняет, дизайн подбирается вручную, цена и ожидания плавают.",
      bullets: ["медленно", "неясно", "не масштабируется"]
    }),
    card({
      id: "visualChoice",
      kind: "skill",
      weight: 3,
      title: "Выбор вместо объяснений",
      kicker: "клиентская ценность",
      body: "Клиент видит готовый дизайн на 3D-мокапе, выбирает, меняет 0-3 поля и отправляет заказ без длинного диалога.",
      bullets: ["выбрал", "настроил", "отправил"]
    }),
    card({
      id: "curatedCatalog",
      kind: "memory",
      weight: 3,
      title: "Курируемый каталог дизайнов",
      kicker: "главный актив",
      body: "Основная ценность MAVO — библиотека готовых SKU на мокапах. Чем шире и качественнее каталог, тем легче клиенту найти подходящий товар.",
      bullets: ["ассортимент", "качество", "готовые SKU"]
    }),
    card({
      id: "physicalMoat",
      kind: "truth",
      weight: 2,
      title: "Физический товар нельзя скачать",
      kicker: "защита от AI-замены",
      body: "Даже если картинку можно сгенерировать, кружку, футболку или печатное изделие всё равно нужно произвести локально.",
      bullets: ["физический продукт", "печать", "локальное исполнение"]
    }),
    card({
      id: "localContext",
      kind: "branch",
      weight: 2,
      title: "Локальный контекст повышает желание купить",
      kicker: "контентный множитель",
      body: "Город, язык, культурные поводы и сезонные темы делают глобальный каталог ощущаемым как местный.",
      bullets: ["город", "язык", "сезон"]
    }),
    card({
      id: "studioStorefront",
      kind: "output",
      weight: 3,
      title: "Витрина студии даёт первый канал",
      kicker: "go-to-market",
      body: "Студия ведёт свой существующий трафик в собственную витрину MAVO. Платформа получает заказы без необходимости сразу покупать весь спрос рекламой.",
      bullets: ["низкий CAC", "свой трафик", "первые заказы"]
    }),
    card({
      id: "studioValue",
      kind: "truth",
      weight: 3,
      title: "Студии получают понятную выгоду",
      kicker: "партнёрская мотивация",
      body: "MAVO приносит дизайн-слой, стандартизирует заявку и даёт канал продаж, а студия сохраняет контроль над оплатой, печатью и клиентом.",
      bullets: ["спрос", "меньше хаоса", "контроль"]
    }),
    card({
      id: "selfServe",
      kind: "skill",
      weight: 2,
      title: "Self-serve подключение расширяет supply",
      kicker: "масштаб студий",
      body: "Модель рассчитана на малые студии: вход не должен требовать долгого внедрения, сложной команды или локальной операционки MAVO.",
      bullets: ["малые студии", "быстрый вход", "плотное покрытие"]
    }),
    card({
      id: "notMerchant",
      kind: "gate",
      weight: 3,
      title: "MAVO не продавец товара",
      kicker: "юридическая масштабируемость",
      body: "Клиент платит студии напрямую. MAVO остаётся дизайн-платформой и каналом заказов, не берёт на себя кассу, возвраты и товарную ответственность.",
      bullets: ["не merchant", "меньше регуляторики", "глобальная модель"]
    }),
    card({
      id: "localExecution",
      kind: "gate",
      weight: 2,
      title: "Студия ведёт локальное исполнение",
      kicker: "операционная гибкость",
      body: "Оплата, печать, выдача, доставка и часть коммуникации остаются у производителя, который знает свой рынок и клиента.",
      bullets: ["оплата", "печать", "выдача"]
    }),
    card({
      id: "standardOrder",
      kind: "gate",
      weight: 3,
      title: "Стандартизированный заказ снижает риск",
      kicker: "операционный контур",
      body: "До отправки заказа MAVO задаёт структуру: выбранный SKU, поля персонализации, студия, цена и понятный статусный путь.",
      bullets: ["структура", "статусы", "меньше споров"]
    }),
    card({
      id: "snapshot",
      kind: "review",
      weight: 2,
      title: "Order Snapshot фиксирует договорённость",
      kicker: "доверие и учёт",
      body: "После принятия заказа появляется каноничная запись: что именно заказано, кто исполнитель, какие события уже произошли.",
      bullets: ["учёт", "споры", "прозрачность"]
    }),
    card({
      id: "trustControl",
      kind: "review",
      weight: 2,
      title: "Qualification и санкции защищают качество",
      kicker: "контроль партнёров",
      body: "MAVO не производит товар сам, но управляет допуском, сигналами качества, паузами, отключениями и реактивацией студий.",
      bullets: ["допуск", "сигналы", "санкции"]
    }),
    card({
      id: "economics",
      kind: "truth",
      weight: 3,
      title: "Экономика привязана к оплате",
      kicker: "unit-profit",
      body: "MAVO зарабатывает только после подтверждённой оплаты: комиссия на marketplace-заказах и Техсбор за инфраструктуру заказа.",
      bullets: ["Commission", "Техсбор", "после оплаты"]
    }),
    card({
      id: "lowRiskLaunch",
      kind: "branch",
      weight: 2,
      title: "Пилот можно запускать узко",
      kicker: "проверяемость",
      body: "Не нужно сразу строить весь marketplace: можно начать с витрин студий, ограниченного каталога и понятных событий заказа.",
      bullets: ["узкий MVP", "быстрая проверка", "меньше burn"]
    }),
    card({
      id: "flywheel",
      kind: "output",
      weight: 3,
      title: "Позитивная петля роста",
      kicker: "flywheel",
      body: "Больше студий и витрин дают больше заказов; больше заказов даёт данные спроса; данные улучшают каталог; каталог повышает конверсию.",
      bullets: ["студии", "заказы", "лучший каталог"]
    })
  ],
  edges: [
    edge("chatPain", "visualChoice", { label: "убирает переписку", kind: "bold" }),
    edge("physicalMoat", "curatedCatalog", { label: "защищает товар", kind: "solid" }),
    edge("localContext", "curatedCatalog", { label: "делает местным", kind: "solid" }),
    edge("curatedCatalog", "visualChoice", { label: "даёт выбор", kind: "bold" }),

    edge("visualChoice", "studioStorefront", { label: "понятно клиенту", kind: "bold" }),
    edge("selfServe", "studioStorefront", { label: "больше витрин", kind: "solid" }),
    edge("lowRiskLaunch", "studioStorefront", { label: "старт узко", kind: "dashed" }),
    edge("studioStorefront", "studioValue", { label: "приносит заказы", kind: "bold" }),

    edge("notMerchant", "localExecution", { label: "ответственность у студии", kind: "solid" }),
    edge("localExecution", "standardOrder", { label: "нужна форма", kind: "solid" }),
    edge("studioValue", "standardOrder", { label: "меньше хаоса", kind: "bold" }),

    edge("standardOrder", "snapshot", { label: "фиксирует заказ", kind: "solid" }),
    edge("snapshot", "trustControl", { label: "даёт сигналы", kind: "solid" }),
    edge("standardOrder", "economics", { label: "после оплаты", kind: "bold" }),

    edge("trustControl", "success", { label: "держит доверие", kind: "accent" }),
    edge("economics", "success", { label: "даёт прибыль", kind: "bold" }),
    edge("success", "flywheel", { label: "запускает рост", kind: "bold" })
  ]
};
