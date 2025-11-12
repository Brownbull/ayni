# ayni UX Design Specification

_Created on 2025-11-11 by Gabe_
_Generated using BMad Method - Create UX Design Workflow v1.0_

---

## Executive Summary

### Project Vision

**Ayni** transforms how multi-location retail SMBs in Chile and Latin America understand their business performance. By replacing teams of data engineers, scientists, and analysts with automated analytics infrastructure, Ayni delivers enterprise-grade insights at SMB-friendly prices.

The platform solves a critical blind spot: retail business owners with 3-10 locations have transaction data scattered across multiple POS systems but lack the analytical infrastructure to turn this data into competitive intelligence. We're essentially building "Warcraft Logs for Business" - making performance analytics engaging through gamification while delivering serious business value.

### Technical Approach

Based on pragmatic development considerations:
- **Initial UI:** Chakra UI (FastAPI cookiecutter default) - migration to Tailwind post-MVP
- **Deployment:** Early and continuous deployment to Railway (backend) + Render (frontend)
- **Testing:** Playwright/Chrome DevTools verification of actual UI functionality
- **Architecture:** Keep FastAPI backend, eventually rebuild frontend fresh with React + Tailwind

### Target Users

Chilean retail SMBs with 3-10 locations, 10-50 employees - operations managers and business owners who currently spend 10+ hours weekly on manual Excel reporting, making $50-100K expansion decisions without data-driven insights.

---

## Core Experience Definition

### The ONE Thing Users Do Most
**View company dashboard and monthly stats on principal location** - This is the daily/weekly ritual where users check their business health. The dashboard must load instantly and show meaningful insights at a glance.

### What Must Be Effortless
1. **Navigate statistics** - Moving between time periods, locations, and metrics should feel fluid
2. **Upload data** - The CSV upload process must be foolproof with smart column mapping

### Most Critical User Action
**Data upload with intelligent column mapping** - This is the make-or-break moment. Features needed:
- View first row preview to verify data
- Configure formats per column (date, int, float for amounts)
- Set default formats that persist
- Visual validation before processing

### Platform Priority
- **Desktop-first design** optimized for Chrome browser
- Mobile responsiveness as secondary consideration
- Focus on desktop power-user workflows initially

### Desired Emotional Response

**Competitive and motivated** - "I'm in the 68th percentile - let's get to top 25%!"

Users should feel they are:
- **Gaining control** of their business trajectory
- **Building awareness** that grows with each data upload
- **Understanding their position** relative to the market
- **Seeing the full picture** including external factors (buffs/debuffs) that impact performance
- **Freed from manual work** - no more sorting, aggregating, or making sense of raw transactions

The emotional journey: From overwhelmed → informed → competitive → motivated to improve. Each data upload makes them smarter, each dashboard view reveals opportunities, and the percentile ranking transforms business management into an engaging challenge.

### UX Inspiration Analysis

**Current Tools (What Users Know):**
- **Defontana, Siigo, Gesnex** - Chilean accounting/ERP systems
- **Diario Financiero** - Chilean financial news
- *Problem:* None show data in a clever, engaging way

**Inspiration Sources (What We Aspire To):**

**1. Warcraft Logs** - Gaming Analytics Excellence
- **Dense information display** that power users love
- **Percentile rankings** prominently displayed
- **Timeline views** showing events and patterns
- **Color-coded performance** (green/blue/purple/grey)
- **Shareable components** for comparing/competing
- **Deep drill-down** capability without losing context

**2. WipeFest** - Simplified Complex Data
- **Player Score Grid** - Heatmaps showing performance at a glance
- **Mechanics prioritization** - Highlighting what matters most
- **Concise summaries** from complex data
- **Visual scoring system** that's instantly understandable
- **Focus on improvement** - Shows exactly where to get better

**3. Yahoo Finance** - Financial Data Mastery
- **Advanced charts** with 25+ types and 100+ indicators
- **Compare mode** - Side-by-side analysis
- **Clean, modern design** with horizontal navigation
- **Full-screen charting** experience
- **Smart annotations** on corporate events
- **Auto-detection** of technical patterns
- **40% fewer ads** for premium experience

