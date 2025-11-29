import { Composition } from "remotion";
import { HelloWorld, myCompSchema } from "./HelloWorld";
import { Logo, myCompSchema2 } from "./HelloWorld/Logo";
import { CountdownVideo, CountdownVideoProps } from "./CountdownVideo/CountdownVideo";
import { ProductionCountdownVideo } from "./compositions/ProductionComposition";
import { WowCountdownVideo, WowVideoPropsSchema } from "./compositions/WowCountdownVideo";
import { WowVideoUltra, WowUltraSchema } from "./compositions/WowVideoUltra";

// Each <Composition> is an entry in the sidebar!

export const RemotionRoot: React.FC = () => {
  // WOW video timeline - MUST be exactly 55 seconds (1650 frames)
  const wowTimeline = {
    intro_frames: 150,      // 5 seconds
    product_frames: 270,     // 9 seconds per product
    outro_frames: 150,      // 5 seconds
    transition_overlap_frames: 30,  // Overlap frames for smooth transitions (doesn't reduce total duration)
  };
  
  // CORRECT Total frames calculation:
  // Intro: 150 frames (5 seconds)
  // Products: 5 products * 270 frames = 1350 frames (45 seconds)
  // Outro: 150 frames (5 seconds)
  // Total: 150 + 1350 + 150 = 1650 frames (55 seconds)
  // Note: transition_overlap_frames DO NOT reduce total duration, they just control visual overlap
  const wowTotalFrames = 1650; // Exactly 55 seconds at 30fps
  
  return (
    <>
      <Composition
        // You can take the "id" to render a video:
        // npx remotion render HelloWorld
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        // You can override these props for each render:
        // https://www.remotion.dev/docs/parametrized-rendering
        schema={myCompSchema}
        defaultProps={{
          titleText: "Welcome to Remotion",
          titleColor: "#000000",
          logoColor1: "#91EAE4",
          logoColor2: "#86A8E7",
        }}
      />

      {/* Mount any React component to make it show up in the sidebar and work on it individually! */}
      <Composition
        id="OnlyLogo"
        component={Logo}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        schema={myCompSchema2}
        defaultProps={{
          logoColor1: "#91dAE2" as const,
          logoColor2: "#86A8E7" as const,
        }}
      />
      
      {/* Production Countdown Video Composition - Legacy */}
      <Composition
        id="CountdownVideo"
        component={CountdownVideo}
        durationInFrames={1650} // 55 seconds at 30fps
        fps={30}
        width={1080}
        height={1920} // Vertical format for social media
        defaultProps={{
          title: 'Top 5 Amazing Products',
          products: [
            {
              rank: 5,
              title: 'Sample Product 5',
              price: 99.99,
              rating: 4.0,
              reviews: 500,
              image: '',
            },
            {
              rank: 4,
              title: 'Sample Product 4',
              price: 89.99,
              rating: 4.2,
              reviews: 750,
              image: '',
            },
            {
              rank: 3,
              title: 'Sample Product 3',
              price: 79.99,
              rating: 4.3,
              reviews: 1000,
              image: '',
            },
            {
              rank: 2,
              title: 'Sample Product 2',
              price: 69.99,
              rating: 4.4,
              reviews: 1500,
              image: '',
            },
            {
              rank: 1,
              title: 'Sample Product 1',
              price: 59.99,
              rating: 4.5,
              reviews: 2000,
              image: '',
            },
          ],
          audioUrls: {},
          imageUrls: {},
        }}
      />
      
      {/* Production Countdown Video - New Schema */}
      <Composition
        id="ProductionCountdownVideo"
        component={ProductionCountdownVideo}
        durationInFrames={1650} // 55 seconds at 30fps
        fps={30}
        width={1080}
        height={1920} // Vertical format for social media
        defaultProps={{
          data: {
            videoTitle: 'Top 5 Amazing Products',
            recordId: 'test',
            introPhoto: '',
            introMp3: '',
            outroPhoto: '',
            outroMp3: '',
            product1: {
              title: 'Product 1',
              price: '59.99',
              rating: 4.5,
              reviews: '2000',
              photo: '',
              mp3: '',
              description: '',
              affiliateLink: '',
              badge: 'BEST_SELLER',
            },
            product2: {
              title: 'Product 2',
              price: '69.99',
              rating: 4.4,
              reviews: '1500',
              photo: '',
              mp3: '',
              description: '',
            },
            product3: {
              title: 'Product 3',
              price: '79.99',
              rating: 4.3,
              reviews: '1000',
              photo: '',
              mp3: '',
              description: '',
            },
            product4: {
              title: 'Product 4',
              price: '89.99',
              rating: 4.2,
              reviews: '750',
              photo: '',
              mp3: '',
              description: '',
            },
            product5: {
              title: 'Product 5',
              price: '99.99',
              rating: 4.0,
              reviews: '500',
              photo: '',
              mp3: '',
              description: '',
            },
          },
          platform: 'tiktok',
          transition: 'slide-up',
          brandColors: {
            primary: '#FFFF00',
            accent: '#00FF00',
            background: '#000000',
          },
          socialMedia: {
            showSubscribe: true,
            subscribeCTA: 'Subscribe for More!',
            platform: 'tiktok',
          },
        }}
      />
      
      {/* WOW Countdown Video Composition - FIXED to 55 seconds */}
      <Composition
        id="WowCountdownVideo"
        component={WowCountdownVideo}
        durationInFrames={wowTotalFrames} // Exactly 1650 frames = 55 seconds at 30fps
        fps={30}
        width={1080}
        height={1920}
        schema={WowVideoPropsSchema}
        defaultProps={{
          meta: {
            fps: 30,
            width: 1080,
            height: 1920,
            max_total_frames: 1650, // Updated to match actual duration
            brand: 'default',
            primary_color: '#00D3A7',
          },
          timeline: wowTimeline,
          intro: {
            title: 'Top 5 Products',
            bg_image_url: '',
            caption_style: 'karaoke',
            transition_out: 'glitch',
          },
          products: [
            {
              rank: 5,
              name: 'Sample Product 5',
              subtitle: 'Amazing features and great value',
              bg_image_url: '',
              ken_burns: {
                zoom_start: 1.05,
                zoom_end: 1.12,
                pan: 'up',
              },
              rating: 4.0,
              reviews_count: 500,
              price: 99.99,
              currency: 'EUR',
              discount_pct: 10,
              feature_chips: ['Feature 1', 'Feature 2'],
              layout: 'full',
              transition_in: 'wipe',
              transition_out: 'slide',
            },
            {
              rank: 4,
              name: 'Sample Product 4',
              subtitle: 'Professional quality at affordable price',
              bg_image_url: '',
              ken_burns: {
                zoom_start: 1.03,
                zoom_end: 1.10,
                pan: 'right',
              },
              rating: 4.2,
              reviews_count: 750,
              price: 89.99,
              currency: 'EUR',
              discount_pct: 15,
              feature_chips: ['Premium', 'Durable'],
              layout: 'image-left',
              transition_in: 'circle',
              transition_out: 'whip-pan',
            },
            {
              rank: 3,
              name: 'Sample Product 3',
              subtitle: 'Best in class performance',
              bg_image_url: '',
              ken_burns: {
                zoom_start: 1.05,
                zoom_end: 1.14,
                pan: 'left',
              },
              rating: 4.3,
              reviews_count: 1000,
              price: 79.99,
              currency: 'EUR',
              discount_pct: 20,
              feature_chips: ['Fast', 'Reliable', 'Efficient'],
              layout: 'split',
              transition_in: 'slide',
              transition_out: 'wipe',
            },
            {
              rank: 2,
              name: 'Sample Product 2',
              subtitle: 'Customer favorite with thousands of reviews',
              bg_image_url: '',
              ken_burns: {
                zoom_start: 1.02,
                zoom_end: 1.08,
                pan: 'down',
              },
              rating: 4.4,
              reviews_count: 1500,
              price: 69.99,
              currency: 'EUR',
              discount_pct: 25,
              feature_chips: ['Popular', 'Tested', 'Proven'],
              layout: 'image-right',
              transition_in: 'depth-blur',
              transition_out: 'slide',
            },
            {
              rank: 1,
              name: 'Sample Product 1',
              subtitle: 'The ultimate choice for professionals',
              bg_image_url: '',
              ken_burns: {
                zoom_start: 1.00,
                zoom_end: 1.10,
                pan: 'none',
              },
              rating: 4.5,
              reviews_count: 2000,
              price: 59.99,
              currency: 'EUR',
              discount_pct: 30,
              feature_chips: ['#1 Rated', 'Award Winner', 'Best Seller'],
              layout: 'full',
              transition_in: 'glitch',
              transition_out: 'glitch',
            },
          ],
          outro: {
            bg_image_url: '',
            cta_text: 'Subscribe for More!',
            cta_animation: 'shimmer',
            legal_note: 'Affiliate links in description',
            transition_in: 'glitch',
          },
        }}
      />
      
      {/* WOW VIDEO ULTRA - Amazing Effects Version */}
      <Composition
        id="WowVideoUltra"
        component={WowVideoUltra}
        durationInFrames={1800} // 60 seconds at 30fps
        fps={30}
        width={1080}
        height={1920}
        schema={WowUltraSchema}
        defaultProps={{
          meta: {
            fps: 30,
            width: 1080,
            height: 1920,
            durationInSeconds: 60,
          },
          products: [
            {
              rank: 5,
              title: 'Amazing Product 5',
              description: 'This product features cutting-edge technology and exceptional build quality.',
              price: 99.99,
              originalPrice: 149.99,
              currency: '$',
              rating: 4.0,
              reviewCount: 1250,
              imageUrl: '',
              features: ['Premium Quality', 'Fast Shipping', 'Great Value'],
              badge: 'LIMITED_DEAL',
              affiliateLink: '#',
              topReview: {
                author: 'John D.',
                rating: 5,
                title: 'Exceeded expectations!',
                text: 'Best purchase I have made this year. Highly recommend!',
                verified: true,
              },
            },
            {
              rank: 4,
              title: 'Premium Product 4',
              description: 'Professional grade quality at an affordable price point.',
              price: 89.99,
              originalPrice: 129.99,
              currency: '$',
              rating: 4.2,
              reviewCount: 2340,
              imageUrl: '',
              features: ['Durable', 'Efficient', 'Eco-Friendly'],
              badge: null,
              affiliateLink: '#',
              topReview: {
                author: 'Sarah M.',
                rating: 5,
                title: 'Amazing quality!',
                text: 'Worth every penny. Will definitely buy again!',
                verified: true,
              },
            },
            {
              rank: 3,
              title: 'Top Rated Product 3',
              description: 'Industry leading performance with outstanding customer satisfaction.',
              price: 79.99,
              originalPrice: 119.99,
              currency: '$',
              rating: 4.3,
              reviewCount: 5670,
              imageUrl: '',
              features: ['Fast', 'Reliable', 'Warranty'],
              badge: 'TOP_RATED',
              affiliateLink: '#',
              topReview: {
                author: 'Mike R.',
                rating: 4,
                title: 'Great value',
                text: 'Good quality for the price. Fast shipping too!',
                verified: true,
              },
            },
            {
              rank: 2,
              title: 'Customer Favorite 2',
              description: 'Thousands of satisfied customers cant be wrong. See why this is a bestseller.',
              price: 69.99,
              originalPrice: 99.99,
              currency: '$',
              rating: 4.5,
              reviewCount: 12500,
              imageUrl: '',
              features: ['Popular', 'Tested', 'Proven'],
              badge: 'AMAZON_CHOICE',
              affiliateLink: '#',
              topReview: {
                author: 'Emma L.',
                rating: 5,
                title: 'Love it!',
                text: 'Exactly as described. Perfect!',
                verified: true,
              },
            },
            {
              rank: 1,
              title: '#1 Best Seller',
              description: 'The ultimate choice for professionals and enthusiasts alike. Unmatched quality.',
              price: 59.99,
              originalPrice: 89.99,
              currency: '$',
              rating: 4.8,
              reviewCount: 25000,
              imageUrl: '',
              features: ['#1 Rated', 'Award Winner', 'Best Value'],
              badge: 'BEST_SELLER',
              affiliateLink: '#',
              topReview: {
                author: 'David K.',
                rating: 5,
                title: 'Game changer!',
                text: 'This is the best in its category. Highly recommend!',
                verified: true,
              },
            },
          ],
          audio: {
            backgroundMusic: '',
            voiceoverUrl: '',
            subtitles: [
              { startTime: 0, endTime: 5, text: "Let's discover the top 5 amazing products that will change your life!" },
              { startTime: 5, endTime: 15, text: "Number 5: Amazing Product 5 - Premium quality at an unbeatable price!", productIndex: 0 },
              { startTime: 15, endTime: 25, text: "Number 4: Premium Product 4 - Professional grade for everyone!", productIndex: 1 },
              { startTime: 25, endTime: 35, text: "Number 3: Top Rated Product 3 - Industry leading performance!", productIndex: 2 },
              { startTime: 35, endTime: 45, text: "Number 2: Customer Favorite - Thousands can't be wrong!", productIndex: 3 },
              { startTime: 45, endTime: 55, text: "Number 1: The Best Seller - Unmatched quality and value!", productIndex: 4 },
              { startTime: 55, endTime: 60, text: "Thanks for watching! Click the links to shop these amazing deals!" },
            ],
          },
          effects: {
            transitionStyle: 'morph',
            colorScheme: 'vibrant',
            particleEffects: true,
            glowEffects: true,
            parallaxDepth: true,
          },
          branding: {
            primaryColor: '#FF6B35',
            secondaryColor: '#4ECDC4',
            accentColor: '#FFE66D',
            fontFamily: 'Inter',
          },
        }}
      />
    </>
  );
};