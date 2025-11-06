# SentricS2 - Insanely Great Edition
## Frontend v2: Experience-First UI

> "Design is not just what it looks like and feels like. Design is how it works." - Steve Jobs

---

## The Vision

This is not an iteration. This is a **reimagination**.

We took the solid foundation of SentricS2's backend and asked: **What if the UI felt like magic?**

### The Three-Second Experience

Every screen answers ONE question:
- **CER Billing**: "How much did I make?"
- **15-Min Trading**: "How much am I leaving on the table?"
- **BESS Monitoring**: "Why am I losing money?"

## What Makes This "Insanely Great"?

### 1. CER Billing: Know Your Number Instantly

**Before:** Upload CSV → Wait → Navigate tables → Calculate manually → **4-6 hours**

**Now:** Drag file → See processing → Instant insights → **3 seconds**

### 2. 15-Min Trading: Money on the Table

```
Your 6 plants will make €847 today
BUT you could make €1,203 (+€356)
```

### 3. BESS Monitoring: Stop Losing Money

```
Performance Score: 87/100
You're losing €15,284/year
Here's how to fix it →
```

## Tech Stack

- **React 18** + **TypeScript**
- **Tailwind CSS 4** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Zustand** - Lightweight state management
- **react-dropzone** - File upload magic
- **Recharts** - Beautiful charts
- **Vite** - Lightning-fast build

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

Open http://localhost:5173

## Project Structure

```
src/
├── components/
│   ├── cer/           # CER Billing components
│   ├── trading/       # 15-Min Trading components
│   └── bess/          # BESS Monitoring components
├── store/             # Zustand state management
├── types/             # TypeScript definitions
├── App.tsx            # Main app + navigation
└── index.css          # Tailwind + custom styles
```

## Key Features

### Drag-Drop File Upload
- Entire screen becomes drop zone
- Real-time processing feedback
- Automatic format detection

### Hero Number Display
- 72px minimum for key metrics
- Count-up animations
- Tabular figures for alignment

### Actionable Insights
- Issue → Impact → Fix pattern
- One-click optimization buttons
- "Show Me The Math" transparency

## Design System

```css
Colors:
- Money Green: #10B981
- Loss Red: #EF4444
- Warning: #F59E0B
- Success: #3B82F6

Typography:
- Hero: 72px bold, tabular
- Headers: 24px semibold
- Body: 16px comfortable

Motion:
- Scale: 1.02x on interaction
- Transitions: 200-400ms ease-out
- Stagger: 100ms between items
```

## State Management

Using Zustand for simplicity:

```typescript
const useCERStore = create<CERStore>((set) => ({
  data: null,
  insights: [],
  startUpload: (fileName) => set({ isUploading: true }),
  completeUpload: (data, insights) => set({ data, insights }),
}));
```

## API Integration

Currently uses mock data. To connect real API:

```typescript
const response = await fetch('http://localhost:8000/api/v2/cer/upload', {
  method: 'POST',
  body: formData,
});
```

See `../api-gateway` for backend bridge.

## Design Philosophy

1. **Hero → Context → Action** information hierarchy
2. **Progressive disclosure** - summary first, details on demand
3. **Actionable insights** - never just data, always "what to do"
4. **Instant feedback** - every action gets immediate response

## Performance

- Code splitting via lazy loading
- Memoization for expensive components
- <200KB initial bundle size
- 60fps animations

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile: iOS 14+, Android Chrome 90+

## Future Enhancements

### Phase 2
- Real API integration
- WebSocket live updates
- Offline support (PWA)
- Mobile app

### Phase 3
- AI recommendations
- Voice commands
- Multi-language
- Dark mode

## The Difference

**Most energy management UIs:**
- Show data
- Require interpretation
- Need training

**This UI:**
- Shows insights
- Provides answers
- Feels intuitive

**That's insanely great.**

---

Built with ❤️ and an obsession with craft.
