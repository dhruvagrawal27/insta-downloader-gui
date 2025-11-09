"""
Test script for iiiLabCrawler - Instagram Video Downloader
This script tests the iiilab.py Instagram downloader functionality

NOTE: As of the test date, the Instagram API endpoint (instagram.iiilab.com) 
returns 404 errors. This may indicate:
1. The service is temporarily down
2. The API has changed
3. Instagram specifically is no longer supported

Alternative solutions are provided at the end.
"""

import sys
import json
from pathlib import Path

# Add iiiLabCrawler to path
iiilab_path = Path(__file__).parent / "iiiLabCrawler"
sys.path.insert(0, str(iiilab_path))

try:
    from iiilab import get_resource, INSTAGRAM, YOUTUBE, TIKTOK
except ImportError as e:
    print(f"❌ Error importing iiilab: {e}")
    print(f"Make sure iiiLabCrawler is cloned to: {iiilab_path}")
    sys.exit(1)


def test_instagram_download(url: str):
    """
    Test Instagram video download using iiilab
    
    Args:
        url: Instagram URL (reel or post)
    
    Returns:
        tuple: (success, data)
    """
    print("=" * 80)
    print("🎬 Testing iiilab Instagram Downloader")
    print("=" * 80)
    print(f"\n📍 URL: {url}\n")
    
    try:
        # Fetch resource
        print("🔍 Fetching Instagram content...")
        res_instagram = get_resource(url, INSTAGRAM)
        
        if res_instagram is None:
            print("❌ Failed to fetch Instagram content (returned None)")
            print("\n💡 Possible reasons:")
            print("   1. API endpoint is down (instagram.iiilab.com)")
            print("   2. Instagram API specifically was deprecated")
            print("   3. Rate limiting or IP blocking")
            return False, None
        
        # Display results
        print("\n✅ Successfully fetched content!")
        print("\n" + "=" * 80)
        print("📊 RESPONSE DATA:")
        print("=" * 80)
        print(json.dumps(res_instagram, indent=2, ensure_ascii=False))
        
        # Parse and display key information
        print("\n" + "=" * 80)
        print("📝 PARSED INFORMATION:")
        print("=" * 80)
        
        # Text/Caption
        text = res_instagram.get("text", "N/A")
        print(f"\n📄 Caption/Text:\n{text}")
        
        # Media information
        medias = res_instagram.get("medias", [])
        print(f"\n🎞️ Media Count: {len(medias)}")
        
        for idx, media in enumerate(medias, 1):
            print(f"\n--- Media #{idx} ---")
            media_type = media.get("media_type", "unknown")
            resource_url = media.get("resource_url", "N/A")
            preview_url = media.get("preview_url", "N/A")
            
            print(f"Type: {media_type}")
            print(f"Resource URL: {resource_url[:100]}..." if len(resource_url) > 100 else f"Resource URL: {resource_url}")
            print(f"Preview URL: {preview_url[:100]}..." if len(preview_url) > 100 else f"Preview URL: {preview_url}")
        
        # Stats
        stats = res_instagram.get("stats")
        if stats:
            print(f"\n📊 Stats: {stats}")
        
        # Overseas flag
        overseas = res_instagram.get("overseas")
        if overseas:
            print(f"🌍 Overseas: {overseas}")
        
        print("\n" + "=" * 80)
        print("✅ TEST PASSED!")
        print("=" * 80)
        return True, res_instagram
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        print("\n🔍 Traceback:")
        print(traceback.format_exc())
        return False, None


def test_youtube_as_comparison():
    """Test YouTube to verify the library is working (uses new API)"""
    print("\n\n" + "=" * 80)
    print("🧪 VERIFICATION TEST: YouTube (using new API)")
    print("=" * 80)
    print("\nTesting if iiilab library works with platforms using the NEW API...")
    
    url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # Short video
    print(f"📍 URL: {url}\n")
    
    try:
        print("🔍 Fetching YouTube content...")
        res = get_resource(url, YOUTUBE)
        
        if res:
            print("✅ YouTube API works!")
            print(f"📝 Title: {res.get('text', 'N/A')}")
            medias = res.get("medias", [])
            print(f"🎞️ Media count: {len(medias)}")
            if medias:
                print(f"🎬 Video URL available: {medias[0].get('resource_url', 'N/A')[:80]}...")
            return True
        else:
            print("❌ YouTube API also failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def show_alternatives():
    """Show alternative methods for Instagram downloads"""
    print("\n\n" + "=" * 80)
    print("� ALTERNATIVE SOLUTIONS FOR INSTAGRAM DOWNLOADS")
    print("=" * 80)
    
    print("""
1. ✅ RapidAPI (Currently Used in Your App)
   - Endpoint: instagram-story-downloader-media-downloader.p.rapidapi.com
   - Status: Working ✅
   - Pros: Reliable, bypasses rate limits
   - Your implementation is already using this!

2. ⚠️ iiilab.com Instagram API
   - Endpoint: instagram.iiilab.com/api/extract
   - Status: Not working (404 error)
   - Likely deprecated or service down

3. 🔄 yt-dlp (Alternative)
   - Python package or binary
   - Status: Works for public content
   - Issues: Rate limits on cloud servers

4. 🔄 Instaloader
   - Python package
   - Status: Works but faces API restrictions
   - Issues: Frequent Instagram blocks

RECOMMENDATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Your current RapidAPI implementation in streamlit_preview_app.py is the
BEST solution. The iiilab API for Instagram appears to be unavailable.

Stick with your current RapidAPI approach! 🎯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == "__main__":
    print("🚀 iiiLabCrawler Instagram Downloader Test\n")
    
    if len(sys.argv) > 1:
        # Test single URL from command line
        url = sys.argv[1]
        success, data = test_instagram_download(url)
        
        if not success:
            print("\n" + "=" * 80)
            print("� DIAGNOSING THE ISSUE...")
            print("=" * 80)
            test_youtube_as_comparison()
        
        show_alternatives()
        
    else:
        # Default test
        test_url = "https://www.instagram.com/p/DOONdzLEy9v/"
        success, data = test_instagram_download(test_url)
        
        if not success:
            print("\n" + "=" * 80)
            print("🔍 DIAGNOSING THE ISSUE...")
            print("=" * 80)
            test_youtube_as_comparison()
        
        show_alternatives()

