import { useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  Bookmark,
  Box,
  ChevronUp,
  CloudSun,
  Compass,
  Heart,
  Landmark,
  Layers,
  Map,
  MapPin,
  Minus,
  Mountain,
  Navigation,
  Plus,
  Route,
  Search,
  Star,
  Sun,
  TrainFront,
  Trees,
  User,
  Wind,
} from "lucide-react";
import CityScene from "./components/CityScene.jsx";
import { layerOptions, metrics, places, tabs, timeModes } from "./data/cityData.js";

const tabIds = tabs.map((tab) => tab.id);

const iconByLayer = {
  routes: Route,
  metro: TrainFront,
  parks: Trees,
  culture: Landmark,
};

const iconByMetric = {
  elevation: Mountain,
  air: Wind,
  pulse: Heart,
};

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function App() {
  const [activeTab, setActiveTab] = useState("skyline");
  const [cameraMode, setCameraMode] = useState("wide");
  const [layers, setLayers] = useState({
    routes: true,
    metro: true,
    parks: true,
    culture: true,
  });
  const [selectedPlace, setSelectedPlace] = useState("koktobe");
  const [sheetOpen, setSheetOpen] = useState(false);
  const [time, setTime] = useState("dawn");
  const [zoomOffset, setZoomOffset] = useState(0);
  const dragStart = useRef(null);

  const selected = places.find((place) => place.id === selectedPlace) ?? places[1];
  const activeCopy = tabs.find((tab) => tab.id === activeTab)?.copy ?? tabs[0].copy;
  const theme = timeModes[time];

  const shownPlaces = useMemo(() => {
    if (activeTab === "routes") return places.filter((place) => place.id !== "panfilov");
    if (activeTab === "culture") return places.filter((place) => place.id !== "medeu");
    return places.slice(0, 3);
  }, [activeTab]);

  useEffect(() => {
    document.documentElement.style.setProperty("--app-sky", theme.sky);
    document.documentElement.style.setProperty("--theme-accent", theme.accent);
  }, [theme]);

  function toggleLayer(id) {
    setLayers((current) => ({ ...current, [id]: !current[id] }));
  }

  function cycleTab(direction) {
    const index = tabIds.indexOf(activeTab);
    const next = (index + direction + tabIds.length) % tabIds.length;
    setActiveTab(tabIds[next]);
  }

  function handleSheetPointerDown(event) {
    dragStart.current = { y: event.clientY, open: sheetOpen };
    event.currentTarget.setPointerCapture?.(event.pointerId);
  }

  function handleSheetPointerUp(event) {
    if (!dragStart.current) return;
    const delta = event.clientY - dragStart.current.y;
    if (Math.abs(delta) > 34) {
      setSheetOpen(delta < 0);
    } else {
      setSheetOpen((open) => !open);
    }
    dragStart.current = null;
  }

  return (
    <main className={`app-shell is-${time}`} style={{ "--selected-accent": selected.accent }}>
      <section className="scene-stage" aria-label="Interactive 3D map of Almaty">
        <CityScene
          activeTab={activeTab}
          cameraMode={cameraMode}
          layers={layers}
          onSelectPlace={setSelectedPlace}
          selectedPlace={selectedPlace}
          time={time}
          zoomOffset={zoomOffset}
        />
      </section>

      <header className="top-bar">
        <div>
          <h1>Almaty Altitude</h1>
          <nav className="tab-row" aria-label="City views">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={activeTab === tab.id ? "is-active" : ""}
                onClick={() => setActiveTab(tab.id)}
                type="button"
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
        <button className="round-button search-button" aria-label="Search places" type="button">
          <Search size={22} />
        </button>
      </header>

      <aside className="left-tools" aria-label="Camera controls">
        <button className="tool-button compass-button" aria-label="Recenter camera" onClick={() => setCameraMode("wide")} type="button">
          <Compass size={23} />
          <span>N</span>
        </button>
        <button
          className="tool-button"
          aria-label="Switch camera tilt"
          onClick={() => setCameraMode((mode) => (mode === "wide" ? "near" : "wide"))}
          type="button"
        >
          <Navigation size={21} />
        </button>
        <div className="zoom-stack" aria-label="Zoom controls">
          <button aria-label="Zoom in" onClick={() => setZoomOffset((value) => clamp(value - 1.25, -3, 2.5))} type="button">
            <Plus size={20} />
          </button>
          <button aria-label="Zoom out" onClick={() => setZoomOffset((value) => clamp(value + 1.25, -3, 2.5))} type="button">
            <Minus size={20} />
          </button>
        </div>
      </aside>

      <aside className="layer-stack" aria-label="Map layers">
        {layerOptions.map((layer) => {
          const Icon = iconByLayer[layer.id];
          return (
            <button
              key={layer.id}
              aria-label={`Toggle ${layer.label}`}
              className={layers[layer.id] ? "is-on" : ""}
              onClick={() => toggleLayer(layer.id)}
              type="button"
            >
              <Icon size={18} />
              <span>{layer.label}</span>
            </button>
          );
        })}
      </aside>

      <section className="selected-callout" aria-live="polite">
        <MapPin size={18} />
        <div>
          <strong>{selected.name}</strong>
          <span>{selected.type}</span>
        </div>
        <ArrowUpRight size={18} />
      </section>

      <div className="time-switcher" role="group" aria-label="Time of day">
        {Object.entries(timeModes).map(([id, mode]) => {
          const Icon = id === "dawn" ? CloudSun : id === "day" ? Sun : Navigation;
          return (
            <button key={id} className={time === id ? "is-active" : ""} onClick={() => setTime(id)} type="button">
              <Icon size={20} />
              <span>{mode.label}</span>
            </button>
          );
        })}
      </div>

      <section className={`bottom-sheet ${sheetOpen ? "is-open" : ""}`}>
        <button
          className="sheet-handle"
          aria-label={sheetOpen ? "Collapse city panel" : "Expand city panel"}
          onPointerDown={handleSheetPointerDown}
          onPointerUp={handleSheetPointerUp}
          type="button"
        >
          <span />
          <ChevronUp size={22} />
        </button>

        <div className="sheet-scroll">
          <div className="sheet-heading">
            <div>
              <h2>Today in Almaty</h2>
              <p>{activeCopy}</p>
            </div>
            <button onClick={() => cycleTab(1)} type="button" aria-label="Next city view">
              <Layers size={20} />
            </button>
          </div>

          <div className="place-strip" aria-label="Featured places">
            {shownPlaces.map((place) => (
              <button
                key={place.id}
                aria-label={`Select ${place.name}`}
                className={`place-card ${selectedPlace === place.id ? "is-selected" : ""}`}
                onClick={() => setSelectedPlace(place.id)}
                style={{ "--place-accent": place.accent, "--place-image": `url(${place.image})` }}
                type="button"
              >
                <span className="place-icon">
                  {place.id === "medeu" ? <Mountain size={17} /> : place.id === "green-bazaar" ? <Landmark size={17} /> : <MapPin size={17} />}
                </span>
                <span className="place-text">
                  <strong>{place.name}</strong>
                  <small>
                    <ArrowUpRight size={13} />
                    {place.distance}
                  </small>
                </span>
                <Star className="star" size={17} />
              </button>
            ))}
          </div>

          <div className="metric-grid">
            {metrics.map((metric) => {
              const Icon = iconByMetric[metric.id];
              return (
                <article className="metric-card" key={metric.id}>
                  <div>
                    <Icon size={18} />
                    <span>{metric.label}</span>
                  </div>
                  <strong>
                    {metric.value}
                    <small>{metric.unit}</small>
                  </strong>
                  <p>{metric.detail}</p>
                  <i aria-hidden="true" />
                </article>
              );
            })}
          </div>
        </div>

        <nav className="dock" aria-label="Primary app navigation">
          <button className="is-active" type="button">
            <Navigation size={21} />
            <span>Explore</span>
          </button>
          <button type="button">
            <Map size={21} />
            <span>Map</span>
          </button>
          <button className="dock-primary" onClick={() => setCameraMode("near")} type="button">
            <Box size={25} />
            <span>Explore 3D</span>
          </button>
          <button type="button">
            <Bookmark size={21} />
            <span>Saved</span>
          </button>
          <button type="button">
            <User size={21} />
            <span>Profile</span>
          </button>
        </nav>
      </section>

      <aside className="desktop-rail" aria-label="Desktop city summary">
        <h2>Almaty Altitude</h2>
        <div className="rail-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={activeTab === tab.id ? "is-active" : ""}
              onClick={() => setActiveTab(tab.id)}
              type="button"
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="rail-places">
          {places.slice(0, 3).map((place) => (
            <button
              key={place.id}
              className={selectedPlace === place.id ? "is-selected" : ""}
              onClick={() => setSelectedPlace(place.id)}
              type="button"
            >
              <span style={{ background: place.accent }} />
              <strong>{place.name}</strong>
              <small>{place.distance}</small>
            </button>
          ))}
        </div>
        <div className="rail-metrics">
          {metrics.map((metric) => {
            const Icon = iconByMetric[metric.id];
            return (
              <article key={metric.id}>
                <Icon size={16} />
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
              </article>
            );
          })}
        </div>
        <button className="rail-action" onClick={() => setCameraMode("near")} type="button">
          <Activity size={18} />
          Explore 3D
        </button>
      </aside>
    </main>
  );
}

export default App;
