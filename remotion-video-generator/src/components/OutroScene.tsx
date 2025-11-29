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

interface OutroSceneProps {
  backgroundImage: string;
  brandColor: string;
}

export const OutroScene: React.FC<OutroSceneProps> = ({
  backgroundImage,
  brandColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // CTA button animation
  const ctaScale = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: ANIMATIONS.BOUNCE_SPRING,
  });
  
  const ctaOpacity = interpolate(
    frame,
    [0, 20],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Subscribe button animation
  const subscribeY = spring({
    frame: frame - 15,
    fps,
    from: 50,
    to: 0,
    config: ANIMATIONS.SMOOTH_SPRING,
  });
  
  const subscribeOpacity = interpolate(
    frame,
    [15, 35],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Social icons animation
  const socialScale = spring({
    frame: frame - 25,
    fps,
    from: 0,
    to: 1,
    config: ANIMATIONS.SPRING_CONFIG,
  });
  
  // Pulse effect for CTA
  const pulseScale = interpolate(
    frame % 60,
    [0, 30, 60],
    [1, 1.05, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Background zoom
  const bgScale = interpolate(
    frame,
    [0, 300],
    [1, 1.1],
    { extrapolateRight: 'clamp' }
  );
  
  return (
    <AbsoluteFill>
      {/* Background Image */}
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
        {/* Dark overlay */}
        <AbsoluteFill
          style={{
            background: `linear-gradient(
              to bottom,
              rgba(0, 0, 0, 0.7) 0%,
              rgba(0, 0, 0, 0.85) 50%,
              rgba(0, 0, 0, 0.95) 100%
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
        {/* Thank You Message */}
        <div
          style={{
            position: 'absolute',
            top: 600,
            width: '100%',
            textAlign: 'center',
            opacity: ctaOpacity,
          }}
        >
          <h2
            style={{
              color: STYLES.COLORS.TEXT_PRIMARY,
              fontSize: 56,
              fontFamily: STYLES.FONTS.DISPLAY,
              fontWeight: 800,
              margin: 0,
              marginBottom: 20,
              textShadow: STYLES.SHADOWS.TEXT,
            }}
          >
            Thanks for Watching!
          </h2>
          <p
            style={{
              color: brandColor,
              fontSize: 32,
              fontFamily: STYLES.FONTS.PRIMARY,
              fontWeight: 600,
              margin: 0,
            }}
          >
            Found your perfect match?
          </p>
        </div>
        
        {/* CTA Button */}
        <div
          style={{
            position: 'absolute',
            top: LAYOUTS.OUTRO.CTA_Y,
            transform: `scale(${ctaScale * pulseScale})`,
            opacity: ctaOpacity,
          }}
        >
          <div
            style={{
              backgroundColor: brandColor,
              padding: '24px 60px',
              borderRadius: STYLES.RADIUS.PILL,
              boxShadow: `
                0 10px 30px rgba(0, 0, 0, 0.5),
                0 0 60px ${brandColor}66
              `,
              cursor: 'pointer',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <span
              style={{
                color: STYLES.COLORS.BACKGROUND,
                fontSize: STYLES.FONT_SIZES.CTA,
                fontFamily: STYLES.FONTS.DISPLAY,
                fontWeight: 900,
                letterSpacing: 1,
                position: 'relative',
                zIndex: 2,
              }}
            >
              SHOP NOW
            </span>
            
            {/* Animated shine effect */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
                animation: 'shine 2s infinite',
              }}
            />
          </div>
        </div>
        
        {/* Subscribe Section */}
        <div
          style={{
            position: 'absolute',
            top: LAYOUTS.OUTRO.SUBSCRIBE_BUTTON_Y,
            width: '100%',
            textAlign: 'center',
            transform: `translateY(${subscribeY}px)`,
            opacity: subscribeOpacity,
          }}
        >
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 20,
              padding: '16px 40px',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              borderRadius: STYLES.RADIUS.PILL,
              border: `2px solid ${brandColor}`,
            }}
          >
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill={brandColor}
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" />
            </svg>
            <span
              style={{
                color: STYLES.COLORS.TEXT_PRIMARY,
                fontSize: 28,
                fontFamily: STYLES.FONTS.PRIMARY,
                fontWeight: 700,
              }}
            >
              Subscribe for More
            </span>
          </div>
        </div>
        
        {/* Social Media Icons */}
        <div
          style={{
            position: 'absolute',
            top: LAYOUTS.OUTRO.SOCIAL_ICONS_Y,
            width: '100%',
            display: 'flex',
            justifyContent: 'center',
            gap: 40,
            transform: `scale(${socialScale})`,
          }}
        >
          {['instagram', 'tiktok', 'youtube'].map((platform, index) => (
            <div
              key={platform}
              style={{
                width: 60,
                height: 60,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: `2px solid ${brandColor}`,
                transform: `scale(${spring({
                  frame: frame - 25 - index * 5,
                  fps,
                  from: 0,
                  to: 1,
                  config: ANIMATIONS.BOUNCE_SPRING,
                })})`,
              }}
            >
              <span
                style={{
                  color: brandColor,
                  fontSize: 24,
                  fontWeight: 700,
                }}
              >
                {platform[0].toUpperCase()}
              </span>
            </div>
          ))}
        </div>
        
        {/* Link in Bio Text */}
        <div
          style={{
            position: 'absolute',
            bottom: STYLES.SAFE_ZONE.BOTTOM + 40,
            width: '100%',
            textAlign: 'center',
            opacity: interpolate(
              frame,
              [40, 60],
              [0, 1],
              { extrapolateRight: 'clamp' }
            ),
          }}
        >
          <span
            style={{
              color: STYLES.COLORS.TEXT_SECONDARY,
              fontSize: 24,
              fontFamily: STYLES.FONTS.PRIMARY,
              fontWeight: 500,
            }}
          >
            🔗 Links in bio
          </span>
        </div>
      </AbsoluteFill>
      
      <style jsx>{`
        @keyframes shine {
          0% { left: -100%; }
          100% { left: 200%; }
        }
      `}</style>
    </AbsoluteFill>
  );
};