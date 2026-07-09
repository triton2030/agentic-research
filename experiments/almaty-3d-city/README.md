# Almaty 3D City

Mobile-first interactive 3D web app about Almaty. This is a standalone
experiment under `agentic-research/experiments`, not part of the root project
canon.

## What It Tests

- A full-bleed Three.js city scene instead of a static tourism landing page.
- Local interactive state: time of day, selected place, layer toggles, route
  focus, sheet size, and camera tilt.
- Responsive mobile app shell with a desktop rail continuation.
- Public static deployment through Vercel.

## Run

```bash
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5194/
```

## Build

```bash
npm run build
```

## Design Reference

`assets/concept-almaty-altitude.png` is the generated visual reference used to
derive the design system. It is not shipped as pasted UI.
