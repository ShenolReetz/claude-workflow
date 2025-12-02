import React from 'react';
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  Img,
  Audio,
  interpolate,
  spring,
  Easing,
  Video,
  staticFile,
} from 'remotion';
import { z } from 'zod';

// ============================================
// SCHEMA DEFINITIONS
// ============================================

export const WowUltraSchema = z.object({
  // Video Configuration
  meta: z.object({
    fps: z.number().default(30),
    width: z.number().default(1080),
    height: z.number().default(1920),
    durationInSeconds: z.number().default(60),
  }),
  
  // Product Data
  products: z.array(z.object({
    rank: z.number(),
    title: z.string(),
    description: z.string(),
    price: z.number(),
    originalPrice: z.number().optional(),
    currency: z.string().default('$'),
    rating: z.number().min(0).max(5),
    reviewCount: z.number(),
    imageUrl: z.string(),
    videoUrl: z.string().optional(),
    features: z.array(z.string()).max(3),
    badge: z.enum(['BEST_SELLER', 'AMAZON_CHOICE', 'TOP_RATED', 'LIMITED_DEAL']).optional(),
    affiliateLink: z.string(),
    // Review highlights
    topReview: z.object({
      author: z.string(),
      rating: z.number(),
      title: z.string(),
      text: z.string(),
      verified: z.boolean(),
    }).optional(),
  })).length(5),
  
  // Audio & Subtitles
  audio: z.object({
    backgroundMusic: z.string().optional(),
    voiceoverUrl: z.string().optional(),
    subtitles: z.array(z.object({
      startTime: z.number(),
      endTime: z.number(),
      text: z.string(),
      productIndex: z.number().optional(), // Which product this subtitle relates to
    })),
  }),
  
  // Visual Effects
  effects: z.object({
    transitionStyle: z.enum(['swipe', 'morph', 'glitch', 'zoom', 'rotate3d', 'particle']).default('morph'),
    colorScheme: z.enum(['vibrant', 'dark', 'pastel', 'neon', 'gradient']).default('vibrant'),
    particleEffects: z.boolean().default(true),
    glowEffects: z.boolean().default(true),
    parallaxDepth: z.boolean().default(true),
  }),
  
  // Branding
  branding: z.object({
    logo: z.string().optional(),
    primaryColor: z.string().default('#FF6B35'),
    secondaryColor: z.string().default('#4ECDC4'),
    accentColor: z.string().default('#FFE66D'),
    fontFamily: z.string().default('Inter'),
  }),
});

export type WowUltraProps = z.infer<typeof WowUltraSchema>;

// ============================================
// ANIMATION UTILITIES
// ============================================

const useSpringAnimation = (frame: number, config = {}) => {
  return spring({
    frame,
    fps: 30,
    config: {
      damping: 100,
      stiffness: 200,
      mass: 0.5,
      ...config,
    },
  });
};

// ============================================
// PARTICLE SYSTEM COMPONENT
// ============================================

