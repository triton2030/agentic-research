import { useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Banknote,
  Bell,
  Bike,
  Bookmark,
  Bus,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Coffee,
  ExternalLink,
  HeartPulse,
  Home,
  Hotel,
  Info,
  Landmark,
  Link as LinkIcon,
  Map,
  MapPin,
  Mountain,
  Navigation,
  Plane,
  Plus,
  Search,
  Shield,
  ShoppingBasket,
  SlidersHorizontal,
  Star,
  TrainFront,
  Utensils,
  WalletCards,
} from "lucide-react";
import {
  budgetProfiles,
  checklist,
  emergencyActions,
  foodSpots,
  itineraryDays,
  navItems,
  neighborhoods,
  plans,
  routes,
  sourceLinks,
} from "./data/cityData.js";

const iconMap = {
  dashboard: Home,
  routes: Navigation,
  neighborhoods: Map,
  food: Utensils,
  mobility: Bus,
  safety: Shield,
  budget: Banknote,
  planner: CalendarDays,
  sources: LinkIcon,
};

const tagIconMap = {
  mountain: Mountain,
  city: Landmark,
  food: Coffee,
  airport: Plane,
  mobility: TrainFront,
  safety: HeartPulse,
  budget: WalletCards,
};

const formatTenge = (value) => `${value.toLocaleString("en-US")} ₸`;

