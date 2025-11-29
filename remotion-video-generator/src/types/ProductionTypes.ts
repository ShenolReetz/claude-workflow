/**
 * TypeScript type definitions for production video generation
 * Provides strong typing for all video components and props
 */

import { SpringConfig } from 'remotion';
import { z } from 'zod';
import { 
  AirtableProductSchema, 
  AirtableVideoDataSchema,
  TIMING_30FPS,
  VISUAL_CONFIG,
  ANIMATIONS,
  LAYOUTS,
  COMPONENTS,
} from '../schemas/ProductionVideoSchema';

// ============================================================================
// BASE TYPES
// ============================================================================

export type Product = z.infer<typeof AirtableProductSchema>;
export type VideoData = z.infer<typeof AirtableVideoDataSchema>;

export type ProductRank = 1 | 2 | 3 | 4 | 5;

export type TransitionType = 
  | 'fade'
  | 'slide-left'
  | 'slide-right'
  | 'slide-up'
  | 'slide-down'
  | 'scale'
  | 'rotate'
  | 'flip'
  | 'zoom-blur'
  | 'wipe'
  | 'glitch';

export type BadgeType = 
  | 'BEST_SELLER'
  | 'AMAZON_CHOICE'
  | 'LIMITED_DEAL'
  | 'TOP_RATED';

export type Platform = 
  | 'tiktok'
  | 'instagram'
  | 'youtube';

// ============================================================================
// COMPONENT PROPS
// ============================================================================

/**
 * Props for the main CountdownVideo component
 */
export interface CountdownVideoProps {
  data: VideoData;
  platform?: Platform;
  transition?: TransitionType;
  enableDebug?: boolean;
}

/**
 * Props for IntroScene component
 */
export interface IntroSceneProps {
  title: string;
  subtitle?: string;
  imageUrl: string;
  audioUrl: string;
  brandColors?: {
    primary: string;
    accent: string;
    background: string;
  };
  animationType?: 'fade' | 'slide' | 'zoom' | 'rotate';
}

/**
 * Props for ProductScene component
 */
export interface ProductSceneProps {
  product: Product;
  rank: ProductRank;
  transitionIn?: TransitionType;
  transitionOut?: TransitionType;
  showBadge?: boolean;
  badgeType?: BadgeType;
  enableParallax?: boolean;
}

/**
 * Props for OutroScene component
 */
export interface OutroSceneProps {
  imageUrl: string;
  audioUrl: string;
  ctaText?: string;
  subscribeCTA?: string;
  platform?: Platform;
  socialHandles?: {
    tiktok?: string;
    instagram?: string;
    youtube?: string;
  };
  showDisclaimer?: boolean;
}

/**
 * Props for StarRating component
 */
export interface StarRatingProps {
  rating: number;
  maxRating?: number;
  size?: 'small' | 'medium' | 'large';
  showNumber?: boolean;
  animated?: boolean;
  color?: string;
  emptyColor?: string;
  glowEffect?: boolean;
}

/**
 * Props for PriceTag component
 */
export interface PriceTagProps {
  currentPrice: string | number;
  originalPrice?: string | number;
  discount?: number;
  currency?: string;
  size?: 'regular' | 'large';
  showGlow?: boolean;
  pulseAnimation?: boolean;
  color?: string;
}

/**
 * Props for CountdownBadge component
 */
export interface CountdownBadgeProps {
  rank: ProductRank;
  size?: 'small' | 'medium' | 'large';
  style?: 'gold' | 'silver' | 'bronze';
  animated?: boolean;
  springConfig?: SpringConfig;
  rotateAnimation?: boolean;
  pulseAnimation?: boolean;
}

/**
 * Props for ReviewCount component
 */
export interface ReviewCountProps {
  count: string | number;
  format?: 'full' | 'short' | 'compact';
  showBadge?: boolean;
  badgeThreshold?: 'hot' | 'trending' | 'popular';
  color?: string;
  fontSize?: number;
}

/**
 * Props for ProductBadge component
 */
export interface ProductBadgeProps {
  type: BadgeType;
  customText?: string;
  animated?: boolean;
  size?: 'small' | 'medium' | 'large';
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}