const ParticleSystem: React.FC<{ intensity?: number }> = ({ intensity = 1 }) => {
  const frame = useCurrentFrame();
  
  return (
    <AbsoluteFill>
      {[...Array(Math.floor(20 * intensity))].map((_, i) => {
        const delay = i * 3;
        const y = interpolate(
          (frame - delay) % 100,
          [0, 100],
          [1920, -50],
          { extrapolateLeft: 'clamp' }
        );
        
        const x = Math.sin(i) * 540 + 540;
        const opacity = interpolate(
          (frame - delay) % 100,
          [0, 20, 80, 100],
          [0, 1, 1, 0]
        );
        
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: y,
              width: 4,
              height: 4,
              borderRadius: '50%',
              background: `rgba(255, 255, 255, ${opacity * 0.8})`,
              boxShadow: '0 0 10px rgba(255, 255, 255, 0.5)',
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// ============================================
// AMAZON REVIEW CARD COMPONENT
// ============================================

const ReviewCard: React.FC<{
  review: any;
  startFrame: number;
  duration: number;
}> = ({ review, startFrame, duration }) => {
  const frame = useCurrentFrame();
  const progress = (frame - startFrame) / duration;
  
  const slideIn = interpolate(
    progress,
    [0, 0.1],
    [100, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  const opacity = interpolate(
    progress,
    [0, 0.1, 0.9, 1],
    [0, 1, 1, 0]
  );
  
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 200,
        left: 50,
        right: 50,
        transform: `translateY(${slideIn}px)`,
        opacity,
        background: 'linear-gradient(135deg, rgba(0,0,0,0.9), rgba(0,0,0,0.7))',
        borderRadius: 20,
        padding: 30,
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255,255,255,0.1)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 15 }}>
        <div style={{ marginRight: 15 }}>
          {/* Star Rating */}
          <div style={{ display: 'flex' }}>
            {[...Array(5)].map((_, i) => (
              <span
                key={i}
                style={{
                  color: i < review.rating ? '#FFA500' : '#444',
                  fontSize: 24,
                  marginRight: 2,
                }}
              >
                ★
              </span>
            ))}
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ color: '#FFF', fontWeight: 'bold', fontSize: 18 }}>
            {review.author}
          </div>
          {review.verified && (
            <div style={{ color: '#4CAF50', fontSize: 14 }}>
              ✓ Verified Purchase
            </div>
          )}
        </div>
      </div>
      <div style={{ color: '#FFF', fontSize: 20, fontWeight: 'bold', marginBottom: 10 }}>
        "{review.title}"
      </div>
      <div style={{ color: '#DDD', fontSize: 16, lineHeight: 1.5 }}>
        {review.text}
      </div>
    </div>
  );
};

// ============================================
// PRODUCT SHOWCASE COMPONENT
// ============================================

const ProductShowcase: React.FC<{
  product: any;
  index: number;
  startFrame: number;
  duration: number;
}> = ({ product, index, startFrame, duration }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const progress = Math.max(0, Math.min(1, (frame - startFrame) / duration));
  
  // Complex animations
  const zoomScale = interpolate(progress, [0, 0.5, 1], [1.2, 1, 1.1]);
  const rotateY = interpolate(progress, [0, 0.3, 0.7, 1], [90, 0, 0, -90]);
  const slideX = interpolate(
    progress,
    [0, 0.2, 0.8, 1],
    [-width, 0, 0, width],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  // Parallax effect for background
  const parallaxX = interpolate(progress, [0, 1], [-100, 100]);
  
  // Pulsing glow effect
  const glowIntensity = Math.sin(frame * 0.1) * 0.5 + 0.5;
  
  return (
    <AbsoluteFill>
      {/* Background Image with Parallax */}
      <div
        style={{
          position: 'absolute',
          left: -200,
          right: -200,
          top: -200,
          bottom: -200,
          transform: `translateX(${parallaxX}px) scale(${zoomScale})`,
        }}
      >
        <Img
          src={staticFile(product.imageUrl)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter: 'blur(8px) brightness(0.4)',
          }}
        />
      </div>
      
      {/* Gradient Overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `linear-gradient(
            135deg,
            rgba(255, 107, 53, ${0.3 * glowIntensity}),
            rgba(78, 205, 196, ${0.3 * glowIntensity})
          )`,
        }}
      />
      
      {/* Main Product Card */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: `
            translate(-50%, -50%)
            translateX(${slideX}px)
            rotateY(${rotateY}deg)
            perspective(1000px)
          `,
          transformStyle: 'preserve-3d',
          width: '80%',
          maxWidth: 900,
        }}
      >
        {/* Rank Badge */}
        <div
          style={{
            position: 'absolute',
            top: -80,
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'linear-gradient(135deg, #FFD700, #FFA500)',
            borderRadius: '50%',
            width: 120,
            height: 120,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 48,
            fontWeight: 'bold',
            color: '#000',
            boxShadow: `0 0 ${30 * glowIntensity}px rgba(255, 215, 0, 0.8)`,
            animation: 'pulse 2s infinite',
          }}
        >
          #{index + 1}
        </div>
        
        {/* Product Image */}
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: 30,
            overflow: 'hidden',
            boxShadow: `0 20px 60px rgba(0, 0, 0, 0.3)`,
          }}
        >
          <Img
            src={staticFile(product.imageUrl)}
            style={{
              width: '100%',
              height: 400,
              objectFit: 'contain',
              background: '#FFF',
            }}
          />
          
          {/* Product Info */}
          <div style={{ padding: 40 }}>
            {/* Title */}
            <h2
              style={{
                fontSize: 36,
                fontWeight: 'bold',
                color: '#000',
                marginBottom: 10,
                lineHeight: 1.2,
              }}
            >
              {product.title}
            </h2>
            
            {/* Rating and Reviews */}
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
              <div style={{ display: 'flex', marginRight: 10 }}>
                {[...Array(5)].map((_, i) => (
                  <span
                    key={i}
                    style={{
                      color: i < Math.floor(product.rating) ? '#FFA500' : '#DDD',
                      fontSize: 28,
                    }}
                  >
                    ★
                  </span>
                ))}
              </div>
              <span style={{ fontSize: 24, color: '#666' }}>
                {product.rating} ({product.reviewCount.toLocaleString()} reviews)
              </span>
            </div>
            
            {/* Price */}
            <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: 20 }}>
              <span style={{ fontSize: 48, fontWeight: 'bold', color: '#B12704' }}>
                {product.currency}{product.price}
              </span>
              {product.originalPrice && (
                <>
                  <span
                    style={{
                      fontSize: 28,
                      color: '#999',
                      textDecoration: 'line-through',
                      marginLeft: 15,
                    }}
                  >
                    {product.currency}{product.originalPrice}
                  </span>
                  <span
                    style={{
                      background: '#B12704',
                      color: '#FFF',
                      padding: '5px 15px',
                      borderRadius: 10,
                      marginLeft: 15,
                      fontSize: 20,
                      fontWeight: 'bold',
                    }}
                  >
                    -{Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100)}%
                  </span>
                </>
              )}
            </div>
            
            {/* Features */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {product.features.map((feature, i) => (
                <div
                  key={i}
                  style={{
                    background: 'linear-gradient(135deg, #4ECDC4, #44A3AA)',
                    color: '#FFF',
                    padding: '10px 20px',
                    borderRadius: 20,
                    fontSize: 18,
                    fontWeight: '500',
                  }}
                >
                  ✓ {feature}
                </div>
              ))}
            </div>
            
            {/* Badge */}
            {product.badge && (
              <div
                style={{
                  position: 'absolute',
                  top: 20,
                  right: 20,
                  background: product.badge === 'BEST_SELLER' ? '#FF6B35' : '#4ECDC4',
                  color: '#FFF',
                  padding: '10px 20px',
                  borderRadius: 10,
                  fontSize: 18,
                  fontWeight: 'bold',
                  transform: 'rotate(-5deg)',
                }}
              >
                {product.badge.replace('_', ' ')}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Show Review if available */}
      {product.topReview && progress > 0.5 && (
        <ReviewCard
          review={product.topReview}
          startFrame={startFrame + duration * 0.5}
          duration={duration * 0.4}
        />
      )}
    </AbsoluteFill>
  );
};

