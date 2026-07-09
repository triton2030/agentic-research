const medeuImage = new URL("../../assets/places/medeu.jpg", import.meta.url).href;
const koktobeImage = new URL("../../assets/places/koktobe.jpg", import.meta.url).href;
const greenBazaarImage = new URL("../../assets/places/green-bazaar.jpg", import.meta.url).href;

export const places = [
  {
    id: "medeu",
    name: "Medeu",
    type: "Mountain rink",
    distance: "16 km",
    elevation: "1,691 m",
    signal: "+542 m",
    mood: "Ice valley",
    accent: "#9bd7ff",
    image: medeuImage,
    position: [-5.6, 1.35, -5.9],
    route: [
      [-0.4, 0.14, 2.6],
      [-1.6, 0.18, 0.8],
      [-3.1, 0.26, -1.6],
      [-4.5, 0.4, -3.9],
      [-5.6, 0.68, -5.9],
    ],
  },
  {
    id: "koktobe",
    name: "Kok-Tobe",
    type: "Hill park and tower",
    distance: "2.7 km",
    elevation: "1,100 m",
    signal: "+142 m",
    mood: "City balcony",
    accent: "#9cff3f",
    image: koktobeImage,
    position: [1.7, 1.08, -2.4],
    route: [
      [-2.8, 0.13, 2.1],
      [-1.3, 0.17, 1.4],
      [0.4, 0.24, 0.3],
      [1.8, 0.42, -1.2],
      [1.7, 0.72, -2.4],
    ],
  },
  {
    id: "green-bazaar",
    name: "Green Bazaar",
    type: "Market quarter",
    distance: "1.9 km",
    elevation: "760 m",
    signal: "+36 m",
    mood: "Food and rhythm",
    accent: "#ffcf69",
    image: greenBazaarImage,
    position: [-2.3, 0.58, 1.8],
    route: [
      [1.8, 0.13, 2.8],
      [0.7, 0.15, 2.5],
      [-0.8, 0.2, 2.2],
      [-2.3, 0.35, 1.8],
    ],
  },
  {
    id: "panfilov",
    name: "Panfilov Park",
    type: "Cultural garden",
    distance: "1.2 km",
    elevation: "810 m",
    signal: "+58 m",
    mood: "Quiet center",
    accent: "#70ffb5",
    image: greenBazaarImage,
    position: [0.2, 0.62, 1.3],
    route: [
      [-1.8, 0.13, 2.4],
      [-0.8, 0.19, 2.0],
      [0.2, 0.32, 1.3],
    ],
  },
];

export const tabs = [
  {
    id: "skyline",
    label: "Skyline",
    copy: "Tilt the city toward the mountains and read the skyline from Kok-Tobe to the foothills.",
  },
  {
    id: "routes",
    label: "Routes",
    copy: "Trace fast city moves: metro spine, green corridors, hill climbs, and walkable culture loops.",
  },
  {
    id: "culture",
    label: "Culture",
    copy: "Open market heat, old parks, tower views, and mountain rituals as one living map.",
  },
];

export const layerOptions = [
  { id: "routes", label: "Routes" },
  { id: "metro", label: "Metro" },
  { id: "parks", label: "Parks" },
  { id: "culture", label: "Culture" },
];

export const metrics = [
  {
    id: "elevation",
    label: "Elevation",
    value: "727",
    unit: "m",
    detail: "City floor",
  },
  {
    id: "air",
    label: "Air",
    value: "Foothill",
    unit: "flow",
    detail: "Mountain corridor",
  },
  {
    id: "pulse",
    label: "Pulse",
    value: "Evening",
    unit: "bright",
    detail: "City lights rising",
  },
];

export const timeModes = {
  dawn: {
    label: "Dawn",
    sky: "linear-gradient(180deg, #06111d 0%, #0f2940 40%, #183c44 72%, #071014 100%)",
    sceneBg: "#07131e",
    ground: "#0b241f",
    road: "#ffd488",
    metro: "#dff46a",
    park: "#59f08f",
    water: "#59c8ff",
    city: "#1d3440",
    cityLit: "#ffe09d",
    text: "#f6fbff",
    accent: "#9cff3f",
    fog: "#0c1a24",
    sun: "#ffc477",
  },
  day: {
    label: "Day",
    sky: "linear-gradient(180deg, #8ec8e8 0%, #c7edf3 36%, #7bbf9d 72%, #213b34 100%)",
    sceneBg: "#9fd5ec",
    ground: "#244c3e",
    road: "#fff2bb",
    metro: "#2a8cff",
    park: "#42dc78",
    water: "#2ab7ff",
    city: "#6b8791",
    cityLit: "#ffffff",
    text: "#f9fcff",
    accent: "#1dff78",
    fog: "#9fd5ec",
    sun: "#fff4ba",
  },
  night: {
    label: "Night",
    sky: "linear-gradient(180deg, #04101b 0%, #0a1d31 45%, #0b2722 72%, #02080a 100%)",
    sceneBg: "#06101a",
    ground: "#0a241f",
    road: "#ffb957",
    metro: "#9cff3f",
    park: "#24d96f",
    water: "#4ed1ff",
    city: "#24323c",
    cityLit: "#ffc865",
    text: "#f6fbff",
    accent: "#9cff3f",
    fog: "#02070d",
    sun: "#9ad7ff",
  },
};