/**
 * Props for SubscribeButton component
 */
export interface SubscribeButtonProps {
  platform: Platform;
  text?: string;
  animated?: boolean;
  pulseEffect?: boolean;
  glowEffect?: boolean;
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
}

/**
 * Props for TransitionWrapper component
 */
export interface TransitionWrapperProps {
  type: TransitionType;
  duration?: number;
  delay?: number;
  easing?: keyof typeof ANIMATIONS.EASINGS;
  children: React.ReactNode;
}

/**
 * Props for AnimatedText component
 */
export interface AnimatedTextProps {
  text: string;
  fontSize?: number;
  fontWeight?: number;
  color?: string;
  animation?: 'typewriter' | 'fade' | 'slide' | 'scale' | 'blur';
  delay?: number;
  duration?: number;
  letterSpacing?: number;
  shadowEffect?: boolean;
}

/**
 * Props for ProductImage component
 */
export interface ProductImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  borderRadius?: number;
  shadow?: boolean;
  zoomEffect?: boolean;
  parallaxEffect?: boolean;
  blurredBackground?: boolean;
}

/**
 * Props for GlassCard component
 */
export interface GlassCardProps {
  children: React.ReactNode;
  padding?: number;
  borderRadius?: number;
  blurAmount?: number;
  opacity?: number;
  borderColor?: string;
  shadowEffect?: boolean;
}

// ============================================================================
// ANIMATION TYPES
// ============================================================================

/**
 * Animation configuration for components
 */
export interface AnimationConfig {
  type: keyof typeof ANIMATIONS.TRANSITIONS;
  duration: number;
  delay?: number;
  easing?: keyof typeof ANIMATIONS.EASINGS;
  springConfig?: SpringConfig;
}

/**
 * Keyframe animation definition
 */
export interface KeyframeAnimation {
  frames: Array<{
    [key: string]: number | string;
  }>;
  duration: number;
  loop?: boolean;
  easing?: keyof typeof ANIMATIONS.EASINGS;
}

/**
 * Parallax configuration
 */
export interface ParallaxConfig {
  layers: Array<{
    speed: number;
    offset: number;
    blur?: number;
  }>;
  direction?: 'vertical' | 'horizontal';
  intensity?: number;
}

// ============================================================================
// EFFECT TYPES
// ============================================================================

/**
 * Visual effect configuration
 */
export interface VisualEffect {
  blur?: number;
  brightness?: number;
  contrast?: number;
  grayscale?: number;
  hueRotate?: number;
  invert?: number;
  opacity?: number;
  saturate?: number;
  sepia?: number;
  dropShadow?: {
    x: number;
    y: number;
    blur: number;
    color: string;
  };
}

/**
 * Glow effect configuration
 */
export interface GlowEffect {
  color: string;
  intensity: number;
  radius: number;
  animated?: boolean;
  pulseSpeed?: number;
}

/**
 * Particle effect configuration
 */
export interface ParticleEffect {
  count: number;
  size: { min: number; max: number };
  speed: { min: number; max: number };
  color: string | string[];
  shape?: 'circle' | 'square' | 'star';
  fadeOut?: boolean;
}

// ============================================================================
// LAYOUT TYPES
// ============================================================================

/**
 * Component position configuration
 */
export interface Position {
  x: number;
  y: number;
  z?: number;
}

/**
 * Component dimensions
 */
export interface Dimensions {
  width: number;
  height: number;
  depth?: number;
}

/**
 * Safe zone configuration for mobile
 */
