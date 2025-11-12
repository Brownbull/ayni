# 1. Design System Foundation

## 1.1 Design System Choice

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
