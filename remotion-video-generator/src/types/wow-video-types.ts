/**
 * WOW Top-5 9:16 Video Type Definitions
 * Strict TypeScript types for the vertical countdown video format
 */

// Frame count branded types for compile-time safety
type Frame = number & { readonly __brand: 'Frame' };
type Seconds = number & { readonly __brand: 'Seconds' };

// Constants
export const FPS = 30 as const;
export const INTRO_FRAMES = 150 as Frame;
export const PRODUCT_FRAMES = 270 as Frame;
export const OUTRO_FRAMES = 150 as Frame;
export const TRANSITION_OVERLAP_FRAMES = 90 as Frame;

// Calculate total frames (43 seconds)
export const TOTAL_FRAMES = (
  INTRO_FRAMES + 
  (5 * PRODUCT_FRAMES - 4 * TRANSITION_OVERLAP_FRAMES) + 
  OUTRO_FRAMES
) as Frame; // 1290 frames

// Helper functions
export const framesToSeconds = (frames: Frame): Seconds => (frames / FPS) as Seconds;
export const secondsToFrames = (seconds: Seconds): Frame => (seconds * FPS) as Frame;

// Meta configuration
export interface WowMeta {
  readonly fps: 30;
  readonly width: 1080;
  readonly height: 1920;
  readonly max_total_frames: number;
  readonly brand: string;
  readonly primary_color: `#${string}`;
}

// Timeline configuration
export interface WowTimeline {
  readonly intro_frames: typeof INTRO_FRAMES;
  readonly product_frames: typeof PRODUCT_FRAMES;
  readonly outro_frames: typeof OUTRO_FRAMES;
  readonly transition_overlap_frames: number;
}

// Safe margins for content
export interface WowSafeMargins {
  readonly top: number;
  readonly bottom: number;
  readonly left: number;
  readonly right: number;
}

// Ken Burns effect configuration
export type PanDirection = 'up' | 'down' | 'left' | 'right' | 'none';

export interface KenBurnsConfig {
  readonly zoom_start: number; // 0.8 - 1.5
  readonly zoom_end: number;   // 0.8 - 1.5
  readonly pan: PanDirection;
}

// Transition types
export type TransitionType = 'slide' | 'wipe' | 'circle' | 'glitch' | 'whip-pan' | 'depth-blur';

// Product rank (countdown order)
export type ProductRank = 1 | 2 | 3 | 4 | 5;

// Layout types for product display
export type ProductLayout = 'image-left' | 'image-right' | 'split' | 'full';

// Currency types
export type Currency = 'USD' | 'EUR' | 'GBP';

// Product definition
export interface WowProduct {
  readonly rank: ProductRank;
  readonly name: string;
  readonly subtitle: string;
  readonly bg_image_url: string;
  readonly ken_burns: KenBurnsConfig;
  readonly rating: number; // 0-5
  readonly reviews_count: number;
  readonly price: number;
  readonly currency: Currency;
  readonly discount_pct: number; // 0-100
  readonly feature_chips: readonly string[]; // max 4 items
  readonly layout: ProductLayout;
  readonly transition_in: TransitionType;
  readonly transition_out: TransitionType;
}

// Caption word timing
export interface CaptionWord {
  readonly w: string;  // word text
  readonly t0: number; // start time
  readonly t1: number; // end time
}

// Caption segment
export interface Caption {
  readonly start: number; // seconds
  readonly end: number;   // seconds
  readonly text: string;
  readonly words?: readonly CaptionWord[];
}

// Caption style
export type CaptionStyle = 'karaoke' | 'static';

// Intro configuration
export interface WowIntro {
  readonly title: string;
  readonly bg_image_url: string;
  readonly caption_style: CaptionStyle;
  readonly captions?: readonly Caption[];
  readonly transition_out: TransitionType;
}

// CTA animation type
export type CTAAnimation = 'shimmer' | 'pulse' | 'bounce';

// Outro configuration
export interface WowOutro {
  readonly bg_image_url: string;
  readonly cta_text: string;
  readonly cta_animation: CTAAnimation;
  readonly legal_note?: string;
  readonly transition_in: TransitionType;
}

