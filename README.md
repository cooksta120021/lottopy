# LottoPy

Multi-game lottery scraper and analyzer for Texas Lottery games. It pulls draw histories, counts number frequencies, and generates suggestion sets using a dynamic frequency threshold.

## Table of Contents

- [About](#about)
- [Setup](#setup)
- [Usage](#usage)
- [GUI](#gui)
- [Outputs](#outputs)
- [Notes](#notes)
- [Extending](#extending)

## About <a name="about"></a>

Games supported (extensible via config):

- **Mega Millions** (`mega_millions`)
- **Texas Two Step** (`texas_two_step`)

Workflow per game:

1. Scrape the game’s winning numbers page and save raw draws.
2. Count how often each ball appears (main numbers and special balls).
3. Derive a dynamic threshold from draw history and generate suggestion sets using frequently occurring numbers.

## Setup <a name="setup"></a>

Prerequisites:

- Python 3.8+
- Dependencies: `requests`, `beautifulsoup4`

Install dependencies:

```bash
pip install -r requirements.txt  # if available
# or install directly:
pip install requests beautifulsoup4
```

## Usage <a name="usage"></a>

Run the GUI (includes scrape, count, and suggestion flow):

```bash
python main.py  # launches Tkinter GUI
```

Direct module launch (equivalent):

```bash
python -m lottopy.gui
```

Options:

- Adjust options inside the GUI: game, output dir, threshold divisor, suggestion sets, and load results.

## GUI <a name="gui"></a>

Run the simple Tkinter GUI to select a game, tweak options, and run the pipeline:

```bash
python -m lottopy.gui
```

Controls:

- **Game**: choose `mega_millions` or `texas_two_step`.
- **Output dir**: where results will be saved.
- **Threshold divisor**: adjusts frequency cutoff (`total_draws / divisor`).
- **Suggestion sets**: number of suggestion rows to generate.
- **Load results**: after running (or if files already exist), loads `{game}_suggestions.txt` from the output dir into the GUI for review.

## Outputs <a name="outputs"></a>

Outputs live in `data/` by default:

- `{game}_raw.csv`: Raw draw rows scraped from the site.
- `{game}_counts.csv`: Frequency table (`category,value,count`) for numbers and special balls.
- `{game}_suggestions.txt`: Up to N suggestion rows composed of frequently occurring numbers.

## Notes <a name="notes"></a>

- Live scrape depends on the Texas Lottery website; network availability and site layout changes may affect results.
- Threshold scales with draw history (`total_draws / threshold_divisor`), so outputs shift as more draws arrive.
- The original standalone script is preserved at `legacy/scraper.py` (manual run; writes `temp.txt`/`temp2.txt`/`final.txt` in the working directory).

## Extending <a name="extending"></a>

Add a new game without touching existing ones:

1. Create `lottopy/games/<your_game>.py` exporting a `GameConfig` and calling `register_game(...)`.
2. Implement a `parse_row(row)` function that returns `(numbers: List[str], specials: List[str])`.
3. Import the module in `lottopy/games/__init__.py` to auto-register.

The CLI/GUI will pick up new games via the registry—no other code changes needed.
