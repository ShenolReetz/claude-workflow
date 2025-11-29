import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { STYLES, LAYOUTS, ANIMATIONS } from '../schemas/CountdownVideoSchema';
import { StarRating } from './StarRating';
import { CountdownBadge } from './CountdownBadge';
import { PriceTag } from './PriceTag';

interface ProductProps {
  rank: number;
  product: {
    title: string;
    price: string;
    rating: number;
    reviews: number;
    photo: string;
    description: string;
  };
  isLast: boolean;
  brandColor: string;
  accentColor: string;
}

export const ProductCard: React.FC<ProductProps> = ({
  rank,
  product,
  isLast,
  brandColor,
  accentColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Stagger animations for elements
  const imageScale = spring({
    frame,
    fps,
    from: 0.9,
    to: 1,
    config: ANIMATIONS.SMOOTH_SPRING,
  });
  
  const imageOpacity = interpolate(
    frame,
    [0, 15],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Title animation
  const titleX = spring({
    frame: frame - 10,
    fps,
    from: -50,
    to: 0,
    config: ANIMATIONS.SPRING_CONFIG,
  });
  
  const titleOpacity = interpolate(
    frame,
    [10, 25],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Price animation
  const priceScale = spring({
    frame: frame - 20,
    fps,
    from: 0,
    to: 1,
    config: ANIMATIONS.BOUNCE_SPRING,
  });
  
  // Rating animation
  const ratingOpacity = interpolate(
    frame,
    [25, 40],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Description animation
  const descriptionY = spring({
    frame: frame - 30,
    fps,
    from: 30,
    to: 0,
    config: ANIMATIONS.SMOOTH_SPRING,
  });
  
  const descriptionOpacity = interpolate(
    frame,
    [30, 45],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );
  
  // Special effect for #1 product
  const crownScale = isLast
    ? spring({
        frame: frame - 40,
        fps,
        from: 0,
        to: 1,
        config: ANIMATIONS.BOUNCE_SPRING,
      })
    : 0;
  
  // Format review count
  const formatReviews = (count: number) => {
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };
  
  return (
    <AbsoluteFill>
      {/* Product Image Container */}
      <AbsoluteFill
        style={{
          top: LAYOUTS.PRODUCT_CARD.IMAGE_Y,
          height: LAYOUTS.PRODUCT_CARD.IMAGE_HEIGHT,
          transform: `scale(${imageScale})`,
          opacity: imageOpacity,
        }}
      >
        <div
          style={{
            width: '80%',
            height: '100%',
            margin: '0 auto',
            borderRadius: STYLES.RADIUS.LARGE,
            overflow: 'hidden',
            boxShadow: STYLES.SHADOWS.CARD,
            position: 'relative',
          }}
        >
          <Img
            src={product.photo}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
          
          {/* Gradient overlay for bottom text */}
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: '30%',
              background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)',
            }}
          />
        </div>
      </AbsoluteFill>
      
      {/* Countdown Badge */}
      <CountdownBadge
        rank={rank}
        isLast={isLast}
        brandColor={brandColor}
      />
      
      {/* Crown for #1 Product */}
      {isLast && (
        <div
          style={{
            position: 'absolute',
            top: LAYOUTS.PRODUCT_CARD.IMAGE_Y - 80,
            left: '50%',
            transform: `translateX(-50%) scale(${crownScale})`,
          }}
        >
          <svg width="120" height="100" viewBox="0 0 24 24" fill={brandColor}>
            <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5z" />
          </svg>
        </div>
      )}
      
      {/* Product Info Container */}
      <div
        style={{
          position: 'absolute',
          top: LAYOUTS.PRODUCT_CARD.TITLE_Y,
          left: STYLES.SAFE_ZONE.SIDES,
          right: STYLES.SAFE_ZONE.SIDES,
        }}
      >
        {/* Product Title */}
        <h2
          style={{
            color: STYLES.COLORS.TEXT_PRIMARY,
            fontSize: STYLES.FONT_SIZES.PRODUCT_NAME,
            fontFamily: STYLES.FONTS.DISPLAY,
            fontWeight: 700,
            lineHeight: 1.2,
            margin: 0,
            marginBottom: 20,
            transform: `translateX(${titleX}px)`,
            opacity: titleOpacity,
            textShadow: STYLES.SHADOWS.TEXT,
          }}
        >
          {product.title}
        </h2>
        
        {/* Price Tag */}
        <div
          style={{
            transform: `scale(${priceScale})`,
            transformOrigin: 'left center',
            marginBottom: 20,
          }}
        >
          <PriceTag
            price={product.price}
            accentColor={accentColor}
          />
        </div>
        
        {/* Rating and Reviews */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 20,
            opacity: ratingOpacity,
            marginBottom: 20,
          }}
        >
          <StarRating rating={product.rating} size={40} />
          <span
            style={{
              color: STYLES.COLORS.TEXT_SECONDARY,
              fontSize: STYLES.FONT_SIZES.REVIEWS,
              fontFamily: STYLES.FONTS.PRIMARY,
            }}
          >
            {formatReviews(product.reviews)} reviews
          </span>
        </div>
        
        {/* Description */}
        <p
          style={{
            color: STYLES.COLORS.TEXT_SECONDARY,
            fontSize: STYLES.FONT_SIZES.DESCRIPTION,
            fontFamily: STYLES.FONTS.PRIMARY,
            lineHeight: 1.4,
            margin: 0,
            transform: `translateY(${descriptionY}px)`,
            opacity: descriptionOpacity,
            maxWidth: '90%',
          }}
        >
          {product.description}
        </p>
      </div>
      
      {/* Bottom Action Hint */}
      <div
        style={{
          position: 'absolute',
          bottom: STYLES.SAFE_ZONE.BOTTOM + 40,
          left: 0,
          right: 0,
          textAlign: 'center',
          opacity: interpolate(frame, [50, 70], [0, 0.7]),
        }}
      >
        <span
          style={{
            color: brandColor,
            fontSize: 24,
            fontFamily: STYLES.FONTS.PRIMARY,
            fontWeight: 600,
          }}
        >
          Swipe up to shop ↑
        </span>
      </div>
    </AbsoluteFill>
  );
};