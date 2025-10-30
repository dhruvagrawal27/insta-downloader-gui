# 🎨 Instagram Downloader - React + TypeScript Frontend

## 🎯 Overview

A beautiful, modern React frontend for the Instagram Downloader with:
- ✨ Beautiful gradient UI/UX
- 🌓 Dark mode support
- 📱 Fully responsive
- 🚀 Zero local storage (Vercel-friendly)
- 📥 Individual file downloads
- 📋 Copy caption/transcript
- 🎤 Groq AI transcription

## 🚀 Quick Setup

### Windows
```bash
.\setup.ps1
npm run dev
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
npm run dev
```

Open **http://localhost:3000** 🎉

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[README.md](README.md)** - Full documentation
- **[../docs/README.md](../docs/README.md)** - Main project docs

## 🌐 Deploy to Vercel

```bash
npm i -g vercel
vercel
```

Set environment variable:
- `VITE_API_URL` = your backend URL

## 🛠️ Tech Stack

- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS + shadcn/ui
- Zustand (state)
- Axios (HTTP)
- Hot Toast (notifications)

## 📂 Structure

```
frontend/
├── src/
│   ├── components/ui/   # UI components
│   ├── lib/            # API, store, utils
│   ├── App.tsx         # Main app
│   └── main.tsx        # Entry point
├── public/             # Static files
└── ...config files
```

## ⚙️ Available Scripts

```bash
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview build
npm run lint     # Run linter
```

## 🎨 Features

### Download Options
- ✅ Video (MP4)
- ✅ Thumbnail (JPG)
- ✅ Audio (MP3)
- ✅ Caption (TXT)
- ✅ Transcription (AI)

### UI Features
- Dark/Light mode toggle
- Responsive design
- Toast notifications
- Loading states
- Error handling
- Copy to clipboard
- Individual downloads

## 🔧 Configuration

### Environment Variables

`.env.local`:
```env
VITE_API_URL=http://localhost:8502
```

### Tailwind Colors

Edit `tailwind.config.js` to customize colors.

## 🐛 Troubleshooting

**Build errors?**
```bash
rm -rf node_modules
npm install
```

**API not connecting?**
1. Check backend is running
2. Verify `.env.local` URL
3. Check CORS settings

**Port in use?**
Change port in `vite.config.ts`

## 📱 Mobile Support

Fully responsive and mobile-optimized with:
- Touch-friendly controls
- Adaptive layouts
- Mobile-friendly sizes

## 🔐 Security

- API keys in localStorage
- No server-side storage
- Client-side downloads
- HTTPS recommended

## 📈 Performance

- Bundle: ~150KB gzipped
- First Load: < 1s
- Lighthouse: 90+

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit PR

## 📄 License

MIT License - see main LICENSE file

---

**Made with ❤️ by Dhruv Agrawal**

**Links:**
- [Main Project](../docs/README.md)
- [Backend Setup](../STREAMLIT_README.md)
- [Groq Setup](../QUICK_START_GROQ.md)
- [GitHub](https://github.com/dhruvagrawal27/insta-downloader-gui)
