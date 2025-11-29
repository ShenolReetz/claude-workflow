/**
 * Airtable integration utilities for Remotion video generation
 * Handles data transformation, validation, and rendering pipeline
 */

import { z } from 'zod';
import { 
  AirtableVideoDataSchema,
  validateAirtableData,
  formatReviewCount,
  formatPrice,
  ProductionVideoConfig,
} from '../schemas/ProductionVideoSchema';
import { VideoData, Product } from '../types/ProductionTypes';

// ============================================================================
// AIRTABLE DATA TRANSFORMATION
// ============================================================================

/**
 * Transform raw Airtable record to video data format
 */
export function transformAirtableRecord(record: any): VideoData {
  try {
    // Map Airtable field names to our schema
    const transformedData = {
      videoTitle: record.VideoTitle || record.fields?.VideoTitle,
      recordId: record.id,
      
      // Intro assets
      introPhoto: record.IntroPhoto || record.fields?.IntroPhoto,
      introMp3: record.IntroMp3 || record.fields?.IntroMp3,
      
      // Products (reverse order for countdown)
      product1: transformProduct(record, 1),
      product2: transformProduct(record, 2),
      product3: transformProduct(record, 3),
      product4: transformProduct(record, 4),
      product5: transformProduct(record, 5),
      
      // Outro assets
      outroPhoto: record.OutroPhoto || record.fields?.OutroPhoto,
      outroMp3: record.OutroMp3 || record.fields?.OutroMp3,
      
      // Optional branding
      brandColors: record.BrandColors ? {
        primary: record.BrandColors.primary || '#FFFF00',
        accent: record.BrandColors.accent || '#00FF00',
        background: record.BrandColors.background || '#000000',
        cardBg: record.BrandColors.cardBg || 'rgba(20, 20, 20, 0.95)',
      } : undefined,
      
      // Social media settings
      socialMedia: {
        showSubscribe: true,
        subscribeCTA: 'Subscribe for More!',
        platform: detectPlatform(record),
      },
    };
    
    // Validate with schema
    return validateAirtableData(transformedData);
  } catch (error) {
    console.error('Error transforming Airtable record:', error);
    throw new Error(`Failed to transform Airtable data: ${error.message}`);
  }
}

/**
 * Transform individual product data from Airtable
 */
function transformProduct(record: any, index: number): Product {
  const fields = record.fields || record;
  
  return {
    title: fields[`ProductNo${index}Title`] || `Product ${index}`,
    price: fields[`ProductNo${index}Price`] || '0',
    rating: parseFloat(fields[`ProductNo${index}Rating`]) || 0,
    reviews: fields[`ProductNo${index}Reviews`] || '0',
    photo: fields[`ProductNo${index}Photo`] || '',
    description: fields[`ProductNo${index}Description`] || '',
    mp3: fields[`Product${index}Mp3`] || '',
    affiliateLink: fields[`ProductNo${index}AffiliateLink`],
    badge: determineBadge(fields, index),
    discount: calculateDiscount(fields, index),
  };
}

/**
 * Determine product badge based on data
 */
function determineBadge(fields: any, index: number): string | undefined {
  const reviews = parseReviewCount(fields[`ProductNo${index}Reviews`]);
  const rating = parseFloat(fields[`ProductNo${index}Rating`]) || 0;
  
  if (index === 1) return 'BEST_SELLER'; // #1 product
  if (reviews > 10000) return 'TOP_RATED';
  if (rating >= 4.5) return 'AMAZON_CHOICE';
  if (fields[`ProductNo${index}Discount`] > 30) return 'LIMITED_DEAL';
  
  return undefined;
}

/**
 * Calculate discount percentage if original price is available
 */
function calculateDiscount(fields: any, index: number): number | undefined {
  const currentPrice = parsePrice(fields[`ProductNo${index}Price`]);
  const originalPrice = parsePrice(fields[`ProductNo${index}OriginalPrice`]);
  
  if (originalPrice && originalPrice > currentPrice) {
    return Math.round(((originalPrice - currentPrice) / originalPrice) * 100);
  }
  
  return undefined;
}

/**
 * Parse review count from various formats
 */
function parseReviewCount(value: any): number {
  if (!value) return 0;
  if (typeof value === 'number') return value;
  
  const str = value.toString().toUpperCase();
  if (str.includes('K')) {
    return parseFloat(str.replace('K', '')) * 1000;
  }
  if (str.includes('M')) {
    return parseFloat(str.replace('M', '')) * 1000000;
  }
  
  return parseInt(str.replace(/[^0-9]/g, '')) || 0;
}

/**
 * Parse price from various formats
 */
function parsePrice(value: any): number {
  if (!value) return 0;
  if (typeof value === 'number') return value;
  
  const str = value.toString();
  return parseFloat(str.replace(/[^0-9.]/g, '')) || 0;
}

/**
 * Detect platform from record metadata
 */
function detectPlatform(record: any): 'tiktok' | 'instagram' | 'youtube' {
  const platform = record.Platform || record.fields?.Platform;
  if (platform) {
    return platform.toLowerCase() as any;
  }
  return 'tiktok'; // Default
}

// ============================================================================
// VALIDATION AND ERROR HANDLING
// ============================================================================

/**
 * Validation result type
 */
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  data?: VideoData;
}

/**
 * Comprehensive validation for Airtable data
 */
