import { z } from 'zod';

/**
 * Production-ready schema for Amazon countdown videos
 * Matches Airtable field structure exactly
 */

// ============================================================================
// DATA SCHEMAS - Match Airtable Structure
// ============================================================================

/**
 * Individual product schema matching Airtable columns
 */
export const AirtableProductSchema = z.object({
  // Core product data
  title: z.string().describe('ProductNoXTitle from Airtable'),
  price: z.union([
    z.string(), // "$99.99" format
    z.number(), // 99.99 format
  ]).transform((val) => {
    if (typeof val === 'string') {
      return val.replace(/[^0-9.]/g, '');
    }
    return val.toString();
  }),
  rating: z.number().min(0).max(5).describe('ProductNoXRating'),
  reviews: z.union([
    z.string(), // "1.2K", "5M" format
    z.number(), // 1234 format
  ]).transform((val) => {
    if (typeof val === 'string') {
      return val;
    }
    // Format large numbers
    if (val >= 1000000) {
      return `${(val / 1000000).toFixed(1)}M`;
    }
    if (val >= 1000) {
      return `${(val / 1000).toFixed(1)}K`;
    }
    return val.toString();
  }),
  photo: z.string().url().describe('ProductNoXPhoto URL'),
  description: z.string().describe('ProductNoXDescription'),
  mp3: z.string().url().describe('ProductNoXMp3 audio URL'),
  
  // Additional metadata
  affiliateLink: z.string().url().optional(),
  badge: z.enum(['BEST_SELLER', 'AMAZON_CHOICE', 'LIMITED_DEAL', 'TOP_RATED']).optional(),
  discount: z.number().min(0).max(100).optional(), // Percentage off
});

/**
 * Complete video data schema from Airtable
 */
export const AirtableVideoDataSchema = z.object({
  // Video metadata
  videoTitle: z.string().describe('Main video title'),
  recordId: z.string().optional().describe('Airtable record ID'),
  
  // Intro assets
  introPhoto: z.string().url().describe('IntroPhoto URL'),
  introMp3: z.string().url().describe('IntroMp3 audio URL'),
  
  // Product data (exactly 5 products)
  product1: AirtableProductSchema,
  product2: AirtableProductSchema,
  product3: AirtableProductSchema,
  product4: AirtableProductSchema,
  product5: AirtableProductSchema,
  
  // Outro assets
  outroPhoto: z.string().url().describe('OutroPhoto URL'),
  outroMp3: z.string().url().describe('OutroMp3 audio URL'),
  
  // Optional branding customization
  brandColors: z.object({
    primary: z.string().default('#FFFF00'), // Yellow
    accent: z.string().default('#00FF00'), // Green for price
    background: z.string().default('#000000'),
    cardBg: z.string().default('rgba(20, 20, 20, 0.95)'),
  }).optional(),
  
  // Social media configuration
  socialMedia: z.object({
    showSubscribe: z.boolean().default(true),
    subscribeCTA: z.string().default('Subscribe for More!'),
    platform: z.enum(['tiktok', 'instagram', 'youtube']).default('tiktok'),
  }).optional(),
});

// Type exports
export type AirtableProduct = z.infer<typeof AirtableProductSchema>;
export type AirtableVideoData = z.infer<typeof AirtableVideoDataSchema>;

// ============================================================================
// TIMING CONFIGURATION - 30fps for social media
// ============================================================================

