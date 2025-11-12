# 7. UX Pattern Decisions

## 7.1 Consistency Rules

**Based on Analytics Insights + Chilean SMB Reality**

## Navigation Patterns

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

## Data Display Patterns

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

## Interaction Patterns

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

## Feedback Patterns

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

## Mobile-Specific Patterns

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

## Form Patterns

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

## Visual Hierarchy Rules

1. **Percentile always largest** - It's the core value
2. **Revenue second** - Key business metric
3. **Trends third** - Direction matters
4. **Details on demand** - Progressive disclosure
5. **Actions at thumb reach** - Bottom on mobile

## Consistency Checklist

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
