# Kalembang Client - Demo Deployment

This directory contains the Kalembang alarm controller UI.

## Development

```bash
# Install dependencies
bun install

# Start development server (requires backend API on localhost:8088)
bun run dev

# Start development server in demo mode (no backend required)
bun run dev:demo
```

## Building

### Production Build (requires API server)
```bash
bun run build
```

### Demo Build (for Cloudflare Pages)
```bash
bun run build:demo
```

The built files will be in the `dist/` directory.

## Cloudflare Pages Deployment

### Option 1: Via Git Integration (Recommended)

1. Push your code to GitHub/GitLab
2. Go to [Cloudflare Pages](https://pages.cloudflare.com/)
3. Click "Create a project" → "Connect to Git"
4. Select your repository
5. Configure build settings:
   - **Build command:** `cd client && bun install && bun run build:demo`
   - **Build output directory:** `client/dist`
   - **Environment variables:**
     - `VITE_DEMO_MODE`: `true`

### Option 2: Direct Upload

1. Build the demo version locally:
   ```bash
   bun run build:demo
   ```
2. Go to [Cloudflare Pages](https://pages.cloudflare.com/)
3. Click "Create a project" → "Direct Upload"
4. Drag and drop the `dist/` folder

### Option 3: Wrangler CLI

1. Install Wrangler:
   ```bash
   bun add -g wrangler
   ```
2. Login to Cloudflare:
   ```bash
   wrangler login
   ```
3. Build and deploy:
   ```bash
   bun run build:demo
   wrangler pages deploy dist --project-name=kalembang-demo
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE` | Base URL for API (empty for same-origin) | `""` |
| `VITE_DEMO_MODE` | Enable demo mode with mock data | `false` |

## Demo Mode

When `VITE_DEMO_MODE=true`, the app uses simulated data instead of calling the real API:

- **Status**: Simulated clock states that persist during the session
- **Clocks**: ON/OFF and duty cycle controls work in-memory
- **Alarms**: Full CRUD operations with sample alarms
- **Time**: Uses local browser time

This allows the full UI to be demonstrated without requiring the Orange Pi backend.

## Preview

To preview the built demo locally:

```bash
bun run build:demo
bun run preview
```

Open http://localhost:5173 in your browser.