export const TIMING_30FPS = {
  FPS: 30,
  TOTAL_DURATION: 1650, // 55 seconds * 30fps
  
  INTRO: {
    START: 0,
    DURATION: 150, // 5 seconds
    END: 149,
    // Sub-timings for intro animations
    LOGO_FADE: { start: 0, end: 30 },
    TITLE_REVEAL: { start: 30, end: 90 },
    HOOK_TEXT: { start: 90, end: 150 },
  },
  
  PRODUCT_5: {
    START: 150,
    DURATION: 270, // 9 seconds
    END: 419,
    // Sub-timings for product animations
    TRANSITION_IN: { start: 150, duration: 20 },
    BADGE_REVEAL: { start: 170, duration: 30 },
    IMAGE_ZOOM: { start: 200, duration: 60 },
    INFO_REVEAL: { start: 260, duration: 40 },
    RATING_ANIMATE: { start: 300, duration: 30 },
    PRICE_GLOW: { start: 330, duration: 30 },
    DESCRIPTION_FADE: { start: 360, duration: 30 },
    TRANSITION_OUT: { start: 400, duration: 20 },
  },
  
  PRODUCT_4: {
    START: 420,
    DURATION: 270,
    END: 689,
  },
  
  PRODUCT_3: {
    START: 690,
    DURATION: 270,
    END: 959,
  },
  
  PRODUCT_2: {
    START: 960,
    DURATION: 270,
    END: 1229,
  },
  
  PRODUCT_1: {
    START: 1230,
    DURATION: 270,
    END: 1499,
  },
  
  OUTRO: {
    START: 1500,
    DURATION: 150, // 5 seconds
    END: 1649,
    // Sub-timings for outro animations
    RECAP_FADE: { start: 1500, duration: 30 },
    CTA_PULSE: { start: 1530, duration: 60 },
    SOCIAL_ICONS: { start: 1590, duration: 30 },
    FINAL_FADE: { start: 1620, duration: 30 },
  },
};

// ============================================================================
// VISUAL CONFIGURATION
// ============================================================================

export const VISUAL_CONFIG = {
  // Video dimensions
  DIMENSIONS: {
    WIDTH: 1080,
    HEIGHT: 1920,
    ASPECT_RATIO: '9:16',
  },
  
  // Safe zones for mobile viewing
  SAFE_ZONES: {
    TOP: 120, // Account for notches/status bar
    BOTTOM: 100, // Account for UI elements
    LEFT: 60,
    RIGHT: 60,
    // Content area
    CONTENT_WIDTH: 960, // 1080 - 60*2
    CONTENT_HEIGHT: 1700, // 1920 - 120 - 100
  },
  
  // Typography configuration
  TYPOGRAPHY: {
    FONTS: {
      PRIMARY: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      DISPLAY: "'Montserrat', 'Inter', sans-serif",
      ACCENT: "'Bebas Neue', 'Montserrat', sans-serif",
    },
    
    // Font sizes optimized for mobile
    SIZES: {
      INTRO_TITLE: 72,
      INTRO_SUBTITLE: 36,
      COUNTDOWN_NUMBER: 140, // Big countdown badge
      PRODUCT_RANK: 48,
      PRODUCT_TITLE: 44,
      PRODUCT_PRICE: 56,
      PRODUCT_ORIGINAL_PRICE: 36,
      RATING_TEXT: 32,
      REVIEW_COUNT: 28,
      DESCRIPTION: 26,
      BADGE_TEXT: 24,
      CTA_BUTTON: 42,
      SOCIAL_HANDLE: 24,
    },
    
    // Font weights
    WEIGHTS: {
      THIN: 300,
      REGULAR: 400,
      MEDIUM: 500,
      SEMIBOLD: 600,
      BOLD: 700,
      BLACK: 900,
    },
  },
  
  // Color palette
  COLORS: {
    // Primary colors
    PRIMARY: '#FFFF00', // Yellow
    PRIMARY_DARK: '#FFD700',
    PRIMARY_LIGHT: '#FFFFE0',
    
    // Accent colors
    ACCENT: '#00FF00', // Green for price
    ACCENT_DARK: '#00C000',
    ACCENT_LIGHT: '#90EE90',
    
    // Amazon orange
    AMAZON: '#FF9900',
    AMAZON_DARK: '#E47911',
    
    // Background colors
    BG_PRIMARY: '#000000',
    BG_SECONDARY: '#0A0A0A',
    BG_CARD: 'rgba(20, 20, 20, 0.95)',
    BG_OVERLAY: 'rgba(0, 0, 0, 0.7)',
    
    // Text colors
    TEXT_PRIMARY: '#FFFFFF',
    TEXT_SECONDARY: '#B0B0B0',
    TEXT_MUTED: '#808080',
    
    // Rating colors
    STAR_FILLED: '#FFA41C',
    STAR_EMPTY: '#434343',
    
    // Status colors
    SUCCESS: '#00D46A',
    WARNING: '#FFA724',
    ERROR: '#FF4747',
    
    // Gradient definitions
    GRADIENTS: {
      GOLD: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
      SILVER: 'linear-gradient(135deg, #C0C0C0 0%, #808080 100%)',
      BRONZE: 'linear-gradient(135deg, #CD7F32 0%, #8B4513 100%)',
      GLOW: 'radial-gradient(circle, rgba(255,255,0,0.3) 0%, transparent 70%)',
      CARD: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(10,10,10,0.95) 100%)',
    },
  },
  
  // Visual effects
  EFFECTS: {
    // Shadows
    SHADOWS: {
      SMALL: '0 2px 4px rgba(0,0,0,0.5)',
      MEDIUM: '0 4px 12px rgba(0,0,0,0.6)',
      LARGE: '0 8px 24px rgba(0,0,0,0.7)',
      GLOW_YELLOW: '0 0 40px rgba(255,255,0,0.5)',
      GLOW_GREEN: '0 0 40px rgba(0,255,0,0.4)',
      TEXT: '2px 2px 4px rgba(0,0,0,0.8)',
      CARD: '0 20px 60px rgba(0,0,0,0.8)',
    },
    
    // Blur effects
    BLUR: {
      NONE: 'blur(0px)',
      SMALL: 'blur(2px)',
      MEDIUM: 'blur(8px)',
      LARGE: 'blur(20px)',
      BACKGROUND: 'blur(40px)',
    },
    
    // Border radius
    RADIUS: {
      SMALL: 8,
      MEDIUM: 16,
      LARGE: 24,
      XLARGE: 32,
      PILL: 999,
    },
    
    // Glass morphism
    GLASS: {
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
    },
  },
};