**Key UX Patterns to Adopt:**
1. **Dense but organized** - Show lots of data without overwhelming
2. **Percentile/ranking focus** - Make competition visible and engaging
3. **Timeline/temporal navigation** - Easy movement through time periods
4. **Heatmaps and color coding** - Visual performance indicators
5. **Compare mode** - Location vs location, period vs period
6. **Full-screen focus modes** - Immersive chart experiences
7. **Progressive disclosure** - Simple overview → detailed analysis

---

## 1. Design System Foundation

### 1.1 Design System Choice

**Decision: Tailwind CSS + shadcn/ui from Day 1**

Based on your clear directive to avoid migration nightmares:
1. **Delete entire Chakra frontend** after cookiecutter generation
2. **Build fresh with Tailwind CSS** - no migration, clean slate
3. **Add shadcn/ui components** for rapid development

**Implementation Strategy:**
```bash
# After cookiecutter generation:
git tag v0.1-cookiecutter  # Preserve for reference
rm -rf frontend/            # Delete Chakra completely
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install -D tailwindcss postcss autoprefixer
npm install axios react-router-dom @tanstack/react-query zustand
```

**Why Tailwind + shadcn/ui:**
- **Full control** from the start - no framework conflicts
- **shadcn/ui** provides copy-paste components (not a dependency)
- **Perfect for dense layouts** inspired by Warcraft Logs
- **Excellent for data tables** and analytics displays
- **Dark mode first-class** support for gaming aesthetic
- **Highly customizable** for unique Ayni brand

**What We Keep from Cookiecutter (for reference):**
- Auth flow patterns from `hooks/useAuth.ts`
- JWT interceptor setup from `client/index.ts`
- Protected route logic from `routes/_authenticated.tsx`
- Form validation patterns from `login.tsx`

**Component Approach:**
- Use shadcn/ui for standard components (buttons, forms, modals)
- **Leverage Tailwind UI premium components** from `.ignore/tailwind_templates/`
- Build custom components for:
  - Percentile ranking displays
  - Performance index cards
  - Location comparison grids
  - CSV mapping interface
  - Dense data tables with heatmaps

**Available Premium Resources:**
- Tailwind UI components stored in `/home/khujta/projects/bmad/ayni/.ignore/tailwind_templates/`
- Can reference and adapt these for rapid development
- Already optimized and production-ready

This eliminates all Chakra-Tailwind conflicts and gives us complete design freedom from the start.

---

## 2. Core User Experience

### 2.1 Defining Experience

**"It's the app that shows me how I rank against other businesses like mine"**

The core experience is **The Percentile Reveal** - that moment when users discover their competitive position. This transforms business metrics from abstract numbers into a competitive challenge.

**The Magic Moment:**
- User uploads their data
- System processes and aggregates
- Dashboard loads with a prominent **Performance Index**
- Animated reveal: "You rank in the 68th percentile"
- Color-coded tier appears (Green/Blue/Purple/Grey)
- Immediate understanding: "I'm doing better than 68% of similar businesses"

**Why This Defines Ayni:**
- **Unique differentiator** - No Chilean SMB tool shows competitive rankings
- **Emotional hook** - Triggers competitive motivation
- **Network effect** - Every new user makes rankings more valuable
- **Viral potential** - Users want to share/brag about high percentiles
- **Retention driver** - Users return to improve their "parse"

**UX Implications:**
- Percentile ranking must be **prominently displayed** on main dashboard
- Use **gaming-inspired visuals** (progress bars, tier colors, animations)
- Make rankings **shareable** (export images, social proof)
- Show **trend arrows** (improving or declining vs last period)
- Provide **clear path to improvement** (what moves the needle)

### 2.2 Novel UX Patterns

{{novel_ux_patterns}}

---

## 3. Visual Foundation

### 3.1 Color System

**Chosen Direction: Trust + Competition Hybrid**

Combining professional credibility with competitive gaming aesthetics:

**Primary Palette - Professional Trust:**
- **Primary:** `#0ea5e9` (Sky Blue) - Trust, reliability, data
- **Primary Dark:** `#0284c7` - Depth and focus
- **Primary Light:** `#38bdf8` - Highlights and accents
- **Primary Subtle:** `#e0f2fe` - Backgrounds in light mode