export function validateVideoData(record: any): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  try {
    // Required fields check
    if (!record.VideoTitle && !record.fields?.VideoTitle) {
      errors.push('Missing required field: VideoTitle');
    }
    
    if (!record.IntroPhoto && !record.fields?.IntroPhoto) {
      errors.push('Missing required field: IntroPhoto');
    }
    
    if (!record.IntroMp3 && !record.fields?.IntroMp3) {
      errors.push('Missing required field: IntroMp3');
    }
    
    // Check all 5 products
    for (let i = 1; i <= 5; i++) {
      const fields = record.fields || record;
      const productTitle = fields[`ProductNo${i}Title`];
      const productPhoto = fields[`ProductNo${i}Photo`];
      const productMp3 = fields[`Product${i}Mp3`];
      
      if (!productTitle) {
        errors.push(`Missing ProductNo${i}Title`);
      }
      
      if (!productPhoto) {
        errors.push(`Missing ProductNo${i}Photo`);
      }
      
      if (!productMp3) {
        warnings.push(`Missing Product${i}Mp3 audio - will use TTS fallback`);
      }
      
      // Validate rating range
      const rating = parseFloat(fields[`ProductNo${i}Rating`]);
      if (rating && (rating < 0 || rating > 5)) {
        errors.push(`ProductNo${i}Rating out of range (0-5): ${rating}`);
      }
      
      // Validate URLs
      if (productPhoto && !isValidUrl(productPhoto)) {
        errors.push(`Invalid URL for ProductNo${i}Photo: ${productPhoto}`);
      }
      
      if (productMp3 && !isValidUrl(productMp3)) {
        errors.push(`Invalid URL for Product${i}Mp3: ${productMp3}`);
      }
    }
    
    // Check outro fields
    if (!record.OutroPhoto && !record.fields?.OutroPhoto) {
      errors.push('Missing required field: OutroPhoto');
    }
    
    if (!record.OutroMp3 && !record.fields?.OutroMp3) {
      errors.push('Missing required field: OutroMp3');
    }
    
    // If no critical errors, try to transform
    if (errors.length === 0) {
      try {
        const data = transformAirtableRecord(record);
        return {
          isValid: true,
          errors,
          warnings,
          data,
        };
      } catch (transformError) {
        errors.push(`Data transformation failed: ${transformError.message}`);
      }
    }
    
    return {
      isValid: false,
      errors,
      warnings,
    };
    
  } catch (error) {
    return {
      isValid: false,
      errors: [`Validation failed: ${error.message}`],
      warnings,
    };
  }
}

/**
 * Check if string is valid URL
 */
function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// ============================================================================
// REMOTION RENDER CONFIGURATION
// ============================================================================

/**
 * Generate Remotion render configuration from Airtable data
 */
export function generateRenderConfig(videoData: VideoData, outputPath: string) {
  return {
    composition: 'ProductionCountdownVideo',
    output: outputPath,
    props: {
      data: videoData,
      platform: videoData.socialMedia?.platform || 'tiktok',
      transition: 'slide-up',
      enableDebug: false,
    },
    config: {
      imageFormat: 'jpeg',
      jpegQuality: 95,
      scale: 1,
      chromiumOptions: {
        enableMultiProcessOnLinux: true,
      },
      timeoutInMilliseconds: 120000, // 2 minutes
      numberOfGifLoops: null,
      everyNthFrame: 1,
      concurrency: 4,
      muted: false,
      enforceAudioTrack: true,
      pixelFormat: 'yuv420p',
      codec: 'h264',
      crf: 18, // High quality
      videoBitrate: '8M',
      audioBitrate: '320k',
      audioCodec: 'aac',
    },
  };
}

// ============================================================================
// BATCH PROCESSING
// ============================================================================

/**
 * Process multiple Airtable records
 */
export async function processBatch(records: any[]): Promise<Map<string, ValidationResult>> {
  const results = new Map<string, ValidationResult>();
  
  for (const record of records) {
    const recordId = record.id || `record_${Date.now()}`;
    const validation = validateVideoData(record);
    results.set(recordId, validation);
    
    if (!validation.isValid) {
      console.error(`Validation failed for record ${recordId}:`, validation.errors);
    }
  }
  
  return results;
}

// ============================================================================
// STATUS REPORTING
// ============================================================================

/**
 * Generate status report for Airtable update
 */
export function generateStatusReport(
  recordId: string,
  status: 'success' | 'failed' | 'processing',
  details?: any
) {
  return {
    id: recordId,
    fields: {
      VideoGenerationStatus: status === 'success' ? 'Ready' : status === 'failed' ? 'Failed' : 'Processing',
      VideoGenerationTimestamp: new Date().toISOString(),
      VideoGenerationDetails: JSON.stringify(details || {}),
      ...(status === 'success' && details?.videoUrl ? {
        VideoURL: details.videoUrl,
        VideoDuration: '55',
        VideoFormat: '9:16',
        VideoFPS: '30',
        VideoResolution: '1080x1920',
      } : {}),
    },
  };
}

// ============================================================================
// EXPORT UTILITIES
// ============================================================================

export const AirtableIntegration = {
  transform: transformAirtableRecord,
  validate: validateVideoData,
  processBatch,
  generateRenderConfig,
  generateStatusReport,
  helpers: {
    parseReviewCount,
    parsePrice,
    formatReviewCount,
    formatPrice,
    isValidUrl,
  },
};

export default AirtableIntegration;