// ============================================================================
// ANIMATION CONFIGURATIONS
// ============================================================================

export const ANIMATIONS = {
  // Spring animations
  SPRINGS: {
    SMOOTH: {
      damping: 100,
      mass: 0.8,
      stiffness: 200,
      overshootClamping: true,
    },
    BOUNCY: {
      damping: 10,
      mass: 1,
      stiffness: 180,
      overshootClamping: false,
    },
    STIFF: {
      damping: 200,
      mass: 1,
      stiffness: 500,
      overshootClamping: false,
    },
    WOBBLY: {
      damping: 5,
      mass: 2,
      stiffness: 100,
      overshootClamping: false,
    },
  },
  
  // Easing functions
  EASINGS: {
    LINEAR: [0, 0, 1, 1],
    EASE_IN: [0.42, 0, 1, 1],
    EASE_OUT: [0, 0, 0.58, 1],
    EASE_IN_OUT: [0.42, 0, 0.58, 1],
    EASE_IN_QUAD: [0.55, 0.085, 0.68, 0.53],
    EASE_OUT_QUAD: [0.25, 0.46, 0.45, 0.94],
    EASE_IN_OUT_QUAD: [0.455, 0.03, 0.515, 0.955],
    EASE_IN_CUBIC: [0.55, 0.055, 0.675, 0.19],
    EASE_OUT_CUBIC: [0.215, 0.61, 0.355, 1],
    EASE_IN_OUT_CUBIC: [0.645, 0.045, 0.355, 1],
    EASE_IN_EXPO: [0.95, 0.05, 0.795, 0.035],
    EASE_OUT_EXPO: [0.19, 1, 0.22, 1],
    EASE_IN_OUT_EXPO: [1, 0, 0, 1],
    EASE_IN_BACK: [0.6, -0.28, 0.735, 0.045],
    EASE_OUT_BACK: [0.175, 0.885, 0.32, 1.275],
    BOUNCE: [0.68, -0.55, 0.265, 1.55],
  },
  
  // Transition types
  TRANSITIONS: {
    FADE: {
      type: 'fade',
      duration: 15, // frames
    },
    SLIDE_LEFT: {
      type: 'slide',
      direction: 'left',
      duration: 20,
    },
    SLIDE_RIGHT: {
      type: 'slide',
      direction: 'right',
      duration: 20,
    },
    SLIDE_UP: {
      type: 'slide',
      direction: 'up',
      duration: 20,
    },
    SCALE: {
      type: 'scale',
      duration: 25,
    },
    ROTATE: {
      type: 'rotate',
      duration: 30,
    },
    FLIP: {
      type: 'flip',
      duration: 25,
    },
    ZOOM_BLUR: {
      type: 'zoom-blur',
      duration: 20,
    },
    WIPE: {
      type: 'wipe',
      duration: 30,
    },
    GLITCH: {
      type: 'glitch',
      duration: 15,
    },
  },
  
  // Keyframe animations
  KEYFRAMES: {
    PULSE: {
      frames: [
        { scale: 1, opacity: 1 },
        { scale: 1.05, opacity: 0.9 },
        { scale: 1, opacity: 1 },
      ],
      duration: 60, // 2 seconds at 30fps
      loop: true,
    },
    FLOAT: {
      frames: [
        { y: 0 },
        { y: -10 },
        { y: 0 },
      ],
      duration: 90, // 3 seconds at 30fps
      loop: true,
    },
    ROTATE_CONTINUOUS: {
      frames: [
        { rotation: 0 },
        { rotation: 360 },
      ],
      duration: 150, // 5 seconds at 30fps
      loop: true,
    },
    GLOW_PULSE: {
      frames: [
        { glowIntensity: 0 },
        { glowIntensity: 1 },
        { glowIntensity: 0 },
      ],
      duration: 45, // 1.5 seconds at 30fps
      loop: true,
    },
  },
};

