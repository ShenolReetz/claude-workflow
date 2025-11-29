/**
 * Production-ready Remotion composition for Amazon countdown videos
 * Implements the complete 55-second video format with professional animations
 */

import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Composition,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from 'remotion';
import { z } from 'zod';

// Import schema and types
import { 
  ProductionVideoConfig,
  AirtableVideoDataSchema,
  validateAirtableData,
  formatReviewCount,
  formatPrice,
  TIMING_30FPS,
  VISUAL_CONFIG,
  ANIMATIONS,
  LAYOUTS,
  COMPONENTS,
} from '../schemas/ProductionVideoSchema';

import {
  VideoData,
  Product,
  ProductRank,
  CountdownVideoProps,
  IntroSceneProps,
  ProductSceneProps,
  OutroSceneProps,
} from '../types/ProductionTypes';

// ============================================================================
// MAIN COMPOSITION COMPONENT
// ============================================================================

export const ProductionCountdownVideo: React.FC<CountdownVideoProps> = ({
  data,
  platform = 'tiktok',
  transition = 'slide-up',
  enableDebug = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Debug overlay
  if (enableDebug) {
    console.log(`Frame: ${frame}, Second: ${(frame / fps).toFixed(2)}`);
  }
  
  return (
    <AbsoluteFill style={{ backgroundColor: VISUAL_CONFIG.COLORS.BG_PRIMARY }}>
      {/* Background gradient overlay */}
      <AbsoluteFill
        style={{
          background: 'radial-gradient(circle at center, rgba(255,255,0,0.05) 0%, transparent 50%)',
          opacity: 0.5,
        }}
      />
      
      {/* Intro Scene - 5 seconds */}
      <Sequence from={TIMING_30FPS.INTRO.START} durationInFrames={TIMING_30FPS.INTRO.DURATION}>
        <IntroScene
          title={data.videoTitle}
          imageUrl={data.introPhoto}
          audioUrl={data.introMp3}
          brandColors={data.brandColors}
        />
      </Sequence>
      
      {/* Product #5 - 9 seconds */}
      <Sequence from={TIMING_30FPS.PRODUCT_5.START} durationInFrames={TIMING_30FPS.PRODUCT_5.DURATION}>
        <ProductScene
          product={data.product5}
          rank={5}
          transitionIn={transition}
          transitionOut={transition}
        />
      </Sequence>
      
      {/* Product #4 - 9 seconds */}
      <Sequence from={TIMING_30FPS.PRODUCT_4.START} durationInFrames={TIMING_30FPS.PRODUCT_4.DURATION}>
        <ProductScene
          product={data.product4}
          rank={4}
          transitionIn={transition}
          transitionOut={transition}
        />
      </Sequence>
      
      {/* Product #3 - 9 seconds */}
      <Sequence from={TIMING_30FPS.PRODUCT_3.START} durationInFrames={TIMING_30FPS.PRODUCT_3.DURATION}>
        <ProductScene
          product={data.product3}
          rank={3}
          transitionIn={transition}
          transitionOut={transition}
        />
      </Sequence>
      
      {/* Product #2 - 9 seconds */}
      <Sequence from={TIMING_30FPS.PRODUCT_2.START} durationInFrames={TIMING_30FPS.PRODUCT_2.DURATION}>
        <ProductScene
          product={data.product2}
          rank={2}
          transitionIn={transition}
          transitionOut={transition}
        />
      </Sequence>
      
      {/* Product #1 - 9 seconds */}
      <Sequence from={TIMING_30FPS.PRODUCT_1.START} durationInFrames={TIMING_30FPS.PRODUCT_1.DURATION}>
        <ProductScene
          product={data.product1}
          rank={1}
          transitionIn={transition}
          transitionOut={transition}
          showBadge={true}
          badgeType="BEST_SELLER"
        />
      </Sequence>
      
      {/* Outro Scene - 5 seconds */}
      <Sequence from={TIMING_30FPS.OUTRO.START} durationInFrames={TIMING_30FPS.OUTRO.DURATION}>
        <OutroScene
          imageUrl={data.outroPhoto}
          audioUrl={data.outroMp3}
          platform={platform}
          ctaText="Get These Amazing Products!"
          subscribeCTA="Subscribe for More Top Picks!"
        />
      </Sequence>
      
      {/* Debug overlay */}
      {enableDebug && (
        <div
          style={{
            position: 'absolute',
            top: 20,
            left: 20,
            color: 'white',
            fontSize: 24,
            fontFamily: 'monospace',
            backgroundColor: 'rgba(0,0,0,0.7)',
            padding: '10px',
            borderRadius: 8,
            zIndex: 9999,
          }}
        >
          Frame: {frame} | Time: {(frame / fps).toFixed(2)}s
        </div>
      )}
    </AbsoluteFill>
  );
};

// ============================================================================
// INTRO SCENE COMPONENT
// ============================================================================

const IntroScene: React.FC<IntroSceneProps> = ({
  title,
  subtitle,
  imageUrl,
  audioUrl,
  brandColors,
  animationType = 'zoom',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Animation calculations
  const logoScale = spring({
    frame,
    fps,
    config: ANIMATIONS.SPRINGS.BOUNCY,
    durationInFrames: 30,
  });
  
  const titleOpacity = interpolate(
    frame,
    [30, 60],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  const titleY = interpolate(
    frame,
    [30, 60],
    [100, 0],
    { extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) }
  );
  
  const hookScale = spring({
    frame: frame - 90,
    fps,
    config: ANIMATIONS.SPRINGS.SMOOTH,
    durationInFrames: 30,
  });
  
  return (
    <AbsoluteFill>
      {/* Background image with blur */}
      {imageUrl && (
        <AbsoluteFill>
          <img
            src={imageUrl}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              filter: 'blur(20px) brightness(0.4)',
            }}
          />
        </AbsoluteFill>
      )}
      
      {/* Fallback gradient if no image */}
      {!imageUrl && (
        <AbsoluteFill
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          }}
        />
      )}
      
      {/* Audio */}
      {audioUrl && <Audio src={audioUrl} volume={1} />}
      
      {/* Logo/Icon */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.INTRO.LOGO.y,
          left: '50%',
          transform: `translateX(-50%) scale(${logoScale})`,
          fontSize: LAYOUTS.INTRO.LOGO.size,
        }}
      >
        🛍️
      </div>
      
      {/* Main Title */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.INTRO.TITLE.y,
          width: '100%',
          textAlign: 'center',
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <h1
          style={{
            fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.INTRO_TITLE,
            fontFamily: VISUAL_CONFIG.TYPOGRAPHY.FONTS.DISPLAY,
            fontWeight: VISUAL_CONFIG.TYPOGRAPHY.WEIGHTS.BLACK,
            color: brandColors?.primary || VISUAL_CONFIG.COLORS.PRIMARY,
            textShadow: VISUAL_CONFIG.EFFECTS.SHADOWS.TEXT,
            margin: 0,
            padding: '0 60px',
            lineHeight: 1.2,
          }}
        >
          {title}
        </h1>
      </div>
      
      {/* Hook Text */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.INTRO.HOOK.y,
          width: '100%',
          textAlign: 'center',
          transform: `scale(${hookScale})`,
        }}
      >
        <p
          style={{
            fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.INTRO_SUBTITLE,
            fontFamily: VISUAL_CONFIG.TYPOGRAPHY.FONTS.PRIMARY,
            color: VISUAL_CONFIG.COLORS.TEXT_PRIMARY,
            textShadow: VISUAL_CONFIG.EFFECTS.SHADOWS.TEXT,
            margin: 0,
            padding: '0 80px',
          }}
        >
          Discover the Top 5 Must-Have Products!
        </p>
      </div>
      
      {/* Animated particles/sparkles */}
      <Sparkles count={20} />
    </AbsoluteFill>
  );
};

