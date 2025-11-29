import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { ANIMATIONS, TRANSITIONS } from '../schemas/CountdownVideoSchema';

interface TransitionWrapperProps {
  children: React.ReactNode;
  type: string;
  duration: number;
  delay?: number;
}

export const TransitionWrapper: React.FC<TransitionWrapperProps> = ({
  children,
  type,
  duration,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const startFrame = frame - delay;
  
  // Calculate transition progress
  const progress = interpolate(
    startFrame,
    [0, duration],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  // Get transition styles based on type
  const getTransitionStyles = (): React.CSSProperties => {
    switch (type) {
      case TRANSITIONS.CROSSFADE:
        return {
          opacity: progress,
        };
      
      case TRANSITIONS.SLIDE_LEFT:
        return {
          transform: `translateX(${interpolate(progress, [0, 1], [100, 0])}%)`,
          opacity: interpolate(progress, [0, 0.3, 1], [0, 1, 1]),
        };
      
      case TRANSITIONS.SLIDE_RIGHT:
        return {
          transform: `translateX(${interpolate(progress, [0, 1], [-100, 0])}%)`,
          opacity: interpolate(progress, [0, 0.3, 1], [0, 1, 1]),
        };
      
      case TRANSITIONS.SLIDE_UP:
        return {
          transform: `translateY(${interpolate(progress, [0, 1], [100, 0])}%)`,
          opacity: interpolate(progress, [0, 0.3, 1], [0, 1, 1]),
        };
      
      case TRANSITIONS.SCALE_IN:
        const scale = spring({
          frame: startFrame,
          fps,
          from: 0.5,
          to: 1,
          config: ANIMATIONS.SMOOTH_SPRING,
        });
        return {
          transform: `scale(${scale})`,
          opacity: progress,
        };
      
      case TRANSITIONS.ROTATE_IN:
        const rotation = spring({
          frame: startFrame,
          fps,
          from: -90,
          to: 0,
          config: ANIMATIONS.SPRING_CONFIG,
        });
        return {
          transform: `rotate(${rotation}deg) scale(${progress})`,
          opacity: progress,
        };
      
      case TRANSITIONS.BLUR_IN:
        return {
          filter: `blur(${interpolate(progress, [0, 1], [20, 0])}px)`,
          opacity: progress,
        };
      
      case TRANSITIONS.WIPE:
        return {
          clipPath: `polygon(
            0 0,
            ${progress * 100}% 0,
            ${progress * 100}% 100%,
            0 100%
          )`,
        };
      
      default:
        return { opacity: progress };
    }
  };
  
  // Exit transition (optional, for smoother sequences)
  const exitProgress = interpolate(
    frame,
    [duration - 10, duration],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  const exitStyles: React.CSSProperties = {
    opacity: exitProgress,
  };
  
  return (
    <AbsoluteFill
      style={{
        ...getTransitionStyles(),
        ...exitStyles,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};