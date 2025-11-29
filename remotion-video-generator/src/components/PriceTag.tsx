import React from 'react';
import { interpolate, useCurrentFrame, spring, useVideoConfig } from 'remotion';
import { STYLES } from '../schemas/CountdownVideoSchema';

interface PriceTagProps {
  price: string;
  originalPrice?: string; // Optional original price for showing discount
  accentColor: string;
  showBadge?: boolean;
  startFrame?: number;
}

export const PriceTag: React.FC<PriceTagProps> = ({
  price,
  originalPrice,
  accentColor,
  showBadge = false,
  startFrame = 45,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Parse price to handle different formats
  const formatPrice = (priceStr: string) => {
    if (!priceStr) return '';
    const cleanPrice = priceStr.replace(/[^\d.,]/g, '');
    if (priceStr.includes('$')) {
      return priceStr;
    }
    return `$${cleanPrice}`;
  };

  const formattedPrice = formatPrice(price);
  const formattedOriginalPrice = originalPrice ? formatPrice(originalPrice) : null;

  // Calculate discount percentage
  const calculateDiscount = () => {
    if (!originalPrice) return 0;
    const original = parseFloat(originalPrice.replace(/[^\d.]/g, ''));
    const current = parseFloat(price.replace(/[^\d.]/g, ''));
    return Math.round(((original - current) / original) * 100);
  };
  const discountPercent = calculateDiscount();

  // Original price animations (appears first, then struck through)
  const originalPriceOpacity = interpolate(
    frame,
    [startFrame, startFrame + 10],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  const strikeWidth = interpolate(
    frame,
    [startFrame + 15, startFrame + 25],
    [0, 100],
    { extrapolateRight: 'clamp' }
  );

  // Current price dramatic reveal
  const priceScale = spring({
    frame: frame - (startFrame + 20),
    fps,
    from: 0.3,
    to: 1,
    config: {
      damping: 8,
      stiffness: 180,
      mass: 0.8,
    },
  });

  const priceOpacity = interpolate(
    frame,
    [startFrame + 20, startFrame + 30],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  // Flash effect when price appears
  const flashOpacity = interpolate(
    frame,
    [startFrame + 25, startFrame + 27, startFrame + 30],
    [0, 1, 0],
    { extrapolateRight: 'clamp' }
  );

  // Shine effect animation
  const shinePosition = interpolate(
    (frame - startFrame) % 120,
    [0, 120],
    [-100, 200],
    { extrapolateRight: 'clamp' }
  );

  // Pulsing glow effect
  const glowIntensity = interpolate(
    frame % 60,
    [0, 30, 60],
    [0.5, 1, 0.5],
    { extrapolateRight: 'wrap' }
  );
  
  return (
    <div
      style={{
        display: 'inline-flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        gap: 8,
      }}
    >
      {/* Original Price with Strike-through */}
      {formattedOriginalPrice && (
        <div
          style={{
            position: 'relative',
            opacity: originalPriceOpacity,
          }}
        >
          <span
            style={{
              color: '#999999',
              fontSize: STYLES.FONT_SIZES.PRICE * 0.6,
              fontFamily: STYLES.FONTS.PRIMARY,
              fontWeight: 600,
            }}
          >
            {formattedOriginalPrice}
          </span>
          {/* Animated strike-through */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: 0,
              width: `${strikeWidth}%`,
              height: '3px',
              backgroundColor: '#EF4444',
              transform: 'translateY(-50%)',
            }}
          />
        </div>
      )}

      {/* Current Price Container */}
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 12,
        }}
      >
        {/* Price Box */}
        <div
          style={{
            position: 'relative',
            display: 'inline-block',
            padding: '16px 32px',
            background: `linear-gradient(135deg, ${accentColor} 0%, ${accentColor}dd 100%)`,
            borderRadius: STYLES.RADIUS.MEDIUM,
            boxShadow: `
              0 8px 24px rgba(0, 0, 0, 0.4),
              inset 0 2px 4px rgba(255, 255, 255, 0.2),
              0 0 ${30 * glowIntensity}px ${accentColor}${Math.floor(glowIntensity * 100).toString(16)}
            `,
            overflow: 'hidden',
            transform: `scale(${priceScale})`,
            opacity: priceOpacity,
          }}
        >
          {/* Price Text */}
          <span
            style={{
              color: STYLES.COLORS.TEXT_PRIMARY,
              fontSize: STYLES.FONT_SIZES.PRICE,
              fontFamily: STYLES.FONTS.DISPLAY,
              fontWeight: 900,
              position: 'relative',
              zIndex: 2,
              textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
            }}
          >
            {formattedPrice}
          </span>

          {/* Shine Effect */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: `${shinePosition}%`,
              width: '60px',
              height: '100%',
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
              transform: 'skewX(-20deg)',
              pointerEvents: 'none',
            }}
          />

          {/* Flash Effect */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              opacity: flashOpacity,
              pointerEvents: 'none',
            }}
          />
        </div>

        {/* Discount Badge */}
        {discountPercent > 0 && (
          <div
            style={{
              position: 'relative',
              backgroundColor: '#EF4444',
              padding: '8px 16px',
              borderRadius: STYLES.RADIUS.SMALL,
              transform: `scale(${spring({
                frame: frame - (startFrame + 30),
                fps,
                from: 0,
                to: 1,
                config: { damping: 10, stiffness: 200 },
              })}) rotate(${spring({
                frame: frame - (startFrame + 30),
                fps,
                from: -15,
                to: 0,
                config: { damping: 12, stiffness: 150 },
              })}deg)`,
              opacity: interpolate(
                frame,
                [startFrame + 30, startFrame + 40],
                [0, 1],
                { extrapolateRight: 'clamp' }
              ),
              boxShadow: '0 4px 12px rgba(239, 68, 68, 0.4)',
            }}
          >
            <span
              style={{
                color: '#FFFFFF',
                fontSize: 20,
                fontFamily: STYLES.FONTS.PRIMARY,
                fontWeight: 800,
              }}
            >
              -{discountPercent}%
            </span>
            {/* Sparkle on discount badge */}
            <div
              style={{
                position: 'absolute',
                top: -8,
                right: -8,
                fontSize: 16,
                opacity: interpolate(
                  frame % 40,
                  [0, 10, 20],
                  [0, 1, 0],
                  { extrapolateRight: 'wrap' }
                ),
                transform: `rotate(${frame * 8}deg)`,
              }}
            >
              ✨
            </div>
          </div>
        )}
      </div>
      
      {/* Optional Badge */}
      {showBadge && (
        <div
          style={{
            backgroundColor: STYLES.COLORS.SUCCESS,
            padding: '6px 12px',
            borderRadius: STYLES.RADIUS.SMALL,
            opacity: interpolate(
              frame,
              [30, 40],
              [0, 1],
              { extrapolateRight: 'clamp' }
            ),
          }}
        >
          <span
            style={{
              color: STYLES.COLORS.TEXT_PRIMARY,
              fontSize: 18,
              fontFamily: STYLES.FONTS.PRIMARY,
              fontWeight: 700,
            }}
          >
            DEAL
          </span>
        </div>
      )}
      
      {/* Amazon Choice Badge (optional) */}
      {Math.random() > 0.7 && ( // Show randomly for some products
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            backgroundColor: '#232F3E',
            padding: '6px 12px',
            borderRadius: STYLES.RADIUS.SMALL,
            opacity: interpolate(
              frame,
              [35, 45],
              [0, 1],
              { extrapolateRight: 'clamp' }
            ),
          }}
        >
          <div
            style={{
              width: 16,
              height: 16,
              backgroundColor: accentColor,
              borderRadius: '50%',
            }}
          />
          <span
            style={{
              color: STYLES.COLORS.TEXT_PRIMARY,
              fontSize: 14,
              fontFamily: STYLES.FONTS.PRIMARY,
              fontWeight: 600,
            }}
          >
            Amazon's Choice
          </span>
        </div>
      )}
    </div>
  );
};