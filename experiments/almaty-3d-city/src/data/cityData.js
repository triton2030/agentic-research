const medeuImage = new URL("../../assets/places/medeu.jpg", import.meta.url).href;
const koktobeImage = new URL("../../assets/places/koktobe.jpg", import.meta.url).href;
const greenBazaarImage = new URL("../../assets/places/green-bazaar.jpg", import.meta.url).href;

export const lastReviewed = "2026-07-09";

export const navItems = [
  { id: "dashboard", label: "Dashboard" },
  { id: "routes", label: "Routes" },
  { id: "neighborhoods", label: "Neighborhoods" },
  { id: "food", label: "Food" },
  { id: "mobility", label: "Mobility" },
  { id: "safety", label: "Safety" },
  { id: "budget", label: "Budget" },
  { id: "planner", label: "Planner" },
  { id: "sources", label: "Sources" },
];

export const plans = [
  {
    id: "base-3-day",
    title: "3-day base plan",
    subtitle: "First time in Almaty",
    duration: "3 days",
    pace: "Balanced",
    badge: "3 days",
    icon: "mountain",
    image: medeuImage,
  },
  {
    id: "mountain-day",
    title: "Mountain day",
    subtitle: "Medeu, Shymbulak, Big Almaty Lake alternative",
    duration: "1 day",
    pace: "Active",
    badge: "Hiking",
    icon: "mountain",
    image: medeuImage,
  },
  {
    id: "city-core",
    title: "City core",
    subtitle: "Panfilov, Arbat, Green Bazaar, cafes",
    duration: "1 day",
    pace: "Easy",
    badge: "City",
    icon: "city",
    image: greenBazaarImage,
  },
  {
    id: "koktobe-evening",
    title: "Kok-Tobe evening",
    subtitle: "Hill view after central Almaty",
    duration: "3-5 h",
    pace: "Light",
    badge: "View",
    icon: "city",
    image: koktobeImage,
  },
];

export const routes = [
  {
    id: "base-3-day",
    title: "3-day base plan",
    area: "City + mountains",
    summary: "Use the first day for the city core, second for mountains, third for museums, parks, and food.",
    time: "3 days",
    walk: "24-32 km",
    cost: "Mid",
    bestFor: "First visit",
  },
  {
    id: "mountain-day",
    title: "Mountain day",
    area: "Medeu / Shymbulak",
    summary: "Start early, keep weather as the gate, and leave a city fallback if the mountain closes in.",
    time: "7-10 h",
    walk: "8-16 km",
    cost: "Mid+",
    bestFor: "Clear morning",
  },
  {
    id: "city-core",
    title: "City core",
    area: "Almaly / Panfilov",
    summary: "A low-risk central route: parks, market, cafes, museums, and easy taxi or metro exits.",
    time: "5-8 h",
    walk: "7-11 km",
    cost: "Low-mid",
    bestFor: "Arrival day",
  },
  {
    id: "airport-center",
    title: "Airport to center",
    area: "Airport / Almaly",
    summary: "Choose between ride-hailing and public transport after checking airport pickup and current routes.",
    time: "45-90 m",
    walk: "Low",
    cost: "Verify",
    bestFor: "Arrival",
  },
  {
    id: "market-food-loop",
    title: "Market food loop",
    area: "Green Bazaar / Arasan",
    summary: "Bundle food, bathhouse area, parks, and central cafes without crossing the city twice.",
    time: "4-6 h",
    walk: "5-8 km",
    cost: "Low-mid",
    bestFor: "Food day",
  },
];

export const neighborhoods = [
  {
    id: "medeu-shymbulak",
    title: "Medeu & Shymbulak",
    meta: "Mountains · Nature",
    copy: "Best for mountain-first trips. Tradeoff: fewer late-night city options and more weather dependency.",
    icon: "mountain",
    image: medeuImage,
  },
  {
    id: "almaly",
    title: "Almaly",
    meta: "City · Central",
    copy: "Good first base: metro, parks, food, museums, and shorter hops to the classic city core.",
    icon: "city",
    image: koktobeImage,
  },
  {
    id: "panfilov",
    title: "Panfilov Quarter",
    meta: "Culture · History",
    copy: "Good for slow walking, architecture, market access, and museum-heavy days.",
    icon: "city",
    image: greenBazaarImage,
  },
  {
    id: "esentai",
    title: "Esentai / Dostyk",
    meta: "Modern · Shopping",
    copy: "Better for business trips, hotels, restaurants, and taxi-based movement.",
    icon: "budget",
    image: koktobeImage,
  },
  {
    id: "abay-metro",
    title: "Metro corridor",
    meta: "Transport · Budget",
    copy: "Useful if the trip depends on predictable central movement and fewer taxi chains.",
    icon: "mobility",
    image: greenBazaarImage,
  },
  {
    id: "koktobe",
    title: "Kok-Tobe side",
    meta: "Views · Evening",
    copy: "A strong evening layer, especially after a central day when the skyline becomes the reward.",
    icon: "city",
    image: koktobeImage,
  },
];