// ============================================
// ANIMATED SUBTITLE COMPONENT
// ============================================

const AnimatedSubtitle: React.FC<{
  subtitle: any;
  currentTime: number;
}> = ({ subtitle, currentTime }) => {
  const isActive = currentTime >= subtitle.startTime && currentTime <= subtitle.endTime;
  const progress = (currentTime - subtitle.startTime) / (subtitle.endTime - subtitle.startTime);
  
  if (!isActive) return null;
  
  const words = subtitle.text.split(' ');
  
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 150,
        left: 50,
        right: 50,
        textAlign: 'center',
        zIndex: 100,
      }}
    >
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(0,0,0,0.9), rgba(0,0,0,0.7))',
          backdropFilter: 'blur(20px)',
          borderRadius: 20,
          padding: '20px 30px',
          display: 'inline-block',
          border: '2px solid rgba(255, 255, 255, 0.2)',
        }}
      >
        {words.map((word, i) => {
          const wordProgress = interpolate(
            progress,
            [i / words.length, (i + 1) / words.length],
            [0, 1],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );
          
          return (
            <span
              key={i}
              style={{
                fontSize: 32,
                fontWeight: 'bold',
                marginRight: 8,
                display: 'inline-block',
                color: wordProgress > 0.5 ? '#FFE66D' : '#FFF',
                transform: `scale(${wordProgress > 0.5 ? 1.1 : 1})`,
                transition: 'all 0.3s',
                textShadow: wordProgress > 0.5 ? '0 0 20px rgba(255, 230, 109, 0.8)' : 'none',
              }}
            >
              {word}
            </span>
          );
        })}
      </div>
    </div>
  );
};