// ============================================================================
// LAYOUT SPECIFICATIONS
// ============================================================================

export const LAYOUTS = {
  // Intro scene layout
  INTRO: {
    LOGO: {
      y: 300,
      size: 120,
    },
    TITLE: {
      y: 960, // Center
      maxWidth: 900,
    },
    SUBTITLE: {
      y: 1100,
      maxWidth: 800,
    },
    HOOK: {
      y: 1250,
      maxWidth: 700,
    },
  },
  
  // Product card layout
  PRODUCT: {
    // Countdown badge
    COUNTDOWN_BADGE: {
      x: 900,
      y: 120,
      size: 160,
    },
    
    // Product image
    IMAGE: {
      y: 400,
      width: 800,
      height: 600,
      borderRadius: 24,
    },
    
    // Product info card
    INFO_CARD: {
      y: 1050,
      width: 960,
      padding: 40,
      gap: 20, // Space between elements
    },
    
    // Individual elements
    TITLE: {
      y: 1100,
      maxWidth: 880,
    },
    PRICE: {
      y: 1180,
      gap: 20, // Space between current and original price
    },
    RATING: {
      y: 1260,
      starSize: 32,
      gap: 8,
    },
    REVIEWS: {
      y: 1320,
    },
    DESCRIPTION: {
      y: 1380,
      maxWidth: 880,
      maxLines: 3,
    },
    BADGE: {
      y: 1480,
      height: 40,
    },
  },
  
  // Outro scene layout
  OUTRO: {
    TITLE: {
      y: 800,
    },
    CTA: {
      y: 960,
      buttonWidth: 400,
      buttonHeight: 80,
    },
    SUBSCRIBE: {
      y: 1100,
      buttonWidth: 350,
      buttonHeight: 70,
    },
    SOCIAL: {
      y: 1400,
      iconSize: 60,
      gap: 40,
    },
    DISCLAIMER: {
      y: 1600,
      fontSize: 18,
    },
  },
};

// ============================================================================
// COMPONENT SPECIFICATIONS
// ============================================================================

