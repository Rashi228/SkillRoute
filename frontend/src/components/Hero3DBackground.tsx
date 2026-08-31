import { Canvas } from '@react-three/fiber';
import { Float, Environment, MeshTransmissionMaterial, Sphere, MeshDistortMaterial } from '@react-three/drei';

function FloatingShapes() {
  return (
    <group>
      <Float speed={2} rotationIntensity={1.5} floatIntensity={2}>
        <Sphere args={[2, 64, 64]} position={[6, 0, -2]}>
          <MeshTransmissionMaterial
            backside
            samples={4}
            thickness={3}
            roughness={0.1}
            chromaticAberration={0.4}
            anisotropy={0.5}
            distortion={0.3}
            distortionScale={0.2}
            temporalDistortion={0.1}
            color="#0ea5e9" // bright sky blue
          />
        </Sphere>
      </Float>

      {/* Secondary distorted orb, also on the right */}
      <Float speed={2.5} rotationIntensity={2} floatIntensity={3}>
        <Sphere args={[1.5, 64, 64]} position={[4.5, 2.5, -4]}>
          <MeshDistortMaterial
            color="#14b8a6" // teal
            envMapIntensity={1}
            clearcoat={1}
            clearcoatRoughness={0.1}
            metalness={0.1}
            roughness={0.2}
            distort={0.4}
            speed={2}
          />
        </Sphere>
      </Float>

      {/* Tertiary soft glow sphere on the far right */}
      <Float speed={1} rotationIntensity={1} floatIntensity={1.5}>
        <Sphere args={[1, 64, 64]} position={[7, -2.5, 0]}>
          <MeshTransmissionMaterial
            backside
            samples={4}
            thickness={1}
            chromaticAberration={1}
            roughness={0.3}
            color="#34d399" // emerald
          />
        </Sphere>
      </Float>

      {/* Small floating particles clustered on the right */}
      {Array.from({ length: 20 }).map((_, i) => (
        <Float key={i} speed={1 + Math.random() * 2} rotationIntensity={2} floatIntensity={3}>
          <Sphere
            args={[0.06, 16, 16]}
            position={[
              Math.random() * 6 + 3, // X between 3 and 9 (strictly right side)
              (Math.random() - 0.5) * 12, // Y spread
              (Math.random() - 0.5) * 8 - 2, // Z spread
            ]}
          >
            <meshStandardMaterial color="#5eead4" emissive="#2dd4bf" emissiveIntensity={1.5} />
          </Sphere>
        </Float>
      ))}
    </group>
  );
}

export default function Hero3DBackground() {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none opacity-50" style={{ mixBlendMode: 'multiply' }}>
      <Canvas camera={{ position: [0, 0, 10], fov: 40 }}>
        <ambientLight intensity={3} color="#ffffff" />
        <directionalLight position={[10, 10, 10]} intensity={2} color="#ffffff" />
        <directionalLight position={[-10, -10, -10]} intensity={1} color="#2D6A62" />
        <pointLight position={[5, 0, 5]} intensity={5} color="#0ea5e9" distance={20} />

        <FloatingShapes />

        <Environment preset="dawn" />
      </Canvas>
    </div>
  );
}
