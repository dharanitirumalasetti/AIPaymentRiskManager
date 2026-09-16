# RiskLens AI Frontend

React + Vite dashboard for the RiskLens AI prototype.

Run locally:

```bash
npm install
npm run dev
```

The UI expects the backend API at `http://127.0.0.1:8000`. Set `VITE_API_URL` to override it.

With the backend and frontend running, verify the demo flow with:

```bash
npx playwright install chromium
npm run test:e2e
```