// ============================================================================
// PRODUCT SCENE COMPONENT
// ============================================================================

const ProductScene: React.FC<ProductSceneProps> = ({
  product,
  rank,
  transitionIn = 'slide-up',
  transitionOut = 'slide-up',
  showBadge = false,
  badgeType,
  enableParallax = true,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  
  // Transition animations
  const entryProgress = interpolate(
    frame,
    [0, 20],
    [0, 1],
    { extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) }
  );
  
  const exitProgress = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', easing: Easing.in(Easing.cubic) }
  );
  
  // Calculate transition styles
  const getTransitionStyle = (type: string, progress: number) => {
    switch (type) {
      case 'slide-up':
        return {
          transform: `translateY(${interpolate(progress, [0, 1], [100, 0])}px)`,
          opacity: progress,
        };
      case 'scale':
        return {
          transform: `scale(${progress})`,
          opacity: progress,
        };
      case 'fade':
        return {
          opacity: progress,
        };
      default:
        return {};
    }
  };
  
  // Badge animation
  const badgeRotation = spring({
    frame: frame - 15,
    fps,
    config: ANIMATIONS.SPRINGS.BOUNCY,
    durationInFrames: 30,
  });
  
  // Star rating animation
  const ratingProgress = interpolate(
    frame,
    [30, 60],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Price glow animation
  const priceGlow = Math.sin(frame * 0.1) * 0.5 + 0.5;
  
  return (
    <AbsoluteFill style={getTransitionStyle(transitionIn, entryProgress * exitProgress)}>
      {/* Background with product image */}
      <AbsoluteFill>
        <img
          src={product.photo}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter: 'blur(30px) brightness(0.3)',
          }}
        />
      </AbsoluteFill>
      
      {/* Audio */}
      {product.mp3 && <Audio src={product.mp3} volume={1} />}
      
      {/* Countdown Badge */}
      <CountdownBadge rank={rank as ProductRank} rotation={badgeRotation} />
      
      {/* Product Image */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.PRODUCT.IMAGE.y,
          left: '50%',
          transform: 'translateX(-50%)',
          width: LAYOUTS.PRODUCT.IMAGE.width,
          height: LAYOUTS.PRODUCT.IMAGE.height,
        }}
      >
        {product.photo ? (
          <img
            src={product.photo}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              borderRadius: LAYOUTS.PRODUCT.IMAGE.borderRadius,
              boxShadow: VISUAL_CONFIG.EFFECTS.SHADOWS.CARD,
            }}
          />
        ) : (
          <div
            style={{
              width: '100%',
              height: '100%',
              borderRadius: LAYOUTS.PRODUCT.IMAGE.borderRadius,
              background: 'linear-gradient(135deg, #ddd 0%, #999 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 72,
              boxShadow: VISUAL_CONFIG.EFFECTS.SHADOWS.CARD,
            }}
          >
            📦
          </div>
        )}
      </div>
      
      {/* Product Info Card */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.PRODUCT.INFO_CARD.y,
          left: '50%',
          transform: 'translateX(-50%)',
          width: LAYOUTS.PRODUCT.INFO_CARD.width,
          padding: LAYOUTS.PRODUCT.INFO_CARD.padding,
          ...VISUAL_CONFIG.EFFECTS.GLASS,
          borderRadius: VISUAL_CONFIG.EFFECTS.RADIUS.LARGE,
          boxShadow: VISUAL_CONFIG.EFFECTS.SHADOWS.CARD,
        }}
      >
        {/* Product Title */}
        <h2
          style={{
            fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.PRODUCT_TITLE,
            fontFamily: VISUAL_CONFIG.TYPOGRAPHY.FONTS.DISPLAY,
            fontWeight: VISUAL_CONFIG.TYPOGRAPHY.WEIGHTS.BOLD,
            color: VISUAL_CONFIG.COLORS.TEXT_PRIMARY,
            margin: '0 0 20px 0',
            textAlign: 'center',
          }}
        >
          {product.title}
        </h2>
        
        {/* Price */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: 20,
            marginBottom: 20,
          }}
        >
          <span
            style={{
              fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.PRODUCT_PRICE,
              fontFamily: VISUAL_CONFIG.TYPOGRAPHY.FONTS.DISPLAY,
              fontWeight: VISUAL_CONFIG.TYPOGRAPHY.WEIGHTS.BLACK,
              color: VISUAL_CONFIG.COLORS.ACCENT,
              textShadow: `0 0 ${20 * priceGlow}px ${VISUAL_CONFIG.COLORS.ACCENT}`,
            }}
          >
            {formatPrice(product.price)}
          </span>
        </div>
        
        {/* Rating */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: 10,
            marginBottom: 20,
          }}
        >
          <StarRating rating={product.rating} progress={ratingProgress} />
          <span
            style={{
              fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.REVIEW_COUNT,
              color: VISUAL_CONFIG.COLORS.TEXT_SECONDARY,
            }}
          >
            ({formatReviewCount(product.reviews)})
          </span>
        </div>
        
        {/* Description */}
        <p
          style={{
            fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.DESCRIPTION,
            fontFamily: VISUAL_CONFIG.TYPOGRAPHY.FONTS.PRIMARY,
            color: VISUAL_CONFIG.COLORS.TEXT_SECONDARY,
            textAlign: 'center',
            margin: 0,
            lineHeight: 1.4,
          }}
        >
          {product.description}
        </p>
        
        {/* Badge */}
        {showBadge && badgeType && (
          <div
            style={{
              position: 'absolute',
              top: -20,
              right: 40,
              backgroundColor: COMPONENTS.PRODUCT_BADGE.types[badgeType].bg,
              color: COMPONENTS.PRODUCT_BADGE.types[badgeType].text,
              padding: '8px 16px',
              borderRadius: VISUAL_CONFIG.EFFECTS.RADIUS.PILL,
              fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.BADGE_TEXT,
              fontWeight: VISUAL_CONFIG.TYPOGRAPHY.WEIGHTS.BOLD,
              boxShadow: VISUAL_CONFIG.EFFECTS.SHADOWS.MEDIUM,
            }}
          >
            {COMPONENTS.PRODUCT_BADGE.types[badgeType].icon} {badgeType.replace('_', ' ')}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ============================================================================
// OUTRO SCENE COMPONENT
// ============================================================================

const OutroScene: React.FC<OutroSceneProps> = ({
  imageUrl,
  audioUrl,
  ctaText = "Don't Miss Out!",
  subscribeCTA = "Subscribe Now!",
  platform = 'tiktok',
  showDisclaimer = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Animations
  const titleScale = spring({
    frame,
    fps,
    config: ANIMATIONS.SPRINGS.SMOOTH,
    durationInFrames: 30,
  });
  
  const ctaPulse = Math.sin(frame * 0.2) * 0.1 + 1;
  
  const socialIconsStagger = (index: number) => 
    spring({
      frame: frame - (90 + index * 10),
      fps,
      config: ANIMATIONS.SPRINGS.BOUNCY,
      durationInFrames: 20,
    });
  
  return (
    <AbsoluteFill>
      {/* Background */}
      {imageUrl ? (
        <AbsoluteFill>
          <img
            src={imageUrl}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              filter: 'brightness(0.4)',
            }}
          />
        </AbsoluteFill>
      ) : (
        <AbsoluteFill
          style={{
            background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
          }}
        />
      )}
      
      {/* Audio */}
      {audioUrl && <Audio src={audioUrl} volume={1} />}
      
      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.OUTRO.TITLE.y,
          width: '100%',
          textAlign: 'center',
          transform: `scale(${titleScale})`,
        }}
      >
        <h2
          style={{
            fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.INTRO_TITLE,
            fontFamily: VISUAL_CONFIG.TYPOGRAPHY.FONTS.DISPLAY,
            fontWeight: VISUAL_CONFIG.TYPOGRAPHY.WEIGHTS.BLACK,
            color: VISUAL_CONFIG.COLORS.PRIMARY,
            textShadow: VISUAL_CONFIG.EFFECTS.SHADOWS.TEXT,
            margin: 0,
          }}
        >
          Thanks for Watching!
        </h2>
      </div>
      
      {/* CTA Button */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.OUTRO.CTA.y,
          left: '50%',
          transform: `translateX(-50%) scale(${ctaPulse})`,
        }}
      >
        <button
          style={{
            width: LAYOUTS.OUTRO.CTA.buttonWidth,
            height: LAYOUTS.OUTRO.CTA.buttonHeight,
            backgroundColor: VISUAL_CONFIG.COLORS.ACCENT,
            color: VISUAL_CONFIG.COLORS.BG_PRIMARY,
            fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.CTA_BUTTON,
            fontFamily: VISUAL_CONFIG.TYPOGRAPHY.FONTS.DISPLAY,
            fontWeight: VISUAL_CONFIG.TYPOGRAPHY.WEIGHTS.BOLD,
            border: 'none',
            borderRadius: VISUAL_CONFIG.EFFECTS.RADIUS.PILL,
            boxShadow: `0 0 40px ${VISUAL_CONFIG.COLORS.ACCENT}`,
            cursor: 'pointer',
          }}
        >
          {ctaText}
        </button>
      </div>
      
      {/* Subscribe Button */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.OUTRO.SUBSCRIBE.y,
          left: '50%',
          transform: 'translateX(-50%)',
        }}
      >
        <button
          style={{
            width: LAYOUTS.OUTRO.SUBSCRIBE.buttonWidth,
            height: LAYOUTS.OUTRO.SUBSCRIBE.buttonHeight,
            backgroundColor: COMPONENTS.SUBSCRIBE_BUTTON.platforms[platform].bg,
            color: COMPONENTS.SUBSCRIBE_BUTTON.platforms[platform].text,
            fontSize: 36,
            fontFamily: VISUAL_CONFIG.TYPOGRAPHY.FONTS.DISPLAY,
            fontWeight: VISUAL_CONFIG.TYPOGRAPHY.WEIGHTS.SEMIBOLD,
            border: 'none',
            borderRadius: VISUAL_CONFIG.EFFECTS.RADIUS.MEDIUM,
            boxShadow: VISUAL_CONFIG.EFFECTS.SHADOWS.MEDIUM,
          }}
        >
          {COMPONENTS.SUBSCRIBE_BUTTON.platforms[platform].icon} {subscribeCTA}
        </button>
      </div>
      
      {/* Social Icons */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.OUTRO.SOCIAL.y,
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          gap: LAYOUTS.OUTRO.SOCIAL.gap,
        }}
      >
        {['📱', '📷', '🎬'].map((icon, index) => (
          <div
            key={index}
            style={{
              fontSize: LAYOUTS.OUTRO.SOCIAL.iconSize,
              transform: `scale(${socialIconsStagger(index)})`,
            }}
          >
            {icon}
          </div>
        ))}
      </div>
      
      {/* Disclaimer */}
      {showDisclaimer && (
        <div
          style={{
            position: 'absolute',
            bottom: 40,
            width: '100%',
            textAlign: 'center',
            fontSize: 18,
            color: VISUAL_CONFIG.COLORS.TEXT_MUTED,
            padding: '0 60px',
          }}
        >
          *Affiliate links - We may earn commission
        </div>
      )}
    </AbsoluteFill>
  );
};

