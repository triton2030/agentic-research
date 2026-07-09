import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Float, Html, Line, OrbitControls, Sparkles } from "@react-three/drei";
import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { places, timeModes } from "../data/cityData.js";

const routeColors = {
  routes: "#9cff3f",
  metro: "#6fe3ff",
  parks: "#42ef78",
  culture: "#ffc865",
};

function CameraController({ selectedPlace, cameraMode, zoomOffset }) {
  const controlsRef = useRef(null);
  const { camera } = useThree();

  useEffect(() => {
    const place = places.find((item) => item.id === selectedPlace) ?? places[1];
    const near = cameraMode === "near";
    const target = new THREE.Vector3(place.position[0] * 0.24, 0.45, place.position[2] * 0.22);
    const cameraPosition = near
      ? new THREE.Vector3(5.4 + zoomOffset, 4.6, 6.4 + zoomOffset)
      : new THREE.Vector3(7.2 + zoomOffset, 6.4, 9.4 + zoomOffset);

    camera.position.copy(cameraPosition);
    camera.lookAt(target);

    if (controlsRef.current) {
      controlsRef.current.target.copy(target);
      controlsRef.current.update();
    }
  }, [camera, cameraMode, selectedPlace, zoomOffset]);

  return (
    <OrbitControls
      ref={controlsRef}
      enablePan={false}
      enableDamping
      dampingFactor={0.08}
      minDistance={4.2}
      maxDistance={13}
      minPolarAngle={0.42}
      maxPolarAngle={1.25}
      rotateSpeed={0.46}
      zoomSpeed={0.55}
    />
  );
}

function Terrain({ theme }) {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[22, 17, 1, 1]} />
        <meshStandardMaterial color={theme.ground} roughness={0.92} metalness={0.05} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.012, 0]} receiveShadow>
        <ringGeometry args={[1.8, 8.9, 96]} />
        <meshBasicMaterial color="#ffffff" transparent opacity={0.018} />
      </mesh>
    </group>
  );
}

function MountainRange({ theme }) {
  const peaks = [
    [-8.4, -8.4, 3.8, 2.6],
    [-6.1, -8.8, 5.2, 3.4],
    [-3.7, -9.1, 4.3, 2.8],
    [-1.1, -9.2, 6.2, 4.3],
    [1.8, -9.0, 4.8, 3.2],
    [4.3, -8.7, 5.8, 3.8],
    [7.1, -8.5, 4.1, 2.7],
  ];

  return (
    <group position={[0, 0, -0.3]}>
      {peaks.map(([x, z, height, radius], index) => (
        <group key={`${x}-${z}`} position={[x, height / 2 - 0.18, z]}>
          <mesh castShadow>
            <coneGeometry args={[radius, height, 5, 1]} />
            <meshStandardMaterial color={index % 2 ? "#162c3a" : "#102533"} roughness={0.88} />
          </mesh>
          <mesh position={[0, height * 0.29, 0]} castShadow>
            <coneGeometry args={[radius * 0.35, height * 0.34, 5, 1]} />
            <meshStandardMaterial color="#d7eefb" roughness={0.64} metalness={0.02} />
          </mesh>
        </group>
      ))}
      <Line
        points={[
          [-9.4, 0.06, -6.2],
          [-6.2, 0.18, -5.7],
          [-3.4, 0.1, -6.0],
          [-0.2, 0.22, -5.5],
          [2.8, 0.12, -5.8],
          [7.8, 0.18, -6.1],
        ]}
        color="#5e7f8b"
        lineWidth={1.2}
        transparent
        opacity={0.55}
      />
    </group>
  );
}

function buildBlocks() {
  const blocks = [];
  for (let x = -7; x <= 7; x += 0.85) {
    for (let z = -2.2; z <= 5.5; z += 0.75) {
      const riverGap = Math.abs(x + z * 0.34 + 0.8) < 0.48;
      const parkGap = z < 0.3 && x > 1.2 && x < 4.4;
      const skip = riverGap || parkGap || (x + z) % 4.1 < 0.18;
      if (skip) continue;

      const hash = Math.sin(x * 13.11 + z * 9.37) * 10000;
      const normalized = hash - Math.floor(hash);
      const height = 0.16 + normalized * 0.82 + (z > 3 ? 0.22 : 0);
      const lit = normalized > 0.72;
      blocks.push({ x, z, height, lit });
    }
  }
  return blocks;
}

