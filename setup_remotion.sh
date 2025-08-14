#!/bin/bash
# Remotion Setup Script for Production Workflow
# ==============================================

echo "🎬 Setting up Remotion for Video Generation..."
echo "============================================="

# Check Node.js version
NODE_VERSION=$(node -v 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1)
if [ -z "$NODE_VERSION" ] || [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js 16+ is required. Please install Node.js first."
    echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    exit 1
else
    echo "✅ Node.js version: $(node -v)"
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing FFmpeg..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
else
    echo "✅ FFmpeg is installed: $(ffmpeg -version | head -n1)"
fi

# Install system dependencies for headless Chrome (required for some Remotion features)
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 \
    libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 \
    libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 \
    libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \
    libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates \
    fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget \
    libgbm-dev 2>/dev/null || echo "⚠️ Some dependencies may already be installed"

# Create Remotion project directory
REMOTION_DIR="/home/claude-workflow/remotion-countdown"
echo "📁 Creating Remotion project at: $REMOTION_DIR"

if [ -d "$REMOTION_DIR" ]; then
    echo "⚠️ Remotion directory already exists. Backing up..."
    mv "$REMOTION_DIR" "${REMOTION_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

# Initialize Remotion project
cd /home/claude-workflow
echo "🚀 Initializing Remotion project..."
npx create-video@latest --template hello-world remotion-countdown

cd "$REMOTION_DIR"

# Install additional dependencies
echo "📦 Installing additional dependencies..."
npm install --save \
    @remotion/media-utils \
    @remotion/gif \
    @remotion/google-fonts

# Create countdown video template
echo "📝 Creating countdown video template..."

# Create src directory structure
mkdir -p src/compositions
mkdir -p src/components
mkdir -p public/assets

# Create the main Video composition file
cat > src/Video.tsx << 'EOF'
import {Composition} from 'remotion';
import {CountdownVideo} from './compositions/CountdownVideo';

export const RemotionVideo = () => {
  return (
    <>
      <Composition
        id="CountdownVideo"
        component={CountdownVideo}
        durationInFrames={1650} // 55 seconds at 30fps
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "Top 5 Amazing Products",
          products: [],
          audioUrls: {},
          imageUrls: {}
        }}
      />
    </>
  );
};
EOF

# Create the CountdownVideo composition
cat > src/compositions/CountdownVideo.tsx << 'EOF'
import {Audio, Img, Sequence, useCurrentFrame, interpolate} from 'remotion';
import {IntroScene} from '../components/IntroScene';
import {ProductScene} from '../components/ProductScene';
import {OutroScene} from '../components/OutroScene';

interface Product {
  rank: number;
  title: string;
  price: number;
  rating: number;
  reviews: number;
  image: string;
}

interface CountdownVideoProps {
  title: string;
  products: Product[];
  audioUrls: Record<string, string>;
  imageUrls: Record<string, string>;
}

export const CountdownVideo: React.FC<CountdownVideoProps> = ({
  title,
  products,
  audioUrls,
  imageUrls,
}) => {
  return (
    <div style={{flex: 1, backgroundColor: '#000'}}>
      {/* Intro - 5 seconds (150 frames) */}
      <Sequence from={0} durationInFrames={150}>
        <IntroScene 
          title={title}
          audioUrl={audioUrls.intro}
          imageUrl={imageUrls.intro}
        />
      </Sequence>

      {/* Products - 9 seconds each (270 frames) */}
      {products.map((product, index) => (
        <Sequence
          key={index}
          from={150 + index * 270}
          durationInFrames={270}
        >
          <ProductScene
            product={product}
            audioUrl={audioUrls[`product${index + 1}`]}
            imageUrl={imageUrls[`product${index + 1}`] || product.image}
          />
        </Sequence>
      ))}

      {/* Outro - 5 seconds (150 frames) */}
      <Sequence from={1500} durationInFrames={150}>
        <OutroScene
          audioUrl={audioUrls.outro}
          imageUrl={imageUrls.outro}
        />
      </Sequence>
    </div>
  );
};
EOF

# Create IntroScene component
cat > src/components/IntroScene.tsx << 'EOF'
import {Audio, Img, useCurrentFrame, interpolate, spring} from 'remotion';
import {useVideoConfig} from 'remotion';

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
  
  const scale = spring({
    frame,
    fps,
    from: 0.8,
    to: 1,
    durationInFrames: 20,
  });

  const opacity = interpolate(frame, [0, 10], [0, 1]);

  return (
    <div style={{
      width: '100%',
      height: '100%',
      position: 'relative',
      backgroundColor: '#1a1a1a',
    }}>
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
      
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: `translate(-50%, -50%) scale(${scale})`,
        textAlign: 'center',
        opacity,
      }}>
        <h1 style={{
          fontSize: 80,
          color: '#FFFF00',
          fontWeight: 'bold',
          textShadow: '4px 4px 8px rgba(0,0,0,0.8)',
          padding: '0 40px',
          fontFamily: 'Arial, sans-serif',
        }}>
          {title}
        </h1>
      </div>

      {audioUrl && <Audio src={audioUrl} />}
    </div>
  );
};
EOF

