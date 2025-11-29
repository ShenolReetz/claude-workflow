import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';

interface GlitchTransitionProps {
  fromContent: React.ReactNode;
  toContent: React.ReactNode;
  startFrame: number;
  duration?: number;
  intensity?: number;
}

export const GlitchTransition: React.FC<GlitchTransitionProps> = ({
  fromContent,
  toContent,
  startFrame,
  duration = 20,
  intensity = 1,
}) => {
  const frame = useCurrentFrame();

  // Only show transition during the specified frame range
  if (frame < startFrame || frame > startFrame + duration) {
    return frame < startFrame ? <>{fromContent}</> : <>{toContent}</>;
  }

  const localFrame = frame - startFrame;
  const progress = localFrame / duration;

  // RGB split offset
  const rgbSplitAmount = interpolate(
    localFrame,
    [0, duration / 4, duration / 2, (duration * 3) / 4, duration],
    [0, 15 * intensity, 8 * intensity, 12 * intensity, 0],
    { extrapolateRight: 'clamp' }
  );

  // Horizontal glitch offset
  const glitchOffset = interpolate(
    localFrame,
    [0, duration / 3, (duration * 2) / 3, duration],
    [0, 30 * intensity, -25 * intensity, 0],
    { extrapolateRight: 'clamp' }
  );

  // Opacity crossfade
  const fromOpacity = interpolate(localFrame, [0, duration], [1, 0], { extrapolateRight: 'clamp' });
  const toOpacity = interpolate(localFrame, [0, duration], [0, 1], { extrapolateRight: 'clamp' });

  // Random horizontal slice effects
  const getRandomSlices = () => {
    const slices = [];
    const sliceCount = 8;
    const seed = Math.floor(localFrame / 2); // Change every 2 frames

    for (let i = 0; i < sliceCount; i++) {
      const yPos = (i / sliceCount) * 100;
      const height = 100 / sliceCount;
      const offset = ((Math.sin(seed + i) * 50) % 30) * intensity;
      const shouldGlitch = Math.abs(Math.sin(seed + i * 2)) > 0.5;

      if (shouldGlitch && localFrame > duration / 4 && localFrame < (duration * 3) / 4) {
        slices.push({
          yPos,
          height,
          offset,
        });
      }
    }
    return slices;
  };

  const slices = getRandomSlices();

  // Scan line effect
  const scanLinePosition = interpolate(localFrame, [0, duration], [0, 100], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill>
      {/* From content with RGB split */}
      <AbsoluteFill
        style={{
          opacity: fromOpacity,
        }}
      >
        {/* Red channel */}
        <AbsoluteFill
          style={{
            transform: `translateX(${rgbSplitAmount}px)`,
            mixBlendMode: 'screen',
            filter: 'brightness(1) contrast(1.2)',
          }}
        >
          <div style={{ filter: 'sepia(1) hue-rotate(-60deg) saturate(4)' }}>
            {fromContent}
          </div>
        </AbsoluteFill>

        {/* Green channel */}
        <AbsoluteFill
          style={{
            transform: `translateX(${-rgbSplitAmount / 2}px)`,
            mixBlendMode: 'screen',
          }}
        >
          <div style={{ filter: 'sepia(1) hue-rotate(50deg) saturate(4)' }}>
            {fromContent}
          </div>
        </AbsoluteFill>

        {/* Blue channel */}
        <AbsoluteFill
          style={{
            transform: `translateX(${-rgbSplitAmount}px)`,
            mixBlendMode: 'screen',
          }}
        >
          <div style={{ filter: 'sepia(1) hue-rotate(170deg) saturate(4)' }}>
            {fromContent}
          </div>
        </AbsoluteFill>

        {/* Horizontal slices */}
        {slices.map((slice, index) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              left: 0,
              top: `${slice.yPos}%`,
              width: '100%',
              height: `${slice.height}%`,
              overflow: 'hidden',
              transform: `translateX(${slice.offset}px)`,
            }}
          >
            <div
              style={{
                position: 'absolute',
                left: 0,
                top: `-${slice.yPos}%`,
                width: '100%',
                height: `${100 / (slice.height / 100)}%`,
              }}
            >
              {fromContent}
            </div>
          </div>
        ))}
      </AbsoluteFill>

      {/* To content with glitch */}
      <AbsoluteFill
        style={{
          opacity: toOpacity,
          transform: `translateX(${glitchOffset}px)`,
        }}
      >
        {toContent}
      </AbsoluteFill>

      {/* Scan lines overlay */}
      <AbsoluteFill
        style={{
          background: `repeating-linear-gradient(
            0deg,
            rgba(0, 0, 0, 0.15),
            rgba(0, 0, 0, 0.15) 1px,
            transparent 1px,
            transparent 3px
          )`,
          pointerEvents: 'none',
          opacity: interpolate(
            localFrame,
            [0, duration / 4, (duration * 3) / 4, duration],
            [0, 0.5, 0.5, 0],
            { extrapolateRight: 'clamp' }
          ),
        }}
      />

      {/* Moving scan line */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: `${scanLinePosition}%`,
          width: '100%',
          height: '4px',
          background: 'linear-gradient(to bottom, transparent, rgba(255, 255, 255, 0.3), transparent)',
          boxShadow: '0 0 10px rgba(255, 255, 255, 0.5)',
          pointerEvents: 'none',
          opacity: interpolate(
            localFrame,
            [0, duration / 4, (duration * 3) / 4, duration],
            [0, 0.8, 0.8, 0],
            { extrapolateRight: 'clamp' }
          ),
        }}
      />

      {/* Noise overlay */}
      <AbsoluteFill
        style={{
          background: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          opacity: interpolate(
            localFrame,
            [0, duration / 2, duration],
            [0, 0.15 * intensity, 0],
            { extrapolateRight: 'clamp' }
          ),
          mixBlendMode: 'overlay',
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};

// Quick glitch flash effect (very short duration)
export const GlitchFlash: React.FC<{
  content: React.ReactNode;
  triggerFrame: number;
}> = ({ content, triggerFrame }) => {
  const frame = useCurrentFrame();

  if (frame < triggerFrame || frame > triggerFrame + 5) {
    return <>{content}</>;
  }

  const localFrame = frame - triggerFrame;
  const rgbSplit = interpolate(localFrame, [0, 2, 5], [0, 20, 0], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ transform: `translateX(${rgbSplit}px)`, filter: 'sepia(1) hue-rotate(-60deg) saturate(4)', mixBlendMode: 'screen' }}>
        {content}
      </AbsoluteFill>
      <AbsoluteFill style={{ transform: `translateX(${-rgbSplit}px)`, filter: 'sepia(1) hue-rotate(170deg) saturate(4)', mixBlendMode: 'screen' }}>
        {content}
      </AbsoluteFill>
      <AbsoluteFill>{content}</AbsoluteFill>
    </AbsoluteFill>
  );
};