// ============================================
// INTRO SCENE COMPONENT
// ============================================

const IntroScene: React.FC<{
  duration: number;
  title: string;
  branding: any;
}> = ({ duration, title, branding }) => {
  const frame = useCurrentFrame();
  const progress = frame / duration;
  
  // Multiple layer animations
  const scale = interpolate(progress, [0, 0.5, 1], [0.8, 1.2, 1]);
  const rotation = interpolate(progress, [0, 1], [0, 360]);
  const opacity = interpolate(progress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
  
  return (
    <AbsoluteFill>
      {/* Animated gradient background */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `linear-gradient(
            ${rotation}deg,
            ${branding.primaryColor},
            ${branding.secondaryColor},
            ${branding.accentColor}
          )`,
        }}
      />
      
      {/* Particle effects */}
      <ParticleSystem intensity={2} />
      
      {/* Main title */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: `translate(-50%, -50%) scale(${scale})`,
          opacity,
          textAlign: 'center',
        }}
      >
        <h1
          style={{
            fontSize: 72,
            fontWeight: 'bold',
            color: '#FFF',
            textShadow: '0 0 40px rgba(0,0,0,0.5)',
            marginBottom: 20,
          }}
        >
          TOP 5
        </h1>
        <h2
          style={{
            fontSize: 48,
            color: '#FFF',
            textShadow: '0 0 30px rgba(0,0,0,0.3)',
          }}
        >
          {title}
        </h2>
        <div
          style={{
            marginTop: 40,
            fontSize: 28,
            color: '#FFE66D',
            fontWeight: '500',
          }}
        >
          You Won't Believe #1!
        </div>
      </div>
      
      {/* Countdown preview */}
      <div
        style={{
          position: 'absolute',
          bottom: 100,
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: 20,
          opacity: interpolate(progress, [0.5, 0.8], [0, 1]),
        }}
      >
        {[5, 4, 3, 2, 1].map((num) => (
          <div
            key={num}
            style={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.2)',
              backdropFilter: 'blur(10px)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 36,
              fontWeight: 'bold',
              color: '#FFF',
              border: '2px solid rgba(255, 255, 255, 0.3)',
            }}
          >
            {num}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ============================================
// OUTRO SCENE COMPONENT
// ============================================

const OutroScene: React.FC<{
  duration: number;
  branding: any;
}> = ({ duration, branding }) => {
  const frame = useCurrentFrame();
  const progress = frame / duration;
  
  const fadeIn = interpolate(progress, [0, 0.2], [0, 1]);
  const scaleButton = interpolate(
    progress,
    [0.3, 0.4, 0.5],
    [0, 1.2, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  // Pulsing effect
  const pulse = Math.sin(frame * 0.1) * 0.1 + 1;
  
  return (
    <AbsoluteFill>
      {/* Background */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `linear-gradient(135deg, ${branding.primaryColor}, ${branding.secondaryColor})`,
        }}
      />
      
      <ParticleSystem intensity={1} />
      
      {/* Content */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          opacity: fadeIn,
        }}
      >
        <h2
          style={{
            fontSize: 64,
            fontWeight: 'bold',
            color: '#FFF',
            marginBottom: 40,
            textShadow: '0 0 30px rgba(0,0,0,0.3)',
          }}
        >
          Thanks for Watching!
        </h2>
        
        {/* CTA Button */}
        <div
          style={{
            transform: `scale(${scaleButton * pulse})`,
            display: 'inline-block',
          }}
        >
          <div
            style={{
              background: 'linear-gradient(135deg, #FF6B35, #F7931E)',
              color: '#FFF',
              padding: '25px 60px',
              borderRadius: 50,
              fontSize: 32,
              fontWeight: 'bold',
              boxShadow: '0 10px 40px rgba(255, 107, 53, 0.5)',
              cursor: 'pointer',
            }}
          >
            🛒 Shop Now & Save!
          </div>
        </div>
        
        {/* Social icons */}
        <div
          style={{
            marginTop: 60,
            display: 'flex',
            justifyContent: 'center',
            gap: 30,
            opacity: interpolate(progress, [0.5, 0.7], [0, 1]),
          }}
        >
          {['👍', '💬', '🔔', '↗️'].map((icon, i) => (
            <div
              key={i}
              style={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 36,
                backdropFilter: 'blur(10px)',
                transform: `translateY(${interpolate(
                  progress,
                  [0.5 + i * 0.05, 0.6 + i * 0.05],
                  [50, 0]
                )}px)`,
              }}
            >
              {icon}
            </div>
          ))}
        </div>
        
        {/* Disclaimer */}
        <div
          style={{
            position: 'absolute',
            bottom: 50,
            left: 50,
            right: 50,
            fontSize: 14,
            color: 'rgba(255, 255, 255, 0.6)',
            textAlign: 'center',
          }}
        >
          As an Amazon Associate, we earn from qualifying purchases
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================
// MAIN WOW VIDEO COMPONENT
// ============================================

export const WowVideoUltra: React.FC<WowUltraProps> = (props) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const currentTime = frame / fps;
  
  // Calculate durations
  const introDuration = 5 * fps; // 5 seconds
  const productDuration = 10 * fps; // 10 seconds per product
  const outroDuration = 5 * fps; // 5 seconds
  
  // Find active subtitle
  const activeSubtitle = props.audio.subtitles.find(
    (sub) => currentTime >= sub.startTime && currentTime <= sub.endTime
  );
  
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {/* Intro */}
      <Sequence from={0} durationInFrames={introDuration}>
        <IntroScene
          duration={introDuration}
          title="Amazing Products"
          branding={props.branding}
        />
      </Sequence>
      
      {/* Products */}
      {props.products.map((product, index) => {
        const startFrame = introDuration + index * productDuration;
        
        return (
          <Sequence
            key={index}
            from={startFrame}
            durationInFrames={productDuration}
          >
            <ProductShowcase
              product={product}
              index={index}
              startFrame={startFrame}
              duration={productDuration}
            />
          </Sequence>
        );
      })}
      
      {/* Outro */}
      <Sequence
        from={introDuration + props.products.length * productDuration}
        durationInFrames={outroDuration}
      >
        <OutroScene duration={outroDuration} branding={props.branding} />
      </Sequence>
      
      {/* Subtitles Overlay */}
      {activeSubtitle && (
        <AnimatedSubtitle subtitle={activeSubtitle} currentTime={currentTime} />
      )}
      
      {/* Background Music */}
      {props.audio.backgroundMusic && (
        <Audio src={staticFile(props.audio.backgroundMusic)} volume={0.3} />
      )}
      
      {/* Voiceover */}
      {props.audio.voiceoverUrl && (
        <Audio src={props.audio.voiceoverUrl} volume={1} />
      )}
      
      {/* Progress Bar */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 4,
          background: 'rgba(255, 255, 255, 0.2)',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${(frame / (introDuration + props.products.length * productDuration + outroDuration)) * 100}%`,
            background: 'linear-gradient(90deg, #FF6B35, #F7931E)',
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes pulse {
    0% { transform: translateX(-50%) scale(1); }
    50% { transform: translateX(-50%) scale(1.1); }
    100% { transform: translateX(-50%) scale(1); }
  }
`;
document.head.appendChild(style);