# 8. Responsive Design & Accessibility

## 8.1 Responsive Strategy

**Mobile-First with Progressive Enhancement**

## Breakpoints (Mobile Reality)

**Mobile (Primary): 320-768px**
- 94% of use is portrait
- Optimize for 360-414px (most common)
- Single column layout
- Bottom navigation
- Progressive disclosure default
- Touch-optimized

**Tablet: 768-1024px**
- Transitional layout
- 2-column where beneficial
- Maintain mobile navigation
- Larger touch targets

**Desktop: 1024px+**
- Full dashboard view
- Multi-column layout
- Side navigation
- Hover states
- Keyboard shortcuts

## Mobile-First Decisions

**Performance Budget**
- <1MB initial load
- <3 second time to interactive
- Offline-first with service worker
- Image lazy loading
- Code splitting

**Responsive Components**
- Cards stack on mobile, grid on desktop
- Tables become cards on mobile
- Modals become full-screen on mobile
- Navigation: bottom (mobile) → side (desktop)

## Accessibility Requirements

**WCAG 2.1 Level AA Compliance**

**Visual**
- 4.5:1 color contrast minimum
- Never rely on color alone
- Focus indicators visible
- Zoom to 200% without horizontal scroll

**Motor**
- 48x48px touch targets (Chilean standard)
- No time limits on actions
- Gesture alternatives
- One-handed operation on mobile

**Cognitive**
- Simple Spanish language
- Clear error messages
- Consistent navigation
- Progressive disclosure

**Screen Readers**
- Semantic HTML
- ARIA labels where needed
- Logical tab order
- Announced live regions

## Chilean-Specific Adaptations

**Language**
- Spanish as primary
- Chilean Spanish terminology
- No automated translations
- Local business terms

**Formats**
- Numbers: 1.234.567,89
- Currency: $1.234.567 CLP
- Dates: DD/MM/YYYY
- Phone: +56 9 XXXX XXXX

**Connectivity**
- Assume 3G/4G speeds
- Respect data limits
- Aggressive caching
- Offline functionality

## PWA Requirements

**Progressive Web App for Mobile**
- Installable to home screen
- Offline functionality
- Push notifications (optional)
- App-like experience
- No app store needed

**Service Worker Strategy**
- Cache-first for assets
- Network-first for API
- 30-day data cache
- Background sync
- Update prompts

## Testing Requirements

**Devices to Test**
- Xiaomi/Samsung mid-range (common in Chile)
- iPhone 8+ (minimum iOS)
- 3G throttled connection
- Offline mode
- Screen readers

**Browsers**
- Chrome Mobile (primary)
- Safari iOS
- Samsung Internet
- Chrome Desktop
- Firefox

## Performance Metrics

**Core Web Vitals**
- LCP: <2.5s (Largest Contentful Paint)
- FID: <100ms (First Input Delay)
- CLS: <0.1 (Cumulative Layout Shift)

**Business Metrics**
- Time to percentile: <4 seconds
- CSV upload: <30 seconds for 10K rows
- Dashboard refresh: <1 second
- Offline to online sync: <5 seconds

---
