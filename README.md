# Craigslist Auto-Reposter

Automatically repost your Craigslist listings to keep them fresh and visible. Perfect for businesses and anyone who regularly posts on Craigslist.

**Warning:** This tool may stop working if Craigslist changes their website. Always back up your posts before using.

## Requirements

- Python 3.7 or higher
- Google Chrome
- Craigslist account (free at [accounts.craigslist.org](https://accounts.craigslist.org))

## How to Setup

1. Download `repost.py` and `SQWOZ_BAB.opus` file into a folder. Stay in this folder for the remainder of these steps.

2. Run `python -m venv my_env` (on macOS, use `python3`)

3. Install required packages:

```bash
pip install selenium beautifulsoup4 requests pyyaml librosa sounddevice
```
(Use `pip3` on macOS)

4. Create `config.yml` with information about which posts you want to be reposted. Anything not in this file won't be reposted.

```yaml
city_url: "https://newyork.craigslist.org"

posts:
  - id: 1234567890
    category: computers
    area: Brooklyn
    title_slug: brooklyn-macbook-air-2020
    postal: 11201
```

**Field descriptions:**
- `city_url`: Your local Craigslist city URL. For now, only NY metro area is supported.
- `posts`: List of posts to repost
  - `id`: Post ID from your listing URL
  - `category`: Post category (see list below)
  - `area`: Local area/borough (see list below)
  - `title_slug`: Title slug from your post URL (explained below)
  - `postal`: Your ZIP code

### Finding Post Information

**To get your post ID and title slug:**
1. Go to your Craigslist listing
2. Look at the URL: `https://newyork.craigslist.org/brk/sys/d/macbook-air-2020/1234567890.html`
3. The number at the end (1234567890) is your post ID
4. The text after `/d/` and before the ID (macbook-air-2020) is the title slug

Both the title slug and ID are required to identify your post.

**Categories:**
antiques, appliances, arts & crafts, auto parts, baby & kid stuff, bicycles, books & magazines, business/commercial, cars & trucks, cell phones, clothing & accessories, collectibles, computer parts, computers, electronics, farm & garden, free stuff, furniture, garage & moving sales, general for sale, health and beauty, heavy equipment, household items, jewelry, materials, motorcycle parts, motorcycles/scooters, musical instruments, photo/video, rvs, sporting goods, tickets, tools, toys & games, trailers, video gaming, wanted

**NYC Areas:**
manhattan, brooklyn, queens, bronx, staten island, new jersey, long island, westchester, fairfield co (Connecticut)

## How to Use

### Option 1: Automated Scheduling (Recommended)
Set up automated scheduling using the "Automated Scheduling" section below. The script will run automatically at regular intervals (e.g., daily at 7AM) to keep your posts at the top.

### Option 2: Manual Execution
Run the script manually:

1. Open terminal/command prompt
2. Navigate to the folder where we downloaded `repost.py`, etc.
3. Run `source my_env/bin/activate`
3. Run: `python repost.py` (Use `python3` on macOS)

## Login Process
When the tool starts:
1. Chrome browser opens automatically
2. Navigate to Craigslist login page
3. Log in to your account manually
4. Solve any CAPTCHA if prompted
5. Wait for the tool to detect successful login

## What Happens Next
The tool automatically:
1. Finds each post using your provided IDs
2. Saves all content (title, price, description, images, item condition, etc.)
3. Deletes the old post
4. Creates a new post with identical content
5. Moves to the next post

**Important:** Don't close the browser or interfere while running.

## Automated Scheduling (macOS)

Set up automatic reposting using macOS Calendar and Automator.

### Create Automator Script

1. Open **Automator** (Applications > Utilities)
2. Choose **"New Document"** → **"Application"**
3. Search for **"Run Shell Script"** and drag it to workflow
4. Set shell to **"/bin/bash"**
5. Paste this code:

```bash
#!/bin/bash
cd /path/to/your/craigslist-auto-reposter
source my_env/bin/activate
echo "$(date '+%a %b %-d, %Y, %-I:%M %p')" >> debug.log
python3 repost.py >> debug.log 2>&1
echo "=================================================================================================================" >> debug.log
cd -
```

Replace `/path/to/your/craigslist-auto-reposter` with the actual folder where you did the setup.

6. Save as **"Craigslist Reposter.app"**

### Set Up Calendar Event

1. Open **Calendar** app
2. Create new event at desired time (e.g., 7:30 AM)
3. Set event to repeat (daily, weekly, etc.)
4. Click **"Add Alert"** → **"Custom"** → **"Open File"**
5. Select your **"Craigslist Reposter.app"** file
6. Set alert to trigger at script run time

You will hear the SQWOZ BAB song Ой each time when the script starts. This is to let you know that you have to log in. Everything else gets done automatically.

## Example Configuration

See the `config.yml` file. This stores which posts you want to be reposted.
