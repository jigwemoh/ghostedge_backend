import sys
import os
import shutil
from pathlib import Path

print("🕵️‍♂️ STARTING SOCCERDATA DEEP DIAGNOSTIC...")
print(f"   Python Version: {sys.version.split()[0]}")
print(f"   Working Directory: {os.getcwd()}")

# 1. CHECK DEPENDENCIES
required_packages = ['soccerdata', 'pandas', 'lxml', 'html5lib', 'requests']
print("\n📦 CHECKING DEPENDENCIES...")
import importlib.util
missing = []
for pkg in required_packages:
    spec = importlib.util.find_spec(pkg)
    status = "✅ Found" if spec else "❌ MISSING"
    print(f"   - {pkg}: {status}")
    if not spec:
        missing.append(pkg)

if missing:
    print(f"\n❌ CRITICAL: Missing packages: {', '.join(missing)}")
    print(f"   👉 FIX: Run command: pip install {' '.join(missing)}")
    sys.exit(1)

# 2. CHECK CACHE PERMISSIONS
print("\n📂 CHECKING CACHE PERMISSIONS...")
cache_dir = Path(os.getcwd()) / "soccer_data_debug_cache"
try:
    if cache_dir.exists():
        shutil.rmtree(cache_dir) # Clean start
    cache_dir.mkdir(parents=True, exist_ok=True)
    test_file = cache_dir / "test_write.txt"
    test_file.write_text("permission_check")
    print(f"   ✅ Write Permission: OK ({cache_dir})")
except Exception as e:
    print(f"   ❌ PERMISSION ERROR: Cannot write to folder. {e}")
    print("   👉 FIX: Run script with 'sudo' or check folder permissions.")
    sys.exit(1)

# 3. ATTEMPT CONNECTION (THE REAL TEST)
print("\nglobe_with_meridians CONNECTING TO FBREF (VIA SOCCERDATA)...")
try:
    import soccerdata as sd
    
    # Initialize with the debug cache folder
    print("   1. Initializing Scraper Class...")
    # NOTE: Ensure season format is correct. Sometimes '2024' or '2324' is preferred over '2425' if the season hasn't fully started in the library's eyes.
    # We will try '2324' (Last complete season) to rule out "future season" errors, then you can switch back.
    scraper = sd.FBref(leagues="ENG-Premier League", seasons="2324", data_dir=cache_dir)
    
    print("   2. Attempting to fetch Standings (Network Test)...")
    
    # FIX: Trying alternative method names if read_standings fails
    try:
        standings = scraper.read_league_table()
        print("      ✅ Method used: read_league_table()")
    except AttributeError:
        try:
            standings = scraper.read_standings()
            print("      ✅ Method used: read_standings()")
        except AttributeError:
             print("      ❌ CRITICAL: Neither 'read_league_table' nor 'read_standings' exists.")
             print("         listing available methods:")
             print([m for m in dir(scraper) if 'read' in m])
             raise

    if standings.empty:
        print("   ⚠️ WARNING: Connection successful, but returned EMPTY data.")
    else:
        print("   ✅ SUCCESS: Data downloaded!")
        print(f"      Rows fetched: {len(standings)}")
        print(f"      Top Team: {standings.index[0] if not standings.empty else 'N/A'}")

except ImportError as ie:
    print(f"\n❌ IMPORT ERROR: {ie}")
    print("   (This usually means 'lxml' or 'html5lib' is installed but broken)")
except Exception as e:
    print(f"\n❌ RUNTIME ERROR: {type(e).__name__}")
    print(f"   Error Details: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 DIAGNOSTIC COMPLETE.")