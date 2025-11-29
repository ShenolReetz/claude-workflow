import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, spring, useVideoConfig } from 'remotion';

interface ParticleBurstProps {
  triggerFrame: number;
  x?: number; // Center X position (0-100%)
  y?: number; // Center Y position (0-100%)
  particleCount?: number;
  color?: string;
  duration?: number;
  type?: 'stars' | 'confetti' | 'sparkles' | 'fire';
}

export const ParticleBurst: React.FC<ParticleBurstProps> = ({
  triggerFrame,
  x = 50,
  y = 50,
  particleCount = 30,
  color = '#FFD700',
  duration = 45,
  type = 'stars',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Only show particles after trigger frame
  if (frame < triggerFrame) return null;

  const localFrame = frame - triggerFrame;

  // Get particle character based on type
  const getParticleChar = (index: number) => {
    switch (type) {
      case 'stars':
        return '⭐';
      case 'confetti':
        return ['🎊', '🎉', '🎈'][index % 3];
      case 'sparkles':
        return '✨';
      case 'fire':
        return '🔥';
      default:
        return '⭐';
    }
  };

  // Get particle color based on type
  const getParticleColor = (index: number) => {
    if (type === 'confetti') {
      const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'];
      return colors[index % colors.length];
    }
    return color;
  };

  const particles = Array.from({ length: particleCount }, (_, i) => {
    // Random angle for each particle
    const angle = (i / particleCount) * Math.PI * 2 + Math.random() * 0.3;

    // Random speed variation
    const speedMultiplier = 0.7 + Math.random() * 0.6;

    // Distance from center with spring physics
    const distance = spring({
      frame: localFrame,
      fps,
      from: 0,
      to: 300 * speedMultiplier,
      config: {
        damping: 20,
        stiffness: 100,
      },
    });

    // Calculate position
    const particleX = x + Math.cos(angle) * distance;
    const particleY = y + Math.sin(angle) * distance;

    // Fade out animation
    const opacity = interpolate(
      localFrame,
      [0, duration * 0.3, duration],
      [0, 1, 0],
      { extrapolateRight: 'clamp' }
    );

    // Scale animation
    const scale = interpolate(
      localFrame,
      [0, 10, duration],
      [0, 1.5, 0.5],
      { extrapolateRight: 'clamp' }
    );

    // Rotation
    const rotation = interpolate(
      localFrame,
      [0, duration],
      [0, 360 * (i % 2 === 0 ? 1 : -1)],
      { extrapolateRight: 'clamp' }
    );

    return (
      <div
        key={i}
        style={{
          position: 'absolute',
          left: `${particleX}%`,
          top: `${particleY}%`,
          transform: `translate(-50%, -50%) scale(${scale}) rotate(${rotation}deg)`,
          opacity,
          fontSize: type === 'confetti' ? 24 : 20,
          color: getParticleColor(i),
          textShadow: `0 0 10px ${getParticleColor(i)}`,
          pointerEvents: 'none',
          filter: `blur(${interpolate(localFrame, [0, duration], [0, 2], { extrapolateRight: 'clamp' })}px)`,
        }}
      >
        {getParticleChar(i)}
      </div>
    );
  });

  return (
    <AbsoluteFill style={{ pointerEvents: 'none', zIndex: 1000 }}>
      {particles}
    </AbsoluteFill>
  );
};

// Specialized burst for #1 ranking reveal
export const RankingBurst: React.FC<{ triggerFrame: number }> = ({ triggerFrame }) => (
  <ParticleBurst
    triggerFrame={triggerFrame}
    x={50}
    y={30}
    particleCount={40}
    type="stars"
    color="#FFD700"
    duration={50}
  />
);

// Specialized burst for price drop
export const PriceDropBurst: React.FC<{ triggerFrame: number; x: number; y: number }> = ({ triggerFrame, x, y }) => (
  <ParticleBurst
    triggerFrame={triggerFrame}
    x={x}
    y={y}
    particleCount={25}
    type="sparkles"
    color="#10B981"
    duration={40}
  />
);

// Celebration burst for end of video
export const CelebrationBurst: React.FC<{ triggerFrame: number }> = ({ triggerFrame }) => (
  <ParticleBurst
    triggerFrame={triggerFrame}
    x={50}
    y={50}
    particleCount={50}
    type="confetti"
    duration={60}
  />
);
