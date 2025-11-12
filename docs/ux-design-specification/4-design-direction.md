# 4. Design Direction

## 4.1 Chosen Design Approach

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
