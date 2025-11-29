import { WowCountdownVideoData, WowProduct, WowCaption, WowTransition } from '../schemas/WowCountdownSchema';

/**
 * Adapter to transform Airtable data into the WOW Remotion schema format
 */
export class WowAirtableAdapter {
  /**
   * Transform raw Airtable data into WowCountdownVideoData format
   */
  static transformToWowFormat(airtableData: any): WowCountdownVideoData {
    // Extract and transform products
    const products = this.buildProducts(airtableData);
    
    // Build intro captions from title
    const videoTitle = airtableData.VideoTitle || 'Top 5 Products You Need';
    const introCaptions = this.generateIntroCaptions(videoTitle, airtableData.IntroHook);
    
    // Determine brand color from data or use defaults
    const primaryColor = airtableData.BrandColorPrimary || '#00D3A7';
    
    return {
      meta: {
        fps: 30,
        width: 1080,
        height: 1920,
        max_total_frames: 1770,
        brand: 'default',
        primary_color: primaryColor,
      },
      timeline: {
        intro_frames: 150,
        product_frames: 270,
        outro_frames: 150,
        transition_overlap_frames: 90,
      },
      safe_margins: {
        top: 96,
        bottom: 96,
        left: 48,
        right: 48,
      },
      audio: {
        // Combine all audio files into voiceover
        voiceover_url: this.buildVoiceoverUrl(airtableData),
        music_url: undefined, // Can be added if music URL is available
        music_ducking_db: -12,
      },
      intro: {
        title: videoTitle,
        bg_image_url: airtableData.IntroPhoto || 'https://via.placeholder.com/1080x1920/000/fff?text=INTRO',
        caption_style: 'karaoke',
        captions: introCaptions,
        transition_out: 'glitch',
      },
      products: products,
      outro: {
        bg_image_url: airtableData.OutroPhoto || 'https://via.placeholder.com/1080x1920/000/fff?text=OUTRO',
        cta_text: airtableData.OutroCallToAction || 'Subscribe for More!',
        cta_animation: 'shimmer',
        legal_note: 'Affiliate links are in the description below.',
        transition_in: 'glitch',
      },
      overlays: {
        show_progress_bar: true,
        caption_style: 'karaoke',
      },
      datasource: {
        type: 'airtable',
        airtable: {
          base: 'appTtNBJ8dAnjvkPP',
          table: 'tblhGDEW6eUbmaYZx',
          mapping: {
            title: 'VideoTitle',
            intro_photo: 'IntroPhoto',
            outro_photo: 'OutroPhoto',
          },
        },
      },
    };
  }
  
  /**
   * Build products array from Airtable data
   */
  private static buildProducts(data: any): WowProduct[] {
    const products: WowProduct[] = [];
    const transitions = this.getTransitionSequence();
    const layouts = this.getLayoutSequence();
    
    // Process products in reverse order (5 to 1)
    for (let i = 5; i >= 1; i--) {
      const productIndex = 5 - i; // 0 to 4
      
      // Extract product data
      const title = data[`ProductNo${i}Title`] || `Product #${i}`;
      const description = data[`ProductNo${i}Description`] || '';
      const price = this.parsePrice(data[`ProductNo${i}Price`]);
      const rating = this.parseRating(data[`ProductNo${i}Rating`]);
      const reviews = this.parseReviews(data[`ProductNo${i}Reviews`]);
      const photo = data[`ProductNo${i}Photo`] || `https://via.placeholder.com/1080x1920/333/fff?text=Product+${i}`;
      
      // Generate subtitle from description (first 50 chars)
      const subtitle = this.generateSubtitle(description);
      
      // Extract feature chips from description
      const featureChips = this.extractFeatures(description);
      
      // Calculate discount if original price is available
      const discount = this.calculateDiscount(
        data[`ProductNo${i}Price`],
        data[`ProductNo${i}OriginalPrice`]
      );
      
      // Determine Ken Burns effect based on rank
      const kenBurns = this.getKenBurnsEffect(i);
      
      const product: WowProduct = {
        rank: i as 1 | 2 | 3 | 4 | 5,
        name: this.truncateText(title, 140),
        subtitle: subtitle,
        bg_image_url: photo,
        ken_burns: kenBurns,
        rating: rating,
        reviews_count: reviews,
        price: price,
        currency: 'EUR',
        discount_pct: discount,
        feature_chips: featureChips,
        layout: layouts[productIndex],
        transition_in: transitions.in[productIndex],
        transition_out: transitions.out[productIndex],
      };
      
      products.push(product);
    }
    
    return products;
  }
  
