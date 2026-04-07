# Making Kalembang a PWA (Progressive Web App)

This guide covers how to make the Vite React client installable on your iPhone home screen.

## Step 1: Install vite-plugin-pwa

```bash
cd client
bun add vite-plugin-pwa -D
```

## Step 2: Update `vite.config.ts`

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'robots.txt'],
      manifest: {
        name: 'Kalembang',
        short_name: 'Kalembang',
        description: 'Kalembang alarm clock app',
        theme_color: '#ffffff',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      }
    })
  ]
})
```

## Step 3: Add Required Icons

Place these files in `client/public/`:

| File | Size | Purpose |
|------|------|---------|
| `pwa-192x192.png` | 192×192 px | Android/general PWA icon |
| `pwa-512x512.png` | 512×512 px | Large icon, splash screens |
| `apple-touch-icon.png` | 180×180 px | iOS home screen icon |

## Step 4: Add meta tags to `index.html`

Add these inside the `<head>` tag:

```html
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#ffffff">
```

## Step 5: Add to iPhone Home Screen

1. **Deploy your app** to a server with HTTPS (required for PWAs)
2. Open **Safari** on your iPhone and navigate to your app URL
3. Tap the **Share button** (square with arrow pointing up)
4. Scroll down and tap **"Add to Home Screen"**
5. Give it a name and tap **"Add"**

## Important Notes

- **HTTPS Required**: iOS requires the site to be served over HTTPS for PWA features
- **Safari Only**: On iOS, you must use Safari to add to home screen (not Chrome/Firefox)
- **Standalone Mode**: With `display: 'standalone'`, the app launches without browser UI
- **Service Worker**: The plugin auto-generates a service worker for offline caching

## Testing PWA Locally

You can test the PWA manifest in Chrome DevTools:
1. Open DevTools (F12)
2. Go to **Application** tab
3. Check **Manifest** and **Service Workers** sections

## Troubleshooting

- If the "Add to Home Screen" option doesn't appear, ensure HTTPS is configured
- Clear Safari cache if icons don't update
- Check that all icon files exist in the `public/` folder