# Create ProductScene component
cat > src/components/ProductScene.tsx << 'EOF'
import {Audio, Img, useCurrentFrame, interpolate} from 'remotion';

interface Product {
  rank: number;
  title: string;
  price: number;
  rating: number;
  reviews: number;
}

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
  const slideIn = interpolate(frame, [0, 15], [-100, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{
      width: '100%',
      height: '100%',
      position: 'relative',
      backgroundColor: '#000',
    }}>
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

      {/* Rank Badge */}
      <div style={{
        position: 'absolute',
        top: 40,
        left: 40,
        width: 120,
        height: 120,
        borderRadius: '50%',
        backgroundColor: '#FFFF00',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transform: `translateX(${slideIn}px)`,
      }}>
        <span style={{
          fontSize: 60,
          fontWeight: 'bold',
          color: '#000',
        }}>
          #{product.rank}
        </span>
      </div>

      {/* Product Info */}
      <div style={{
        position: 'absolute',
        bottom: 100,
        left: 40,
        right: 40,
        backgroundColor: 'rgba(0,0,0,0.9)',
        padding: 40,
        borderRadius: 20,
        border: '3px solid #FFFF00',
      }}>
        <h2 style={{
          fontSize: 48,
          color: '#FFF',
          marginBottom: 20,
          fontFamily: 'Arial, sans-serif',
        }}>
          {product.title}
        </h2>
        
        <div style={{display: 'flex', justifyContent: 'space-between'}}>
          <div style={{fontSize: 72, color: '#00FF00', fontWeight: 'bold'}}>
            ${product.price}
          </div>
          <div style={{textAlign: 'right'}}>
            <div style={{fontSize: 48, color: '#FFA500'}}>
              ⭐ {product.rating}/5
            </div>
            <div style={{fontSize: 36, color: '#FFF'}}>
              {product.reviews.toLocaleString()} reviews
            </div>
          </div>
        </div>
      </div>

      {audioUrl && <Audio src={audioUrl} />}
    </div>
  );
};
EOF

# Create OutroScene component
cat > src/components/OutroScene.tsx << 'EOF'
import {Audio, Img, useCurrentFrame, interpolate, spring} from 'remotion';
import {useVideoConfig} from 'remotion';

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
  
  const buttonScale = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    durationInFrames: 30,
  });

  return (
    <div style={{
      width: '100%',
      height: '100%',
      position: 'relative',
      backgroundColor: '#0a0a0a',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
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

      <h1 style={{
        fontSize: 90,
        color: '#FFFF00',
        fontWeight: 'bold',
        textAlign: 'center',
        marginBottom: 100,
        textShadow: '4px 4px 10px rgba(0,0,0,0.8)',
        zIndex: 1,
      }}>
        Thanks for Watching!
      </h1>

      <div style={{
        transform: `scale(${buttonScale})`,
        backgroundColor: '#FF0000',
        padding: '40px 100px',
        borderRadius: 50,
        border: '4px solid #FFF',
        zIndex: 1,
      }}>
        <span style={{
          fontSize: 60,
          color: '#FFF',
          fontWeight: 'bold',
        }}>
          SUBSCRIBE
        </span>
      </div>

      <p style={{
        fontSize: 48,
        color: '#FFF',
        marginTop: 80,
        zIndex: 1,
      }}>
        👇 Links in Description 👇
      </p>

      {audioUrl && <Audio src={audioUrl} />}
    </div>
  );
};
EOF

# Update the Root.tsx file
cat > src/Root.tsx << 'EOF'
import {Composition} from 'remotion';
import {CountdownVideo} from './compositions/CountdownVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="CountdownVideo"
        component={CountdownVideo}
        durationInFrames={1650}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "Top 5 Amazing Products",
          products: [
            {rank: 5, title: "Product 5", price: 99.99, rating: 4.0, reviews: 500, image: ""},
            {rank: 4, title: "Product 4", price: 89.99, rating: 4.2, reviews: 750, image: ""},
            {rank: 3, title: "Product 3", price: 79.99, rating: 4.3, reviews: 1000, image: ""},
            {rank: 2, title: "Product 2", price: 69.99, rating: 4.4, reviews: 1500, image: ""},
            {rank: 1, title: "Product 1", price: 59.99, rating: 4.5, reviews: 2000, image: ""},
          ],
          audioUrls: {},
          imageUrls: {}
        }}
      />
    </>
  );
};
EOF

echo "✅ Remotion template created!"

# Test the setup
echo ""
echo "🧪 Testing Remotion setup..."
cd "$REMOTION_DIR"
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ Remotion Setup Complete!"
    echo "========================================="
    echo "📁 Project location: $REMOTION_DIR"
    echo ""
    echo "To test the video generation:"
    echo "  cd $REMOTION_DIR"
    echo "  npm start  # Opens preview studio"
    echo ""
    echo "To render a test video:"
    echo "  npx remotion render CountdownVideo out/test.mp4"
    echo ""
    echo "To integrate with workflow:"
    echo "  python3 /home/claude-workflow/remotion_countdown_implementation.py"
    echo "========================================="
else
    echo "❌ Remotion setup failed. Check the errors above."
    exit 1
fi