function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [saved, setSaved] = useState(["base-3-day", "koktobe-evening"]);
  const [selectedRoute, setSelectedRoute] = useState("base-3-day");
  const [budgetLevel, setBudgetLevel] = useState(1);
  const [checked, setChecked] = useState(() => new Set(["transport-card", "metro-hours"]));
  const [query, setQuery] = useState("");

  const selectedPlan = plans.find((plan) => plan.id === selectedRoute) ?? plans[0];
  const budget = budgetProfiles[budgetLevel];
  const filteredRoutes = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return routes;
    return routes.filter((route) =>
      [route.title, route.area, route.summary, route.bestFor].join(" ").toLowerCase().includes(normalized),
    );
  }, [query]);

  function toggleSaved(id) {
    setSaved((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  }

  function toggleChecked(id) {
    setChecked((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  const activeLabel = navItems.find((item) => item.id === activePage)?.label ?? "Dashboard";
  const ActiveIcon = iconMap[activePage] ?? Home;

  return (
    <main className="app-shell">
      <aside className="desktop-sidebar" aria-label="Primary navigation">
        <div className="brand-lockup">
          <span>AA</span>
          <div>
            <strong>Almaty Altitude</strong>
            <small>City operating guide</small>
          </div>
        </div>
        <nav>
          {navItems.map((item) => {
            const Icon = iconMap[item.id];
            return (
              <button
                key={item.id}
                className={activePage === item.id ? "is-active" : ""}
                onClick={() => setActivePage(item.id)}
                type="button"
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="sidebar-note">
          <Info size={17} />
          <span>Changing facts are routed to Sources instead of being treated as permanent.</span>
        </div>
      </aside>

      <section className="app-main">
        <header className="app-header">
          <div>
            <h1>Almaty Altitude</h1>
            <p>Your city command center.</p>
          </div>
          <div className="header-actions">
            <button className="icon-button" aria-label="Alerts" type="button">
              <Bell size={20} />
              <span />
            </button>
            <button className="icon-button" aria-label="Search" type="button">
              <Search size={20} />
            </button>
          </div>
        </header>

        <nav className="top-nav" aria-label="Pages">
          {navItems.map((item) => {
            const Icon = iconMap[item.id];
            return (
              <button
                key={item.id}
                className={activePage === item.id ? "is-active" : ""}
                onClick={() => setActivePage(item.id)}
                type="button"
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <section className="page-title">
          <div className="page-kicker">
            <ActiveIcon size={18} />
            <span>{activeLabel}</span>
          </div>
          <h2>{pageTitle(activePage)}</h2>
          <p>{pageIntro(activePage)}</p>
        </section>

        <PageContent
          activePage={activePage}
          budget={budget}
          budgetLevel={budgetLevel}
          checked={checked}
          filteredRoutes={filteredRoutes}
          query={query}
          saved={saved}
          selectedPlan={selectedPlan}
          selectedRoute={selectedRoute}
          setActivePage={setActivePage}
          setBudgetLevel={setBudgetLevel}
          setQuery={setQuery}
          setSelectedRoute={setSelectedRoute}
          toggleChecked={toggleChecked}
          toggleSaved={toggleSaved}
        />
      </section>

      <aside className="right-rail" aria-label="Trip summary">
        <RailSummary
          budget={budget}
          checked={checked}
          saved={saved}
          selectedPlan={selectedPlan}
          setActivePage={setActivePage}
        />
      </aside>

      <nav className="mobile-dock" aria-label="Mobile navigation">
        {["dashboard", "routes", "neighborhoods", "planner", "sources"].map((id) => {
          const item = navItems.find((nav) => nav.id === id);
          const Icon = iconMap[id];
          return (
            <button
              key={id}
              className={activePage === id ? "is-active" : ""}
              onClick={() => setActivePage(id)}
              type="button"
            >
              <Icon size={21} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </main>
  );
}

function pageTitle(page) {
  return {
    dashboard: "Plan a real day",
    routes: "Build routes that hold up",
    neighborhoods: "Choose the right base",
    food: "Eat by area, not by hype",
    mobility: "Move smart in the city",
    safety: "Know what to do fast",
    budget: "Estimate the day honestly",
    planner: "Turn ideas into an itinerary",
    sources: "Verify live info",
  }[page];
}

function pageIntro(page) {
  return {
    dashboard: "Start with ready plans, or build your own by area, pace, time, and cost.",
    routes: "Compare practical city days: mountain weather, metro reach, taxi legs, walking load, and backup moves.",
    neighborhoods: "Almaty changes by slope, traffic, and time of day. Pick the area that matches the job.",
    food: "Useful food stops grouped by market, Kazakh classics, coffee, late-night, and recovery meals.",
    mobility: "Airport, metro, buses, ride-hailing, walking and payment setup in one checklist.",
    safety: "Emergency contacts, medical fallback, and common travel risk reducers.",
    budget: "A plain per-day model for food, transport, activities, and buffer.",
    planner: "A three-day editable skeleton with saved cards and live-source reminders.",
    sources: "Links to primary or official sources for the facts that can change.",
  }[page];
}

function PageContent(props) {
  switch (props.activePage) {
    case "routes":
      return <RoutesPage {...props} />;
    case "neighborhoods":
      return <NeighborhoodsPage />;
    case "food":
      return <FoodPage />;
    case "mobility":
      return <MobilityPage checked={props.checked} toggleChecked={props.toggleChecked} />;
    case "safety":
      return <SafetyPage />;
    case "budget":
      return <BudgetPage budget={props.budget} budgetLevel={props.budgetLevel} setBudgetLevel={props.setBudgetLevel} />;
    case "planner":
      return <PlannerPage selectedPlan={props.selectedPlan} saved={props.saved} toggleSaved={props.toggleSaved} />;
    case "sources":
      return <SourcesPage />;
    default:
      return <DashboardPage {...props} />;
  }
}

function DashboardPage({
  budget,
  checked,
  saved,
  selectedPlan,
  setActivePage,
  setSelectedRoute,
  toggleChecked,
  toggleSaved,
}) {
  return (
    <div className="page-stack">
      <section className="panel">
        <SectionHeader title="Plan a real day" action="View all" onAction={() => setActivePage("routes")} />
        <div className="plan-strip">
          {plans.map((plan) => (
            <PlanCard
              key={plan.id}
              plan={plan}
              isSaved={saved.includes(plan.id)}
              isSelected={selectedPlan.id === plan.id}
              onSelect={() => setSelectedRoute(plan.id)}
              onSave={() => toggleSaved(plan.id)}
            />
          ))}
        </div>
        <button className="builder-row" onClick={() => setActivePage("planner")} type="button">
          <span className="builder-icon">
            <MapPin size={20} />
            <Plus size={14} />
          </span>
          <span>
            <strong>Build your own route</strong>
            <small>Add places, set pace, get time and cost</small>
          </span>
          <ArrowRight size={20} />
        </button>
      </section>

      <section className="section-grid two-col">
        <CompactList title="Neighborhoods" action="View all" onAction={() => setActivePage("neighborhoods")} items={neighborhoods.slice(0, 4)} />
        <CompactList title="Food & markets" action="View all" onAction={() => setActivePage("food")} items={foodSpots.slice(0, 4)} />
      </section>

      <section className="section-grid two-col align-start">
        <MobilityCard checked={checked} toggleChecked={toggleChecked} />
        <BudgetCard budget={budget} onOpen={() => setActivePage("budget")} />
      </section>

      <section className="panel">
        <SectionHeader title="Safety quick actions" action="See all" onAction={() => setActivePage("safety")} />
        <div className="emergency-grid">
          {emergencyActions.slice(0, 4).map((item) => (
            <EmergencyCard key={item.id} item={item} />
          ))}
        </div>
      </section>

      <SavedItinerary selectedPlan={selectedPlan} saved={saved} onOpen={() => setActivePage("planner")} />
    </div>
  );
}

function RoutesPage({ filteredRoutes, query, saved, selectedRoute, setQuery, setSelectedRoute, toggleSaved }) {
  return (
    <div className="page-stack">
      <section className="panel">
        <div className="filter-bar">
          <label>
            <Search size={18} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search mountain, market, airport..." />
          </label>
          <button type="button">
            <SlidersHorizontal size={18} />
            Filters
          </button>
        </div>
        <div className="route-list">
          {filteredRoutes.map((route) => (
            <RouteCard
              key={route.id}
              route={route}
              isSaved={saved.includes(route.id)}
              isSelected={selectedRoute === route.id}
              onSelect={() => setSelectedRoute(route.id)}
              onSave={() => toggleSaved(route.id)}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

function NeighborhoodsPage() {
  return (
    <div className="page-stack">
      <section className="card-grid">
        {neighborhoods.map((item) => (
          <InfoCard key={item.id} item={item} />
        ))}
      </section>
      <section className="panel">
        <SectionHeader title="How to choose" />
        <div className="decision-table">
          <DecisionRow label="First visit" value="Almaly or Panfilov Quarter" note="Best tradeoff: walking, food, metro, museums." />
          <DecisionRow label="Mountain priority" value="Medeu & Shymbulak side" note="Fewer city hops, faster morning starts." />
          <DecisionRow label="Business trip" value="Esentai or Dostyk corridor" note="Hotels, malls, restaurants, taxi access." />
          <DecisionRow label="Budget base" value="Metro-adjacent center" note="Avoid long taxi chains; verify night transport." />
        </div>
      </section>
    </div>
  );
}

function FoodPage() {
  return (
    <div className="page-stack">
      <section className="card-grid">
        {foodSpots.map((item) => (
          <InfoCard key={item.id} item={item} />
        ))}
      </section>
      <section className="panel">
        <SectionHeader title="Food logic" />
        <div className="timeline">
          <TimelineRow time="Morning" title="Coffee + light breakfast near base" copy="Keep the first taxi leg short; mountains punish late starts." />
          <TimelineRow time="Lunch" title="Kazakh classics or market food" copy="Use Green Bazaar/Arasan area when you are already in the core." />
          <TimelineRow time="Evening" title="View dinner or quiet recovery" copy="Kok-Tobe and Dostyk corridor work better after the city heat." />
        </div>
      </section>
    </div>
  );
}

function MobilityPage({ checked, toggleChecked }) {
  return (
    <div className="page-stack">
      <section className="section-grid two-col align-start">
        <MobilityCard checked={checked} toggleChecked={toggleChecked} full />
        <section className="panel map-panel">
          <SectionHeader title="City movement model" />
          <RouteDiagram />
        </section>
      </section>
      <section className="panel">
        <SectionHeader title="Airport to center" />
        <div className="decision-table">
          <DecisionRow label="Fastest simple path" value="Ride-hailing or official taxi" note="Best when arriving late or with luggage. Verify pickup zone at airport." />
          <DecisionRow label="Public transport" value="Check current airport bus routes" note="Use airport/live transport sources before relying on route numbers." />
          <DecisionRow label="Metro" value="Useful inside city core" note="Good for central hops; not a full airport solution." />
        </div>
      </section>
    </div>
  );
}

function SafetyPage() {
  return (
    <div className="page-stack">
      <section className="emergency-grid">
        {emergencyActions.map((item) => (
          <EmergencyCard key={item.id} item={item} />
        ))}
      </section>
      <section className="panel">
        <SectionHeader title="Practical safety checklist" />
        <div className="check-list">
          <StaticCheck title="Save hotel address in Russian/Kazakh and map app" status="Before arrival" />
          <StaticCheck title="Avoid mountain weather improvisation without checking forecast" status="Morning gate" />
          <StaticCheck title="Keep a taxi fallback after late dinners" status="Night movement" />
          <StaticCheck title="Use primary sources for emergency numbers and travel advisories" status="Verify live" />
        </div>
      </section>
    </div>
  );
}

function BudgetPage({ budget, budgetLevel, setBudgetLevel }) {
  return (
    <div className="page-stack">
      <section className="panel budget-panel">
        <SectionHeader title="Budget estimator" />
        <div className="budget-hero">
          <div>
            <span>{budget.label}</span>
            <strong>{formatTenge(budget.total)}</strong>
            <small>Per person / day estimate</small>
          </div>
          <input
            aria-label="Budget level"
            max="2"
            min="0"
            onChange={(event) => setBudgetLevel(Number(event.target.value))}
            type="range"
            value={budgetLevel}
          />
        </div>
        <div className="budget-breakdown">
          {budget.parts.map((part) => (
            <div key={part.label}>
              <span>{part.label}</span>
              <strong>{formatTenge(part.value)}</strong>
              <i style={{ "--bar": `${(part.value / budget.total) * 100}%`, "--bar-color": part.color }} />
            </div>
          ))}
        </div>
      </section>
      <section className="panel">
        <SectionHeader title="Budget caveats" />
        <div className="decision-table">
          <DecisionRow label="Do not trust exact prices" value="Use as planning range" note="Transport, restaurants, and attraction costs change." />
          <DecisionRow label="Hidden cost" value="Weather fallback" note="Mountain days often add taxi, gear, or changed-route costs." />
          <DecisionRow label="Best saving move" value="Base near metro/food" note="Cut taxi chains before cutting experience quality." />
        </div>
      </section>
    </div>
  );
}

function PlannerPage({ selectedPlan, saved, toggleSaved }) {
  return (
    <div className="page-stack">
      <section className="panel">
        <SectionHeader title="3-day base plan" action={saved.includes(selectedPlan.id) ? "Saved" : "Save"} onAction={() => toggleSaved(selectedPlan.id)} />
        <div className="planner-days">
          {itineraryDays.map((day) => (
            <article key={day.day} className="day-card">
              <div>
                <span>Day {day.day}</span>
                <strong>{day.title}</strong>
              </div>
              <ul>
                {day.steps.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>
      <SavedItinerary selectedPlan={selectedPlan} saved={saved} />
    </div>
  );
}

function SourcesPage() {
  return (
    <div className="page-stack">
      <section className="panel">
        <SectionHeader title="Verify live info" />
        <div className="source-list">
          {sourceLinks.map((source) => (
            <a key={source.url} href={source.url} rel="noreferrer" target="_blank">
              <span>
                <strong>{source.label}</strong>
                <small>{source.reason}</small>
              </span>
              <ExternalLink size={18} />
            </a>
          ))}
        </div>
      </section>
      <section className="panel caution-panel">
        <AlertTriangle size={22} />
        <div>
          <strong>Live facts are not hardcoded as truth</strong>
          <p>Airport routes, fares, opening hours, weather, and events can change. The app treats them as verification tasks.</p>
        </div>
      </section>
    </div>
  );
}

function SectionHeader({ action, onAction, title }) {
  return (
    <div className="section-header">
      <h3>{title}</h3>
      {action ? (
        <button onClick={onAction} type="button">
          {action}
          <ChevronRight size={16} />
        </button>
      ) : null}
    </div>
  );
}

function PlanCard({ isSaved, isSelected, onSave, onSelect, plan }) {
  const Icon = tagIconMap[plan.icon] ?? Mountain;
  return (
    <article className={`plan-card ${isSelected ? "is-selected" : ""}`} style={{ "--image": `url(${plan.image})` }}>
      <button className="card-hit" onClick={onSelect} type="button" aria-label={`Select ${plan.title}`} />
      <div className="card-top">
        <span>
          <Icon size={15} />
          {plan.badge}
        </span>
        <button className={isSaved ? "is-saved" : ""} onClick={onSave} type="button" aria-label={`Save ${plan.title}`}>
          <Bookmark size={17} />
        </button>
      </div>
      <div className="card-copy">
        <strong>{plan.title}</strong>
        <small>{plan.subtitle}</small>
        <em>{plan.duration} · {plan.pace}</em>
      </div>
    </article>
  );
}

function RouteCard({ isSaved, isSelected, onSave, onSelect, route }) {
  return (
    <article className={`route-card ${isSelected ? "is-selected" : ""}`}>
      <button className="route-main" onClick={onSelect} type="button">
        <span>{route.area}</span>
        <strong>{route.title}</strong>
        <small>{route.summary}</small>
        <RouteMeta route={route} />
      </button>
      <button className={isSaved ? "save-button is-saved" : "save-button"} onClick={onSave} type="button" aria-label={`Save ${route.title}`}>
        <Bookmark size={18} />
      </button>
    </article>
  );
}

function RouteMeta({ route }) {
  return (
    <div className="route-meta">
      <span><Clock3 size={14} />{route.time}</span>
      <span><Navigation size={14} />{route.walk}</span>
      <span><WalletCards size={14} />{route.cost}</span>
      <span><Star size={14} />{route.bestFor}</span>
    </div>
  );
}

function CompactList({ action, items, onAction, title }) {
  return (
    <section className="panel">
      <SectionHeader title={title} action={action} onAction={onAction} />
      <div className="compact-grid">
        {items.map((item) => (
          <InfoCard key={item.id} item={item} compact />
        ))}
      </div>
    </section>
  );
}

function InfoCard({ compact = false, item }) {
  const Icon = tagIconMap[item.icon] ?? MapPin;
  return (
    <article className={`info-card ${compact ? "is-compact" : ""}`} style={{ "--image": `url(${item.image})` }}>
      <div className="info-image">
        <span><Icon size={17} /></span>
      </div>
      <div className="info-copy">
        <strong>{item.title}</strong>
        <small>{item.meta}</small>
        {!compact ? <p>{item.copy}</p> : null}
      </div>
    </article>
  );
}

function MobilityCard({ checked, full = false, toggleChecked }) {
  return (
    <section className="panel">
      <SectionHeader title="Mobility quick check" />
      <div className={full ? "check-list is-full" : "check-list"}>
        {checklist.map((item) => (
          <button key={item.id} className={checked.has(item.id) ? "is-checked" : ""} onClick={() => toggleChecked(item.id)} type="button">
            <span className="check-icon">{item.icon}</span>
            <span>
              <strong>{item.title}</strong>
              <small>{item.detail}</small>
            </span>
            <CheckCircle2 size={18} />
          </button>
        ))}
      </div>
    </section>
  );
}

function BudgetCard({ budget, onOpen }) {
  return (
    <section className="panel budget-mini">
      <SectionHeader title="Budget estimator" action="Open" onAction={onOpen} />
      <div className="budget-mini-body">
        <strong>{formatTenge(budget.total)}</strong>
        <small>{budget.label} / day</small>
        <div className="donut" aria-hidden="true">
          {budget.parts.map((part, index) => (
            <span key={part.label} style={{ "--i": index, "--color": part.color }} />
          ))}
        </div>
      </div>
    </section>
  );
}

function EmergencyCard({ item }) {
  return (
    <article className="emergency-card">
      <span style={{ "--tone": item.color }}>{item.icon}</span>
      <strong>{item.number}</strong>
      <small>{item.label}</small>
    </article>
  );
}

function DecisionRow({ label, note, value }) {
  return (
    <div className="decision-row">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </div>
  );
}

function TimelineRow({ copy, time, title }) {
  return (
    <article className="timeline-row">
      <span>{time}</span>
      <div>
        <strong>{title}</strong>
        <p>{copy}</p>
      </div>
    </article>
  );
}

function StaticCheck({ status, title }) {
  return (
    <div className="static-check">
      <CheckCircle2 size={18} />
      <span>
        <strong>{title}</strong>
        <small>{status}</small>
      </span>
    </div>
  );
}

function RouteDiagram() {
  return (
    <div className="route-diagram" aria-label="Schematic Almaty route map">
      <span className="line metro" />
      <span className="line mountain" />
      <span className="line market" />
      <i style={{ left: "28%", top: "62%" }}>Abay</i>
      <i style={{ left: "45%", top: "45%" }}>Almaly</i>
      <i style={{ left: "63%", top: "28%" }}>Almaty-1</i>
      <b style={{ left: "22%", top: "68%" }} />
      <b style={{ left: "46%", top: "48%" }} />
      <b style={{ left: "66%", top: "31%" }} />
      <b style={{ left: "75%", top: "18%" }} />
    </div>
  );
}

function SavedItinerary({ onOpen, saved, selectedPlan }) {
  return (
    <section className="panel saved-card">
      <SectionHeader title="Your saved itinerary" action={onOpen ? "Open" : undefined} onAction={onOpen} />
      <article>
        <img alt="" src={selectedPlan.image} />
        <div>
          <strong>{selectedPlan.title}</strong>
          <small>{selectedPlan.duration} · {saved.length} saved cards</small>
          <RouteMeta route={{ time: "32 h", walk: "28.4 km", cost: "64,800 ₸", bestFor: "Balanced" }} />
        </div>
        <Bookmark size={20} />
      </article>
    </section>
  );
}

function RailSummary({ budget, checked, saved, selectedPlan, setActivePage }) {
  return (
    <div className="rail-stack">
      <section>
        <h2>Dashboard</h2>
        <p>Your city command center.</p>
      </section>
      <section className="rail-panel">
        <h3>Selected plan</h3>
        <InfoCard item={{ ...selectedPlan, title: selectedPlan.title, meta: `${selectedPlan.duration} · ${selectedPlan.pace}`, copy: selectedPlan.subtitle }} compact />
      </section>
      <section className="rail-panel">
        <h3>Mobility ready</h3>
        <div className="rail-meter">
          <i style={{ width: `${(checked.size / checklist.length) * 100}%` }} />
        </div>
        <p>{checked.size} of {checklist.length} setup checks done</p>
      </section>
      <section className="rail-panel">
        <h3>Budget</h3>
        <strong>{formatTenge(budget.total)}</strong>
        <p>{budget.label} per day estimate</p>
      </section>
      <section className="rail-panel">
        <h3>Saved</h3>
        <p>{saved.length} route cards saved</p>
        <button onClick={() => setActivePage("planner")} type="button">
          Open planner
          <ArrowRight size={16} />
        </button>
      </section>
      <section className="rail-panel">
        <h3>Verify live info</h3>
        {sourceLinks.slice(0, 4).map((source) => (
          <a key={source.url} href={source.url} rel="noreferrer" target="_blank">
            {source.label}
            <ExternalLink size={14} />
          </a>
        ))}
      </section>
    </div>
  );
}

export default App;
