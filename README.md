# Craigslist Auto-Reposter

Tool that automatically reposts your Craigslist listings to keep them fresh and visible to potential customers. Perfect for small businesses, real estate agents, and anyone who regularly posts on Craigslist. Note that this script may break at any moment, if Craigslist updates their UI/layout.

## What This Tool Does

- **Automatically reposts your listings**: Keeps your ads at the top of search results
- **Preserves all content**: Maintains your original title, description, price, and images
- **Handles multiple posts**: Process multiple listings in one session
- **Smart URL handling**: Automatically finds your posts using just the post ID

## Prerequisites

1. **Python 3.7 or higher** installed on your computer
2. **Google Chrome browser** installed
3. **A Craigslist account** (free to create at [accounts.craigslist.org](https://accounts.craigslist.org))

## Installation

### Step 1: Download the Tool
Download all the files in this folder to your computer.

### Step 2: Install Required Software
Open your terminal/command prompt and run:

```bash
pip install selenium beautifulsoup4 requests pyyaml
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
    postal: 11201
```

**What each field means:**
- `email`: Your email address (used for contact information)
- `city_url`: Your local Craigslist city (e.g., "https://newyork.craigslist.org" for NYC)
- `posts`: List of your posts to repost
  - `id`: The post ID from your Craigslist listing URL
  - `category`: The category your post is in (see categories list below)
  - `area`: Your local area/borough (see areas list below)
  - `postal`: Your ZIP code

### Step 2: Find Your Post Information

**To find your post ID:**
1. Go to your Craigslist listing
2. Look at the URL: `https://newyork.craigslist.org/brk/sys/d/macbook-air-2020/1234567890.html`
3. The number at the end (1234567890) is your post ID

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

### Step 3: Test Your Configuration
Before running the full tool, test your setup:

```bash
python test_title_slug.py
```

This will verify that the tool can find your posts correctly.

## How to Use

### Step 1: Run the Tool
Open your terminal/command prompt, navigate to the folder with the tool, and run:

```bash
python repost.py
```

### Step 2: Log In to Craigslist
When the tool starts:
1. A Chrome browser window will open
2. You'll be taken to the Craigslist login page
3. **Manually log in** to your Craigslist account
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

## What Happens During Reposting

For each post, the tool will:

1. **Find your post** using the ID and category information
2. **Extract content** including:
   - Title
   - Price
   - Description
   - All images
3. **Delete the old post** from your account
4. **Create a new post** with identical content
5. **Upload images** (up to 8 images per post)
6. **Publish the new post**

## Troubleshooting

### Common Issues and Solutions

**"Could not derive title_slug for post"**
- Make sure your post ID is correct
- Verify the category and area match your actual post
- Check that your post is still active on Craigslist

**"Failed to process post"**
- Your post may have been deleted or expired
- Check that you're logged into the correct Craigslist account
- Verify your internet connection

**Browser closes unexpectedly**
- Make sure you have the latest version of Chrome
- Update ChromeDriver to match your Chrome version
- Check that no antivirus software is blocking the tool

**"Timed out waiting for manual login"**
- Make sure you completed the login process
- Check for any CAPTCHA that needs to be solved
- Try running the tool again

### Getting Help

If you encounter issues:
1. Check that all your configuration is correct
2. Make sure your posts are still active on Craigslist
3. Verify your internet connection is stable
4. Try running the test script first: `python test_title_slug.py`

## Best Practices

1. **Keep backups**: Save your original post content in case you need to recreate manually
2. **Schedule regular reposting**: Run this tool periodically to keep your listings fresh
3. **Monitor your posts**: Check that reposting was successful
4. **Follow Craigslist rules**: Don't repost too frequently to avoid being flagged

### What the Tool Does NOT Do

- It doesn't create new content
- It doesn't change your prices or descriptions
- It doesn't post to multiple cities automatically
- It doesn't bypass Craigslist's posting limits

## Example Configuration

Here's a complete example of a `config.yml` file:

```yaml
email: "mybusiness@gmail.com"
city_url: "https://newyork.craigslist.org"

posts:
  - id: 7867090337
    category: computers
    area: Brooklyn
    postal: 11204

  - id: 7867090338
    category: furniture
    area: Manhattan
    postal: 10001

  - id: 7867090339
    category: electronics
    area: Queens
    postal: 11101
```