export interface SafeZone {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

/**
 * Grid layout configuration
 */
export interface GridLayout {
  columns: number;
  rows: number;
  gap: number;
  padding: number;
  alignItems?: 'start' | 'center' | 'end';
  justifyContent?: 'start' | 'center' | 'end' | 'space-between' | 'space-around';
}

// ============================================================================
// TIMING TYPES
// ============================================================================

/**
 * Scene timing configuration
 */
export interface SceneTiming {
  start: number;
  duration: number;
  end: number;
  transitions?: {
    in?: number;
    out?: number;
  };
}

/**
 * Animation timing configuration
 */
export interface AnimationTiming {
  delay: number;
  duration: number;
  stagger?: number;
  repeat?: number | 'infinite';
  yoyo?: boolean;
}

// ============================================================================
// STYLE TYPES
// ============================================================================

/**
 * Typography configuration
 */
export interface Typography {
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  lineHeight?: number;
  letterSpacing?: number;
  textAlign?: 'left' | 'center' | 'right' | 'justify';
  textTransform?: 'none' | 'uppercase' | 'lowercase' | 'capitalize';
  textDecoration?: 'none' | 'underline' | 'line-through';
}

/**
 * Color scheme configuration
 */
export interface ColorScheme {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
  textSecondary: string;
  success: string;
  warning: string;
  error: string;
}

/**
 * Shadow configuration
 */
export interface Shadow {
  x: number;
  y: number;
  blur: number;
  spread?: number;
  color: string;
  inset?: boolean;
}

/**
 * Gradient configuration
 */
export interface Gradient {
  type: 'linear' | 'radial' | 'conic';
  angle?: number;
  stops: Array<{
    color: string;
    position: number;
  }>;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Deep partial type for configuration objects
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * Configuration override type
 */
export type ConfigOverride<T> = DeepPartial<T>;

/**
 * Component variant type
 */
export type Variant<T extends string> = T | (string & {});

/**
 * Responsive value type
 */
export type ResponsiveValue<T> = T | {
  mobile?: T;
  tablet?: T;
  desktop?: T;
};

// ============================================================================
// HOOK RETURN TYPES
// ============================================================================

/**
 * Animation hook return type
 */
export interface UseAnimationReturn {
  style: React.CSSProperties;
  isAnimating: boolean;
  progress: number;
  start: () => void;
  stop: () => void;
  reset: () => void;
}

/**
 * Transition hook return type
 */
export interface UseTransitionReturn {
  style: React.CSSProperties;
  isTransitioning: boolean;
  phase: 'enter' | 'active' | 'exit';
}

/**
 * Parallax hook return type
 */
export interface UseParallaxReturn {
  layers: Array<{
    style: React.CSSProperties;
    ref: React.RefObject<HTMLDivElement>;
  }>;
  scrollProgress: number;
}

// ============================================================================
// CONSTANTS
// ============================================================================

export const FRAME_RATE = TIMING_30FPS.FPS;
export const VIDEO_WIDTH = VISUAL_CONFIG.DIMENSIONS.WIDTH;
export const VIDEO_HEIGHT = VISUAL_CONFIG.DIMENSIONS.HEIGHT;
export const SAFE_ZONES = VISUAL_CONFIG.SAFE_ZONES;
export const COLORS = VISUAL_CONFIG.COLORS;
export const FONTS = VISUAL_CONFIG.TYPOGRAPHY.FONTS;
export const FONT_SIZES = VISUAL_CONFIG.TYPOGRAPHY.SIZES;
export const COMPONENT_LAYOUTS = LAYOUTS;
export const COMPONENT_SPECS = COMPONENTS;

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Check if value is a valid product rank
 */
export function isProductRank(value: number): value is ProductRank {
  return value >= 1 && value <= 5;
}

/**
 * Check if value is a valid transition type
 */
export function isTransitionType(value: string): value is TransitionType {
  const validTypes: TransitionType[] = [
    'fade', 'slide-left', 'slide-right', 'slide-up', 'slide-down',
    'scale', 'rotate', 'flip', 'zoom-blur', 'wipe', 'glitch'
  ];
  return validTypes.includes(value as TransitionType);
}

/**
 * Check if value is a valid badge type
 */
export function isBadgeType(value: string): value is BadgeType {
  const validTypes: BadgeType[] = [
    'BEST_SELLER', 'AMAZON_CHOICE', 'LIMITED_DEAL', 'TOP_RATED'
  ];
  return validTypes.includes(value as BadgeType);
}

/**
 * Check if value is a valid platform
 */
export function isPlatform(value: string): value is Platform {
  const validPlatforms: Platform[] = ['tiktok', 'instagram', 'youtube'];
  return validPlatforms.includes(value as Platform);
}