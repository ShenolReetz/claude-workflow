import {Audio, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import React from 'react';

interface OutroSceneProps {
	audioUrl?: string;
	imageUrl?: string;
}

export const OutroScene: React.FC<OutroSceneProps> = ({
	audioUrl,
	imageUrl,
}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	// Subscribe button animation
	const buttonScale = spring({
		frame,
		fps,
		from: 0,
		to: 1,
		durationInFrames: 30,
		config: {
			damping: 15,
			stiffness: 100,
		},
	});

	// Pulse animation for subscribe button
	const pulse = Math.sin(frame * 0.1) * 0.05 + 1;

	// Text animations
	const thanksOpacity = interpolate(frame, [0, 20], [0, 1], {
		extrapolateRight: 'clamp',
	});

	const linksOpacity = interpolate(frame, [40, 60], [0, 1], {
		extrapolateRight: 'clamp',
	});

	// Background zoom animation
	const bgScale = interpolate(frame, [0, 150], [1, 1.1], {
		extrapolateRight: 'clamp',
	});

	return (
		<div
			style={{
				width: '100%',
				height: '100%',
				position: 'relative',
				backgroundColor: '#0a0a0a',
				display: 'flex',
				flexDirection: 'column',
				alignItems: 'center',
				justifyContent: 'center',
				overflow: 'hidden',
			}}
		>
			{/* Background Image with zoom effect */}
			{imageUrl && (
				<div
					style={{
						position: 'absolute',
						width: '100%',
						height: '100%',
						transform: `scale(${bgScale})`,
					}}
				>
					<Img
						src={imageUrl}
						style={{
							width: '100%',
							height: '100%',
							objectFit: 'cover',
							opacity: 0.5,
						}}
					/>
				</div>
			)}

			{/* Dark overlay */}
			<div
				style={{
					position: 'absolute',
					top: 0,
					left: 0,
					right: 0,
					bottom: 0,
					background: 'radial-gradient(circle, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.9) 100%)',
				}}
			/>

			{/* Content Container */}
			<div
				style={{
					position: 'relative',
					zIndex: 1,
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					gap: 60,
				}}
			>
				{/* Thanks Message */}
				<h1
					style={{
						fontSize: 80,
						color: '#FFFF00',
						fontWeight: 'bold',
						textAlign: 'center',
						textShadow: '4px 4px 10px rgba(0,0,0,0.8)',
						fontFamily: 'Arial, sans-serif',
						opacity: thanksOpacity,
						marginBottom: 20,
					}}
				>
					Thanks for Watching!
				</h1>

				{/* Subscribe Button */}
				<div
					style={{
						transform: `scale(${buttonScale * pulse})`,
					}}
				>
					<div
						style={{
							backgroundColor: '#FF0000',
							padding: '35px 90px',
							borderRadius: 60,
							border: '5px solid #FFF',
							boxShadow: '0 10px 40px rgba(255, 0, 0, 0.6)',
							display: 'flex',
							alignItems: 'center',
							gap: 20,
							cursor: 'pointer',
						}}
					>
						{/* Bell Icon */}
						<span
							style={{
								fontSize: 56,
								color: '#FFF',
							}}
						>
							🔔
						</span>
						<span
							style={{
								fontSize: 52,
								color: '#FFF',
								fontWeight: 'bold',
								fontFamily: 'Arial, sans-serif',
								letterSpacing: '2px',
							}}
						>
							SUBSCRIBE
						</span>
					</div>
				</div>

				{/* Links in Description */}
				<div
					style={{
						opacity: linksOpacity,
						display: 'flex',
						flexDirection: 'column',
						alignItems: 'center',
						gap: 20,
					}}
				>
					<p
						style={{
							fontSize: 44,
							color: '#FFF',
							fontFamily: 'Arial, sans-serif',
							textAlign: 'center',
						}}
					>
						👇 Check Links in Description 👇
					</p>
					<p
						style={{
							fontSize: 32,
							color: '#AAA',
							fontFamily: 'Arial, sans-serif',
							textAlign: 'center',
						}}
					>
						Get the best deals on all products!
					</p>
				</div>

				{/* Social Icons */}
				<div
					style={{
						display: 'flex',
						gap: 40,
						marginTop: 20,
						opacity: interpolate(frame, [80, 100], [0, 1], {
							extrapolateRight: 'clamp',
						}),
					}}
				>
					{['📧', '📱', '💬', '🌐'].map((icon, index) => (
						<div
							key={index}
							style={{
								fontSize: 48,
								transform: `translateY(${interpolate(
									frame,
									[80 + index * 5, 90 + index * 5],
									[20, 0],
									{extrapolateRight: 'clamp'}
								)}px)`,
							}}
						>
							{icon}
						</div>
					))}
				</div>
			</div>

			{/* Audio */}
			{audioUrl && <Audio src={audioUrl} />}
		</div>
	);
};