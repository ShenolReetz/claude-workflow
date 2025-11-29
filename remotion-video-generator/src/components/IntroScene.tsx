import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { STYLES, LAYOUTS, ANIMATIONS } from '../schemas/CountdownVideoSchema';

interface IntroSceneProps {
  title: string;
  backgroundImage: string;
  brandColor: string;
}

export const IntroScene: React.FC<IntroSceneProps> = ({
  title,
  backgroundImage,
  brandColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Title animation
  const titleScale = spring({
    frame,
    fps,
    from: 0.8,
    to: 1,
    config: ANIMATIONS.BOUNCE_SPRING,
  });
  
  const titleOpacity = interpolate(
    frame,
    [0, 20],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Subtitle animation
  const subtitleY = spring({
    frame: frame - 10,
    fps,
    from: 50,
    to: 0,
    config: ANIMATIONS.SMOOTH_SPRING,
  });
  
  const subtitleOpacity = interpolate(
    frame,
    [10, 30],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Background zoom effect
  const bgScale = interpolate(
    frame,
    [0, 300],
    [1.2, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Pulse effect for emphasis
  const pulseScale = interpolate(
    frame % 60,
    [0, 30, 60],
    [1, 1.05, 1],
    { extrapolateRight: 'clamp' }
  );
  
  return (
    <AbsoluteFill>
      {/* Background Image with Ken Burns effect */}
      <AbsoluteFill
        style={{
          transform: `scale(${bgScale})`,
        }}
      >
        <Img
          src={backgroundImage}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
        {/* Dark overlay for text readability */}
        <AbsoluteFill
          style={{
            background: `linear-gradient(
              to bottom,
              rgba(0, 0, 0, 0.3) 0%,
              rgba(0, 0, 0, 0.7) 50%,
              rgba(0, 0, 0, 0.9) 100%
            )`,
          }}
        />
      </AbsoluteFill>
      
      {/* Content Container */}
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          padding: `${STYLES.SAFE_ZONE.SIDES}px`,
        }}
      >
        {/* Top Badge */}
        <div
          style={{
            position: 'absolute',
            top: LAYOUTS.INTRO.LOGO_Y,
            backgroundColor: brandColor,
            padding: '12px 32px',
            borderRadius: STYLES.RADIUS.PILL,
            boxShadow: STYLES.SHADOWS.GLOW,
            transform: `scale(${pulseScale})`,
          }}
        >
          <span
            style={{
              color: STYLES.COLORS.BACKGROUND,
              fontSize: 28,
              fontFamily: STYLES.FONTS.DISPLAY,
              fontWeight: 900,
              letterSpacing: 2,
            }}
          >
            TOP 5
          </span>
        </div>
        
        {/* Main Title */}
        <div
          style={{
            position: 'absolute',
            top: LAYOUTS.INTRO.TITLE_Y,
            width: '100%',
            textAlign: 'center',
            transform: `scale(${titleScale})`,
            opacity: titleOpacity,
          }}
        >
          <h1
            style={{
              color: STYLES.COLORS.TEXT_PRIMARY,
              fontSize: STYLES.FONT_SIZES.TITLE,
              fontFamily: STYLES.FONTS.DISPLAY,
              fontWeight: 800,
              lineHeight: 1.2,
              textShadow: STYLES.SHADOWS.TEXT,
              margin: 0,
              padding: '0 20px',
            }}
          >
            {title}
          </h1>
        </div>
        
        {/* Subtitle */}
        <div
          style={{
            position: 'absolute',
            top: LAYOUTS.INTRO.SUBTITLE_Y,
            width: '100%',
            textAlign: 'center',
            transform: `translateY(${subtitleY}px)`,
            opacity: subtitleOpacity,
          }}
        >
          <p
            style={{
              color: brandColor,
              fontSize: 36,
              fontFamily: STYLES.FONTS.PRIMARY,
              fontWeight: 600,
              margin: 0,
              letterSpacing: 1,
            }}
          >
            Must-Have Products
          </p>
        </div>
        
        {/* Animated Arrow */}
        <div
          style={{
            position: 'absolute',
            bottom: 200,
            animation: 'bounce 2s infinite',
          }}
        >
          <svg
            width="60"
            height="60"
            viewBox="0 0 24 24"
            fill="none"
            style={{
              filter: `drop-shadow(${STYLES.SHADOWS.TEXT})`,
            }}
          >
            <path
              d="M12 5v14M19 12l-7 7-7-7"
              stroke={brandColor}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </AbsoluteFill>
      
      <style jsx>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-20px); }
        }
      `}</style>
    </AbsoluteFill>
  );
};