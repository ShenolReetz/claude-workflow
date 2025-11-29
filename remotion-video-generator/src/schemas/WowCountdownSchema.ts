import { z } from 'zod';

// Meta configuration schema
export const WowMetaSchema = z.object({
  fps: z.literal(30),
  width: z.literal(1080),
  height: z.literal(1920),
  max_total_frames: z.number().max(1770).default(1770),
  brand: z.string().default('default'),
  primary_color: z.string().regex(/^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$/).optional(),
});

// Timeline configuration schema
export const WowTimelineSchema = z.object({
  intro_frames: z.literal(150),
  product_frames: z.literal(270),
  outro_frames: z.literal(150),
  transition_overlap_frames: z.number().min(0).max(120),
});

// Safe margins schema
export const WowSafeMarginsSchema = z.object({
  top: z.number().min(0).max(200).default(96),
  bottom: z.number().min(0).max(200).default(96),
  left: z.number().min(0).max(200).default(48),
  right: z.number().min(0).max(200).default(48),
}).default({ top: 96, bottom: 96, left: 48, right: 48 });

// Audio configuration schema
export const WowAudioSchema = z.object({
  voiceover_url: z.string().url().optional(),
  music_url: z.string().url().optional(),
  music_ducking_db: z.number().default(-12),
});

// Caption word timing schema
export const WowWordTimingSchema = z.object({
  w: z.string(),
  t0: z.number().min(0),
  t1: z.number().min(0),
});

// Caption schema
export const WowCaptionSchema = z.object({
  start: z.number().min(0),
  end: z.number().min(0),
  text: z.string().min(1),
  words: z.array(WowWordTimingSchema).optional(),
});

// Transition types
export const WowTransitionType = z.enum(['wipe', 'slide', 'circle', 'glitch', 'depth-blur', 'whip-pan']);

// Intro schema
export const WowIntroSchema = z.object({
  title: z.string().min(8).max(120),
  bg_image_url: z.string().url(),
  caption_style: z.enum(['karaoke', 'subtitle']).default('karaoke'),
  captions: z.array(WowCaptionSchema).optional(),
  transition_out: WowTransitionType.default('glitch'),
});

// Ken Burns effect schema
export const WowKenBurnsSchema = z.object({
  zoom_start: z.number().min(1.0).max(1.3).default(1.05),
  zoom_end: z.number().min(1.0).max(1.5).default(1.12),
  pan: z.enum(['none', 'left', 'right', 'up', 'down']).default('none'),
});

// Product schema
export const WowProductSchema = z.object({
  rank: z.union([z.literal(5), z.literal(4), z.literal(3), z.literal(2), z.literal(1)]),
  name: z.string().min(2).max(140),
  subtitle: z.string().max(140).default(''),
  bg_image_url: z.string().url(),
  ken_burns: WowKenBurnsSchema.optional(),
  rating: z.number().min(0).max(5),
  reviews_count: z.number().min(0),
  price: z.number().min(0),
  currency: z.string().min(1).max(4).default('EUR'),
  discount_pct: z.number().min(0).max(100).default(0),
  feature_chips: z.array(z.string().min(3).max(80)).max(4).default([]),
  layout: z.enum(['image-left', 'image-right', 'split', 'full']).default('image-left'),
  transition_in: WowTransitionType.default('wipe'),
  transition_out: WowTransitionType.default('slide'),
});

// Outro schema
export const WowOutroSchema = z.object({
  bg_image_url: z.string().url(),
  cta_text: z.string().default('Subscribe'),
  cta_animation: z.enum(['pulse', 'bounce', 'shimmer', 'tilt']).default('pulse'),
  legal_note: z.string().default('Affiliate links are in the description below.'),
  transition_in: WowTransitionType.default('glitch'),
});

// Overlays schema
export const WowOverlaysSchema = z.object({
  show_progress_bar: z.boolean().default(true),
  caption_style: z.enum(['karaoke', 'subtitle']).default('karaoke'),
});

// Airtable mapping schema
export const WowAirtableMappingSchema = z.record(z.string());

// Airtable config schema
export const WowAirtableConfigSchema = z.object({
  base: z.string().optional(),
  table: z.string().optional(),
  mapping: WowAirtableMappingSchema.optional(),
});

// Datasource schema
export const WowDatasourceSchema = z.object({
  type: z.enum(['static', 'airtable']).default('static'),
  airtable: WowAirtableConfigSchema.optional(),
});

// Complete WOW Countdown Video Schema
export const WowCountdownVideoSchema = z.object({
  meta: WowMetaSchema,
  timeline: WowTimelineSchema,
  safe_margins: WowSafeMarginsSchema.optional(),
  audio: WowAudioSchema.optional(),
  intro: WowIntroSchema,
  products: z.array(WowProductSchema).min(5).max(5),
  outro: WowOutroSchema,
  overlays: WowOverlaysSchema.optional(),
  datasource: WowDatasourceSchema.optional(),
});

// Type exports
export type WowMeta = z.infer<typeof WowMetaSchema>;
export type WowTimeline = z.infer<typeof WowTimelineSchema>;
export type WowSafeMargins = z.infer<typeof WowSafeMarginsSchema>;
export type WowAudio = z.infer<typeof WowAudioSchema>;
export type WowWordTiming = z.infer<typeof WowWordTimingSchema>;
export type WowCaption = z.infer<typeof WowCaptionSchema>;
export type WowTransition = z.infer<typeof WowTransitionType>;
export type WowIntro = z.infer<typeof WowIntroSchema>;
export type WowKenBurns = z.infer<typeof WowKenBurnsSchema>;
export type WowProduct = z.infer<typeof WowProductSchema>;
export type WowOutro = z.infer<typeof WowOutroSchema>;
export type WowOverlays = z.infer<typeof WowOverlaysSchema>;
export type WowDatasource = z.infer<typeof WowDatasourceSchema>;
export type WowCountdownVideoData = z.infer<typeof WowCountdownVideoSchema>;

// Helper functions
export function validateWowData(data: unknown): { valid: boolean; errors?: string[] } {
  try {
    WowCountdownVideoSchema.parse(data);
    return { valid: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        valid: false,
        errors: error.errors.map(e => `${e.path.join('.')}: ${e.message}`),
      };
    }
    return { valid: false, errors: ['Unknown validation error'] };
  }
}