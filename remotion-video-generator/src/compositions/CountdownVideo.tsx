import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { CountdownVideoData, TIMING, STYLES, LAYOUTS, ANIMATIONS } from '../schemas/CountdownVideoSchema';
import { IntroScene } from '../components/IntroScene';
import { ProductCard } from '../components/ProductCard';
import { OutroScene } from '../components/OutroScene';
import { TransitionWrapper } from '../components/TransitionWrapper';

interface CountdownVideoProps {
  data: CountdownVideoData;
}

export const CountdownVideo: React.FC<CountdownVideoProps> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  
  // Calculate current section for background effects
  const currentSection = React.useMemo(() => {
    if (frame < TIMING.INTRO.END) return 'intro';
    if (frame < TIMING.PRODUCT_5.END) return 'product5';
    if (frame < TIMING.PRODUCT_4.END) return 'product4';
    if (frame < TIMING.PRODUCT_3.END) return 'product3';
    if (frame < TIMING.PRODUCT_2.END) return 'product2';
    if (frame < TIMING.PRODUCT_1.END) return 'product1';
    return 'outro';
  }, [frame]);
  
  // Dynamic background gradient based on section
  const backgroundGradient = React.useMemo(() => {
    const colors = {
      intro: `linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)`,
      product5: `linear-gradient(135deg, #1a1a1a 0%, #2a2a3a 100%)`,
      product4: `linear-gradient(135deg, #1a1a1a 0%, #2a3a3a 100%)`,
      product3: `linear-gradient(135deg, #1a1a1a 0%, #3a3a2a 100%)`,
      product2: `linear-gradient(135deg, #1a1a1a 0%, #3a2a2a 100%)`,
      product1: `linear-gradient(135deg, #1a1a1a 0%, #3a2a1a 100%)`,
      outro: `linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)`,
    };
    return colors[currentSection];
  }, [currentSection]);
  
  // Global parallax effect
  const parallaxOffset = interpolate(
    frame,
    [0, TIMING.TOTAL_DURATION],
    [0, -100],
    {
      extrapolateRight: 'clamp',
    }
  );
  
  return (
    <AbsoluteFill
      style={{
        backgroundColor: STYLES.COLORS.BACKGROUND,
        background: backgroundGradient,
      }}
    >
      {/* Background Pattern */}
      <AbsoluteFill
        style={{
          opacity: 0.05,
          transform: `translateY(${parallaxOffset}px)`,
        }}
      >
        <div
          style={{
            width: '100%',
            height: '100%',
            backgroundImage: `repeating-linear-gradient(
              45deg,
              transparent,
              transparent 10px,
              rgba(255, 255, 0, 0.1) 10px,
              rgba(255, 255, 0, 0.1) 20px
            )`,
          }}
        />
      </AbsoluteFill>
      
      {/* Intro Sequence */}
      <Sequence
        from={TIMING.INTRO.START}
        durationInFrames={TIMING.INTRO.DURATION}
      >
        <TransitionWrapper
          type="scale-in"
          duration={ANIMATIONS.FADE_IN}
        >
          <IntroScene
            title={data.videoTitle}
            backgroundImage={data.introPhoto}
            brandColor={data.brandColor}
          />
        </TransitionWrapper>
        <Audio src={data.introMp3} volume={1} />
      </Sequence>
      
      {/* Product Cards */}
      {data.products.map((product, index) => {
        const rank = 5 - index;
        const timingKey = `PRODUCT_${rank}` as keyof typeof TIMING;
        const timing = TIMING[timingKey];
        
        return (
          <Sequence
            key={`product-${rank}`}
            from={timing.START}
            durationInFrames={timing.DURATION}
          >
            <TransitionWrapper
              type={index % 2 === 0 ? 'slide-left' : 'slide-right'}
              duration={ANIMATIONS.SLIDE_DURATION}
            >
              <ProductCard
                rank={rank}
                product={product}
                isLast={rank === 1}
                brandColor={data.brandColor}
                accentColor={data.accentColor}
              />
            </TransitionWrapper>
            <Audio
              src={product.mp3}
              volume={1}
              startFrom={0}
            />
          </Sequence>
        );
      })}
      
      {/* Outro Sequence */}
      <Sequence
        from={TIMING.OUTRO.START}
        durationInFrames={TIMING.OUTRO.DURATION}
      >
        <TransitionWrapper
          type="scale-in"
          duration={ANIMATIONS.FADE_IN}
        >
          <OutroScene
            backgroundImage={data.outroPhoto}
            brandColor={data.brandColor}
          />
        </TransitionWrapper>
        <Audio src={data.outroMp3} volume={1} />
      </Sequence>
      
      {/* Global Vignette Effect */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(
            ellipse at center,
            transparent 0%,
            transparent 50%,
            rgba(0, 0, 0, 0.3) 100%
          )`,
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};

// Export composition configuration
export const countdownVideoConfig = {
  id: 'CountdownVideo',
  component: CountdownVideo,
  durationInFrames: TIMING.TOTAL_DURATION,
  fps: TIMING.FPS,
  width: STYLES.VIDEO_WIDTH,
  height: STYLES.VIDEO_HEIGHT,
  defaultProps: {
    data: null, // Will be provided at render time
  },
};