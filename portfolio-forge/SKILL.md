---
name: portfolio-forge
description: |
  Generates static HTML portfolio and developer activity log from Obsidian knowledge base.
  Creates project cards, activity timelines, and statistics dashboards.
  
  Triggers: "generate portfolio", "build site", "create dev log", "/portfolio"
version: 1.0.0
author: Claude Code
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
---

# Portfolio Forge

Transforms your Obsidian knowledge base into a beautiful static HTML portfolio.

## What It Generates

### Project Portfolio Page
- Project cards with tech stack badges
- LOC statistics
- Recent activity
- Quick links to documentation

### Activity Timeline
- Chronological view of all sessions
- Commit frequency charts
- Project breakdown

### Statistics Dashboard
- Total lines written
- Languages used
- Projects active
- Contribution calendar

## Output Structure

```
~/Documents/Vaultage/06_Metadata/Portfolio/
├── index.html          # Main portfolio page
├── activity.html       # Activity timeline
├── stats.html          # Statistics dashboard
├── projects/
│   ├── atlas.html      # Individual project pages
│   └── ...
├── css/
│   └── style.css       # Styling
└── data/
    ├── projects.json   # Project data
    └── activity.json   # Activity feed
```

## Usage

```bash
# Generate full portfolio
/portfolio

# Generate specific section
/portfolio --only projects

# Custom output directory
/portfolio --output ~/Sites/dev-portfolio

# Include private projects
/portfolio --include-private
```

## Design

Clean, minimal design inspired by:
- GitHub profile pages
- Linear.app aesthetics
- Vercel dashboard

### Color Scheme
- Background: `#0a0a0a` (dark)
- Cards: `#141414`
- Accent: `#3b82f6` (blue)
- Text: `#e5e5e5`

### Features
- Responsive design
- Dark mode by default
- Smooth animations
- Fast loading (no JS frameworks)
