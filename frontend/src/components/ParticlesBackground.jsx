import React from 'react';
import { motion } from 'framer-motion';

export default function ParticlesBackground() {
  // Generate a larger amount of smaller particles statically so they don't jump on re-renders
  const particles = Array.from({ length: 25 }).map((_, i) => ({
    id: i,
    // Smaller particles: 20px to 100px
    size: 20 + (i * 3) % 80, 
    x: (i * 17) % 100, 
    y: (i * 23) % 100, 
    duration: 15 + (i % 15), 
    delay: -(i % 20),
    // Give them varied floating path formulas
    moveX: i % 2 === 0 ? [0, 40, -30, 0] : [0, -50, 40, 0],
    moveY: i % 3 === 0 ? [0, -60, 50, 0] : [0, 40, -40, 0]
  }));

  return (
    <div style={{ position: 'fixed', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
      {particles.map((p) => (
        <motion.div
          key={p.id}
          style={{
            position: 'absolute',
            width: p.size,
            height: p.size,
            borderRadius: '50%',
            background: 'var(--accent)',
            opacity: 0.15, // Tuned for visibility
            filter: 'blur(40px)', // Reduced blur so small particles don't completely evaporate
            left: `${p.x}%`,
            top: `${p.y}%`,
          }}
          animate={{
            x: p.moveX,   // Floating animation X
            y: p.moveY,   // Floating animation Y
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            ease: "easeInOut",
            delay: p.delay
          }}
        />
      ))}
    </div>
  );
}