**Performance Tiers - Competitive Motivation:**
- **Elite (90-100%):** `#10b981` (Emerald) - Top performers
- **Strong (75-89%):** `#3b82f6` (Blue) - Above average
- **Average (50-74%):** `#8b5cf6` (Purple) - Mid-tier
- **Needs Improvement (0-49%):** `#6b7280` (Gray) - Below average

**Semantic Colors:**
- **Success:** `#10b981` - Positive trends, growth
- **Warning:** `#f59e0b` - Attention needed
- **Error:** `#ef4444` - Critical issues
- **Info:** `#0ea5e9` - Neutral information

**Neutral Scale (Dark Mode First):**
- **Background:** `#0a0a0a` - Primary canvas
- **Surface:** `#111111` - Cards and panels
- **Border:** `#27272a` - Subtle dividers
- **Text Primary:** `#ffffff` - Main content
- **Text Secondary:** `#a1a1aa` - Supporting text
- **Text Muted:** `#71717a` - De-emphasized

**Special Elements:**
- **Percentile Gradient:** Linear gradient from `#0ea5e9` to `#3b82f6`
- **Chart Colors:** Array of distinct colors for multi-series data
- **Heatmap Scale:** Green → Yellow → Red for performance intensity

**Typography System:**
- **Font Family:** `Inter, system-ui, -apple-system, sans-serif`
- **Headings:** Bold weights (600-800) for hierarchy
- **Body:** Regular (400) for readability
- **Monospace:** `'JetBrains Mono', monospace` for data/numbers

**Visual Language:**
- Dark mode as default (gaming aesthetic)
- High contrast for data visibility
- Smooth gradients for premium feel
- Subtle animations for engagement
- Dense but organized layouts

**Interactive Visualizations:**

- Color Theme Explorer: [ux-color-themes.html](./ux-color-themes.html)

---

## 4. Design Direction

### 4.1 Chosen Design Approach

**Decision: Progressive Disclosure + Mobile-First Reality**

Based on analytics insights and Chilean SMB reality:

