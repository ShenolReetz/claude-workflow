import { CountdownVideoData } from '../schemas/CountdownVideoSchema';

/**
 * Adapter to transform Airtable data into the Remotion video schema format
 */
export class AirtableDataAdapter {
  /**
   * Transform raw Airtable data into CountdownVideoData format
   */
  static transformToVideoData(airtableData: any): CountdownVideoData {
    // Extract products data
    const products = [];
    for (let i = 1; i <= 5; i++) {
      const product = {
        title: airtableData[`ProductNo${i}Title`] || `Product #${6 - i}`,
        price: this.formatPrice(airtableData[`ProductNo${i}Price`]),
        rating: this.parseRating(airtableData[`ProductNo${i}Rating`]),
        reviews: this.parseReviews(airtableData[`ProductNo${i}Reviews`]),
        photo: airtableData[`ProductNo${i}Photo`] || '',
        description: airtableData[`ProductNo${i}Description`] || '',
        mp3: airtableData[`Product${i}Mp3`] || '',
      };
      products.push(product);
    }
    
    // Reverse products array so index 0 is Product #5, index 4 is Product #1
    products.reverse();
    
    return {
      videoTitle: airtableData.VideoTitle || 'Top 5 Products',
      introPhoto: airtableData.IntroPhoto || '',
      introMp3: airtableData.IntroMp3 || '',
      products,
      outroPhoto: airtableData.OutroPhoto || '',
      outroMp3: airtableData.OutroMp3 || '',
      brandColor: '#FFFF00', // Yellow
      accentColor: '#FF9900', // Amazon Orange
      backgroundColor: '#000000',
    };
  }
  
  /**
   * Format price string
   */
  private static formatPrice(price: any): string {
    if (!price) return '$0.00';
    
    // If it's already a string with $, return as is
    if (typeof price === 'string' && price.includes('$')) {
      return price;
    }
    
    // Convert to number and format
    const numPrice = typeof price === 'string' 
      ? parseFloat(price.replace(/[^\d.]/g, ''))
      : price;
    
    if (isNaN(numPrice)) return '$0.00';
    
    return `$${numPrice.toFixed(2)}`;
  }
  
  /**
   * Parse rating value (0-5)
   */
  private static parseRating(rating: any): number {
    if (!rating) return 0;
    
    const numRating = typeof rating === 'string'
      ? parseFloat(rating)
      : rating;
    
    if (isNaN(numRating)) return 0;
    
    // Clamp between 0 and 5
    return Math.min(5, Math.max(0, numRating));
  }
  
  /**
   * Parse review count
   */
  private static parseReviews(reviews: any): number {
    if (!reviews) return 0;
    
    // Handle string formats like "1,234" or "5.2K" or "1.3M"
    if (typeof reviews === 'string') {
      // Remove commas
      let cleanReviews = reviews.replace(/,/g, '');
      
      // Handle K/M suffixes
      if (cleanReviews.includes('K')) {
        const num = parseFloat(cleanReviews.replace('K', ''));
        return Math.round(num * 1000);
      }
      if (cleanReviews.includes('M')) {
        const num = parseFloat(cleanReviews.replace('M', ''));
        return Math.round(num * 1000000);
      }
      
      return parseInt(cleanReviews) || 0;
    }
    
    return parseInt(reviews) || 0;
  }
  
  /**
   * Validate that all required fields are present
   */
  static validateData(data: CountdownVideoData): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Check required fields
    if (!data.videoTitle) errors.push('Missing video title');
    if (!data.introPhoto) errors.push('Missing intro photo');
    if (!data.introMp3) errors.push('Missing intro audio');
    if (!data.outroPhoto) errors.push('Missing outro photo');
    if (!data.outroMp3) errors.push('Missing outro audio');
    
    // Check products
    if (!data.products || data.products.length !== 5) {
      errors.push('Must have exactly 5 products');
    } else {
      data.products.forEach((product, index) => {
        const rank = 5 - index;
        if (!product.title) errors.push(`Product #${rank}: Missing title`);
        if (!product.photo) errors.push(`Product #${rank}: Missing photo`);
        if (!product.mp3) errors.push(`Product #${rank}: Missing audio`);
        if (!product.price) errors.push(`Product #${rank}: Missing price`);
      });
    }
    
    return {
      valid: errors.length === 0,
      errors,
    };
  }
  
  /**
   * Generate mock data for testing
   */
  static generateMockData(): CountdownVideoData {
    const mockProducts = [
      {
        title: 'Premium Wireless Headphones',
        price: '$299.99',
        rating: 4.5,
        reviews: 12543,
        photo: 'https://via.placeholder.com/800x800/333/fff?text=Headphones',
        description: 'Active noise cancellation with 30-hour battery life',
        mp3: 'https://example.com/audio1.mp3',
      },
      {
        title: 'Smart Home Security Camera',
        price: '$129.99',
        rating: 4.3,
        reviews: 8921,
        photo: 'https://via.placeholder.com/800x800/333/fff?text=Camera',
        description: '4K resolution with night vision and AI detection',
        mp3: 'https://example.com/audio2.mp3',
      },
      {
        title: 'Ergonomic Office Chair',
        price: '$449.99',
        rating: 4.7,
        reviews: 5672,
        photo: 'https://via.placeholder.com/800x800/333/fff?text=Chair',
        description: 'Lumbar support with breathable mesh design',
        mp3: 'https://example.com/audio3.mp3',
      },
      {
        title: 'Portable Power Bank 20000mAh',
        price: '$59.99',
        rating: 4.4,
        reviews: 15234,
        photo: 'https://via.placeholder.com/800x800/333/fff?text=PowerBank',
        description: 'Fast charging with 3 USB ports and LED display',
        mp3: 'https://example.com/audio4.mp3',
      },
      {
        title: 'Bluetooth Mechanical Keyboard',
        price: '$149.99',
        rating: 4.8,
        reviews: 3421,
        photo: 'https://via.placeholder.com/800x800/333/fff?text=Keyboard',
        description: 'RGB backlit with hot-swappable switches',
        mp3: 'https://example.com/audio5.mp3',
      },
    ];
    
    return {
      videoTitle: 'Top 5 Tech Gadgets of 2025',
      introPhoto: 'https://via.placeholder.com/1080x1920/222/fff?text=Intro',
      introMp3: 'https://example.com/intro.mp3',
      products: mockProducts,
      outroPhoto: 'https://via.placeholder.com/1080x1920/222/fff?text=Outro',
      outroMp3: 'https://example.com/outro.mp3',
      brandColor: '#FFFF00',
      accentColor: '#FF9900',
      backgroundColor: '#000000',
    };
  }
}