  /**
   * Generate intro captions with timing
   */
  private static generateIntroCaptions(title: string, introHook?: string): WowCaption[] {
    const captions: WowCaption[] = [];
    
    // Default hook or use provided one
    const hook = introHook || 'Stop scrolling!';
    
    // First caption - attention grabber
    captions.push({
      start: 0.0,
      end: 1.2,
      text: hook,
      words: this.generateWordTimings(hook, 0.0, 1.2),
    });
    
    // Second caption - introduce the topic
    const introText = `Here are the Top 5 you need to see.`;
    captions.push({
      start: 1.2,
      end: 3.0,
      text: introText,
      words: this.generateWordTimings(introText, 1.2, 3.0),
    });
    
    // Third caption - category mention (if title is short enough)
    if (title.length < 60) {
      captions.push({
        start: 3.0,
        end: 4.5,
        text: title,
        words: this.generateWordTimings(title, 3.0, 4.5),
      });
    }
    
    return captions;
  }
  
  /**
   * Generate word timings for karaoke effect
   */
  private static generateWordTimings(text: string, startTime: number, endTime: number): Array<{w: string, t0: number, t1: number}> {
    const words = text.split(' ');
    const duration = endTime - startTime;
    const wordDuration = duration / words.length;
    
    return words.map((word, index) => ({
      w: word,
      t0: startTime + (index * wordDuration),
      t1: startTime + ((index + 1) * wordDuration),
    }));
  }
  
  /**
   * Extract feature chips from product description
   */
  private static extractFeatures(description: string): string[] {
    if (!description) return [];
    
    const features: string[] = [];
    
    // Common feature patterns to look for
    const patterns = [
      /(\d+[hH]?\s*(?:hour|hr|battery))/gi,  // Battery life
      /(ANC|Active Noise)/gi,                 // Noise cancellation
      /(IPX\d+|waterproof|water resistant)/gi, // Water resistance
      /(USB-?C|Type-?C|Lightning)/gi,         // Charging type
      /(wireless|bluetooth|BT\s*\d+\.\d+)/gi, // Connectivity
      /(\d+mm\s*drivers?)/gi,                 // Driver size
      /(fast charge|quick charge)/gi,         // Charging speed
      /(LDAC|aptX|AAC|SBC)/gi,               // Audio codecs
      /(foldable|portable|compact)/gi,        // Portability
      /(multi-?point)/gi,                     // Multi-device
      /(\d+W\s*(?:power|output))/gi,         // Power output
      /(touch control|gesture)/gi,            // Controls
    ];
    
    // Extract features using patterns
    for (const pattern of patterns) {
      const matches = description.match(pattern);
      if (matches && matches.length > 0) {
        const feature = matches[0].trim();
        if (feature.length <= 20 && features.length < 4) {
          features.push(this.formatFeature(feature));
        }
      }
    }
    
    // If not enough features found, extract key words
    if (features.length < 3) {
      const keywords = ['Premium', 'Pro', 'Ultra', 'HD', '4K', 'Smart', 'Advanced'];
      for (const keyword of keywords) {
        if (description.toLowerCase().includes(keyword.toLowerCase()) && features.length < 4) {
          features.push(keyword);
        }
      }
    }
    
    // Ensure we have at least 2 features, max 4
    return features.slice(0, 4);
  }
  
  /**
   * Format feature text for display
   */
  private static formatFeature(feature: string): string {
    // Standardize common abbreviations
    return feature
      .replace(/bluetooth/gi, 'BT')
      .replace(/hours?/gi, 'h')
      .replace(/waterproof/gi, 'Waterproof')
      .replace(/water resistant/gi, 'Water-resist')
      .trim();
  }
  
  /**
   * Generate subtitle from description
   */
  private static generateSubtitle(description: string): string {
    if (!description) return '';
    
    // Take first sentence or first 50 chars
    const firstSentence = description.split('.')[0];
    const subtitle = firstSentence.length > 50 
      ? firstSentence.substring(0, 47) + '...'
      : firstSentence;
    
    return subtitle.trim();
  }
  