// ============================================================================
// HELPER COMPONENTS
// ============================================================================

const CountdownBadge: React.FC<{ rank: ProductRank; rotation: number }> = ({ rank, rotation }) => {
  const style = rank === 1 ? 'gold' : rank === 2 ? 'silver' : 'bronze';
  const config = COMPONENTS.COUNTDOWN_BADGE.styles[style];
  
  return (
    <div
      style={{
        position: 'absolute',
        top: LAYOUTS.PRODUCT.COUNTDOWN_BADGE.y,
        right: LAYOUTS.PRODUCT.COUNTDOWN_BADGE.x - 900,
        width: LAYOUTS.PRODUCT.COUNTDOWN_BADGE.SIZE,
        height: LAYOUTS.PRODUCT.COUNTDOWN_BADGE.SIZE,
        background: config.bg,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.COUNTDOWN_NUMBER,
        fontFamily: VISUAL_CONFIG.TYPOGRAPHY.FONTS.DISPLAY,
        fontWeight: VISUAL_CONFIG.TYPOGRAPHY.WEIGHTS.BLACK,
        color: config.text,
        border: `4px solid ${config.border}`,
        boxShadow: VISUAL_CONFIG.EFFECTS.SHADOWS.LARGE,
        transform: `rotate(${rotation * 360}deg)`,
      }}
    >
      #{rank}
    </div>
  );
};

