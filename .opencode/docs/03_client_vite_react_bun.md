# Kalembang Client (React + Vite + Bun)

## Tech Stack

- **React 18** with TypeScript
- **Vite** for bundling
- **Bun** as package manager
- **TanStack Router** for client-side routing
- **TanStack Query** for server state management
- **Motion** (Framer Motion) for animations
- **Zod** for form validation

## Pages

### Home (`/`)
- Digital clock with 12-hour AM/PM format
- Clock 1 & 2 control cards (ON/OFF, duty slider)
- STOP button section
- Status panel

### Alarms (`/alarms`)
- List of all alarms with toggle switches
- Add new alarm button
- Delete alarm functionality

### Alarm Edit (`/alarms/new`, `/alarms/:id`)
- Time picker (12-hour format with AM/PM)
- Day selection (everyday/weekdays/weekends/custom)
- Clock selection (1 or 2)
- Duration setting (auto-off timer)
- Zod validation with error display

## Project Structure

```
client/src/
├── components/
│   ├── AlarmItem.tsx      # Single alarm row with toggle
│   ├── ClockCard.tsx      # Motor control card
│   ├── DigitalClock.tsx   # Animated time display
│   ├── StatusPanel.tsx    # System status display
│   └── StopSection.tsx    # Emergency stop controls
├── pages/
│   ├── HomePage.tsx       # Main control page
│   ├── AlarmsPage.tsx     # Alarm list
│   ├── AlarmEditPage.tsx  # Create/edit alarm
│   └── RootLayout.tsx     # App shell with nav
├── lib/
│   ├── api.ts             # API client (switches demo/real)
│   ├── demo.ts            # Mock API for demo mode
│   └── queries.ts         # TanStack Query hooks
├── router.tsx             # Route definitions
├── main.tsx               # App entry point
└── index.css              # All styles
```

## Demo Mode

Set `VITE_DEMO_MODE=true` to use mock API:
- Clock states persist in memory during session
- Sample alarms pre-loaded
- Full CRUD operations simulated
- Uses browser time for clock display

## Commands

```bash
bun install                 # Install dependencies
bun run dev                 # Development (needs API)
bun run dev:demo            # Development (demo mode)
bun run build               # Production build
bun run build:demo          # Demo build for Cloudflare
bun run preview             # Preview built app
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE` | API base URL | `""` (same-origin) |
| `VITE_DEMO_MODE` | Enable demo mode | `"false"` |

## Deployment

### Cloudflare Pages (Automatic)

Push to `main` branch triggers GitHub Action:
1. Builds with `VITE_DEMO_MODE=true`
2. Deploys to `kalembang.pages.dev`

### Manual Deploy

```bash
bun run build:demo
npx wrangler pages deploy dist --project-name=kalembang
```
