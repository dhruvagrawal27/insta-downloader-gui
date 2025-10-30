import React, { useState } from 'react'
import { Download, Instagram, Loader2, Copy, X } from 'lucide-react'
import { Button } from './components/ui/button'
import { Input } from './components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { useAppStore } from './lib/store'
import { apiService } from './lib/api'
import { isValidInstagramUrl, copyToClipboard, formatBytes } from './lib/utils'
import toast, { Toaster } from 'react-hot-toast'
import './index.css'

function App() {
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | null>(null)

  const {
    isDarkMode,
    toggleDarkMode,
    downloadOptions,
    setDownloadOption,
    mediaFiles,
    setMediaFiles,
    clearMediaFiles,
    isLoading,
    setIsLoading,
    caption,
    transcript,
    setCaption,
    setTranscript,
  } = useAppStore()

  const handleDownload = async () => {
    if (!url.trim()) {
      setError('Please enter an Instagram URL')
      return
    }

    if (!isValidInstagramUrl(url)) {
      setError('Please enter a valid Instagram URL')
      return
    }

    setError(null)
    setIsLoading(true)
    clearMediaFiles()

    try {
      const result = await apiService.downloadMedia({
        url,
        ...downloadOptions,
      })

      if (result.success) {
        setMediaFiles(result.files)
        if (result.caption) setCaption(result.caption)
        if (result.transcript) setTranscript(result.transcript)
        toast.success('Media downloaded successfully!')
      } else {
        setError(result.error || 'Download failed')
        toast.error(result.error || 'Download failed')
      }
    } catch (err: any) {
      const errorMsg = err.message || 'An error occurred'
      setError(errorMsg)
      toast.error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopyText = async (text: string, label: string) => {
    try {
      await copyToClipboard(text)
      toast.success(`${label} copied to clipboard!`)
    } catch (err) {
      toast.error('Failed to copy to clipboard')
    }
  }

  const downloadFile = (file: any) => {
    try {
      // Properly decode base64 to binary data
      const binaryString = atob(file.data)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      
      const blob = new Blob([bytes], { type: file.mimeType })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success(`Downloaded ${file.filename}`)
    } catch (err) {
      console.error('Download error:', err)
      toast.error('Failed to download file')
    }
  }

  React.useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode)
  }, [isDarkMode])

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-purple-900 dark:to-blue-900 transition-colors duration-300">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="border-b bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 p-2 rounded-lg">
              <Instagram className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
                Instagram Downloader
              </h1>
              <p className="text-sm text-muted-foreground">with Groq AI Transcription</p>
            </div>
          </div>
          
          <Button
            variant="outline"
            size="icon"
            onClick={toggleDarkMode}
            className="rounded-full"
          >
            {isDarkMode ? '🌞' : '🌙'}
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Settings */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg">Download Options</CardTitle>
              <CardDescription>Configure what to download</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Downloader Selection */}
              <div>
                <label className="text-sm font-medium mb-2 block">Downloader</label>
                <select
                  value={downloadOptions.downloader}
                  onChange={(e) => setDownloadOption('downloader', e.target.value)}
                  className="w-full h-10 px-3 rounded-md border border-input bg-background"
                >
                  <option value="yt-dlp">yt-dlp (Recommended)</option>
                  <option value="instaloader">Instaloader</option>
                </select>
              </div>

              {/* Content Options */}
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={downloadOptions.downloadVideo}
                    onChange={(e) => setDownloadOption('downloadVideo', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">📹 Download Video</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={downloadOptions.downloadThumbnail}
                    onChange={(e) => setDownloadOption('downloadThumbnail', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">🖼️ Download Thumbnail</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={downloadOptions.downloadAudio}
                    onChange={(e) => setDownloadOption('downloadAudio', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">🎵 Download Audio</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={downloadOptions.downloadCaption}
                    onChange={(e) => setDownloadOption('downloadCaption', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">📝 Download Caption</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={downloadOptions.transcribe}
                    onChange={(e) => setDownloadOption('transcribe', e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">🎤 Transcribe Audio</span>
                </label>
              </div>

              {/* Hinglish Processing Option */}
              {downloadOptions.transcribe && (
                <div className="space-y-2 border-t pt-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={downloadOptions.enableHinglish}
                      onChange={(e) => setDownloadOption('enableHinglish', e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">🇮🇳 Enable Hinglish Processing</span>
                  </label>
                  <p className="text-xs text-muted-foreground">
                    Requires Groq API key configured in backend .env file
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* URL Input */}
            <Card>
              <CardHeader>
                <CardTitle>Enter Instagram URL</CardTitle>
                <CardDescription>Paste a link to an Instagram post or reel</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="https://www.instagram.com/reel/..."
                    value={url}
                    onChange={(e) => {
                      setUrl(e.target.value)
                      setError(null)
                    }}
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button
                    onClick={handleDownload}
                    disabled={isLoading || !url}
                    className="min-w-[120px]"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Download className="mr-2 h-4 w-4" />
                        Preview
                      </>
                    )}
                  </Button>
                </div>

                {error && (
                  <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md flex items-start gap-2">
                    <X className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    <span className="text-sm">{error}</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Results */}
            {mediaFiles.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Downloaded Content</CardTitle>
                  <CardDescription>Click to download individual files</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Media Files */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {mediaFiles.map((file, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        className="h-auto p-4 flex flex-col items-start gap-2"
                        onClick={() => downloadFile(file)}
                      >
                        <div className="flex items-center gap-2 w-full">
                          <span className="text-2xl">
                            {file.type === 'video' ? '📹' : file.type === 'audio' ? '🎵' : file.type === 'thumbnail' ? '🖼️' : '📄'}
                          </span>
                          <div className="flex-1 text-left">
                            <div className="font-medium text-sm">{file.filename}</div>
                            {file.size && (
                              <div className="text-xs text-muted-foreground">{formatBytes(file.size)}</div>
                            )}
                          </div>
                          <Download className="h-4 w-4" />
                        </div>
                      </Button>
                    ))}
                  </div>

                  {/* Caption */}
                  {caption && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-sm">Caption</h4>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleCopyText(caption, 'Caption')}
                        >
                          <Copy className="h-3 w-3 mr-1" />
                          Copy
                        </Button>
                      </div>
                      <div className="bg-muted/50 p-4 rounded-md text-sm">
                        {caption}
                      </div>
                    </div>
                  )}

                  {/* Transcript */}
                  {transcript && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-sm">Transcript (AI Generated)</h4>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleCopyText(transcript, 'Transcript')}
                        >
                          <Copy className="h-3 w-3 mr-1" />
                          Copy
                        </Button>
                      </div>
                      <div className="bg-muted/50 p-4 rounded-md text-sm">
                        {transcript}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
          <p>Made with ❤️ by Dhruv Agrawal | For educational purposes only</p>
          <p className="mt-1">Respect Instagram's Terms of Service and content creators' rights</p>
        </div>
      </footer>
    </div>
  )
}

export default App
