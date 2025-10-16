# Presets Folder

This folder contains predefined `.env` configuration files for different car search scenarios.

## Available Presets

| Preset File | Description | Brand/Model | Price Range | Power Range |
|------------|-------------|-------------|-------------|-------------|
| `.env.bmw-x5` | Luxury German SUVs | BMW X5 | 20k-80k BGN | 200-500 HP |
| `.env.honda-crv` | Reliable Family SUVs | Honda CR-V | 8k-25k BGN | 120-200 HP |
| `.env.toyota-corolla` | Budget-Friendly Cars | Toyota Corolla | 3k-15k BGN | 90-150 HP |
| `.env.mercedes-e` | Executive Sedans | Mercedes E-Class | 15k-60k BGN | 150-400 HP |
| `.env.audi-a4` | Diesel Efficiency | Audi A4 | 8k-35k BGN | 120-250 HP |
| `.env.bmw-3series` | Sports Cars | BMW Seria 3 | 10k-50k BGN | 180-400 HP |
| `.env.vw-touran` | Family Vans | VW Touran | 5k-30k BGN | 100-200 HP |
| `.env.tesla-model3` | Electric Vehicles | Tesla Model 3 | 25k-100k BGN | 200-500 HP |
| `.env.bmw-4cabrio` | Convertibles | BMW Seria 4 | 15k-70k BGN | 180-400 HP |
| `.env.default` | Balanced Search | BMW Seria 3 | 5k-50k BGN | 100-300 HP |

## How to Use

### Method 1: Preset Switcher Script
```bash
./switch-preset
```
Interactive menu to switch between presets.

### Method 2: Manual Copy
```bash
# Copy preset to main .env file
cp presets/.env.bmw-x5 .env

# Run crawler with preset settings
.venv/bin/python run_crawler.py --max-pages 5
```

### Method 3: Use Menu Systems
The `quick_crawler.py` and `menu_crawler.py` automatically update the root `.env` file when you select options.

## File Structure

- **Root `.env`**: The active configuration used by `run_crawler.py`
- **presets/.env.xxx**: Preset configurations you can switch between
- **switch-preset**: Script to easily switch between presets

## Creating Custom Presets

1. Copy an existing preset:
   ```bash
   cp presets/.env.default presets/.env.my-custom-search
   ```

2. Edit the new file with your preferred settings:
   ```bash
   nano presets/.env.my-custom-search
   ```

3. Use the switcher to activate it:
   ```bash
   ./switch-preset
   ```

## Tips

- Always backup your current `.env` before switching presets
- The switcher automatically creates backups
- Use meaningful names for custom presets
- Test new presets with `--max-pages 1` first