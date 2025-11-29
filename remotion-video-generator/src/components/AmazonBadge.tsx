import React from 'react';
import { interpolate, useCurrentFrame, spring, useVideoConfig } from 'remotion';
import { STYLES } from '../schemas/CountdownVideoSchema';

interface AmazonBadgeProps {
  type: 'choice' | 'bestseller' | 'deal' | 'prime';
  startFrame?: number;
  accentColor?: string;
  size?: number;
}

export const AmazonBadge: React.FC<AmazonBadgeProps> = ({
  type,
  startFrame = 50,
  accentColor = '#FF9900',
  size = 1,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Drop animation with bounce
  const dropY = spring({
    frame: frame - startFrame,
    fps,
    from: -100,
    to: 0,
    config: {
      damping: 12,
      stiffness: 120,
    },
  });

  // Spin animation
  const spin = spring({
    frame: frame - startFrame,
    fps,
    from: -180,
    to: 0,
    config: {
      damping: 15,
      stiffness: 100,
    },
  });

  // Scale bounce
  const scaleSpring = spring({
    frame: frame - (startFrame + 20),
    fps,
    from: 1,
    to: 1.1,
    config: {
      damping: 10,
      stiffness: 200,
    },
  });

  const scale = interpolate(
    frame % 90,
    [0, 45, 90],
    [1, 1.05, 1],
    { extrapolateRight: 'wrap' }
  ) * scaleSpring;

  // Pulsing glow
  const glowIntensity = interpolate(
    frame % 60,
    [0, 30, 60],
    [0.6, 1, 0.6],
    { extrapolateRight: 'wrap' }
  );

  // Fade in
  const opacity = interpolate(
    frame,
    [startFrame, startFrame + 15],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  // Badge content based on type
  const getBadgeContent = () => {
    switch (type) {
      case 'choice':
        return {
          text: "Amazon's Choice",
          icon: '✓',
          bgColor: '#232F3E',
          textColor: '#FFFFFF',
          iconBgColor: accentColor,
        };
      case 'bestseller':
        return {
          text: '#1 Best Seller',
          icon: '👑',
          bgColor: '#FF9900',
          textColor: '#FFFFFF',
          iconBgColor: '#FFD700',
        };
      case 'deal':
        return {
          text: 'Limited Time Deal',
          icon: '⚡',
          bgColor: '#B12704',
          textColor: '#FFFFFF',
          iconBgColor: '#FF4444',
        };
      case 'prime':
        return {
          text: 'Prime',
          icon: '✓',
          bgColor: '#00A8E1',
          textColor: '#FFFFFF',
          iconBgColor: '#FFFFFF',
        };
      default:
        return {
          text: 'Featured',
          icon: '⭐',
          bgColor: '#232F3E',
          textColor: '#FFFFFF',
          iconBgColor: accentColor,
        };
    }
  };

  const badge = getBadgeContent();

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8 * size,
        backgroundColor: badge.bgColor,
        padding: `${10 * size}px ${16 * size}px`,
        borderRadius: STYLES.RADIUS.SMALL,
        transform: `translateY(${dropY}px) rotate(${spin}deg) scale(${scale})`,
        opacity,
        boxShadow: `
          0 ${4 * size}px ${12 * size}px rgba(0, 0, 0, 0.3),
          0 0 ${20 * glowIntensity * size}px ${badge.bgColor}${Math.floor(glowIntensity * 50).toString(16)},
          inset 0 ${1 * size}px ${2 * size}px rgba(255, 255, 255, 0.2)
        `,
      }}
    >
      {/* Icon Circle */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 24 * size,
          height: 24 * size,
          backgroundColor: badge.iconBgColor,
          borderRadius: '50%',
          fontSize: 14 * size,
          transform: `rotate(${interpolate(
            frame % 120,
            [0, 60, 120],
            [0, 10, 0],
            { extrapolateRight: 'wrap' }
          )}deg)`,
          boxShadow: type === 'bestseller'
            ? `0 0 ${10 * glowIntensity}px rgba(255, 215, 0, ${glowIntensity})`
            : 'none',
        }}
      >
        <span style={{ filter: type === 'bestseller' ? 'drop-shadow(0 0 2px rgba(255, 215, 0, 0.8))' : 'none' }}>
          {badge.icon}
        </span>
      </div>

      {/* Text */}
      <span
        style={{
          color: badge.textColor,
          fontSize: 16 * size,
          fontFamily: STYLES.FONTS.PRIMARY,
          fontWeight: 700,
          textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
          whiteSpace: 'nowrap',
        }}
      >
        {badge.text}
      </span>

      {/* Sparkle effect for bestseller */}
      {type === 'bestseller' && (
        <div
          style={{
            fontSize: 12 * size,
            opacity: interpolate(
              frame % 40,
              [0, 10, 20],
              [0, 1, 0],
              { extrapolateRight: 'wrap' }
            ),
            transform: `rotate(${frame * 10}deg)`,
          }}
        >
          ✨
        </div>
      )}

      {/* Lightning bolt animation for deal */}
      {type === 'deal' && (
        <div
          style={{
            fontSize: 14 * size,
            opacity: interpolate(
              frame % 30,
              [0, 5, 10],
              [0.5, 1, 0.5],
              { extrapolateRight: 'wrap' }
            ),
            filter: 'drop-shadow(0 0 4px rgba(255, 68, 68, 0.8))',
          }}
        >
          ⚡
        </div>
      )}
    </div>
  );
};

// Convenience components for specific badge types
export const AmazonChoice: React.FC<{ startFrame?: number }> = ({ startFrame }) => (
  <AmazonBadge type="choice" startFrame={startFrame} />
);

export const BestSellerBadge: React.FC<{ startFrame?: number }> = ({ startFrame }) => (
  <AmazonBadge type="bestseller" startFrame={startFrame} />
);

export const DealBadge: React.FC<{ startFrame?: number }> = ({ startFrame }) => (
  <AmazonBadge type="deal" startFrame={startFrame} />
);

export const PrimeBadge: React.FC<{ startFrame?: number }> = ({ startFrame }) => (
  <AmazonBadge type="prime" startFrame={startFrame} />
);
