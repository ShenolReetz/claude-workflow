import {Audio, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import React from 'react';
import {Product} from './CountdownVideo';

interface ProductSceneProps {
	product: Product;
	audioUrl?: string;
	imageUrl?: string;
}

export const ProductScene: React.FC<ProductSceneProps> = ({
	product,
	audioUrl,
	imageUrl,
}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	// Rank badge animation
	const rankScale = spring({
		frame,
		fps,
		from: 0,
		to: 1,
		durationInFrames: 15,
	});

	// Product info slide in from bottom
	const infoY = interpolate(frame, [10, 25], [100, 0], {
		extrapolateRight: 'clamp',
	});

	// Star rating animation
	const starsWidth = interpolate(frame, [30, 50], [0, product.rating * 20], {
		extrapolateRight: 'clamp',
	});

	// Price reveal animation
	const priceOpacity = interpolate(frame, [40, 55], [0, 1], {
		extrapolateRight: 'clamp',
	});

	// Format price
	const formatPrice = (price: number) => {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 2,
			maximumFractionDigits: 2,
		}).format(price);
	};

	// Format reviews count
	const formatReviews = (reviews: number) => {
		if (reviews >= 1000) {
			return `${(reviews / 1000).toFixed(1)}K`;
		}
		return reviews.toString();
	};

	return (
		<div
			style={{
				width: '100%',
				height: '100%',
				position: 'relative',
				backgroundColor: '#000',
				overflow: 'hidden',
			}}
		>
			{/* Product Image Background */}
			{imageUrl && (
				<Img
					src={imageUrl}
					style={{
						width: '100%',
						height: '100%',
						objectFit: 'cover',
						position: 'absolute',
					}}
				/>
			)}

			{/* Dark gradient overlay */}
			<div
				style={{
					position: 'absolute',
					top: 0,
					left: 0,
					right: 0,
					bottom: 0,
					background: 'linear-gradient(to bottom, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.8) 70%)',
				}}
			/>

			{/* Rank Badge - Top Left */}
			<div
				style={{
					position: 'absolute',
					top: 40,
					left: 40,
					transform: `scale(${rankScale})`,
				}}
			>
				<div
					style={{
						width: 140,
						height: 140,
						borderRadius: '50%',
						backgroundColor: '#FFFF00',
						display: 'flex',
						alignItems: 'center',
						justifyContent: 'center',
						boxShadow: '0 8px 20px rgba(255, 255, 0, 0.4)',
						border: '4px solid #FFF',
					}}
				>
					<span
						style={{
							fontSize: 72,
							fontWeight: 'bold',
							color: '#000',
							fontFamily: 'Arial Black, sans-serif',
						}}
					>
						#{product.rank}
					</span>
				</div>
			</div>

			{/* Product Information Card - Bottom */}
			<div
				style={{
					position: 'absolute',
					bottom: 0,
					left: 0,
					right: 0,
					transform: `translateY(${infoY}px)`,
				}}
			>
				<div
					style={{
						backgroundColor: 'rgba(0,0,0,0.95)',
						padding: '40px',
						borderTop: '4px solid #FFFF00',
						backdropFilter: 'blur(10px)',
					}}
				>
					{/* Product Title */}
					<h2
						style={{
							fontSize: 52,
							color: '#FFF',
							marginBottom: 20,
							fontFamily: 'Arial, sans-serif',
							fontWeight: 'bold',
							lineHeight: 1.2,
							maxHeight: '130px',
							overflow: 'hidden',
							textOverflow: 'ellipsis',
							display: '-webkit-box',
							WebkitLineClamp: 2,
							WebkitBoxOrient: 'vertical',
						}}
					>
						{product.title}
					</h2>

					{/* Price and Rating Row */}
					<div
						style={{
							display: 'flex',
							justifyContent: 'space-between',
							alignItems: 'center',
							marginTop: 30,
						}}
					>
						{/* Price */}
						<div
							style={{
								opacity: priceOpacity,
							}}
						>
							<div
								style={{
									fontSize: 72,
									color: '#00FF00',
									fontWeight: 'bold',
									fontFamily: 'Arial, sans-serif',
									textShadow: '0 0 20px rgba(0, 255, 0, 0.5)',
								}}
							>
								{formatPrice(product.price)}
							</div>
						</div>

						{/* Rating and Reviews */}
						<div style={{textAlign: 'right'}}>
							{/* Star Rating */}
							<div
								style={{
									fontSize: 42,
									color: '#FFA500',
									marginBottom: 10,
									display: 'flex',
									alignItems: 'center',
									gap: 10,
								}}
							>
								<div style={{position: 'relative', display: 'inline-flex'}}>
									{/* Empty stars */}
									<span style={{color: '#444'}}>★★★★★</span>
									{/* Filled stars */}
									<span
										style={{
											position: 'absolute',
											left: 0,
											top: 0,
											color: '#FFA500',
											overflow: 'hidden',
											width: `${starsWidth}%`,
										}}
									>
										★★★★★
									</span>
								</div>
								<span
									style={{
										fontSize: 36,
										color: '#FFF',
										fontWeight: 'bold',
									}}
								>
									{product.rating.toFixed(1)}
								</span>
							</div>
							
							{/* Review Count */}
							<div
								style={{
									fontSize: 28,
									color: '#AAA',
									fontFamily: 'Arial, sans-serif',
								}}
							>
								{formatReviews(product.reviews)} reviews
							</div>
						</div>
					</div>

					{/* Description if available */}
					{product.description && (
						<p
							style={{
								fontSize: 24,
								color: '#CCC',
								marginTop: 20,
								lineHeight: 1.4,
								maxHeight: '60px',
								overflow: 'hidden',
								textOverflow: 'ellipsis',
								display: '-webkit-box',
								WebkitLineClamp: 2,
								WebkitBoxOrient: 'vertical',
							}}
						>
							{product.description}
						</p>
					)}
				</div>
			</div>

			{/* Audio */}
			{audioUrl && <Audio src={audioUrl} />}
		</div>
	);
};