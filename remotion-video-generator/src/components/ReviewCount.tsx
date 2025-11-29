import React from 'react';
import { interpolate, useCurrentFrame, spring, useVideoConfig } from 'remotion';
import { STYLES } from '../schemas/CountdownVideoSchema';

interface ReviewCountProps {
  count: number;
  size?: number;
  startFrame?: number;
}

export const ReviewCount: React.FC<ReviewCountProps> = ({
  count,
  size = 24,
  startFrame = 40,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Count up animation from 0 to actual count
  const currentCount = Math.floor(
    interpolate(
      frame,
      [startFrame, startFrame + 30],
      [0, count],
      { extrapolateRight: 'clamp' }
    )
  );

  // Pulse effect when counting
  const pulseScale = spring({
    frame: frame - startFrame,
    fps,
    from: 1.5,
    to: 1,
    config: {
      damping: 10,
      stiffness: 200,
    },
  });

  // Fade in animation
  const opacity = interpolate(
    frame,
    [startFrame, startFrame + 10],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  // Glow pulse that cycles
  const glowIntensity = interpolate(
    frame % 60,
    [0, 30, 60],
    [0.4, 0.8, 0.4],
    { extrapolateRight: 'wrap' }
  );

  // Format number with commas
  const formatNumber = (num: number) => {
    return num.toLocaleString('en-US');
  };

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        opacity,
      }}
    >
      {/* Review count number */}
      <span
        style={{
          fontSize: size,
          fontFamily: STYLES.FONTS.PRIMARY,
          fontWeight: 700,
          color: '#4A90E2',
          transform: `scale(${pulseScale})`,
          textShadow: `0 0 ${10 * glowIntensity}px rgba(74, 144, 226, ${glowIntensity})`,
          display: 'inline-block',
        }}
      >
        {formatNumber(currentCount)}
      </span>

      {/* "Reviews" text */}
      <span
        style={{
          fontSize: size * 0.7,
          fontFamily: STYLES.FONTS.PRIMARY,
          fontWeight: 500,
          color: '#666666',
          opacity: interpolate(
            frame,
            [startFrame + 20, startFrame + 30],
            [0, 1],
            { extrapolateRight: 'clamp' }
          ),
        }}
      >
        Reviews
      </span>

      {/* Animated checkmark icon */}
      <div
        style={{
          opacity: interpolate(
            frame,
            [startFrame + 25, startFrame + 35],
            [0, 1],
            { extrapolateRight: 'clamp' }
          ),
          transform: `scale(${spring({
            frame: frame - (startFrame + 25),
            fps,
            from: 0,
            to: 1,
            config: { damping: 8, stiffness: 250 },
          })})`,
        }}
      >
        <svg
          width={size * 0.8}
          height={size * 0.8}
          viewBox="0 0 24 24"
          fill="none"
          style={{
            filter: 'drop-shadow(0 0 4px rgba(76, 175, 80, 0.5))',
          }}
        >
          <circle cx="12" cy="12" r="10" fill="#4CAF50" />
          <path
            d="M7 12l3 3 7-7"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </div>
  );
};