**Primary Direction: "Smart Progressive" (Hybrid of Clean + Command Center)**
- **First Screen:** 5-9 key metrics only (Miller's Law)
- **Percentile as Hero:** Large, animated, unmissable
- **Progressive Depth:** Tap/click to reveal more without navigation
- **Mobile Reality:** Designed for scratched phones, spotty connection

**Key Adjustments from Analytics Insights:**

**Mobile-First Compromises:**
- **Portrait mode primary** - 94% of mobile use is vertical
- **Bottom navigation** - One-handed operation
- **48x48px touch targets** - Better for Chile
- **Offline-first** - Cache 30 days, sync when connected
- **<1MB initial load** - Respect prepaid data plans

**Progressive Disclosure Implementation:**
- **Level 1:** Today's revenue, percentile, top location (3 metrics)
- **Level 2:** Week trends, all locations, alerts (tap to expand)
- **Level 3:** Historical data, comparisons, detailed analytics

**Chilean-Specific UX:**
- **Number formatting:** $1.234.567,89 CLP
- **WhatsApp share buttons** on every report
- **Spanish-first labels** (not translations)
- **"Last updated" timestamp** always visible

**Time to First Value:**
- **0-60 seconds:** See today's revenue and percentile
- **60-120 seconds:** Upload first CSV
- **120-240 seconds:** View competitive ranking
- **Goal:** "Aha moment" in <4 minutes

**Visual Hierarchy:**
1. **Percentile ranking** - Biggest, brightest
2. **Revenue today** - Large, prominent
3. **Trend arrow** - Green/red immediate feedback
4. **Location performance** - Progressive reveal
5. **Historical data** - Hidden until requested

**Interactive Mockups:**

- Design Direction Showcase: [ux-design-directions.html](./ux-design-directions.html)

---

## 5. User Journey Flows

### 5.1 Critical User Paths

### Journey 1: First-Time User Onboarding (Time to First Insight)

**Goal:** Reach "aha moment" in <4 minutes

**Flow:**
1. **Land on login** (0:00)
   - See value prop: "Descubre tu ranking competitivo"
   - One button: "Comenzar Gratis"

2. **Quick registration** (0:30)
   - Email + password only
   - Skip everything else

3. **Instant demo data** (1:00)
   - Auto-populate with restaurant demo
   - Show percentile animation immediately
   - "Estos son datos de ejemplo - sube los tuyos"

4. **CSV upload prompt** (1:30)
   - Drag & drop zone prominent
   - "Arrastra tu archivo CSV aquí"
   - Smart column detection

5. **First real insight** (3:00)
   - Processing animation with tips
   - Percentile reveal animation
   - "¡Estás en el percentil 68!"

6. **Share moment** (3:30)
   - WhatsApp share button
   - "Comparte tu ranking"
   - Social proof generation

### Journey 2: Daily Check (Mobile Reality)

**Goal:** Get business pulse in 30 seconds on phone

**Flow:**
1. **Open app** (cached PWA)
   - Face/Touch ID login
   - Instant load from cache

2. **See hero metrics**
   - Percentile badge (big, colorful)
   - Today's revenue: $1.234.567
   - Trend arrow: ↑ 12%

3. **Swipe for locations** (if multiple)
   - Card stack of locations
   - Red/green indicators
   - Top performer highlighted

4. **Pull to refresh**
   - Sync if connected
   - Show "Actualizado hace 2 min"
   - Work offline otherwise

### Journey 3: CSV Upload (Critical Path)

**Goal:** Foolproof data ingestion

**Flow:**
1. **Tap upload button**
   - Bottom nav, always visible
   - Big target (48x48px)

2. **Select file**
   - Native file picker
   - Recent files shown

3. **Preview first row**
   - Show actual data
   - Auto-detect columns
   - Chilean formats recognized

4. **Map columns**
   - Smart suggestions
   - Remember mappings
   - "Usar configuración anterior"

5. **Process**
   - Show progress bar
   - "Procesando 3,421 transacciones..."
   - Estimated time

6. **Success**
   - Green checkmark animation
   - Updated metrics immediately
   - "¡Datos actualizados!"

### Journey 4: Competitive Benchmarking (Core Value)

**Goal:** Understand market position

**Flow:**
1. **See percentile on dashboard**
   - Always visible
   - Color-coded tier

2. **Tap for details**
   - Expand to show:
   - "Mejor que 68% de negocios similares"
   - "Promedio sector: $987.654"
   - "Tu promedio: $1.234.567 (+25%)"

3. **View peer comparison**
   - Anonymous peers
   - Similar size/location
   - Performance distribution curve

4. **Get improvement tips**
   - "Sube al top 25% mejorando márgenes"
   - Specific, actionable advice
   - Based on peer success patterns

### Journey 5: Location Comparison (Multi-location)

**Goal:** Identify winners and problems fast

**Flow:**
1. **Dashboard shows top/bottom**
   - Best: "Las Condes $45K ↑"
   - Worst: "Providencia $28K ↓"

2. **Tap to expand all**
   - Progressive reveal
   - Swipeable cards on mobile
   - Color-coded performance

3. **Deep dive on location**
   - 30-day trend
   - Hour-by-hour patterns
   - Product performance

4. **Compare side-by-side**
   - Select 2 locations
   - Mirror charts
   - Highlight differences

### Journey 6: WhatsApp Report Sharing

**Goal:** Share success, get help

**Flow:**
1. **Tap share on any screen**
   - WhatsApp icon prominent
   - Pre-formatted message

2. **Auto-generate image**
   - Clean report card
   - Key metrics visible
   - Percentile highlighted
   - Ayni branding

3. **Add context**
   - "Mira nuestro progreso este mes"
   - Editable message

4. **Send to contacts**
   - Business partners
   - Investors
   - Team members

---

## 6. Component Library

### 6.1 Component Strategy

**Mobile-First Components with Progressive Enhancement**

### Core Components (MVP Priority)

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

### Data Visualization Components

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

### Form Components

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

### Feedback Components

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

### Component Design Principles

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

## 7. UX Pattern Decisions

### 7.1 Consistency Rules

**Based on Analytics Insights + Chilean SMB Reality**

### Navigation Patterns

**Mobile Bottom Nav (Primary)**
- Fixed bottom position
- 5 items maximum
- Icons + labels
- Badge notifications
- Active state obvious

**Desktop Side Nav (Secondary)**
- Collapsible for more space
- Icons when collapsed
- Full labels when expanded
- Same order as mobile

### Data Display Patterns

**Progressive Disclosure**
- Show 5-9 metrics initially (Miller's Law)
- Tap/click to expand
- Maintain context when expanding
- Remember user's preference

**Number Formatting**
- Chilean standard: $1.234.567,89
- Always show CLP
- Red for negative (parentheses option)
- Green for positive growth
- K/M abbreviations for space-limited mobile

**Time Patterns**
- Default: Today
- Quick toggles: Week, Month, Year
- Always show "last updated"
- Relative time on mobile ("hace 2h")
- Absolute time on desktop

### Interaction Patterns

**Touch Targets**
- 48x48px minimum (Chilean standard)
- 12px spacing between targets
- Visual feedback on touch
- Prevent accidental taps

**Loading States**
- Skeleton screens (not spinners)
- Progress bars for uploads
- Estimated time remaining
- Cancel option always visible

**Error Handling**
- Clear Spanish error messages
- Suggest solution
- Retry button prominent
- Maintain user's data

### Feedback Patterns

**Success States**
- Green checkmark animation
- Brief message
- Auto-dismiss after 3 seconds
- Non-blocking

**Alerts/Warnings**
- Bottom sheet on mobile
- Toast on desktop
- Dismissable
- Action button if needed

### Mobile-Specific Patterns

**Offline Mode**
- Cache 30 days of data
- Sync indicator
- Work without connection
- Queue actions for later

**WhatsApp Integration**
- Share button on every screen
- Pre-formatted messages
- Generated image cards
- Deep links back to app

**Pull to Refresh**
- Standard iOS/Android pattern
- Show last update time
- Haptic feedback
- Loading indicator

### Form Patterns

**CSV Upload**
- Drag & drop on desktop
- File picker on mobile
- Preview before processing
- Remember column mappings
- Progress with percentage

**Quick Actions**
- One-tap filters
- Toggle switches for options
- Immediate apply (no submit)
- Clear reset option

### Visual Hierarchy Rules

1. **Percentile always largest** - It's the core value
2. **Revenue second** - Key business metric
3. **Trends third** - Direction matters
4. **Details on demand** - Progressive disclosure
5. **Actions at thumb reach** - Bottom on mobile

### Consistency Checklist

✓ Spanish-first, not translated
✓ Chilean number formatting throughout
✓ 48x48px touch targets minimum
✓ WhatsApp share everywhere
✓ Offline-first architecture
✓ Progressive disclosure default
✓ Bottom nav on mobile
✓ "Last updated" always visible
✓ Green growth, red decline
✓ Skeleton screens for loading

---

## 8. Responsive Design & Accessibility

### 8.1 Responsive Strategy

**Mobile-First with Progressive Enhancement**

### Breakpoints (Mobile Reality)

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

### Mobile-First Decisions

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

### Accessibility Requirements

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

### Chilean-Specific Adaptations

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

### PWA Requirements

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

### Testing Requirements

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

### Performance Metrics

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

## 9. Implementation Guidance

### 9.1 Completion Summary

**UX Design Specification Complete - Optimized for Chilean SMB Reality**

### What We Created

**Design Foundation:**
- **Mobile-first reality** - Designed for scratched phones with spotty connection
- **Progressive disclosure** - 5-9 metrics max initially (Miller's Law)
- **<4 minute onboarding** - Time to first insight optimized
- **Spanish-first** - Not translations, native Chilean Spanish
- **WhatsApp integration** - Share everything through dominant platform
- **Offline-first** - 30-day cache, works without connection

**Key Design Decisions:**
- **Trust + Competition colors** - Professional blue with gaming tiers
- **Bottom navigation** - One-handed mobile operation
- **48x48px touch targets** - Chilean accessibility standard
- **$1.234.567,89 formatting** - Local number conventions
- **PWA over native app** - No app store friction

**Critical Success Factors:**
1. **Percentile as hero metric** - Always visible, always motivating
2. **CSV upload intelligence** - Remember mappings, Chilean formats
3. **Progressive depth** - Start simple, reveal complexity
4. **WhatsApp shareability** - Social proof generation
5. **Offline capability** - Work anywhere, sync later

### Implementation Priorities

**Week 1-2: Core Dashboard**
- Percentile hero card
- Revenue display
- Bottom navigation
- Demo data instant load

**Week 3-4: CSV Upload**
- Smart column mapping
- Chilean format detection
- Progress indication
- Mapping templates

**Week 5-6: Multi-location**
- Location cards
- Swipeable comparison
- Performance indicators
- Location drill-down

**Week 7-8: Offline + PWA**
- Service worker setup
- 30-day cache
- Background sync
- Install prompts

**Week 9-10: WhatsApp Integration**
- Share card generation
- Pre-formatted messages
- Image exports
- Deep linking

### Success Metrics

**Activation:**
- Time to first insight: <4 minutes
- CSV upload success: >80% first try
- Demo to real data: <7 days

**Engagement:**
- Daily active users: >75%
- Mobile usage: >60%
- WhatsApp shares: >20% of users

**Performance:**
- Initial load: <1MB
- Time to interactive: <3 seconds
- Offline functionality: 100%
- Percentile display: <4 seconds

### Technical Requirements

**Frontend Stack:**
- React 19 + TypeScript
- Tailwind CSS (delete Chakra)
- PWA with service workers
- shadcn/ui components
- Recharts for visualizations

**Performance Budget:**
- Bundle size: <500KB gzipped
- Images: WebP with fallbacks
- Fonts: System fonts first
- Code splitting by route

**Testing Strategy:**
- Playwright for UI testing
- Mobile-first testing
- Offline scenario testing
- Chilean format validation
- 3G throttled testing

### Bottom Line

This UX design prioritizes the reality of Chilean retail SMBs: owners checking metrics on phones during busy service, with intermittent connectivity, needing instant insights not complex analysis. Every decision optimizes for mobile, speed, and simplicity while maintaining the competitive gamification that drives engagement.

**The design mantra:** "Make it work on a scratched phone with one hand while handling customers."

---

## Appendix

### Related Documents

- Product Requirements: `/home/khujta/projects/bmad/ayni/docs/*prd*.md`
- Product Brief: `/home/khujta/projects/bmad/ayni/docs/*brief*.md`
- Brainstorming: `/home/khujta/projects/bmad/ayni/docs/*brainstorm*.md`

### Core Interactive Deliverables

This UX Design Specification was created through visual collaboration:

- **Color Theme Visualizer**: /home/khujta/projects/bmad/ayni/docs/ux-color-themes.html
  - Interactive HTML showing all color theme options explored
  - Live UI component examples in each theme
  - Side-by-side comparison and semantic color usage

- **Design Direction Mockups**: /home/khujta/projects/bmad/ayni/docs/ux-design-directions.html
  - Interactive HTML with 6-8 complete design approaches
  - Full-screen mockups of key screens
  - Design philosophy and rationale for each direction

### Optional Enhancement Deliverables

_This section will be populated if additional UX artifacts are generated through follow-up workflows._

<!-- Additional deliverables added here by other workflows -->

### Next Steps & Follow-Up Workflows

This UX Design Specification can serve as input to:

- **Wireframe Generation Workflow** - Create detailed wireframes from user flows
- **Figma Design Workflow** - Generate Figma files via MCP integration
- **Interactive Prototype Workflow** - Build clickable HTML prototypes
- **Component Showcase Workflow** - Create interactive component library
- **AI Frontend Prompt Workflow** - Generate prompts for v0, Lovable, Bolt, etc.
- **Solution Architecture Workflow** - Define technical architecture with UX context

### Version History

| Date     | Version | Changes                         | Author        |
| -------- | ------- | ------------------------------- | ------------- |
| 2025-11-11 | 1.0     | Initial UX Design Specification | Gabe |

---

_This UX Design Specification was created through collaborative design facilitation, not template generation. All decisions were made with user input and are documented with rationale._
