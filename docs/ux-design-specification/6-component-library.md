# 6. Component Library

## 6.1 Component Strategy

**Mobile-First Components with Progressive Enhancement**

## Core Components (MVP Priority)

**1. Percentile Hero Card**
- Large animated number (68th)
- Color-coded background gradient
- Trend arrow with animation
- WhatsApp share button
- 48x48px touch target minimum

**2. Revenue Card**
- Chilean formatting: $1.234.567,89
- Large, readable numbers
- Green/red trend indicator
- Tap to expand history
- "Actualizado hace X min" timestamp

**3. Location Performance Card**
- Swipeable on mobile
- Name + revenue + trend
- Color-coded border (performance tier)
- Progressive reveal of details
- Comparison checkbox

**4. CSV Upload Zone**
- Drag & drop with visual feedback
- Mobile: Large button (48x48px)
- Progress bar with percentage
- Column mapping preview
- Remember previous mappings

**5. Bottom Navigation (Mobile)**
- 5 items max: Dashboard, Locations, Upload, Reports, More
- Active state clearly visible
- Badge for alerts
- Fixed position
- One-handed reachable

**6. Progressive Disclosure Container**
- Collapsed: 3 key metrics
- Tap to expand: Full details
- Smooth animation
- Clear expand/collapse indicator
- Maintains scroll position

**7. Offline Indicator**
- Subtle banner when offline
- "Trabajando sin conexión"
- Last sync timestamp
- Auto-hide when connected

**8. WhatsApp Share Card**
- Auto-generated image
- Clean layout with branding
- Key metrics included
- Pre-formatted message
- One-tap sharing

## Data Visualization Components

**9. Trend Sparkline**
- Minimal, no axes
- Touch to see value
- 30-day default view
- Green up, red down

**10. Performance Bar**
- Horizontal progress bar
- Color-coded by tier
- Animated on load
- Percentage label

**11. Comparison Chart**
- Side-by-side bars
- Touch to highlight
- Swipe between periods
- Clear labels

## Form Components

**12. Smart Column Mapper**
- Auto-detect column types
- Dropdown with suggestions
- Preview first row
- Save mapping template
- Visual validation

**13. Quick Filter Pills**
- Horizontal scroll on mobile
- Single tap to toggle
- Clear active state
- Count badge

## Feedback Components

**14. Success Animation**
- Green checkmark
- Brief celebration
- Auto-dismiss
- Non-blocking

**15. Loading State**
- Skeleton screens
- Progress percentage
- Estimated time
- Cancel option

## Component Design Principles

**Performance:**
- Lazy load below the fold
- Skeleton screens while loading
- <100ms interaction feedback
- Optimistic UI updates

**Accessibility:**
- 48x48px minimum touch targets
- 4.5:1 color contrast minimum
- Focus indicators on web
- Screen reader labels

**Localization:**
- Spanish-first text
- Chilean number formats
- CLP currency symbol
- Local date formats (DD/MM/YYYY)

---