// Overlay configuration
export interface WowOverlays {
  readonly show_progress_bar: boolean;
  readonly caption_style: CaptionStyle;
}

// Audio configuration
export interface WowAudio {
  readonly voiceover_url?: string | null;
  readonly music_url?: string | null;
  readonly music_ducking_db: number;
}

// Datasource configuration
export interface WowDatasource {
  readonly type: string;
  readonly airtable?: {
    readonly base: string;
    readonly table: string;
    readonly mapping: {
      readonly recordId: string;
    };
  };
}

// Main WOW Video Props
export interface WowVideoProps {
  readonly meta: WowMeta;
  readonly timeline: WowTimeline;
  readonly safe_margins?: WowSafeMargins;
  readonly audio?: WowAudio;
  readonly intro: WowIntro;
  readonly products: readonly [
    WowProduct,
    WowProduct,
    WowProduct,
    WowProduct,
    WowProduct
  ]; // Exactly 5 products
  readonly outro: WowOutro;
  readonly overlays?: WowOverlays;
  readonly datasource?: WowDatasource;
}

// Validation helpers
export const validateProductOrder = (products: readonly WowProduct[]): boolean => {
  if (products.length !== 5) return false;
  
  // Check countdown order: 5, 4, 3, 2, 1
  return products.every((product, index) => product.rank === 5 - index);
};

export const calculateTotalDuration = (timeline: WowTimeline): Frame => {
  const introFrames = timeline.intro_frames;
  const productFrames = 5 * timeline.product_frames - 4 * timeline.transition_overlap_frames;
  const outroFrames = timeline.outro_frames;
  
  return (introFrames + productFrames + outroFrames) as Frame;
};

export const validateDuration = (timeline: WowTimeline): boolean => {
  const totalFrames = calculateTotalDuration(timeline);
  const totalSeconds = framesToSeconds(totalFrames);
  
  // Should be approximately 43 seconds (1290 frames)
  return totalFrames >= 1290 && totalFrames <= 1770;
};

// Type guards
export const isValidProductRank = (rank: number): rank is ProductRank => {
  return rank >= 1 && rank <= 5;
};

export const isValidCurrency = (currency: string): currency is Currency => {
  return ['USD', 'EUR', 'GBP'].includes(currency);
};

export const isValidTransition = (transition: string): transition is TransitionType => {
  return ['slide', 'wipe', 'circle', 'glitch', 'whip-pan', 'depth-blur'].includes(transition);
};

// Default values factory
export const createDefaultWowProps = (): WowVideoProps => ({
  meta: {
    fps: 30,
    width: 1080,
    height: 1920,
    max_total_frames: 1770,
    brand: 'default',
    primary_color: '#00D3A7',
  },
  timeline: {
    intro_frames: INTRO_FRAMES,
    product_frames: PRODUCT_FRAMES,
    outro_frames: OUTRO_FRAMES,
    transition_overlap_frames: 90,
  },
  intro: {
    title: 'Top 5 Products',
    bg_image_url: '',
    caption_style: 'karaoke',
    transition_out: 'glitch',
  },
  products: [
    createDefaultProduct(5),
    createDefaultProduct(4),
    createDefaultProduct(3),
    createDefaultProduct(2),
    createDefaultProduct(1),
  ] as const,
  outro: {
    bg_image_url: '',
    cta_text: 'Subscribe for More!',
    cta_animation: 'shimmer',
    legal_note: 'Affiliate links in description',
    transition_in: 'glitch',
  },
});

const createDefaultProduct = (rank: ProductRank): WowProduct => ({
  rank,
  name: `Product ${rank}`,
  subtitle: 'Amazing product description',
  bg_image_url: '',
  ken_burns: {
    zoom_start: 1.05,
    zoom_end: 1.12,
    pan: 'up',
  },
  rating: 4.0 + rank * 0.1,
  reviews_count: rank * 500,
  price: 50 + rank * 10,
  currency: 'EUR',
  discount_pct: 0,
  feature_chips: [],
  layout: 'full',
  transition_in: 'wipe',
  transition_out: 'slide',
});