  /**
   * Get Ken Burns effect configuration based on rank
   */
  private static getKenBurnsEffect(rank: number): any {
    const effects = [
      { zoom_start: 1.05, zoom_end: 1.12, pan: 'up' },    // Rank 5
      { zoom_start: 1.03, zoom_end: 1.10, pan: 'right' }, // Rank 4
      { zoom_start: 1.05, zoom_end: 1.14, pan: 'left' },  // Rank 3
      { zoom_start: 1.02, zoom_end: 1.08, pan: 'down' },  // Rank 2
      { zoom_start: 1.00, zoom_end: 1.10, pan: 'none' },  // Rank 1 (winner)
    ];
    
    return effects[5 - rank] || effects[0];
  }
  
  /**
   * Get transition sequences for visual variety
   */
  private static getTransitionSequence(): { in: WowTransition[], out: WowTransition[] } {
    return {
      in: ['wipe', 'circle', 'slide', 'depth-blur', 'glitch'],
      out: ['slide', 'whip-pan', 'wipe', 'slide', 'glitch'],
    };
  }
  
  /**
   * Get layout sequence for products
   */
  private static getLayoutSequence(): Array<'image-left' | 'image-right' | 'split' | 'full'> {
    return ['image-left', 'image-right', 'split', 'full', 'image-left'];
  }
  
  /**
   * Parse price from various formats
   */
  private static parsePrice(price: any): number {
    if (!price) return 0;
    
    if (typeof price === 'number') return price;
    
    // Remove currency symbols and parse
    const cleanPrice = String(price)
      .replace(/[€$£¥]/g, '')
      .replace(/,/g, '')
      .trim();
    
    return parseFloat(cleanPrice) || 0;
  }
  
  /**
   * Parse rating (0-5 scale)
   */
  private static parseRating(rating: any): number {
    if (!rating) return 0;
    
    const numRating = typeof rating === 'string' ? parseFloat(rating) : rating;
    
    if (isNaN(numRating)) return 0;
    
    // Clamp between 0 and 5
    return Math.min(5, Math.max(0, numRating));
  }
  
  /**
   * Parse review count
   */
  private static parseReviews(reviews: any): number {
    if (!reviews) return 0;
    
    if (typeof reviews === 'number') return Math.round(reviews);
    
    // Handle string formats
    let reviewStr = String(reviews).toUpperCase().replace(/,/g, '');
    
    // Handle K/M suffixes
    if (reviewStr.includes('K')) {
      return Math.round(parseFloat(reviewStr.replace('K', '')) * 1000);
    }
    if (reviewStr.includes('M')) {
      return Math.round(parseFloat(reviewStr.replace('M', '')) * 1000000);
    }
    
    return parseInt(reviewStr) || 0;
  }
  
  /**
   * Calculate discount percentage
   */
  private static calculateDiscount(currentPrice: any, originalPrice: any): number {
    if (!originalPrice) return 0;
    
    const current = this.parsePrice(currentPrice);
    const original = this.parsePrice(originalPrice);
    
    if (original <= current) return 0;
    
    const discount = ((original - current) / original) * 100;
    return Math.round(discount);
  }
  
  /**
   * Build combined voiceover URL (placeholder for now)
   */
  private static buildVoiceoverUrl(data: any): string | undefined {
    // In production, this would combine all MP3s or return the main voiceover
    // For now, return the intro MP3 as the main voiceover
    return data.IntroMp3 || undefined;
  }
  
  /**
   * Truncate text to maximum length
   */
  private static truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  }
  
  /**
   * Validate WOW data structure
   */
  static validateWowData(data: WowCountdownVideoData): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Check required fields
    if (!data.intro?.title) errors.push('Missing intro title');
    if (!data.intro?.bg_image_url) errors.push('Missing intro background image');
    if (!data.outro?.bg_image_url) errors.push('Missing outro background image');
    
    // Check products
    if (!data.products || data.products.length !== 5) {
      errors.push('Must have exactly 5 products');
    } else {
      data.products.forEach((product, index) => {
        if (!product.name) errors.push(`Product ${5 - index}: Missing name`);
        if (!product.bg_image_url) errors.push(`Product ${5 - index}: Missing image`);
        if (product.price === undefined) errors.push(`Product ${5 - index}: Missing price`);
      });
    }
    
    return {
      valid: errors.length === 0,
      errors,
    };
  }
}