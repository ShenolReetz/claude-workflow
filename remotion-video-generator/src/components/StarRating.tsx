import React from 'react';
import { interpolate, useCurrentFrame, spring, useVideoConfig } from 'remotion';
import { STYLES } from '../schemas/CountdownVideoSchema';

interface StarRatingProps {
  rating: number;
  size?: number;
  showNumber?: boolean;
}

export const StarRating: React.FC<StarRatingProps> = ({
  rating,
  size = 30,
  showNumber = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animate stars appearing one by one with spring bounce
  const starDelay = 8; // frames between each star

  const renderStar = (index: number, filled: number) => {
    const startFrame = index * starDelay;

    // Spring animation for bounce effect
    const starScale = spring({
      frame: frame - startFrame,
      fps,
      from: 0,
      to: 1,
      config: {
        damping: 8,
        stiffness: 200,
        mass: 0.5,
      },
    });

    const starOpacity = interpolate(
      frame,
      [startFrame, startFrame + 5],
      [0, 1],
      { extrapolateRight: 'clamp' }
    );

    // Animate fill progress for this star
    const fillProgress = spring({
      frame: frame - (startFrame + 5),
      fps,
      from: 0,
      to: filled,
      config: {
        damping: 15,
        stiffness: 150,
      },
    });

    // Sparkle appears when star is almost fully filled
    const sparkleOpacity = interpolate(
      frame,
      [startFrame + 15, startFrame + 20, startFrame + 25],
      [0, 1, 0],
      { extrapolateRight: 'clamp' }
    );

    const sparkleScale = interpolate(
      frame,
      [startFrame + 15, startFrame + 25],
      [0.5, 1.5],
      { extrapolateRight: 'clamp' }
    );

    // Glow pulse effect
    const glowIntensity = interpolate(
      frame % 60,
      [0, 30, 60],
      [0.6, 1, 0.6],
      { extrapolateRight: 'wrap' }
    );

    return (
      <div
        key={index}
        style={{
          position: 'relative',
          width: size,
          height: size,
          opacity: starOpacity,
          transform: `scale(${starScale})`,
        }}
      >
        {/* Empty star background */}
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
          }}
        >
          <path
            d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
            stroke="#888888"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        {/* Filled star with glow */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            filter: fillProgress > 0 ? `drop-shadow(0 0 ${8 * glowIntensity}px rgba(255, 215, 0, ${0.8 * glowIntensity}))` : 'none',
          }}
        >
          <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="#FFD700"
            style={{
              clipPath: `inset(0 ${100 - fillProgress * 100}% 0 0)`,
            }}
          >
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </div>

        {/* Sparkle effect */}
        {fillProgress > 0.8 && (
          <div
            style={{
              position: 'absolute',
              top: -size * 0.15,
              right: -size * 0.15,
              fontSize: size * 0.5,
              opacity: sparkleOpacity,
              transform: `scale(${sparkleScale}) rotate(${frame * 10}deg)`,
            }}
          >
            ✨
          </div>
        )}
      </div>
    );
  };

  // Calculate filled stars
  const fullStars = Math.floor(rating);
  const partialStar = rating - fullStars;
  
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 4,
      }}
    >
      <div
        style={{
          display: 'flex',
          gap: 2,
        }}
      >
        {[...Array(5)].map((_, index) => {
          let filled = 0;
          if (index < fullStars) {
            filled = 1;
          } else if (index === fullStars && partialStar > 0) {
            filled = partialStar;
          }
          return renderStar(index, filled);
        })}
      </div>
      
      {showNumber && (
        <span
          style={{
            color: '#FFD700',
            fontSize: size * 0.8,
            fontFamily: STYLES.FONTS.PRIMARY,
            fontWeight: 700,
            marginLeft: 8,
            opacity: interpolate(
              frame,
              [25, 35],
              [0, 1],
              { extrapolateRight: 'clamp' }
            ),
            transform: `scale(${spring({
              frame: frame - 30,
              fps,
              from: 0.8,
              to: 1,
              config: { damping: 10, stiffness: 200 },
            })})`,
            textShadow: '0 0 10px rgba(255, 215, 0, 0.5)',
          }}
        >
          {rating.toFixed(1)}
        </span>
      )}
    </div>
  );
};