const StarRating: React.FC<{ rating: number; progress: number }> = ({ rating, progress }) => {
  const stars = [];
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  
  for (let i = 0; i < 5; i++) {
    const filled = i < fullStars || (i === fullStars && hasHalfStar);
    const fillProgress = interpolate(
      progress,
      [i * 0.2, (i + 1) * 0.2],
      [0, 1],
      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
    );
    
    stars.push(
      <span
        key={i}
        style={{
          fontSize: COMPONENTS.STAR_RATING.sizes.medium,
          color: filled 
            ? `rgba(255, 164, 28, ${fillProgress})`
            : COMPONENTS.STAR_RATING.colors.empty,
          opacity: interpolate(fillProgress, [0, 1], [0.3, 1]),
        }}
      >
        ★
      </span>
    );
  }
  
  return (
    <div style={{ display: 'flex', gap: 4 }}>
      {stars}
      <span
        style={{
          marginLeft: 8,
          fontSize: VISUAL_CONFIG.TYPOGRAPHY.SIZES.RATING_TEXT,
          color: VISUAL_CONFIG.COLORS.TEXT_PRIMARY,
          fontWeight: VISUAL_CONFIG.TYPOGRAPHY.WEIGHTS.SEMIBOLD,
        }}
      >
        {rating.toFixed(1)}
      </span>
    </div>
  );
};

