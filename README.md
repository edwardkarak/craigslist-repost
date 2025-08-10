# Craigslist Auto-Reposter

Tool for reposting your Craigslist listings to keep them fresh and visible to potential customers. Perfect for small businesses, real estate agents, and anyone who regularly posts on Craigslist.

**Note:** This script may break at any moment, if Craigslist updates their UI/layout.

**Important:** Back up your posts before using this tool.

## Prerequisites

1. **Python 3.7 or higher** installed on your computer
2. **Google Chrome** installed
3. **Craigslist account** (free to create at [accounts.craigslist.org](https://accounts.craigslist.org))

## Installation

### Step 1: Download the Tool
Download all the files in this folder to your computer.

### Step 2: Install Required Software
Open your terminal/command prompt and run:

```bash
pip install selenium beautifulsoup4 requests pyyaml librosa sounddevice
```
(On macOS, run pip3 instead of pip)

## Setup Instructions

### Step 1: Configure Your Settings
Open the `config.yml` file in any text editor (Notepad, etc.) and update it with your information:

```yaml
email: "your-email@example.com"
city_url: "https://newyork.craigslist.org"

posts:
  - id: 1234567890
    category: computers
    area: Brooklyn
    title_slug: brooklyn-macbook-air-2020
    postal: 11201
```

**What each field means:**
- `email`: Your email address (used for contact information)
- `city_url`: Your local Craigslist city (e.g., "https://newyork.craigslist.org" for NYC)
- `posts`: List of your posts to repost
  - `id`: The post ID from your Craigslist listing URL
  - `category`: The category your post is in (see categories list below)
  - `area`: Your local area/borough (see areas list below)
  - `title_slug`: The title slug seen in your post URL. Will be explained below.
  - `postal`: Your ZIP code

### Step 2: Find Your Post Information

**To find your post ID and title slug:**
1. Go to your Craigslist listing
2. Look at the URL: `https://newyork.craigslist.org/brk/sys/d/macbook-air-2020/1234567890.html`
3. The number at the end (1234567890) is your post ID
4. The string after the d and before the ID (macbook-air-2020) is the title slug.

Craigslist uses the title slug + the ID to uniquely identify your post. It needs both.

**Available Categories:**
- antiques
- appliances
- arts & crafts
- auto parts
- baby & kid stuff
- bicycles
- books & magazines
- business/commercial
- cars & trucks
- cell phones
- clothing & accessories
- collectibles
- computer parts
- computers
- electronics
- farm & garden
- free stuff
- furniture
- garage & moving sales
- general for sale
- health and beauty
- heavy equipment
- household items
- jewelry
- materials
- motorcycle parts
- motorcycles/scooters
- musical instruments
- photo/video
- rvs
- sporting goods
- tickets
- tools
- toys & games
- trailers
- video gaming
- wanted

**Available Areas (for NYC):**
- manhattan
- brooklyn
- queens
- bronx
- staten island
- new jersey
- long island
- westchester
- fairfield co, CT

## How to Use

### Step 1
#### Option 1: Automated Scheduling (Recommended)
Set up automated scheduling by following the steps in "Automated Scheduling (macOS)" section below. Now, you can repost the same ads, for example, daily at 7AM, keeping your posts at the top. The script will run automatically at regular intervals.

#### Option 2: Manual Execution
If you want to run the script manually:

1. Open your terminal/command prompt, navigate to the folder with the tool, and run:
```bash
python repost.py
```
(on macOS, run python3 instead of python)

### Step 2: Log In to Craigslist
When the tool starts:
1. A Chrome browser window will open
2. You'll be taken to the Craigslist login page
3. Manually log in to your Craigslist account
4. If there's a CAPTCHA, solve it manually
5. Wait for the tool to detect your successful login

### Step 3: Let It Work
The tool will automatically:
1. Find each of your posts using the IDs you provided
2. Extract all the content (title, price, description, images)
3. Delete the old post
4. Create a new post with the same content
5. Move to the next post

**Important:** Don't close the browser window or interfere with the process while it's running.

## Automated Scheduling (macOS)

You can set up automatic reposting using macOS Calendar and Automator to run the script at regular intervals.

### Step 1: Create an Automator Script

1. Open **Automator** (found in Applications > Utilities)
2. Choose **"New Document"** and select **"Application"**
3. In the search bar, type **"Run Shell Script"** and drag it to the workflow area
4. Set the shell to **"/bin/bash"**
5. Paste the following code into the script area:

```bash
#!/bin/bash
cd /path/to/your/craigslist-auto-reposter
source my_env/bin/activate
echo "$(date '+%a %b %-d, %Y, %-I:%M %p')" >> debug.log
python3 repost.py >> debug.log 2>&1
echo "=================================================================================================================" >> debug.log
cd -
```

**Important:** Replace `/path/to/your/craigslist-auto-reposter` with the actual path to your project folder.

6. Save the application as **"Craigslist Reposter.app"** (or any name you want)

### Step 2: Set Up Calendar Event

1. Open **Calendar** app
2. Create a new event
3. Set the event to repeat at your desired interval (e.g., daily, weekly)
4. In the event details, click **"Add Alert"**
5. Choose **"Custom"** and select **"Open File"**
6. Navigate to and select your **"Craigslist Reposter.app"** file
7. Set the alert to trigger at the time you want the script to run. You can also have the event repeat, for example daily.

**Note:** You will hear a sound each time when the script starts. This is to let you know that you have to log in. Everything else gets done automatically.

## Example Configuration

Here's a complete example of a `config.yml` file:

```yaml
email: "mybusiness@gmail.com"
city_url: "https://newyork.craigslist.org"

posts:
  - id: 7867090337
    category: computers
    area: Brooklyn
    title_slug: brooklyn-macbook-air-2020
    postal: 11204

  - id: 7867090338
    category: furniture
    area: Manhattan
    title_slug: my-large-closet-for-sale
    postal: 10001

  - id: 7867090339
    category: electronics
    area: Queens
    title_slug: electronic-keyboard-discount-prices
    postal: 11101
```
