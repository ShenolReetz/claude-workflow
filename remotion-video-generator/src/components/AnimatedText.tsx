import React from 'react';
import { interpolate, useCurrentFrame, spring, useVideoConfig } from 'remotion';
import { STYLES } from '../schemas/CountdownVideoSchema';

interface AnimatedTextProps {
  text: string;
  startFrame?: number;
  style?: React.CSSProperties;
  animationType?: 'bounce' | 'slide' | 'fade' | 'zoom' | 'wave';
  staggerDelay?: number; // frames between each word
  fontSize?: number;
  fontWeight?: number;
  color?: string;
  textAlign?: 'left' | 'center' | 'right';
}

export const AnimatedText: React.FC<AnimatedTextProps> = ({
  text,
  startFrame = 0,
  style = {},
  animationType = 'bounce',
  staggerDelay = 3,
  fontSize = 48,
  fontWeight = 700,
  color = '#FFFFFF',
  textAlign = 'center',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const words = text.split(' ');

  const getWordAnimation = (wordIndex: number) => {
    const wordStartFrame = startFrame + wordIndex * staggerDelay;
    const localFrame = frame - wordStartFrame;

    switch (animationType) {
      case 'bounce': {
        const scale = spring({
          frame: localFrame,
          fps,
          from: 0,
          to: 1,
          config: {
            damping: 8,
            stiffness: 200,
          },
        });

        const opacity = interpolate(
          localFrame,
          [0, 5],
          [0, 1],
          { extrapolateRight: 'clamp' }
        );

        return {
          transform: `scale(${scale})`,
          opacity,
        };
      }

      case 'slide': {
        const translateX = spring({
          frame: localFrame,
          fps,
          from: -50,
          to: 0,
          config: {
            damping: 15,
            stiffness: 100,
          },
        });

        const opacity = interpolate(
          localFrame,
          [0, 10],
          [0, 1],
          { extrapolateRight: 'clamp' }
        );

        return {
          transform: `translateX(${translateX}px)`,
          opacity,
        };
      }

      case 'fade': {
        const opacity = interpolate(
          localFrame,
          [0, 15],
          [0, 1],
          { extrapolateRight: 'clamp' }
        );

        return {
          opacity,
        };
      }

      case 'zoom': {
        const scale = spring({
          frame: localFrame,
          fps,
          from: 2,
          to: 1,
          config: {
            damping: 12,
            stiffness: 150,
          },
        });

        const opacity = interpolate(
          localFrame,
          [0, 8],
          [0, 1],
          { extrapolateRight: 'clamp' }
        );

        return {
          transform: `scale(${scale})`,
          opacity,
        };
      }

      case 'wave': {
        const translateY = spring({
          frame: localFrame,
          fps,
          from: 30,
          to: 0,
          config: {
            damping: 10,
            stiffness: 180,
          },
        });

        const opacity = interpolate(
          localFrame,
          [0, 8],
          [0, 1],
          { extrapolateRight: 'clamp' }
        );

        // Add continuous wave effect after initial animation
        const waveOffset = interpolate(
          (frame + wordIndex * 10) % 60,
          [0, 30, 60],
          [0, -5, 0],
          { extrapolateRight: 'wrap' }
        );

        return {
          transform: `translateY(${translateY + waveOffset}px)`,
          opacity,
        };
      }

      default:
        return { opacity: 1 };
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.3em',
        justifyContent: textAlign === 'center' ? 'center' : textAlign === 'right' ? 'flex-end' : 'flex-start',
        fontFamily: STYLES.FONTS.DISPLAY,
        fontSize,
        fontWeight,
        color,
        ...style,
      }}
    >
      {words.map((word, index) => (
        <span
          key={index}
          style={{
            display: 'inline-block',
            ...getWordAnimation(index),
            textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
          }}
        >
          {word}
        </span>
      ))}
    </div>
  );
};

// Specialized text component for product titles
export const ProductTitleText: React.FC<{
  text: string;
  startFrame?: number;
}> = ({ text, startFrame = 10 }) => (
  <AnimatedText
    text={text}
    startFrame={startFrame}
    animationType="bounce"
    fontSize={56}
    fontWeight={800}
    color="#FFFFFF"
    textAlign="center"
    staggerDelay={4}
    style={{
      textTransform: 'uppercase',
      letterSpacing: '0.02em',
      textShadow: '0 4px 12px rgba(0, 0, 0, 0.5), 0 0 20px rgba(255, 255, 255, 0.1)',
    }}
  />
);

// Specialized text component for callouts/highlights
export const CalloutText: React.FC<{
  text: string;
  startFrame?: number;
  accentColor?: string;
}> = ({ text, startFrame = 20, accentColor = '#FF9900' }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const backgroundPulse = interpolate(
    frame % 60,
    [0, 30, 60],
    [0.8, 1, 0.8],
    { extrapolateRight: 'wrap' }
  );

  return (
    <div
      style={{
        padding: '16px 32px',
        background: `linear-gradient(135deg, ${accentColor} 0%, ${accentColor}dd 100%)`,
        borderRadius: STYLES.RADIUS.MEDIUM,
        transform: `scale(${backgroundPulse})`,
        boxShadow: `0 8px 24px rgba(0, 0, 0, 0.4), 0 0 ${30 * backgroundPulse}px ${accentColor}${Math.floor(backgroundPulse * 50).toString(16)}`,
      }}
    >
      <AnimatedText
        text={text}
        startFrame={startFrame}
        animationType="zoom"
        fontSize={36}
        fontWeight={800}
        color="#FFFFFF"
        textAlign="center"
        staggerDelay={2}
      />
    </div>
  );
};

// Specialized text for descriptions
export const DescriptionText: React.FC<{
  text: string;
  startFrame?: number;
}> = ({ text, startFrame = 30 }) => (
  <AnimatedText
    text={text}
    startFrame={startFrame}
    animationType="fade"
    fontSize={28}
    fontWeight={500}
    color="#E0E0E0"
    textAlign="center"
    staggerDelay={2}
    style={{
      lineHeight: '1.6',
      maxWidth: '80%',
      margin: '0 auto',
    }}
  />
);

// Typewriter effect text
export const TypewriterText: React.FC<{
  text: string;
  startFrame?: number;
  speed?: number; // characters per frame
}> = ({ text, startFrame = 0, speed = 0.5 }) => {
  const frame = useCurrentFrame();

  const charsToShow = Math.floor(Math.max(0, (frame - startFrame) * speed));
  const visibleText = text.substring(0, charsToShow);

  // Blinking cursor
  const cursorOpacity = interpolate(
    frame % 30,
    [0, 15, 30],
    [1, 0, 1],
    { extrapolateRight: 'wrap' }
  );

  return (
    <div
      style={{
        fontFamily: STYLES.FONTS.PRIMARY,
        fontSize: 32,
        fontWeight: 600,
        color: '#FFFFFF',
        textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
      }}
    >
      {visibleText}
      {charsToShow < text.length && (
        <span style={{ opacity: cursorOpacity }}>|</span>
      )}
    </div>
  );
};
