---
name: Frontend Professional Revamp
overview: Complete frontend redesign to transform the current "vibe coded" UI into a premium, Apple-like professional experience with proper icon systems, responsive design, and modern component architecture inspired by kuku.mom, shaped.ai, and cybercut.ai. Includes full rebranding from "SocialAI" to "ElevoAI".
todos:
  - id: rebrand-elevoai
    content: "Rebrand app from SocialAI to ElevoAI: update all references in layouts, pages, nuxt.config.ts, and create new logo component"
    status: pending
  - id: install-deps
    content: Install lucide-vue-next and configure in nuxt.config.ts
    status: pending
  - id: update-tailwind
    content: Refine Tailwind color palette for deeper black theme and add animation utilities
    status: pending
  - id: create-ui-components
    content: "Create base UI components: Button, Card, Input, Badge, Modal, Skeleton, Icon wrapper"
    status: pending
  - id: create-layout-components
    content: Create Header with mobile hamburger menu, Footer, and MobileNav drawer
    status: pending
  - id: update-default-layout
    content: Refactor default.vue to use new Header/Footer components with responsive nav
    status: pending
  - id: create-landing-components
    content: "Create landing page sections: Hero, Features, HowItWorks, Stats, FAQ, CTA"
    status: pending
  - id: redesign-landing-page
    content: Redesign pages/index.vue with professional sections inspired by cybercut.ai
    status: pending
  - id: create-shared-components
    content: Create VideoCard, PlatformIcon, StatusBadge, EmptyState components
    status: pending
  - id: update-dashboard
    content: Replace emojis with icons and use new components in dashboard.vue
    status: pending
  - id: update-videos-page
    content: Refactor videos page with VideoCard component and proper upload modal
    status: pending
  - id: update-publish-page
    content: Refactor publish page with PlatformIcon and improved UI
    status: pending
  - id: update-remaining-pages
    content: Update strategies, scripts, analytics, and auth pages with new design system
    status: pending
  - id: add-loading-states
    content: Add skeleton loading states and smooth transitions throughout
    status: pending
  - id: responsive-polish
    content: Final responsive testing and polish for all breakpoints
    status: pending
isProject: false
---

# Frontend Professional Revamp Plan

## Rebranding: SocialAI to ElevoAI

The application will be rebranded from "SocialAI" to **ElevoAI**. All references must be updated:

### Files Requiring Brand Updates

| File | Changes |
| ---- | ------- |
| `nuxt.config.ts` | Update `app.head.title` from "Social Media AI" to "ElevoAI" |
| `layouts/default.vue` | Update logo text from "SocialAI" to "ElevoAI", update logo icon |
| `layouts/auth.vue` | Update logo text and icon |
| `pages/index.vue` | Update hero copy, CTAs, and any brand mentions |
| Footer component | Update copyright text to "ElevoAI" |

### Logo Design

Create a new `Logo.vue` component with:
- Icon: Stylized "E" with gradient (primary to accent)
- Text: "ElevoAI" in Space Grotesk font
- Variants: full (icon + text), icon-only, text-only
- Sizes: sm, md, lg

```vue
<!-- components/ui/Logo.vue -->
<template>
  <NuxtLink to="/" class="flex items-center gap-2">
    <div class="logo-icon">E</div>
    <span v-if="showText" class="logo-text">ElevoAI</span>
  </NuxtLink>
</template>
```

### Brand Voice Updates

- Hero tagline: Update to reflect "ElevoAI" identity
- Meta descriptions: Update SEO metadata
- Footer copyright: "© 2026 ElevoAI. All rights reserved."

---

## Current State Analysis

The existing frontend has several issues that need addressing:

- **Emoji-based icons** (📹, 🎯, 📊) throughout all pages
- **No reusable components** - all UI is inline in pages
- **Basic responsive design** - hidden nav on mobile, no hamburger menu
- **Missing professional landing page sections** - no social proof, testimonials, process steps
- **No proper loading states** - basic indicators only
- **Limited animations** - simple fade-ins only

## Design System Foundation

### 1. Color Palette Update

Refine the dark theme to match the deep black aesthetic from kuku.mom:

```typescript
// tailwind.config.ts - Updated colors
surface: {
  950: '#030303',  // True black background
  900: '#0a0a0a',  // Card backgrounds
  800: '#141414',  // Elevated surfaces
  700: '#1f1f1f',  // Borders, dividers
  // ... lighter shades
}
```

### 2. Typography Enhancement

Keep the current fonts (DM Sans + Space Grotesk - similar to reference sites) but add proper scale:

```css
/* Type scale: 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72 */
```

### 3. Icon System

Install **Lucide Icons** (MIT licensed, similar to what kuku/shaped use):

```bash
npm install lucide-vue-next
```

Replace all emoji usage with proper SVG icons:


| Emoji | Replacement      |
| ----- | ---------------- |
| 📹    | `<Video />`      |
| 🎯    | `<Target />`     |
| 📊    | `<BarChart3 />`  |
| 📝    | `<FileText />`   |
| 🚀    | `<Rocket />`     |
| 📈    | `<TrendingUp />` |


## Component Architecture

Create a proper component library in `[frontend/components/](frontend/components/)`:

