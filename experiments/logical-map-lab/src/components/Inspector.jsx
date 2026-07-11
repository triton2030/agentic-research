import {
  ArrowDownLeft,
  ArrowUpRight,
  Brain,
  MessageSquareQuote
} from "lucide-react";
import { nodeTitle } from "../reading/model.js";

function SectionHeader({ title, icon: Icon }) {
  return (
    <h3>
      <Icon aria-hidden="true" size={16} />
      {title}
    </h3>
  );
}

function QuoteList({ quotes, title = "Цитаты из документов" }) {
  if (!quotes?.length) return null;

  return (
    <section className="detail-block quote-block">
      <SectionHeader title={title} icon={MessageSquareQuote} />
      <div className="quote-list">
        {quotes.map((quote) => (
          <figure key={`${quote.source}:${quote.text}`}>
            <blockquote>{quote.text}</blockquote>
            <figcaption>{quote.source}</figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

function CausalReader({ edgeTypes, incoming, nodes, onSelectEdge, outgoing, selectedEdgeId }) {
  if (incoming.length === 0 && outgoing.length === 0) return null;

  function renderEdgeLink(item, mode) {
    const relatedId = mode === "incoming" ? item.source : item.target;
    const relatedTitle = nodeTitle(nodes, relatedId);
    const type = edgeTypes[item.type] ?? edgeTypes.defines;
    const selected = item.id === selectedEdgeId;

    return (
      <button
        type="button"
        className={`reader-link ${selected ? "reader-link--selected" : ""}`}
        key={item.id}
        aria-pressed={selected}
        aria-label={`Открыть связь: ${item.label ?? type.label}`}
        onClick={() => onSelectEdge(item.id)}
        style={{ "--edge-color": type.color }}
      >
        <span>{mode === "incoming" ? "из" : "в"} {relatedTitle}</span>
        <strong>{item.label ?? type.label}</strong>
        {item.quotes?.[0] ? <small>{item.quotes[0].source}</small> : null}
      </button>
    );
  }

  return (
    <section className="detail-block reader-block">
      <SectionHeader title="Связи этой ноды" icon={MessageSquareQuote} />
      <div className="reader-columns">
        <div>
          <div className="reader-column-title">
            <ArrowDownLeft aria-hidden="true" size={15} />
            <span>Что ведёт сюда</span>
          </div>
          <div className="reader-link-list">
            {incoming.length > 0 ? incoming.map((item) => renderEdgeLink(item, "incoming")) : <em>Входящих причин нет</em>}
          </div>
        </div>
        <div>
          <div className="reader-column-title">
            <ArrowUpRight aria-hidden="true" size={15} />
            <span>Что из этого следует</span>
          </div>
          <div className="reader-link-list">
            {outgoing.length > 0 ? outgoing.map((item) => renderEdgeLink(item, "outgoing")) : <em>Исходящих следствий нет</em>}
          </div>
        </div>
      </div>
    </section>
  );
}

function EdgeDetail({ edge, edgeTypes, nodes }) {
  const type = edgeTypes[edge.type] ?? edgeTypes.defines;

  return (
    <aside className="inspector inspector--edge">
      <div className="inspector__kicker" style={{ color: type.color }}>
        Ребро · {type.label}
      </div>
      <div className="inspector__title-row">
        <h2>{edge.label ?? type.label}</h2>
      </div>
      <section className="detail-block detail-block--primary">
        <SectionHeader title="Куда ведёт связь" icon={MessageSquareQuote} />
        <div className="causal-link">
          <strong>
            {nodeTitle(nodes, edge.source)} {"->"} {nodeTitle(nodes, edge.target)}
          </strong>
          <p>{edge.why}</p>
        </div>
      </section>
      <QuoteList quotes={edge.quotes} title="Цитаты для этой связи" />
    </aside>
  );
}

export function Inspector({ edgeTypes, node, nodeTypes, nodes, edge, incoming, outgoing, onSelectEdge }) {
  if (edge && !node) {
    return <EdgeDetail edge={edge} edgeTypes={edgeTypes} nodes={nodes} />;
  }

  if (!node) {
    return (
      <aside className="inspector inspector--empty">
        <Brain aria-hidden="true" size={26} />
        <h2>Выберите ноду</h2>
        <p>Клик по ноде подсвечивает её окрестность, а чтение открывается здесь.</p>
      </aside>
    );
  }

  const type = nodeTypes[node.type] ?? nodeTypes.finding;

  return (
    <aside className="inspector">
      <div className="inspector__kicker" style={{ color: type.color }}>
        {type.label}
      </div>
      <div className="inspector__title-row">
        <h2>{node.title}</h2>
        <div className="confidence-pill" aria-label={`Уверенность ${Math.round(node.confidence * 100)} процентов`}>
          <span style={{ background: type.color }} />
          <strong>{Math.round(node.confidence * 100)}%</strong>
        </div>
      </div>
      <p className="inspector__summary">{node.summary}</p>
      <section className="detail-block detail-block--primary">
        <SectionHeader title="Что это за нода" icon={MessageSquareQuote} />
        <p>{node.explanation}</p>
      </section>
      <CausalReader
        edgeTypes={edgeTypes}
        incoming={incoming}
        nodes={nodes}
        onSelectEdge={onSelectEdge}
        outgoing={outgoing}
        selectedEdgeId={edge?.id}
      />
      {edge ? (
        <section className="detail-block detail-block--link">
          <SectionHeader title="Выбранное ребро" icon={MessageSquareQuote} />
          <div className="causal-link">
            <strong>
              {nodeTitle(nodes, edge.source)} {"->"} {nodeTitle(nodes, edge.target)}
            </strong>
            <span>{edge.label ?? edgeTypes[edge.type]?.label ?? edge.type}</span>
            <p>{edge.why}</p>
          </div>
          <QuoteList quotes={edge.quotes} title="Цитаты для этой связи" />
        </section>
      ) : null}
    </aside>
  );
}