export const COMPONENTS = {
  // Star rating component
  STAR_RATING: {
    sizes: {
      small: 24,
      medium: 32,
      large: 40,
    },
    colors: {
      filled: '#FFA41C',
      empty: '#434343',
      glow: 'rgba(255, 164, 28, 0.3)',
    },
    animation: {
      fillDuration: 30, // frames
      glowDuration: 20,
    },
  },
  
  // Price tag component
  PRICE_TAG: {
    sizes: {
      regular: 56,
      large: 64,
      discount: 36,
    },
    colors: {
      current: '#00FF00',
      original: '#808080',
      discount: '#FF4444',
      badge: '#FFD700',
    },
    effects: {
      glow: true,
      pulsate: true,
    },
  },
  
  // Countdown badge component
  COUNTDOWN_BADGE: {
    sizes: {
      small: 120,
      medium: 160,
      large: 200,
    },
    styles: {
      gold: {
        bg: 'linear-gradient(135deg, #FFD700, #FFA500)',
        text: '#000000',
        border: '#FFD700',
      },
      silver: {
        bg: 'linear-gradient(135deg, #C0C0C0, #808080)',
        text: '#000000',
        border: '#C0C0C0',
      },
      bronze: {
        bg: 'linear-gradient(135deg, #CD7F32, #8B4513)',
        text: '#FFFFFF',
        border: '#CD7F32',
      },
    },
    animation: {
      scaleIn: 20,
      rotate: 30,
      pulse: true,
    },
  },
  
  // Review count component
  REVIEW_COUNT: {
    formats: {
      full: (count: number) => `${count.toLocaleString()} reviews`,
      short: (count: string) => `${count} reviews`,
      compact: (count: string) => `(${count})`,
    },
    thresholds: {
      hot: 10000, // Show "hot" badge
      trending: 5000, // Show "trending" badge
      popular: 1000, // Show "popular" badge
    },
  },
  
  // Product badge component
  PRODUCT_BADGE: {
    types: {
      BEST_SELLER: {
        bg: '#FF9900',
        text: '#FFFFFF',
        icon: '🏆',
      },
      AMAZON_CHOICE: {
        bg: '#232F3E',
        text: '#FF9900',
        icon: '✓',
      },
      LIMITED_DEAL: {
        bg: '#CC0C39',
        text: '#FFFFFF',
        icon: '⚡',
      },
      TOP_RATED: {
        bg: '#007185',
        text: '#FFFFFF',
        icon: '⭐',
      },
    },
  },
  
  // Subscribe button component
  SUBSCRIBE_BUTTON: {
    platforms: {
      youtube: {
        bg: '#FF0000',
        text: '#FFFFFF',
        icon: '▶',
      },
      tiktok: {
        bg: '#000000',
        text: '#FFFFFF',
        icon: '♪',
      },
      instagram: {
        bg: 'linear-gradient(45deg, #F58529, #DD2A7B, #8134AF)',
        text: '#FFFFFF',
        icon: '◉',
      },
    },
    animation: {
      pulse: true,
      scale: 1.1,
      glow: true,
    },
  },
};

// ============================================================================
// AUDIO CONFIGURATION
// ============================================================================

export const AUDIO_CONFIG = {
  // Volume levels
  VOLUMES: {
    VOICE: 1.0,
    BACKGROUND: 0.3,
    EFFECTS: 0.5,
  },
  
  // Fade timings (in seconds)
  FADES: {
    IN: 0.5,
    OUT: 0.5,
    CROSS: 0.2,
  },
  
  // Audio sync points (frame numbers for key audio cues)
  SYNC_POINTS: {
    INTRO_BEAT: 30,
    PRODUCT_REVEAL: 15, // Offset from product start
    RATING_DING: 30, // Offset from rating animation
    PRICE_WHOOSH: 15, // Offset from price reveal
    OUTRO_CRESCENDO: 45, // Offset from outro start
  },
};

// ============================================================================
// PLATFORM-SPECIFIC OPTIMIZATIONS
// ============================================================================

export const PLATFORM_CONFIG = {
  TIKTOK: {
    maxDuration: 60, // seconds
    safeZones: {
      top: 150, // Account for username/description
      bottom: 120, // Account for interaction buttons
    },
    features: {
      autoplay: true,
      loop: true,
      showCaptions: true,
    },
  },
  
  INSTAGRAM_REELS: {
    maxDuration: 90, // seconds
    safeZones: {
      top: 120,
      bottom: 150, // Account for larger interaction area
    },
    features: {
      autoplay: true,
      loop: false,
      showCaptions: true,
    },
  },
  
  YOUTUBE_SHORTS: {
    maxDuration: 60, // seconds
    safeZones: {
      top: 100,
      bottom: 100,
    },
    features: {
      autoplay: false,
      loop: false,
      showCaptions: false, // Uses YouTube's caption system
    },
  },
};

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

/**
 * Validate Airtable data before processing
 */
