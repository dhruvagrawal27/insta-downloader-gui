# 🚀 Quick Start Guide - React Frontend

Get your beautiful React frontend up and running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- Your Streamlit backend running (from main project)

## Step 1: Install Dependencies

```bash
cd frontend
npm install
```

This will install all required packages (~2 minutes).

## Step 2: Configure Environment

```bash
# Create environment file
cp .env.example .env.local
```

Edit `.env.local`:
```env
VITE_API_URL=http://localhost:8502
```

## Step 3: Start Development Server

```bash
npm run dev
```

Frontend will open at **http://localhost:3000** 🎉

## Step 4: Test It Out

1. Open http://localhost:3000 in your browser
2. Enter an Instagram URL
3. Configure download options
4. Click "Preview"
5. Download files individually!

## Deploy to Vercel (Optional)

### Quick Deploy

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Follow prompts and you're live! 🚀

### Environment Variables on Vercel

In Vercel Dashboard:
- Add: `VITE_API_URL` = your backend URL

## Troubleshooting

### Port Already in Use?
```bash
# Change port in vite.config.ts
server: {
  port: 3001, // or any port
}
```

### API Not Connecting?
1. Check backend is running on port 8502
2. Verify `.env.local` has correct URL
3. Check browser console for errors

### Build Errors?
```bash
rm -rf node_modules
npm install
npm run build
```

## Next Steps

- Customize colors in `tailwind.config.js`
- Add your logo in `App.tsx`
- Deploy backend to Streamlit Cloud
- Deploy frontend to Vercel

---

**Need Help?** Check `README.md` for detailed documentation!
