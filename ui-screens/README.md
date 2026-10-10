# Pathway LMS Platform — React UI Screens

High-fidelity React (TypeScript + Tailwind CSS) UI screens generated from Google Stitch project:
**`https://stitch.withgoogle.com/projects/15271909917709048010`**

---

## 🎨 Screens Included

1. **Learner Dashboard (`DashboardScreen.tsx`)**
   - Header with cohort metadata (`Cohort #14 • Week 6`) and "Resume Learning" CTA.
   - Spotlight Course Module (`Synthesizing Customer Interview Insights & Affinity Mapping`, 72% progress, checklist 3.1 - 3.4).
   - Side panel with Weekly Study Goal (Radial SVG gauge 75%, 4.5/6.0 hrs).
   - 5-Day Study Streak badge (`🔥 +150 XP`) and 7-day interactive bar chart.
   - 4-milestone roadmap preview (Milestone 1 Complete, Milestone 2 In-Progress, Milestones 3-4 Locked).
   - Upcoming deadlines with interactive RSVP confirmation toggle and Practice & Peer Labs.

2. **Course Catalog (`CourseCatalogScreen.tsx`)**
   - Search Hero Bar with `⌘K` keyboard shortcut and quick topic tags (SQL, Product Discovery, System Design, UX Heuristics, Financial Modeling).
   - Role filter navigation tabs (Product Management, Data & Analytics, UX/UI, Software Engineering, Leadership).
   - Faceted Filter Sidebar: Competency, Experience Level, Format, Duration, Provider with counts.
   - Responsive course card grid with real instructor metadata, ratings, progress bars, bookmark toggles, and status tags.

3. **My Learning Path (`LearningPathScreen.tsx`)**
   - Hero header with track parameters (Target Role, Seniority, 24 Wks Duration, On Track velocity).
   - Curriculum progress card with Radial SVG donut (58%), stacked progress bars, and course count badges.
   - Verified Competency radar matrix (Agile Execution 90%, User Research 85%, Product Strategy 70%, Data Analysis 60%, Stakeholder Alignment 40%).
   - Phased curriculum roadmap (Phase 1 Completed with graded capstone project & reviewer quote, Phase 2 Active, Phase 3 Locked).

---

## 🚀 How to Run & Preview

### Instant Browser Preview (Zero Install)
Simply open [`ui-screens/preview.html`](preview.html) directly in any modern web browser (Chrome, Edge, Firefox, Safari). It runs React 18, Tailwind CSS, and Material Symbols via CDN with full client-side tab switching and interactive controls!

### Using in React / Next.js / Vite Projects
All screen components are modular and typed with TypeScript:
```tsx
import { DashboardScreen } from './ui-screens/src/screens/DashboardScreen';
import { CourseCatalogScreen } from './ui-screens/src/screens/CourseCatalogScreen';
import { LearningPathScreen } from './ui-screens/src/screens/LearningPathScreen';
import { Sidebar } from './ui-screens/src/components/Sidebar';
import { Header } from './ui-screens/src/components/Header';
```

---

## 📁 Directory Structure
```
ui-screens/
├── package.json
├── tailwind.config.js
├── preview.html             <-- Standalone interactive browser preview
├── README.md
├── reference/
│   ├── dashboard_raw.html   <-- Original Stitch Learner Dashboard export
│   ├── catalog_raw.html     <-- Original Stitch Course Catalog export
│   └── learning_path_raw.html<-- Original Stitch My Learning Path export
└── src/
    ├── types.ts             <-- Full TypeScript interfaces
    ├── mockData.ts          <-- Structured data model matching Stitch
    ├── index.tsx            <-- React root entrypoint
    ├── App.tsx              <-- Navigation shell coordinating all screens
    ├── components/
    │   ├── Sidebar.tsx      <-- Navigation sidebar & Q1 target progress
    │   └── Header.tsx       <-- Top header, breadcrumbs, search, profile
    └── screens/
        ├── DashboardScreen.tsx
        ├── CourseCatalogScreen.tsx
        └── LearningPathScreen.tsx
```
