import React from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { STYLES, LAYOUTS, ANIMATIONS } from '../schemas/CountdownVideoSchema';

interface CountdownBadgeProps {
  rank: number;
  isLast: boolean;
  brandColor: string;
}

export const CountdownBadge: React.FC<CountdownBadgeProps> = ({
  rank,
  isLast,
  brandColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Badge entrance animation
  const badgeScale = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: ANIMATIONS.BOUNCE_SPRING,
  });
  
  const badgeRotation = spring({
    frame,
    fps,
    from: -180,
    to: 0,
    config: ANIMATIONS.SPRING_CONFIG,
  });
  
  // Pulse effect for emphasis
  const pulseScale = interpolate(
    frame % 120,
    [0, 60, 120],
    [1, 1.1, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Glow effect intensity
  const glowIntensity = interpolate(
    frame % 90,
    [0, 45, 90],
    [0.5, 1, 0.5],
    { extrapolateRight: 'clamp' }
  );
  
  // Special effects for #1
  const specialEffectOpacity = isLast
    ? interpolate(
        frame,
        [30, 50],
        [0, 1],
        { extrapolateRight: 'clamp' }
      )
    : 0;
  
  const starburstRotation = interpolate(
    frame,
    [0, 300],
    [0, 360],
    { extrapolateRight: 'clamp' }
  );
  
  return (
    <>
      {/* Starburst effect for #1 */}
      {isLast && (
        <div
          style={{
            position: 'absolute',
            top: LAYOUTS.PRODUCT_CARD.COUNTDOWN_BADGE.Y,
            right: LAYOUTS.PRODUCT_CARD.COUNTDOWN_BADGE.X - 900,
            width: LAYOUTS.PRODUCT_CARD.COUNTDOWN_BADGE.SIZE * 2,
            height: LAYOUTS.PRODUCT_CARD.COUNTDOWN_BADGE.SIZE * 2,
            opacity: specialEffectOpacity,
            transform: `rotate(${starburstRotation}deg)`,
            pointerEvents: 'none',
          }}
        >
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 200 200"
            style={{
              filter: `blur(1px)`,
            }}
          >
            {[...Array(12)].map((_, i) => (
              <path
                key={i}
                d={`M100,100 L100,20 L100,100`}
                stroke={brandColor}
                strokeWidth="2"
                opacity={0.6}
                transform={`rotate(${i * 30} 100 100)`}
              />
            ))}
          </svg>
        </div>
      )}
      
      {/* Main Badge Container */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.PRODUCT_CARD.COUNTDOWN_BADGE.Y,
          right: STYLES.SAFE_ZONE.SIDES,
          width: LAYOUTS.PRODUCT_CARD.COUNTDOWN_BADGE.SIZE,
          height: LAYOUTS.PRODUCT_CARD.COUNTDOWN_BADGE.SIZE,
          transform: `scale(${badgeScale * pulseScale}) rotate(${badgeRotation}deg)`,
          transformOrigin: 'center',
        }}
      >
        {/* Glow effect */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '120%',
            height: '120%',
            borderRadius: '50%',
            background: brandColor,
            opacity: glowIntensity * 0.3,
            filter: 'blur(20px)',
          }}
        />
        
        {/* Badge Background */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: '100%',
            borderRadius: '50%',
            background: `linear-gradient(135deg, ${brandColor} 0%, ${brandColor}dd 100%)`,
            boxShadow: `
              0 10px 30px rgba(0, 0, 0, 0.5),
              inset 0 2px 4px rgba(255, 255, 255, 0.3),
              0 0 40px ${brandColor}66
            `,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            border: `4px solid ${STYLES.COLORS.BACKGROUND}`,
          }}
        >
          {/* Number */}
          <span
            style={{
              color: STYLES.COLORS.BACKGROUND,
              fontSize: STYLES.FONT_SIZES.COUNTDOWN,
              fontFamily: STYLES.FONTS.DISPLAY,
              fontWeight: 900,
              lineHeight: 1,
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
            }}
          >
            {rank}
          </span>
          
          {/* Hashtag */}
          <span
            style={{
              color: STYLES.COLORS.BACKGROUND,
              fontSize: 32,
              fontFamily: STYLES.FONTS.DISPLAY,
              fontWeight: 700,
              opacity: 0.9,
              marginTop: -10,
            }}
          >
            #
          </span>
        </div>
        
        {/* Special "BEST" label for #1 */}
        {isLast && (
          <div
            style={{
              position: 'absolute',
              bottom: -15,
              left: '50%',
              transform: 'translateX(-50%)',
              backgroundColor: STYLES.COLORS.SUCCESS,
              padding: '4px 16px',
              borderRadius: STYLES.RADIUS.PILL,
              opacity: specialEffectOpacity,
            }}
          >
            <span
              style={{
                color: STYLES.COLORS.TEXT_PRIMARY,
                fontSize: 14,
                fontFamily: STYLES.FONTS.PRIMARY,
                fontWeight: 800,
                letterSpacing: 1,
              }}
            >
              BEST
            </span>
          </div>
        )}
      </div>
    </>
  );
};