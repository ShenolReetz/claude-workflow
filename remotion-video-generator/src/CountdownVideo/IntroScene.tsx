import {Audio, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import React from 'react';

interface IntroSceneProps {
	title: string;
	audioUrl?: string;
	imageUrl?: string;
}

export const IntroScene: React.FC<IntroSceneProps> = ({
	title,
	audioUrl,
	imageUrl,
}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	// Spring animation for smooth entrance
	const scale = spring({
		frame,
		fps,
		from: 0.8,
		to: 1,
		durationInFrames: 20,
	});

	// Fade in animation
	const opacity = interpolate(frame, [0, 15], [0, 1], {
		extrapolateRight: 'clamp',
	});

	// Text slide up animation
	const textY = interpolate(frame, [0, 20], [50, 0], {
		extrapolateRight: 'clamp',
	});

	return (
		<div
			style={{
				width: '100%',
				height: '100%',
				position: 'relative',
				backgroundColor: '#1a1a1a',
				overflow: 'hidden',
			}}
		>
			{/* Background Image */}
			{imageUrl && (
				<Img
					src={imageUrl}
					style={{
						width: '100%',
						height: '100%',
						objectFit: 'cover',
						position: 'absolute',
						opacity: 0.7,
					}}
				/>
			)}

			{/* Dark overlay for better text visibility */}
			<div
				style={{
					position: 'absolute',
					top: 0,
					left: 0,
					right: 0,
					bottom: 0,
					background: 'linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.7))',
				}}
			/>

			{/* Main Title */}
			<div
				style={{
					position: 'absolute',
					top: '50%',
					left: '50%',
					transform: `translate(-50%, calc(-50% + ${textY}px)) scale(${scale})`,
					textAlign: 'center',
					opacity,
					width: '90%',
				}}
			>
				<h1
					style={{
						fontSize: 72,
						color: '#FFFF00',
						fontWeight: 'bold',
						textShadow: '4px 4px 8px rgba(0,0,0,0.8)',
						margin: 0,
						fontFamily: 'Arial, sans-serif',
						lineHeight: 1.2,
						letterSpacing: '-1px',
					}}
				>
					{title}
				</h1>
				
				{/* Countdown starts text */}
				<p
					style={{
						fontSize: 36,
						color: '#FFFFFF',
						marginTop: 30,
						fontFamily: 'Arial, sans-serif',
						textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
						opacity: interpolate(frame, [30, 50], [0, 1], {
							extrapolateRight: 'clamp',
						}),
					}}
				>
					Countdown Starts Now!
				</p>
			</div>

			{/* Audio */}
			{audioUrl && <Audio src={audioUrl} />}
		</div>
	);
};