export const foodSpots = [
  {
    id: "green-bazaar",
    title: "Green Bazaar",
    meta: "Market · Local",
    copy: "Use as a food-and-walking anchor in the city core. Verify hours before planning around it.",
    icon: "food",
    image: greenBazaarImage,
  },
  {
    id: "arasan",
    title: "Arasan area",
    meta: "Kazakh · Traditional",
    copy: "Pair with central walking and a slower meal; good after museum or park time.",
    icon: "food",
    image: greenBazaarImage,
  },
  {
    id: "coffee-boom",
    title: "Coffee base",
    meta: "Cafe · Recovery",
    copy: "Use a reliable cafe stop to reset between mountain and city legs.",
    icon: "food",
    image: koktobeImage,
  },
  {
    id: "lagman",
    title: "Lagman / noodles",
    meta: "Central · Filling",
    copy: "Good after a long walk. Keep it near your next transport leg, not across town.",
    icon: "food",
    image: greenBazaarImage,
  },
  {
    id: "view-dinner",
    title: "View dinner",
    meta: "Kok-Tobe · Evening",
    copy: "Worth it when sunset and transport align; keep a ride-hailing fallback.",
    icon: "city",
    image: koktobeImage,
  },
  {
    id: "breakfast",
    title: "Early breakfast",
    meta: "Before mountains",
    copy: "Do not let breakfast steal the mountain weather window. Keep it close to your base.",
    icon: "food",
    image: medeuImage,
  },
];

export const checklist = [
  {
    id: "transport-card",
    title: "Get a transport card",
    detail: "ONAY card or current payment option",
    icon: "💳",
  },
  {
    id: "ride-hailing",
    title: "Install ride-hailing",
    detail: "Useful for airport, late routes, and mountain fallback",
    icon: "🚕",
  },
  {
    id: "metro-hours",
    title: "Check metro hours",
    detail: "Verify current operating hours before relying on a late leg",
    icon: "Ⓜ",
  },
  {
    id: "airport-route",
    title: "Verify airport route",
    detail: "Airport transport and pickup zones can change",
    icon: "✈",
  },
  {
    id: "offline-map",
    title: "Save offline map",
    detail: "Mountain and arrival days deserve a fallback map",
    icon: "🗺",
  },
];

export const emergencyActions = [
  { id: "emergency", number: "112", label: "Emergency", icon: "☎", color: "#ff5a4f" },
  { id: "police", number: "102", label: "Police", icon: "🛡", color: "#5ba8ff" },
  { id: "ambulance", number: "103", label: "Ambulance", icon: "✚", color: "#ffb23f" },
  { id: "fire", number: "101", label: "Fire service", icon: "🔥", color: "#ff784d" },
  { id: "gas", number: "104", label: "Gas emergency", icon: "⚠", color: "#9cff3f" },
];

export const budgetProfiles = [
  {
    label: "Backpacker",
    total: 10000,
    parts: [
      { label: "Food", value: 4200, color: "#9cff3f" },
      { label: "Transport", value: 1800, color: "#5bc8ff" },
      { label: "Activities", value: 2500, color: "#ffbf5b" },
      { label: "Buffer", value: 1500, color: "#a8b4c0" },
    ],
  },
  {
    label: "Mid-range",
    total: 21500,
    parts: [
      { label: "Food", value: 8500, color: "#9cff3f" },
      { label: "Transport", value: 4500, color: "#5bc8ff" },
      { label: "Activities", value: 5600, color: "#ffbf5b" },
      { label: "Buffer", value: 2900, color: "#a8b4c0" },
    ],
  },
  {
    label: "Comfort",
    total: 42000,
    parts: [
      { label: "Food", value: 16000, color: "#9cff3f" },
      { label: "Transport", value: 9000, color: "#5bc8ff" },
      { label: "Activities", value: 11500, color: "#ffbf5b" },
      { label: "Buffer", value: 5500, color: "#a8b4c0" },
    ],
  },
];

export const itineraryDays = [
  {
    day: 1,
    title: "City core",
    steps: ["Base near Almaly", "Panfilov / central parks", "Green Bazaar food stop", "Kok-Tobe if weather stays clear"],
  },
  {
    day: 2,
    title: "Mountain day",
    steps: ["Early breakfast", "Medeu / Shymbulak", "Weather gate before lunch", "Quiet dinner near base"],
  },
  {
    day: 3,
    title: "Culture + buffer",
    steps: ["Museum or market revisit", "Cafe work/rest block", "Shopping or bathhouse area", "Airport route verification"],
  },
];

export const sourceLinks = [
  {
    label: "Visit Almaty",
    reason: "Official city travel information and attraction context",
    url: "https://visitalmaty.kz/",
  },
  {
    label: "Almaty Airport",
    reason: "Airport transport, pickup, and passenger updates",
    url: "https://alaport.com/en-EN/",
  },
  {
    label: "Almaty Metro",
    reason: "Stations, schedule, operating notices, and metro context",
    url: "https://metroalmaty.kz/",
  },
  {
    label: "ONAY",
    reason: "Public transport card/payment information",
    url: "https://onay.kz/",
  },
  {
    label: "eGov Kazakhstan emergency numbers",
    reason: "Primary reference for emergency numbers",
    url: "https://egov.kz/",
  },
  {
    label: "2GIS Almaty",
    reason: "Local map, business hours, and route checks",
    url: "https://2gis.kz/almaty",
  },
  {
    label: "Yandex Go Kazakhstan",
    reason: "Ride-hailing availability and pickup flow",
    url: "https://go.yandex/",
  },
];
