# 🍪 Instagram Cookie Authentication Guide

This guide explains how to add Instagram cookies to bypass rate limits and access private content.

---

## 🎯 Why Use Cookies?

Instagram aggressively blocks cloud-hosted applications and unauthenticated requests. By using cookies from your logged-in Instagram session:

- ✅ **Bypass rate limits** - No more 403/401 errors
- ✅ **Access private content** - Download from accounts you follow
- ✅ **Better reliability** - Works like you're browsing Instagram normally
- ✅ **No API limits** - Uses your personal session

---

## 📋 Step-by-Step Guide

### Method 1: Browser Extension (Recommended)

#### **Chrome/Edge/Brave**

1. **Install Extension**
   - Go to Chrome Web Store
   - Search for "Get cookies.txt LOCALLY"
   - Install the extension: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

2. **Export Instagram Cookies**
   - Login to [Instagram.com](https://www.instagram.com)
   - Click the extension icon in toolbar
   - Click "Export" → Choose "Netscape format"
   - Copy all the text

3. **Add to App**
   - Open the Streamlit app
   - Check "🍪 Use Instagram Cookies" in sidebar
   - Paste the copied cookies
   - Click outside the text area

#### **Firefox**

1. **Install Extension**
   - Go to Firefox Add-ons
   - Search for "cookies.txt"
   - Install: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Export Cookies** (same as above)
   - Login to Instagram
   - Click extension icon
   - Export in Netscape format
   - Copy the text

### Method 2: Manual Cookie Export

If you prefer not to use extensions:

1. **Open Browser DevTools**
   - Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
   - Press `Cmd+Option+I` (Mac)

2. **Navigate to Application/Storage Tab**
   - Click "Application" tab (Chrome/Edge)
   - Or "Storage" tab (Firefox)

3. **Find Instagram Cookies**
   - Expand "Cookies" in sidebar
   - Click on `https://www.instagram.com`

4. **Export Cookies Manually**
   - Copy values for these cookies:
     - `sessionid`
     - `csrftoken`
     - `ds_user_id`
     - `ig_did`
   - Format them in Netscape format (see example below)

---

## 📝 Cookie Format Example

Cookies must be in **Netscape HTTP Cookie File format**:

```
# Netscape HTTP Cookie File
.instagram.com	TRUE	/	TRUE	1234567890	sessionid	YOUR_SESSION_ID_HERE
.instagram.com	TRUE	/	FALSE	1234567890	csrftoken	YOUR_CSRF_TOKEN_HERE
.instagram.com	TRUE	/	TRUE	1234567890	ds_user_id	YOUR_USER_ID_HERE
.instagram.com	TRUE	/	FALSE	1234567890	ig_did	YOUR_DEVICE_ID_HERE
```

**Format explanation:**
- Column 1: Domain
- Column 2: Include subdomains (TRUE/FALSE)
- Column 3: Path
- Column 4: Secure connection (TRUE/FALSE)
- Column 5: Expiration timestamp
- Column 6: Cookie name
- Column 7: Cookie value

---

## 🔒 Security & Privacy

### ⚠️ Important Security Notes:

1. **Never share your cookies** - They provide full access to your Instagram account
2. **Cookies are session-only** - Used only for the current download, never stored
3. **Use in private deployments** - Don't paste cookies in public/shared Streamlit apps
4. **Cookies expire** - You may need to re-export them periodically (usually 30-90 days)
5. **Two-factor authentication** - If enabled, you may need to approve the session

### 🛡️ Best Practices:

- ✅ Only use cookies on apps you trust
- ✅ Use private/local deployments when possible
- ✅ Re-export cookies if you change your Instagram password
- ✅ Clear cookies from the app when done
- ❌ Never commit cookies to git/GitHub
- ❌ Don't share screenshots with visible cookie values

---

## 🚨 Troubleshooting

### Issue: "Cookies seem too short"
**Solution:** Make sure you copied the entire cookie export, including the header line `# Netscape HTTP Cookie File`

### Issue: "Still getting rate limited"
**Solution:** 
- Verify cookies are from a logged-in session
- Try re-exporting fresh cookies
- Wait 10-15 minutes between attempts
- Check if your Instagram account has any restrictions

### Issue: "Authentication failed"
**Solution:**
- Make sure you're logged into Instagram
- Try logging out and back in before exporting
- Check if Instagram requires verification (SMS/Email)
- Verify the cookies aren't expired

### Issue: "Can't access private content"
**Solution:**
- Cookies must be from an account that follows the private account
- Make sure you have permission to view the content
- Try accessing the content directly in browser first

---

## 💡 Tips

1. **Test First**: Verify your cookies work by trying a public post first
2. **Keep Updated**: Re-export cookies every month for best results
3. **Desktop App**: Consider using the desktop version for automatic cookie management
4. **Local Run**: Running the app locally is more secure than cloud deployments

---

## 🔗 Related Links

- [yt-dlp Cookie Documentation](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
- [Netscape Cookie Format Spec](http://www.cookiecentral.com/faq/#3.5)
- [Browser Extensions Safety Guide](https://www.eff.org/deeplinks/2020/03/users-guide-browser-extensions)

---

## ❓ FAQ

**Q: Are cookies safe to use?**  
A: Cookies are safe when used in private/local deployments. Avoid using them in public apps.

**Q: Will Instagram detect this?**  
A: Using cookies makes requests appear as normal browsing. However, excessive downloads may still trigger limits.

**Q: Can I use cookies from a different account?**  
A: Yes, but you'll only have access to content that account can view.

**Q: How long do cookies last?**  
A: Instagram cookies typically last 30-90 days. Re-export if they stop working.

**Q: Do I need all cookies?**  
A: At minimum, you need `sessionid`. Other cookies improve reliability.

---

## 📧 Support

If you encounter issues not covered here:
1. Check the [main README](../README.md) for general troubleshooting
2. Open an issue on [GitHub](https://github.com/dhruvagrawal27/insta-downloader-gui/issues)
3. Include error messages (but **never include cookie values!**)

---

**Remember**: Cookies provide full access to your Instagram account. Use responsibly and securely! 🔐
