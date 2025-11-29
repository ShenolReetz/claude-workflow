import React from 'react';
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, Img, Audio, interpolate, spring } from 'remotion';
import { z } from 'zod';

// WOW Schema Types
export const WowMetaSchema = z.object({
  fps: z.number().default(30),
  width: z.number().default(1080),
  height: z.number().default(1920),
  max_total_frames: z.number().default(1650), // Updated to match 55 seconds
  brand: z.string().default('default'),
  primary_color: z.string().default('#00D3A7'),
});

export const WowProductSchema = z.object({
  rank: z.number(),
  name: z.string(),
  subtitle: z.string(),
  bg_image_url: z.string(),
  ken_burns: z.object({
    zoom_start: z.number(),
    zoom_end: z.number(),
    pan: z.enum(['up', 'down', 'left', 'right', 'none']),
  }),
  rating: z.number(),
  reviews_count: z.number(),
  price: z.number(),
  currency: z.string().default('EUR'),
  discount_pct: z.number().default(0),
  feature_chips: z.array(z.string()).default([]),
  layout: z.enum(['image-left', 'image-right', 'split', 'full']).default('full'),
  transition_in: z.enum(['slide', 'wipe', 'circle', 'glitch', 'whip-pan', 'depth-blur']),
  transition_out: z.enum(['slide', 'wipe', 'circle', 'glitch', 'whip-pan', 'depth-blur']),
});

export const WowVideoPropsSchema = z.object({
  meta: WowMetaSchema,
  timeline: z.object({
    intro_frames: z.number().default(150),
    product_frames: z.number().default(270),
    outro_frames: z.number().default(150),
    transition_overlap_frames: z.number().default(30), // Overlap for visual smoothness only
  }),
  safe_margins: z.object({
    top: z.number().default(96),
    bottom: z.number().default(96),
    left: z.number().default(48),
    right: z.number().default(48),
  }).optional(),
  audio: z.object({
    voiceover_url: z.string().nullable().optional(),
    music_url: z.string().nullable().optional(),
    music_ducking_db: z.number().default(-12),
  }).optional(),
  intro: z.object({
    title: z.string(),
    bg_image_url: z.string(),
    caption_style: z.enum(['karaoke', 'static']).default('karaoke'),
    captions: z.array(z.object({
      start: z.number(),
      end: z.number(),
      text: z.string(),
      words: z.array(z.object({
        w: z.string(),
        t0: z.number(),
        t1: z.number(),
      })).optional(),
    })).optional(),
    transition_out: z.enum(['slide', 'wipe', 'circle', 'glitch', 'whip-pan', 'depth-blur']),
  }),
  products: z.array(WowProductSchema).min(5).max(5),
  outro: z.object({
    bg_image_url: z.string(),
    cta_text: z.string(),
    cta_animation: z.enum(['shimmer', 'pulse', 'bounce']).default('shimmer'),
    legal_note: z.string().optional(),
    transition_in: z.enum(['slide', 'wipe', 'circle', 'glitch', 'whip-pan', 'depth-blur']),
  }),
  overlays: z.object({
    show_progress_bar: z.boolean().default(true),
    caption_style: z.enum(['karaoke', 'static']).default('karaoke'),
  }).optional(),
  datasource: z.object({
    type: z.string(),
    airtable: z.object({
      base: z.string(),
      table: z.string(),
      mapping: z.object({
        recordId: z.string(),
      }),
    }).optional(),
  }).optional(),
});

export type WowVideoProps = z.infer<typeof WowVideoPropsSchema>;

// Gradient Background Component
const GradientBackground: React.FC<{ 
  color1?: string; 
  color2?: string;
  style?: React.CSSProperties;
}> = ({ color1 = '#00D3A7', color2 = '#000000', style }) => {
  return (
    <div
      style={{
        position: 'absolute',
        width: '100%',
        height: '100%',
        background: `radial-gradient(circle at center, ${color1}, ${color2})`,
        ...style,
      }}
    />
  );
};