const Sparkles: React.FC<{ count: number }> = ({ count }) => {
  const frame = useCurrentFrame();
  
  return (
    <>
      {Array.from({ length: count }).map((_, i) => {
        const delay = i * 3;
        const x = Math.random() * 1080;
        const y = Math.random() * 1920;
        const size = Math.random() * 20 + 10;
        const opacity = Math.sin((frame - delay) * 0.1) * 0.5 + 0.5;
        
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: y,
              fontSize: size,
              opacity: opacity,
              transform: `rotate(${frame * 2}deg)`,
            }}
          >
            ✨
          </div>
        );
      })}
    </>
  );
};

// ============================================================================
// COMPOSITION REGISTRATION
// ============================================================================

export const ProductionCompositions = () => {
  return (
    <>
      <Composition
        id="ProductionCountdownVideo"
        component={ProductionCountdownVideo}
        durationInFrames={TIMING_30FPS.TOTAL_DURATION}
        fps={TIMING_30FPS.FPS}
        width={VISUAL_CONFIG.DIMENSIONS.WIDTH}
        height={VISUAL_CONFIG.DIMENSIONS.HEIGHT}
        schema={AirtableVideoDataSchema}
        defaultProps={{
          data: {
            videoTitle: "Top 5 Amazing Products",
            introPhoto: "https://example.com/intro.jpg",
            introMp3: "https://example.com/intro.mp3",
            product1: {
              title: "Product 1",
              price: "99.99",
              rating: 4.5,
              reviews: "1.2K",
              photo: "https://example.com/product1.jpg",
              description: "Amazing product description",
              mp3: "https://example.com/product1.mp3",
            },
            // ... other products
            outroPhoto: "https://example.com/outro.jpg",
            outroMp3: "https://example.com/outro.mp3",
          },
          platform: 'tiktok',
          transition: 'slide-up',
          enableDebug: false,
        }}
      />
    </>
  );
};