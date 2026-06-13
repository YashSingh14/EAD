import { Canvas, useFrame } from "@react-three/fiber";
import { Float, MeshDistortMaterial } from "@react-three/drei";
import { Suspense, useRef } from "react";
import type { Mesh } from "three";

function KnowledgeRing({ position, scale, color }: { position: [number, number, number]; scale: number; color: string }) {
  const ref = useRef<Mesh>(null);
  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.18) * 0.24;
    ref.current.rotation.y = state.clock.elapsedTime * 0.16;
    ref.current.rotation.z = Math.cos(state.clock.elapsedTime * 0.12) * 0.18;
  });

  return (
    <mesh ref={ref} position={position} scale={scale}>
      <torusKnotGeometry args={[1, 0.08, 180, 16]} />
      <meshStandardMaterial color={color} roughness={0.25} metalness={0.55} emissive={color} emissiveIntensity={0.12} />
    </mesh>
  );
}

function Blob({
  position,
  color,
  speed,
  scale,
  distort,
}: {
  position: [number, number, number];
  color: string;
  speed: number;
  scale: number;
  distort: number;
}) {
  const ref = useRef<Mesh>(null);
  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.x = state.clock.elapsedTime * 0.08 * speed;
    ref.current.rotation.y = state.clock.elapsedTime * 0.05 * speed;
  });
  return (
    <Float speed={speed} rotationIntensity={0.4} floatIntensity={1.2}>
      <mesh ref={ref} position={position} scale={scale}>
        <sphereGeometry args={[1, 64, 64]} />
        <MeshDistortMaterial
          color={color}
          distort={distort}
          speed={1.5}
          roughness={0.4}
          metalness={0.1}
        />
      </mesh>
    </Float>
  );
}

export function AmbientScene({ variant = "hero" }: { variant?: "hero" | "subtle" }) {
  const subtle = variant === "subtle";
  return (
    <div
      aria-hidden
      className={`pointer-events-none fixed inset-0 z-0 overflow-hidden ${subtle ? "opacity-60" : "opacity-95"}`}
    >
      <Canvas
        camera={{ position: [0, 0, 7], fov: 48 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true }}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={subtle ? 0.7 : 0.9} />
          <directionalLight position={[5, 5, 5]} intensity={subtle ? 1.2 : 1.7} color="#fff5e6" />
          <pointLight position={[-4, -2, 3]} intensity={subtle ? 1.6 : 2.6} color="#e89968" />
          <pointLight position={[4, 3, 2]} intensity={subtle ? 1.2 : 2.0} color="#c47a4a" />

          {!subtle && (
            <KnowledgeRing position={[2.35, 0.55, -0.8]} scale={1.25} color="#b8663d" />
          )}
          <Blob position={[-3.2, 1.45, -1]} color="#c97c4a" speed={subtle ? 0.6 : 1} scale={subtle ? 2.2 : 1.95} distort={0.5} />
          <Blob position={[3.15, -1.05, -1.8]} color="#d9a87a" speed={subtle ? 0.5 : 0.8} scale={subtle ? 2.6 : 2.4} distort={0.52} />
          <Blob position={[-0.15, -2.1, -2.5]} color="#a85a30" speed={subtle ? 0.7 : 1.2} scale={subtle ? 1.9 : 1.65} distort={0.44} />
        </Suspense>
      </Canvas>
      <div
        className={`absolute inset-0 pointer-events-none ${
          subtle
            ? "bg-[radial-gradient(ellipse_at_center,color-mix(in_oklab,var(--background)_55%,transparent),var(--background)_88%)]"
            : "bg-[radial-gradient(ellipse_at_center,color-mix(in_oklab,var(--background)_28%,transparent),var(--background)_82%)]"
        }`}
      />
    </div>
  );
}