// Ken Burns Effect Component
const KenBurnsImage: React.FC<{
  src: string;
  kenBurns: WowVideoProps['products'][0]['ken_burns'];
  duration: number;
}> = ({ src, kenBurns, duration }) => {
  const frame = useCurrentFrame();
  
  const zoom = interpolate(
    frame,
    [0, duration],
    [kenBurns.zoom_start, kenBurns.zoom_end],
    { extrapolateRight: 'clamp' }
  );
  
  let translateX = 0;
  let translateY = 0;
  
  if (kenBurns.pan === 'up') {
    translateY = interpolate(frame, [0, duration], [0, -10], { extrapolateRight: 'clamp' });
  } else if (kenBurns.pan === 'down') {
    translateY = interpolate(frame, [0, duration], [0, 10], { extrapolateRight: 'clamp' });
  } else if (kenBurns.pan === 'left') {
    translateX = interpolate(frame, [0, duration], [0, -10], { extrapolateRight: 'clamp' });
  } else if (kenBurns.pan === 'right') {
    translateX = interpolate(frame, [0, duration], [0, 10], { extrapolateRight: 'clamp' });
  }
  
  // Handle missing images with gradient fallback
  if (!src || src === '' || src.startsWith('data:')) {
    return (
      <AbsoluteFill>
        <GradientBackground color1="#2a2a2a" color2="#000000" />
      </AbsoluteFill>
    );
  }
  
  return (
    <AbsoluteFill>
      <Img
        src={src}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${zoom}) translate(${translateX}px, ${translateY}px)`,
        }}
      />
    </AbsoluteFill>
  );
};

// Background with fallback
const BackgroundImage: React.FC<{ src: string; fallbackColor?: string }> = ({ src, fallbackColor = '#1a1a1a' }) => {
  if (!src || src === '' || src.startsWith('data:')) {
    return <GradientBackground color1={fallbackColor} color2="#000000" />;
  }
  
  return <Img src={src} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />;
};

// Product Card Component
const ProductCard: React.FC<{
  product: WowVideoProps['products'][0];
  safeMargins?: WowVideoProps['safe_margins'];
  primaryColor: string;
}> = ({ product, safeMargins, primaryColor }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Entrance animation
  const entrance = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });
  
  const slideIn = interpolate(entrance, [0, 1], [100, 0]);
  const opacity = interpolate(entrance, [0, 1], [0, 1]);
  
  return (
    <AbsoluteFill>
      {/* Background Image with Ken Burns */}
      <KenBurnsImage 
        src={product.bg_image_url} 
        kenBurns={product.ken_burns} 
        duration={270}
      />
      
      {/* Product Info Overlay */}
      <AbsoluteFill
        style={{
          padding: `${safeMargins?.top || 96}px ${safeMargins?.right || 48}px ${safeMargins?.bottom || 96}px ${safeMargins?.left || 48}px`,
          transform: `translateY(${slideIn}%)`,
          opacity,
        }}
      >
        {/* Rank Badge */}
        <div
          style={{
            position: 'absolute',
            top: 120,
            left: 48,
            backgroundColor: primaryColor,
            color: 'white',
            fontSize: 72,
            fontWeight: 'bold',
            width: 120,
            height: 120,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
          }}
        >
          #{product.rank}
        </div>
        
        {/* Product Info Card */}
        <div
          style={{
            position: 'absolute',
            bottom: 150,
            left: 48,
            right: 48,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderRadius: 24,
            padding: 32,
            boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
          }}
        >
          <h2 style={{ fontSize: 42, marginBottom: 16, color: '#333' }}>{product.name}</h2>
          <p style={{ fontSize: 28, color: '#666', marginBottom: 24 }}>{product.subtitle}</p>
          
          {/* Rating and Reviews */}
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
            <span style={{ fontSize: 32, color: '#FFD700' }}>
              {'★'.repeat(Math.floor(product.rating))}
              {'☆'.repeat(5 - Math.floor(product.rating))}
            </span>
            <span style={{ fontSize: 28, marginLeft: 16, color: '#666' }}>
              {product.rating.toFixed(1)} ({product.reviews_count.toLocaleString()} reviews)
            </span>
          </div>
          
          {/* Price */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 48, fontWeight: 'bold', color: primaryColor }}>
              {product.currency === 'EUR' ? '€' : '$'}{product.price.toFixed(2)}
            </span>
            {product.discount_pct > 0 && (
              <span style={{
                backgroundColor: '#FF4444',
                color: 'white',
                padding: '8px 16px',
                borderRadius: 8,
                fontSize: 24,
                fontWeight: 'bold',
              }}>
                {product.discount_pct}% OFF
              </span>
            )}
          </div>
          
          {/* Feature Chips */}
          {product.feature_chips.length > 0 && (
            <div style={{ display: 'flex', gap: 12, marginTop: 24, flexWrap: 'wrap' }}>
              {product.feature_chips.map((chip, i) => (
                <span
                  key={i}
                  style={{
                    backgroundColor: `${primaryColor}20`,
                    color: primaryColor,
                    padding: '8px 16px',
                    borderRadius: 20,
                    fontSize: 22,
                    border: `2px solid ${primaryColor}`,
                  }}
                >
                  {chip}
                </span>
              ))}
            </div>
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Main WOW Countdown Video Component
export const WowCountdownVideo: React.FC<WowVideoProps> = (props) => {
  const { fps, width, height } = useVideoConfig();
  const { timeline, intro, products, outro, meta, safe_margins } = props;
  
  // CORRECT Timeline Calculation - MUST be exactly 55 seconds (1650 frames)
  // The timeline is fixed and does not subtract overlap frames from total duration
  const TIMELINE = {
    intro: { start: 0, end: 150 },           // 0-149 (150 frames, 5 seconds)
    product5: { start: 150, end: 420 },      // 150-419 (270 frames, 9 seconds)
    product4: { start: 420, end: 690 },      // 420-689 (270 frames, 9 seconds)
    product3: { start: 690, end: 960 },      // 690-959 (270 frames, 9 seconds)
    product2: { start: 960, end: 1230 },     // 960-1229 (270 frames, 9 seconds)
    product1: { start: 1230, end: 1500 },    // 1230-1499 (270 frames, 9 seconds)
    outro: { start: 1500, end: 1650 },       // 1500-1649 (150 frames, 5 seconds)
  };
  
  // Verify total is 1650 frames (55 seconds)
  const currentFrame = useCurrentFrame();
  if (currentFrame > 1650) {
    console.error(`Frame ${currentFrame} exceeds maximum of 1650 frames (55 seconds)`);
  }
  
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {/* Intro Sequence - 5 seconds */}
      <Sequence from={TIMELINE.intro.start} durationInFrames={timeline.intro_frames}>
        <AbsoluteFill>
          <BackgroundImage src={intro.bg_image_url} fallbackColor="#00D3A7" />
          <AbsoluteFill style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            padding: safe_margins ? `${safe_margins.top}px ${safe_margins.right}px ${safe_margins.bottom}px ${safe_margins.left}px` : '96px 48px',
          }}>
            <h1 style={{
              fontSize: 64,
              color: 'white',
              textAlign: 'center',
              textShadow: '0 4px 16px rgba(0,0,0,0.8)',
              lineHeight: 1.2,
            }}>
              {intro.title}
            </h1>
            {intro.captions && intro.captions.map((caption, idx) => {
              const captionFrame = useCurrentFrame();
              const captionStart = caption.start * fps;
              const captionEnd = caption.end * fps;
              const isVisible = captionFrame >= captionStart && captionFrame <= captionEnd;
              
              if (!isVisible) return null;
              
              return (
                <p key={idx} style={{
                  fontSize: 36,
                  color: 'white',
                  textAlign: 'center',
                  marginTop: 24,
                  textShadow: '0 2px 8px rgba(0,0,0,0.8)',
                }}>
                  {caption.text}
                </p>
              );
            })}
          </AbsoluteFill>
        </AbsoluteFill>
      </Sequence>
      
      {/* Product 5 - 9 seconds */}
      <Sequence 
        from={TIMELINE.product5.start} 
        durationInFrames={timeline.product_frames}
      >
        <ProductCard 
          product={products[4]} 
          safeMargins={safe_margins}
          primaryColor={meta.primary_color}
        />
      </Sequence>
      
      {/* Product 4 - 9 seconds */}
      <Sequence 
        from={TIMELINE.product4.start} 
        durationInFrames={timeline.product_frames}
      >
        <ProductCard 
          product={products[3]} 
          safeMargins={safe_margins}
          primaryColor={meta.primary_color}
        />
      </Sequence>
      
      {/* Product 3 - 9 seconds */}
      <Sequence 
        from={TIMELINE.product3.start} 
        durationInFrames={timeline.product_frames}
      >
        <ProductCard 
          product={products[2]} 
          safeMargins={safe_margins}
          primaryColor={meta.primary_color}
        />
      </Sequence>
      
      {/* Product 2 - 9 seconds */}
      <Sequence 
        from={TIMELINE.product2.start} 
        durationInFrames={timeline.product_frames}
      >
        <ProductCard 
          product={products[1]} 
          safeMargins={safe_margins}
          primaryColor={meta.primary_color}
        />
      </Sequence>
      
      {/* Product 1 - 9 seconds */}
      <Sequence 
        from={TIMELINE.product1.start} 
        durationInFrames={timeline.product_frames}
      >
        <ProductCard 
          product={products[0]} 
          safeMargins={safe_margins}
          primaryColor={meta.primary_color}
        />
      </Sequence>
      
      {/* Outro Sequence - 5 seconds */}
      <Sequence from={TIMELINE.outro.start} durationInFrames={timeline.outro_frames}>
        <AbsoluteFill>
          <BackgroundImage src={outro.bg_image_url} fallbackColor="#FF9900" />
          <AbsoluteFill style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            padding: safe_margins ? `${safe_margins.top}px ${safe_margins.right}px ${safe_margins.bottom}px ${safe_margins.left}px` : '96px 48px',
          }}>
            <h2 style={{
              fontSize: 72,
              color: 'white',
              textAlign: 'center',
              marginBottom: 32,
              textShadow: '0 4px 16px rgba(0,0,0,0.8)',
            }}>
              {outro.cta_text}
            </h2>
            {outro.legal_note && (
              <p style={{
                fontSize: 24,
                color: 'rgba(255,255,255,0.8)',
                textAlign: 'center',
              }}>
                {outro.legal_note}
              </p>
            )}
          </AbsoluteFill>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};