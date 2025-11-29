import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, spring, useVideoConfig } from 'remotion';

interface CardFlip3DProps {
  frontContent: React.ReactNode;
  backContent: React.ReactNode;
  startFrame: number;
  duration?: number;
  direction?: 'horizontal' | 'vertical';
}

export const CardFlip3D: React.FC<CardFlip3DProps> = ({
  frontContent,
  backContent,
  startFrame,
  duration = 30,
  direction = 'horizontal',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Calculate rotation angle with spring physics
  const rotation = spring({
    frame: frame - startFrame,
    fps,
    from: 0,
    to: 180,
    config: {
      damping: 20,
      stiffness: 100,
    },
    durationInFrames: duration,
  });

  // Determine which side is visible
  const showFront = rotation < 90;
  const currentRotation = showFront ? rotation : 180 - (rotation - 90);

  // Scale effect for depth perception
  const scale = interpolate(
    rotation,
    [0, 45, 90, 135, 180],
    [1, 0.95, 0.9, 0.95, 1],
    { extrapolateRight: 'clamp' }
  );

  // Shadow intensity for depth
  const shadowIntensity = interpolate(
    rotation,
    [0, 90, 180],
    [0.2, 0.6, 0.2],
    { extrapolateRight: 'clamp' }
  );

  const rotateAxis = direction === 'horizontal' ? 'rotateY' : 'rotateX';

  return (
    <AbsoluteFill
      style={{
        perspective: '2000px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      {/* Card Container */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          transformStyle: 'preserve-3d',
          transform: `${rotateAxis}(${rotation}deg) scale(${scale})`,
          filter: `drop-shadow(0 ${20 * shadowIntensity}px ${40 * shadowIntensity}px rgba(0, 0, 0, ${shadowIntensity}))`,
        }}
      >
        {/* Front Face */}
        <AbsoluteFill
          style={{
            backfaceVisibility: 'hidden',
            opacity: showFront ? 1 : 0,
            pointerEvents: showFront ? 'auto' : 'none',
          }}
        >
          {frontContent}
        </AbsoluteFill>

        {/* Back Face */}
        <AbsoluteFill
          style={{
            backfaceVisibility: 'hidden',
            transform: direction === 'horizontal' ? 'rotateY(180deg)' : 'rotateX(180deg)',
            opacity: !showFront ? 1 : 0,
            pointerEvents: !showFront ? 'auto' : 'none',
          }}
        >
          {backContent}
        </AbsoluteFill>
      </div>
    </AbsoluteFill>
  );
};