```
frontend/components/
├── ui/                    # Base UI primitives
│   ├── Button.vue
│   ├── Input.vue
│   ├── Card.vue
│   ├── Badge.vue
│   ├── Modal.vue
│   ├── Dropdown.vue
│   ├── Skeleton.vue
│   └── Icon.vue
├── layout/                # Layout components
│   ├── Header.vue
│   ├── Footer.vue
│   ├── MobileNav.vue
│   └── Sidebar.vue
├── landing/               # Landing page sections
│   ├── Hero.vue
│   ├── Features.vue
│   ├── HowItWorks.vue
│   ├── Stats.vue
│   ├── Testimonials.vue
│   ├── Pricing.vue
│   ├── FAQ.vue
│   └── CTA.vue
└── shared/                # Shared components
    ├── VideoCard.vue
    ├── PlatformIcon.vue
    ├── StatusBadge.vue
    └── EmptyState.vue
```

## Page-by-Page Redesign

### Landing Page (`[pages/index.vue](frontend/pages/index.vue)`)

**Inspired by cybercut.ai structure:**

1. **Hero Section** - Bold headline, gradient text, animated background, CTA buttons
2. **Stats Bar** - Key metrics (similar to shaped.ai)
3. **Features Grid** - Icon-based cards with proper SVG icons
4. **How It Works** - 3-step process visualization (like cybercut)
5. **Use Cases** - Tabbed content showcasing different scenarios
6. **Social Proof** - Logo cloud + testimonials
7. **FAQ Section** - Accordion component
8. **Final CTA** - Gradient card with compelling copy

### Dashboard (`[pages/dashboard.vue](frontend/pages/dashboard.vue)`)

- Replace emoji stats with proper icons
- Add skeleton loading states
- Add real data visualization placeholders
- Improve responsive grid layout

### Videos Page (`[pages/videos/index.vue](frontend/pages/videos/index.vue)`)

- Replace 📹 emoji with Video icon
- Create proper `VideoCard.vue` component
- Add thumbnail placeholders (gradient/skeleton)
- Improve upload modal design
- Add drag-and-drop visual feedback

### Publish Page (`[pages/publish/index.vue](frontend/pages/publish/index.vue)`)

- Create `PlatformIcon.vue` with proper brand icons
- Improve platform connection cards
- Better scheduling interface

## Responsive Design Strategy

### Breakpoints (Tailwind defaults)

- `sm`: 640px (large phones)
- `md`: 768px (tablets)
- `lg`: 1024px (laptops)
- `xl`: 1280px (desktops)
- `2xl`: 1536px (large screens)

### Mobile Navigation

Create hamburger menu with slide-out drawer:

```vue
<!-- MobileNav.vue -->
- Hamburger icon trigger
- Full-screen overlay
- Slide-in navigation panel
- Smooth transitions
```

### Touch Optimizations

- Larger touch targets (min 44px)
- Swipe gestures for modals
- Bottom sheet pattern for mobile modals

## Animation System

Create subtle, purposeful animations (Apple-like):

```css
/* Micro-interactions */
.btn-hover { transform: translateY(-1px); }
.card-hover { transform: scale(1.01); }

/* Page transitions */
.page-enter { opacity: 0; transform: translateY(8px); }

/* Loading states */
.skeleton-pulse { animation: pulse 1.5s ease-in-out infinite; }
```

## File Changes Summary


| File                      | Action                                              |
| ------------------------- | --------------------------------------------------- |
| `nuxt.config.ts`          | Rebrand to ElevoAI, configure Lucide icons          |
| `tailwind.config.ts`      | Update color palette, add animations                |
| `assets/css/main.css`     | Add new utility classes, animations                 |
| `package.json`            | Add lucide-vue-next dependency                      |
| `components/ui/Logo.vue`  | Create new ElevoAI logo component                   |
| `components/ui/*`         | Create base UI components                           |
| `components/layout/*`     | Create Header/Footer with ElevoAI branding          |
| `components/landing/*`    | Create landing page sections                        |
| `layouts/default.vue`     | Major refactor, use Logo component, add mobile nav  |
| `layouts/auth.vue`        | Update to use Logo component                        |
| `pages/index.vue`         | Complete redesign with ElevoAI branding             |
| `pages/dashboard.vue`     | Replace emojis, add components                      |
| `pages/videos/index.vue`  | Replace emojis, use components                      |
| `pages/publish/index.vue` | Replace emojis, use components                      |
| All other pages           | Update to use new components and ElevoAI branding   |


## Implementation Order

Phase 1: Foundation + Branding

1. Rebrand to ElevoAI (nuxt.config.ts title, meta)
2. Install dependencies (Lucide)
3. Update Tailwind config with refined colors
4. Create Logo.vue component with ElevoAI branding
5. Create base UI components (Button, Card, Input, Icon)

Phase 2: Layout
6. Create Header component with mobile nav and ElevoAI logo
7. Create Footer component with ElevoAI branding
8. Update default layout

Phase 3: Landing Page
9. Create all landing page section components
10. Redesign index.vue with ElevoAI branding and new sections

Phase 4: App Pages
11. Create shared components (VideoCard, PlatformIcon, etc.)
12. Update dashboard, videos, publish pages
13. Update remaining pages (strategies, scripts, analytics)

Phase 5: Polish
14. Add loading skeletons throughout
15. Refine animations and transitions
16. Cross-browser and responsive testing