function CityBlocks({ theme }) {
  const meshRef = useRef(null);
  const blocks = useMemo(buildBlocks, []);

  useEffect(() => {
    if (!meshRef.current) return;
    const temp = new THREE.Object3D();
    blocks.forEach((block, index) => {
      temp.position.set(block.x, block.height / 2, block.z);
      temp.scale.set(0.82, block.height, 0.82);
      temp.rotation.y = (index % 3) * 0.08;
      temp.updateMatrix();
      meshRef.current.setMatrixAt(index, temp.matrix);
      const color = new THREE.Color(block.lit ? theme.cityLit : theme.city);
      meshRef.current.setColorAt(index, color);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
    meshRef.current.instanceColor.needsUpdate = true;
  }, [blocks, theme]);

  return (
    <instancedMesh ref={meshRef} args={[null, null, blocks.length]} castShadow receiveShadow>
      <boxGeometry args={[0.46, 1, 0.46]} />
      <meshStandardMaterial vertexColors roughness={0.7} metalness={0.12} />
    </instancedMesh>
  );
}

function KokTobeTower({ theme }) {
  return (
    <group position={[1.7, 0.62, -2.4]}>
      <mesh castShadow>
        <cylinderGeometry args={[0.08, 0.12, 2.8, 18]} />
        <meshStandardMaterial color="#edf7ff" roughness={0.42} metalness={0.35} />
      </mesh>
      <mesh position={[0, 1.52, 0]} castShadow>
        <sphereGeometry args={[0.24, 20, 20]} />
        <meshStandardMaterial color={theme.cityLit} emissive={theme.cityLit} emissiveIntensity={0.28} />
      </mesh>
      <mesh position={[0, 1.94, 0]}>
        <cylinderGeometry args={[0.035, 0.05, 1.16, 10]} />
        <meshStandardMaterial color="#f5fbff" emissive="#bfefff" emissiveIntensity={0.14} />
      </mesh>
    </group>
  );
}

function LayerLines({ layers, selectedPlace, theme }) {
  const selected = places.find((item) => item.id === selectedPlace) ?? places[1];
  const river = [
    [-3.8, 0.08, 5.8],
    [-2.4, 0.09, 3.8],
    [-1.3, 0.1, 2.2],
    [-0.2, 0.12, 0.5],
    [0.9, 0.18, -1.1],
    [2.1, 0.28, -3.2],
  ];
  const metro = [
    [-6.8, 0.18, 2.8],
    [-4.3, 0.19, 2.4],
    [-2.1, 0.2, 2.0],
    [0.4, 0.2, 1.55],
    [2.7, 0.19, 1.2],
    [5.8, 0.18, 0.9],
  ];
  const park = [
    [1.2, 0.11, 1.4],
    [1.7, 0.13, 0.2],
    [2.4, 0.14, -1.0],
    [3.2, 0.15, -2.1],
  ];

  return (
    <group>
      <Line points={river} color={theme.water} lineWidth={5.8} transparent opacity={0.48} />
      {layers.metro ? (
        <Line points={metro} color={routeColors.metro} lineWidth={3.5} transparent opacity={0.92} />
      ) : null}
      {layers.parks ? (
        <Line points={park} color={routeColors.parks} lineWidth={10} transparent opacity={0.48} />
      ) : null}
      {layers.routes ? (
        <Line points={selected.route} color={selected.accent} lineWidth={4.2} transparent opacity={0.96} />
      ) : null}
      {layers.culture ? (
        <Line
          points={[
            [-2.3, 0.22, 1.8],
            [-0.9, 0.24, 1.15],
            [0.2, 0.25, 1.3],
            [1.4, 0.26, 0.7],
            [1.7, 0.31, -2.4],
          ]}
          color={routeColors.culture}
          lineWidth={2.4}
          transparent
          opacity={0.84}
        />
      ) : null}
    </group>
  );
}

function Hotspot({ place, selected, onSelect }) {
  const groupRef = useRef(null);

  useFrame((state) => {
    if (!groupRef.current) return;
    const lift = Math.sin(state.clock.elapsedTime * 2.3 + place.position[0]) * 0.035;
    groupRef.current.position.y = place.position[1] + lift;
  });

  return (
    <Float speed={2.2} floatIntensity={selected ? 0.18 : 0.06} rotationIntensity={0}>
      <group
        ref={groupRef}
        position={place.position}
        onClick={(event) => {
          event.stopPropagation();
          onSelect(place.id);
        }}
      >
        <mesh castShadow>
          <coneGeometry args={[0.22, 0.72, 24]} />
          <meshStandardMaterial
            color={place.accent}
            emissive={place.accent}
            emissiveIntensity={selected ? 0.44 : 0.12}
            roughness={0.36}
          />
        </mesh>
        <mesh position={[0, -0.39, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.24, selected ? 0.48 : 0.34, 32]} />
          <meshBasicMaterial color={place.accent} transparent opacity={selected ? 0.8 : 0.36} />
        </mesh>
        {selected ? (
          <Html center distanceFactor={5.1} position={[0.52, 0.62, 0]}>
            <button
              className="scene-chip is-selected"
              aria-label={`Scene marker ${place.name}`}
              onClick={(event) => {
                event.stopPropagation();
                onSelect(place.id);
              }}
              style={{ "--chip-accent": place.accent }}
              type="button"
            >
              <span>{place.name}</span>
              <small>{place.type}</small>
            </button>
          </Html>
        ) : null}
      </group>
    </Float>
  );
}

function AtmosphericParticles({ theme }) {
  return (
    <Sparkles
      count={95}
      scale={[18, 7, 12]}
      size={1.8}
      speed={0.18}
      color={theme.cityLit}
      opacity={0.38}
      position={[0, 3.4, -1.6]}
    />
  );
}

function SceneLights({ time, theme }) {
  const night = time === "night";
  return (
    <>
      <ambientLight intensity={night ? 0.55 : 0.62} />
      <directionalLight
        position={time === "day" ? [-3, 8, 4] : [5, 4.4, 2]}
        intensity={time === "day" ? 2.4 : night ? 1.68 : 1.24}
        color={theme.sun}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <pointLight position={[1.7, 2.6, -2.4]} intensity={night ? 5.2 : 2.1} color={theme.cityLit} />
      <pointLight position={[-2.3, 1.2, 1.8]} intensity={night ? 3.6 : 1.2} color="#ffd784" />
    </>
  );
}

export default function CityScene({
  activeTab,
  cameraMode,
  layers,
  onSelectPlace,
  selectedPlace,
  time,
  zoomOffset,
}) {
  const theme = timeModes[time];
  const selected = places.find((item) => item.id === selectedPlace) ?? places[1];

  return (
    <Canvas
      className="city-canvas"
      camera={{ position: [7.2, 6.4, 9.4], fov: 46, near: 0.1, far: 80 }}
      dpr={[1, 1.75]}
      gl={{ antialias: true, alpha: false, preserveDrawingBuffer: true }}
      shadows="percentage"
    >
      <color attach="background" args={[theme.sceneBg]} />
      <fog attach="fog" args={[theme.fog, 12, 27]} />
      <SceneLights time={time} theme={theme} />
      <Terrain theme={theme} />
      <MountainRange theme={theme} />
      <CityBlocks theme={theme} />
      <LayerLines layers={layers} selectedPlace={selected.id} theme={theme} />
      <KokTobeTower theme={theme} />
      {places.map((place) => (
        <Hotspot
          key={place.id}
          place={place}
          selected={place.id === selected.id}
          onSelect={onSelectPlace}
        />
      ))}
      {activeTab === "skyline" ? <AtmosphericParticles theme={theme} /> : null}
      <CameraController selectedPlace={selected.id} cameraMode={cameraMode} zoomOffset={zoomOffset} />
    </Canvas>
  );
}
