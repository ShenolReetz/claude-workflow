import { z } from 'zod';

// Product data schema
export const ProductSchema = z.object({
  title: z.string(),
  price: z.string(),
  rating: z.number().min(0).max(5),
  reviews: z.number(),
  photo: z.string().url(),
  description: z.string(),
  mp3: z.string().url(),
});

// Complete video data schema
export const CountdownVideoSchema = z.object({
  // Video metadata
  videoTitle: z.string(),
  
  // Intro assets
  introPhoto: z.string().url(),
  introMp3: z.string().url(),
  
  // Products (ordered from 5 to 1)
  products: z.array(ProductSchema).length(5),
  
  // Outro assets
  outroPhoto: z.string().url(),
  outroMp3: z.string().url(),
  
  // Optional branding
  brandColor: z.string().default('#FFFF00'),
  accentColor: z.string().default('#FF9900'),
  backgroundColor: z.string().default('#000000'),
});

export type CountdownVideoData = z.infer<typeof CountdownVideoSchema>;

// Timing configuration (in frames at 60fps)
export const TIMING = {
  FPS: 60,
  TOTAL_DURATION: 55 * 60, // 3300 frames
  
  INTRO: {
    START: 0,
    DURATION: 5 * 60, // 300 frames
    END: 5 * 60,
  },
  
  PRODUCT_5: {
    START: 5 * 60,
    DURATION: 9 * 60, // 540 frames
    END: 14 * 60,
  },
  
  PRODUCT_4: {
    START: 14 * 60,
    DURATION: 9 * 60,
    END: 23 * 60,
  },
  
  PRODUCT_3: {
    START: 23 * 60,
    DURATION: 9 * 60,
    END: 32 * 60,
  },
  
  PRODUCT_2: {
    START: 32 * 60,
    DURATION: 9 * 60,
    END: 41 * 60,
  },
  
  PRODUCT_1: {
    START: 41 * 60,
    DURATION: 9 * 60,
    END: 50 * 60,
  },
  
  OUTRO: {
    START: 50 * 60,
    DURATION: 5 * 60,
    END: 55 * 60,
  },
};

// Animation presets
export const ANIMATIONS = {
  // Transition timings (in frames)
  FADE_IN: 15,
  FADE_OUT: 15,
  SLIDE_DURATION: 20,
  SCALE_DURATION: 30,
  
  // Spring configurations
  SPRING_CONFIG: {
    damping: 200,
    mass: 1,
    stiffness: 500,
    overshootClamping: false,
  },
  
  SMOOTH_SPRING: {
    damping: 100,
    mass: 0.8,
    stiffness: 200,
    overshootClamping: true,
  },
  
  BOUNCE_SPRING: {
    damping: 10,
    mass: 1,
    stiffness: 180,
    overshootClamping: false,
  },
};

// Visual style configuration
export const STYLES = {
  // Dimensions
  VIDEO_WIDTH: 1080,
  VIDEO_HEIGHT: 1920,
  
  // Safe zones for mobile
  SAFE_ZONE: {
    TOP: 120, // Account for notches
    BOTTOM: 100, // Account for UI elements
    SIDES: 60,
  },
  
  // Typography
  FONTS: {
    PRIMARY: 'Inter',
    DISPLAY: 'Montserrat',
    FALLBACK: 'system-ui, -apple-system, sans-serif',
  },
  
  FONT_SIZES: {
    TITLE: 72,
    PRODUCT_NAME: 48,
    PRICE: 56,
    RATING: 36,
    REVIEWS: 32,
    DESCRIPTION: 28,
    COUNTDOWN: 120,
    CTA: 42,
  },
  
  // Colors
  COLORS: {
    PRIMARY: '#FFFF00', // Yellow
    ACCENT: '#FF9900', // Amazon Orange
    BACKGROUND: '#000000',
    CARD_BG: 'rgba(20, 20, 20, 0.95)',
    TEXT_PRIMARY: '#FFFFFF',
    TEXT_SECONDARY: '#B0B0B0',
    RATING_STAR: '#FFA41C',
    SUCCESS: '#00D46A',
    OVERLAY: 'rgba(0, 0, 0, 0.6)',
  },
  
  // Shadows and effects
  SHADOWS: {
    CARD: '0 20px 60px rgba(0, 0, 0, 0.8)',
    TEXT: '0 4px 12px rgba(0, 0, 0, 0.8)',
    GLOW: '0 0 40px rgba(255, 255, 0, 0.5)',
  },
  
  // Border radius
  RADIUS: {
    SMALL: 8,
    MEDIUM: 16,
    LARGE: 24,
    PILL: 999,
  },
};

// Component layout specifications
export const LAYOUTS = {
  INTRO: {
    TITLE_Y: 960, // Center vertically
    SUBTITLE_Y: 1100,
    LOGO_Y: 400,
  },
  
  PRODUCT_CARD: {
    PADDING: 40,
    IMAGE_HEIGHT: 600,
    IMAGE_Y: 400,
    TITLE_Y: 1080,
    PRICE_Y: 1180,
    RATING_Y: 1280,
    DESCRIPTION_Y: 1380,
    COUNTDOWN_BADGE: {
      SIZE: 180,
      X: 900, // Top right
      Y: 100,
    },
  },
  
  OUTRO: {
    CTA_Y: 960,
    SUBSCRIBE_BUTTON_Y: 1100,
    SOCIAL_ICONS_Y: 1400,
  },
};

// Transition effects
export const TRANSITIONS = {
  CROSSFADE: 'crossfade',
  SLIDE_LEFT: 'slide-left',
  SLIDE_RIGHT: 'slide-right',
  SLIDE_UP: 'slide-up',
  SCALE_IN: 'scale-in',
  ROTATE_IN: 'rotate-in',
  BLUR_IN: 'blur-in',
  WIPE: 'wipe',
};

// Audio configuration
export const AUDIO = {
  FADE_IN_DURATION: 0.5, // seconds
  FADE_OUT_DURATION: 0.5,
  BACKGROUND_VOLUME: 0.3,
  VOICE_VOLUME: 1.0,
  CROSSFADE_OVERLAP: 0.2,
};

// Export all configurations
export const VideoConfig = {
  schema: CountdownVideoSchema,
  timing: TIMING,
  animations: ANIMATIONS,
  styles: STYLES,
  layouts: LAYOUTS,
  transitions: TRANSITIONS,
  audio: AUDIO,
};

export default VideoConfig;