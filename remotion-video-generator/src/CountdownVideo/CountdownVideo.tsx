import {Audio, Img, Sequence} from 'remotion';
import {IntroScene} from './IntroScene';
import {ProductScene} from './ProductScene';
import {OutroScene} from './OutroScene';
import React from 'react';

export interface Product {
	rank: number;
	title: string;
	description?: string;
	price: number;
	rating: number;
	reviews: number;
	image: string;
	affiliateLink?: string;
}

export interface CountdownVideoProps {
	title: string;
	products: Product[];
	audioUrls: {
		intro?: string;
		outro?: string;
		product1?: string;
		product2?: string;
		product3?: string;
		product4?: string;
		product5?: string;
	};
	imageUrls: {
		intro?: string;
		outro?: string;
		product1?: string;
		product2?: string;
		product3?: string;
		product4?: string;
		product5?: string;
	};
}

export const CountdownVideo: React.FC<CountdownVideoProps> = ({
	title = 'Top 5 Amazing Products',
	products = [],
	audioUrls = {},
	imageUrls = {},
}) => {
	// Ensure we have 5 products (fill with placeholders if needed)
	const productList = [...products];
	while (productList.length < 5) {
		productList.push({
			rank: 5 - productList.length,
			title: `Product ${productList.length + 1}`,
			price: 0,
			rating: 0,
			reviews: 0,
			image: '',
		});
	}

	return (
		<div
			style={{
				flex: 1,
				backgroundColor: '#000',
				width: '100%',
				height: '100%',
			}}
		>
			{/* Intro - 5 seconds (150 frames at 30fps) */}
			<Sequence from={0} durationInFrames={150}>
				<IntroScene
					title={title}
					audioUrl={audioUrls.intro}
					imageUrl={imageUrls.intro}
				/>
			</Sequence>

			{/* Products - 9 seconds each (270 frames at 30fps) */}
			{/* Countdown from 5 to 1 */}
			{productList.reverse().map((product, index) => (
				<Sequence
					key={index}
					from={150 + index * 270}
					durationInFrames={270}
				>
					<ProductScene
						product={{...product, rank: 5 - index}}
						audioUrl={audioUrls[`product${5 - index}` as keyof typeof audioUrls]}
						imageUrl={
							imageUrls[`product${5 - index}` as keyof typeof imageUrls] ||
							product.image
						}
					/>
				</Sequence>
			))}

			{/* Outro - 5 seconds (150 frames at 30fps) */}
			<Sequence from={1500} durationInFrames={150}>
				<OutroScene audioUrl={audioUrls.outro} imageUrl={imageUrls.outro} />
			</Sequence>
		</div>
	);
};