export function validateAirtableData(data: any): AirtableVideoData {
  // Transform flat Airtable structure to nested structure
  const transformedData = {
    videoTitle: data.VideoTitle || data.videoTitle,
    recordId: data.id || data.recordId,
    
    introPhoto: data.IntroPhoto || data.introPhoto,
    introMp3: data.IntroMp3 || data.introMp3,
    
    product1: {
      title: data.ProductNo1Title || '',
      price: data.ProductNo1Price || '0',
      rating: parseFloat(data.ProductNo1Rating) || 0,
      reviews: data.ProductNo1Reviews || '0',
      photo: data.ProductNo1Photo || '',
      description: data.ProductNo1Description || '',
      mp3: data.Product1Mp3 || '',
    },
    
    product2: {
      title: data.ProductNo2Title || '',
      price: data.ProductNo2Price || '0',
      rating: parseFloat(data.ProductNo2Rating) || 0,
      reviews: data.ProductNo2Reviews || '0',
      photo: data.ProductNo2Photo || '',
      description: data.ProductNo2Description || '',
      mp3: data.Product2Mp3 || '',
    },
    
    product3: {
      title: data.ProductNo3Title || '',
      price: data.ProductNo3Price || '0',
      rating: parseFloat(data.ProductNo3Rating) || 0,
      reviews: data.ProductNo3Reviews || '0',
      photo: data.ProductNo3Photo || '',
      description: data.ProductNo3Description || '',
      mp3: data.Product3Mp3 || '',
    },
    
    product4: {
      title: data.ProductNo4Title || '',
      price: data.ProductNo4Price || '0',
      rating: parseFloat(data.ProductNo4Rating) || 0,
      reviews: data.ProductNo4Reviews || '0',
      photo: data.ProductNo4Photo || '',
      description: data.ProductNo4Description || '',
      mp3: data.Product4Mp3 || '',
    },
    
    product5: {
      title: data.ProductNo5Title || '',
      price: data.ProductNo5Price || '0',
      rating: parseFloat(data.ProductNo5Rating) || 0,
      reviews: data.ProductNo5Reviews || '0',
      photo: data.ProductNo5Photo || '',
      description: data.ProductNo5Description || '',
      mp3: data.Product5Mp3 || '',
    },
    
    outroPhoto: data.OutroPhoto || data.outroPhoto,
    outroMp3: data.OutroMp3 || data.outroMp3,
  };
  
  return AirtableVideoDataSchema.parse(transformedData);
}

/**
 * Format review count for display
 */
export function formatReviewCount(count: string | number): string {
  if (typeof count === 'string') {
    return count; // Already formatted
  }
  
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  }
  return count.toString();
}

/**
 * Format price for display
 */
export function formatPrice(price: string | number): string {
  const numPrice = typeof price === 'string' 
    ? parseFloat(price.replace(/[^0-9.]/g, ''))
    : price;
    
  return `$${numPrice.toFixed(2)}`;
}

// ============================================================================
// REMOTION COMPOSITION CONFIGURATION
// ============================================================================

export const COMPOSITION_CONFIG = {
  id: 'CountdownVideo',
  component: 'CountdownVideo',
  width: VISUAL_CONFIG.DIMENSIONS.WIDTH,
  height: VISUAL_CONFIG.DIMENSIONS.HEIGHT,
  fps: TIMING_30FPS.FPS,
  durationInFrames: TIMING_30FPS.TOTAL_DURATION,
  defaultProps: {
    // Will be populated from Airtable data
  },
};

// ============================================================================
// EXPORT ALL CONFIGURATIONS
// ============================================================================

export const ProductionVideoConfig = {
  // Data schemas
  schemas: {
    product: AirtableProductSchema,
    video: AirtableVideoDataSchema,
  },
  
  // Timing configuration
  timing: TIMING_30FPS,
  
  // Visual configuration
  visual: VISUAL_CONFIG,
  
  // Animation configuration
  animations: ANIMATIONS,
  
  // Layout specifications
  layouts: LAYOUTS,
  
  // Component specifications
  components: COMPONENTS,
  
  // Audio configuration
  audio: AUDIO_CONFIG,
  
  // Platform-specific settings
  platforms: PLATFORM_CONFIG,
  
  // Composition settings
  composition: COMPOSITION_CONFIG,
  
  // Helper functions
  helpers: {
    validateAirtableData,
    formatReviewCount,
    formatPrice,
  },
};

export default ProductionVideoConfig;