#!/usr/bin/env python3
"""
AutoGetCars Crawler - Menu Interface
Interactive menu for selecting different car search presets
"""

import os
import sys
import subprocess
from pathlib import Path

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header"""
    print("=" * 80)
    print("🚗 AutoGetCars Crawler - Interactive Menu")
    print("=" * 80)
    print("Select from predefined car search configurations")
    print()

def load_preset_files():
    """Dynamically load available preset files from presets/ folder"""
    presets_dir = Path(__file__).parent / 'presets'
    preset_files = {}
    
    if not presets_dir.exists():
        return preset_files
    
    # Find all .env.* files in presets directory
    preset_paths = list(presets_dir.glob('.env.*'))
    preset_paths.sort()  # Sort for consistent ordering
    
    # Assign dynamic menu numbers starting from 1
    for i, preset_path in enumerate(preset_paths, 1):
        preset_files[i] = str(preset_path)
    
    return preset_files

def extract_preset_info(preset_file_path):
    """Extract information from a preset file to generate description"""
    try:
        with open(preset_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse key information
        info = {}
        for line in content.split('\n'):
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                info[key.strip()] = value.strip()
        
        # Get preset name from filename
        filename = Path(preset_file_path).name
        preset_name = filename.replace('.env.', '').replace('-', ' ').title()
        
        # Generate description
        brand = info.get('BRAND', '').title()
        model = info.get('MODEL', '').replace('-', ' ').title()
        min_price = info.get('MIN_PRICE', '')
        max_price = info.get('MAX_PRICE', '')
        min_power = info.get('MIN_ENGINE_POWER', '')
        max_power = info.get('MAX_ENGINE_POWER', '')
        fuel_type = info.get('FUEL_TYPE', '')
        
        # Format price range
        if min_price and max_price:
            if int(min_price) >= 1000:
                price_str = f"{int(min_price)//1000}k-{int(max_price)//1000}k BGN"
            else:
                price_str = f"{min_price}-{max_price} BGN"
        else:
            price_str = "Price varies"
        
        # Format power range
        power_str = f"{min_power}-{max_power} HP" if min_power and max_power else "Power varies"
        
        # Create emoji based on vehicle type or brand
        emoji_map = {
            'bmw': '🚗', 'mercedes': '🚙', 'audi': '🚘', 'honda': '🌱',
            'toyota': '💰', 'tesla': '⚡', 'volkswagen': '🚐',
            'default': '⚙️'
        }
        
        preset_key = filename.replace('.env.', '').split('-')[0]
        emoji = emoji_map.get(preset_key, '🚗')
        
        return {
            'emoji': emoji,
            'name': f"{brand} {model}".strip() or preset_name,
            'description': f"{price_str} • {power_str} • {fuel_type}",
            'raw_info': info
        }
        
    except Exception as e:
        # Fallback if file can't be read
        filename = Path(preset_file_path).name
        preset_name = filename.replace('.env.', '').replace('-', ' ').title()
        return {
            'emoji': '🚗',
            'name': preset_name,
            'description': 'Configuration preset',
            'raw_info': {}
        }

def create_temp_env(preset_path, temp_name="temp_crawler"):
    """Create a temporary .env file from preset for crawler execution"""
    import tempfile
    import shutil
    
    # Create temporary file in same directory as main .env
    main_env_dir = Path(__file__).parent
    temp_env_path = main_env_dir / f".env.{temp_name}"
    
    # Copy preset to temporary location
    shutil.copy2(preset_path, temp_env_path)
    
    return str(temp_env_path)

def get_presets():
    """Dynamically generate all available car search presets from preset files"""
    preset_files = load_preset_files()
    presets = {}
    
    # Add all dynamically discovered presets
    for menu_id, preset_path in preset_files.items():
        preset_info = extract_preset_info(preset_path)
        filename = Path(preset_path).name
        
        presets[menu_id] = {
            "name": f"{preset_info['emoji']} {preset_info['name']}",
            "description": preset_info['description'],
            "preset_file": preset_path,
            "filename": filename
        }
    
    # Always add option 0 for custom configuration (main .env)
    presets[0] = {
        "name": "⚙️ Custom Configuration",
        "description": "Use current main .env settings (no preset used)",
        "preset_file": None,  # Uses main .env
        "filename": ".env (main)"
    }
    
    return presets

def display_menu():
    """Display the menu options dynamically"""
    presets = get_presets()
    
    print("Available Car Search Presets:")
    print("-" * 60)
    
    # Sort keys to show presets in order (1, 2, 3... then 0 at the end)
    sorted_keys = sorted([k for k in presets.keys() if k != 0]) + [0]
    
    for key in sorted_keys:
        preset = presets[key]
        
        if key == 0:
            # Special formatting for custom configuration
            print(f"\n {key:2d}. {preset['name']}")
            print(f"     {preset['description']}")
        else:
            # Regular preset display
            print(f" {key:2d}. {preset['name']}")
            print(f"     {preset['description']}")
            print(f"     📁 File: {preset['filename']}")
            print()

def get_crawl_options():
    """Get crawler execution options"""
    print("\n" + "=" * 60)
    print("Crawler Options:")
    print("-" * 60)
    
    # Delay option
    print("Select crawling speed:")
    print("1. Fast (0.3s delay) - ⚡ Quick but be respectful")
    print("2. Normal (0.5s delay) - ⚖️ Balanced approach")  
    print("3. Conservative (1.0s delay) - 🐌 Safe and steady")
    
    while True:
        try:
            speed_choice = int(input("\nChoose speed (1-3): ").strip())
            if speed_choice in [1, 2, 3]:
                delays = {1: "0.3", 2: "0.5", 3: "1.0"}
                delay = delays[speed_choice]
                break
            else:
                print("❌ Please enter 1, 2, or 3")
        except ValueError:
            print("❌ Please enter a valid number")
        except (EOFError, KeyboardInterrupt):
            print("\n⏹️ Cancelled")
            sys.exit(0)
    
    # Max pages option
    print("\nSelect page limit:")
    print("1. All pages - 📚 Complete search (recommended)")
    print("2. First 3 pages - 📄 Quick sample")
    print("3. First page only - 🔍 Testing")
    
    while True:
        try:
            pages_choice = int(input("\nChoose pages (1-3): ").strip())
            if pages_choice in [1, 2, 3]:
                max_pages = {1: "100", 2: "3", 3: "1"}
                pages = max_pages[pages_choice]
                break
            else:
                print("❌ Please enter 1, 2, or 3")
        except ValueError:
            print("❌ Please enter a valid number")
        except (EOFError, KeyboardInterrupt):
            print("\n⏹️ Cancelled")
            sys.exit(0)
    
    return delay, pages

def run_crawler(delay, max_pages, preset_file=None):
    """Execute the crawler with specified options and optional preset file"""
    print(f"\n🚀 Starting crawler with {delay}s delay, max {max_pages} pages...")
    
    temp_env_file = None
    try:
        # Get the Python executable path
        python_exe = sys.executable
        script_path = Path(__file__).parent / "crawler.py"
        
        if preset_file:
            # Create temporary env file from preset
            temp_env_file = create_temp_env(preset_file)
            print(f"📁 Using preset configuration: {Path(preset_file).name}")
            
            # Set environment variable to use temp env file
            import os
            original_env = os.environ.get('ENV_FILE')
            os.environ['ENV_FILE'] = temp_env_file
        else:
            print("📁 Using main .env configuration")
        
        print("=" * 60)
        
        # Run the crawler
        cmd = [python_exe, str(script_path), "--delay", delay, "--max-pages", max_pages]
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Crawler failed with error code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ Could not find crawler.py script")
        return False
    finally:
        # Clean up temporary env file and restore original environment
        if temp_env_file and Path(temp_env_file).exists():
            Path(temp_env_file).unlink()
        if preset_file:
            import os
            if 'original_env' in locals() and original_env:
                os.environ['ENV_FILE'] = original_env
            elif 'ENV_FILE' in os.environ:
                del os.environ['ENV_FILE']

def main():
    """Main menu loop"""
    while True:
        clear_screen()
        print_header()
        display_menu()
        
        presets = get_presets()
        max_option = max(presets.keys()) if presets else 0
        
        print("=" * 60)
        try:
            choice = input(f"Select a preset (1-{max_option} or 0) or 'q' to quit: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            sys.exit(0)
        
        if choice == 'q':
            print("👋 Goodbye!")
            sys.exit(0)
        
        try:
            choice_num = int(choice)
            if choice_num not in presets:
                try:
                    input(f"❌ Invalid choice. Please select 0-{max_option} or 'q'. Press Enter to continue...")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Goodbye!")
                    sys.exit(0)
                continue
        except ValueError:
            try:
                input(f"❌ Please enter a number (0-{max_option}) or 'q' to quit. Press Enter to continue...")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                sys.exit(0)
            continue
        
        selected_preset = presets[choice_num]
        
        print(f"\n✅ Selected: {selected_preset['name']}")
        print(f"📋 {selected_preset['description']}")
        
        # Check if preset is available
        if choice_num != 0 and not selected_preset['preset_file']:
            print("❌ This preset is not available (file not found)")
            try:
                input("Press Enter to continue...")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                sys.exit(0)
            continue
        
        if choice_num == 0:
            print("⚙️ Using current main .env configuration")
        else:
            print(f"📁 Will use preset: {selected_preset['filename']}")
            print("💡 Your main .env file will NOT be modified")
        
        # Get crawler options
        delay, max_pages = get_crawl_options()
        
        # Confirm before running
        print(f"\n🎯 Ready to crawl with:")
        print(f"   • Configuration: {selected_preset['name']}")
        print(f"   • Speed: {delay}s delay") 
        print(f"   • Pages: {max_pages} max")
        if choice_num != 0:
            print(f"   • Preset file: {selected_preset['filename']}")
        else:
            print(f"   • Using: main .env file")
        
        try:
            confirm = input("\nProceed? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                continue
        except (EOFError, KeyboardInterrupt):
            print("\n⏹️ Cancelled")
            continue
        
        # Run the crawler with preset file if selected
        preset_file = selected_preset['preset_file'] if choice_num != 0 else None
        success = run_crawler(delay, max_pages, preset_file)
        
        if success:
            print("\n🎉 Crawler completed successfully!")
        else:
            print("\n❌ Crawler encountered errors")
        
        print("\n📊 Check the following files for results:")
        print("   • docs/car-data.xlsx - Excel export")
        print("   • crawler.log - Detailed logs")
        
        try:
            input("\nPress Enter to return to main menu...")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Exiting menu...")
            break

if __name__ == "__main__":
    main()