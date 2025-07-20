import yaml
import time
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import json

CATEGORY_TO_ZBPOS = {
    "antiques": 0,
    "appliances": 1,
    "arts & crafts": 2,
    "atvs, utvs, snowmobiles": 3,
    "auto parts": 4,
    "auto wheels & tires": 5,
    "aviation": 6,
    "baby & kid stuff": 7,
    "barter": 8,
    "bicycle parts": 9,
    "bicycles": 10,
    "boat parts": 11,
    "boats": 12,
    "books & magazines": 13,
    "business/commercial": 14,
    "cars & trucks ($5)": 15,
    "cds / dvds / vhs": 16,
    "cell phones": 17,
    "clothing & accessories": 18,
    "collectibles": 19,
    "computer parts": 20,
    "computers": 21,
    "electronics": 22,
    "farm & garden": 23,
    "free stuff": 24,
    "furniture": 25,
    "garage & moving sales": 26,
    "general for sale": 27,
    "health and beauty": 28,
    "heavy equipment": 29,
    "household items": 30,
    "jewelry": 31,
    "materials": 32,
    "motorcycle parts": 33,
    "motorcycles/scooters ($5)": 34,
    "musical instruments": 35,
    "photo/video": 36,
    "rvs ($5)": 37,
    "sporting goods": 38,
    "tickets": 39,
    "tools": 40,
    "toys & games": 41,
    "trailers": 42,
    "video gaming": 43,
    "wanted": 44
}
CATEGORY_TO_SLUG = {
    "antiques": "atq",
    "appliances": "app",
    "arts+crafts": "art",
    "atv/utv/sno": "snw",
    "auto parts": "pts",
    "aviation": "avo",
    "baby+kid": "bab",
    "barter": "bar",
    "beauty+hlth": "hab",
    "bike parts": "bop",
    "bikes": "bik",
    "boat parts": "bpo",
    "boats": "boa",
    "books": "bks",
    "business": "bfs",
    "cars+trucks": "ctd",
    "cds/dvd/vhs": "emd",
    "cell phones": "mob",
    "clothes+acc": "clo",
    "collectibles": "clt",
    "computer parts": "sop",
    "computers": "sys",
    "electronics": "ele",
    "farm+garden": "grd",
    "free": "zip",
    "furniture": "fuo",
    "garage sale": "gms",
    "general": "for",
    "heavy equip": "hvo",
    "household": "hsh",
    "jewelry": "jwl",
    "materials": "mat",
    "motorcycle parts": "mpo",
    "motorcycles": "mcy",
    "music instr": "msg",
    "photo+video": "pho",
    "rvs+camp": "rvs",
    "sporting": "spo",
    "tickets": "tid",
    "tools": "tls",
    "toys+games": "tag",
    "trailers": "tro",
    "video gaming": "vgm",
    "wanted": "wan",
    "wheels+tires": "wto"
}

BOROUGH_TO_SLUG = {
    "manhattan": "mnh",
    "brooklyn": "brk",
    "queens": "que",
    "bronx": "brx",

    "staten island": "stn",
    "staten": "stn",

    "new jersey": "jsy",
    "jersey": "jsy",

    "long island": "lgi",
    "westchester": "wch",

    "fairfield co, CT": "fct",
    "fairfield": "fct",
}

DEFAULT_ZIP = "10001"

URL_LOGIN = "https://accounts.craigslist.org/login?rp=%2Flogin%2Fhome&rt=L"
URL_DEL_POST = "https://accounts.craigslist.org/login?rp=%2Flogin%2Fhome&rt=L"
URL_POST_AD = "https://post.craigslist.org/c"

# Load config
def loadConfig():
    with open("config.yml") as f:
        return yaml.safe_load(f)

config = loadConfig()
city_url = config["city_url"]
posts = config["posts"]
email = config["email"]

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

def login():
    driver.get(URL_LOGIN)
    print("Please log in manually in the browser window, including solving any captcha if present.")
    # Wait for the user to log in by checking for a post-login element
    try:
        # Wait until the account home page is loaded (look for a known element)
        WebDriverWait(driver, 600).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/logout']"))
        )
        print("DEBUG: Login detected, proceeding...")
    except Exception:
        print("ERROR: Timed out waiting for manual login.")
        raise

def extractPostData(post_url):
    res = requests.get(post_url)
    soup = BeautifulSoup(res.text, "html.parser")
    print(f"DEBUG: Fetching {post_url}")

    title_tag = soup.find("span", id="titletextonly")
    if not title_tag:
        raise Exception(f"Could not find title for post at {post_url}")
    title = title_tag.text.strip()

    price_tag = soup.find("span", class_="price")
    price = price_tag.text.strip().replace("$", "").replace(",", "") if price_tag else ""

    body_elem = soup.find("section", id="postingbody")
    if not body_elem:
        raise Exception(f"Could not find body for post at {post_url}")
    body = body_elem.get_text("\n").strip().replace("QR Code Link to This Post", "").strip()

    images = []
    # Find the <script> tag containing 'imgList'
    for script in soup.find_all("script"):
        if script.string and "imgList" in script.string:
            try:
                # Extract the JSON array from the JS assignment
                img_json = script.string.split("var imgList = ", 1)[1].split(";", 1)[0]
                img_list = json.loads(img_json)
                for img in img_list:
                    if "url" in img:
                        images.append(img["url"])
                print(f"DEBUG: Extracted {len(images)} images from imgList")
                print(f"DEBUG: {images}")
            except Exception as e:
                print(f"WARNING: Failed to parse imgList: {e}")
            break
    # Fallback: scrape <img> tags in the gallery
    if not images:
        for img_tag in soup.select("figure.iw img, div.swipe-wrap img"):
            img_url = img_tag.get("src")
            if img_url and img_url.startswith("http"):
                images.append(img_url)
        print(f"DEBUG: Fallback extracted {len(images)} images from <img> tags")
    return title, price, body, images

def delPost(post_id):
    print(f"DEBUG: delete_post({post_id})")
    driver.get(URL_DEL_POST)
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.manage.delete")))
        form = driver.find_element(By.CSS_SELECTOR, f"form.manage.delete[data-posting-id='{post_id}']")
        delete_button = form.find_element(By.CSS_SELECTOR, "input[type='submit'][value='delete']")
        delete_button.click()
        try:
            confirm_button = wait.until(EC.element_to_be_clickable((By.NAME, "go")))
            confirm_button.click()
        except Exception:
            pass
        print(f"DEBUG: Post {post_id} deleted.")
    except Exception as e:
        print(f"WARNING: Failed to delete post {post_id}: {e}")

def downloadImage(url):
    res = requests.get(url)
    filename = os.path.join("/tmp", os.path.basename(url.split('?')[0]))
    with open(filename, "wb") as f:
        f.write(res.content)
    return filename

def postAd(post, title, price, body, images):
    AREA_MAP = {
        'brk': 'brooklyn',
        'man': 'manhattan',
        'que': 'queens',
        'bx': 'bronx',
        'stn': 'staten island',
        'nj': 'new jersey',
        'li': 'long island',
        'wch': 'westchester',
        'ct': 'fairfield co, CT',
    }
    driver.get(URL_POST_AD)
    print(f"DEBUG: Loaded post URL, URL: {driver.current_url}")
    print(driver.page_source[:1000])

    done = False
    max_steps = 20
    steps = 0
    while not done and steps < max_steps:
        steps += 1
        time.sleep(2)
        page = driver.page_source.lower()
        url = driver.current_url
        print(f"DEBUG: Step {steps}, URL: {url}")

        # 1. City/area selection (dropdown)
        try:
            select = driver.find_element(By.TAG_NAME, "select")
            if select:
                print("DEBUG: Detected city/area selection screen")
                Select(select).select_by_visible_text("new york city")
                driver.find_element(By.NAME, "go").click()
                continue
        except Exception:
            pass
        # 2. Subarea/borough selection (radio)
        try:
            radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            labels = [r.find_element(By.XPATH, "..") for r in radios]
            label_texts = [l.text.strip().lower() for l in labels]
            area_key = post.get('area', '').lower()
            area_label = AREA_MAP.get(area_key, area_key).lower()
            if any(area_label == t for t in label_texts):
                print("DEBUG: Detected subarea/borough selection screen")
                for radio, label in zip(radios, label_texts):
                    if label == area_label:
                        radio.click()
                        break
                else:
                    radios[0].click()
                driver.find_element(By.NAME, "go").click()
                continue
        except Exception:
            pass
        # 3. For sale by owner/dealer (radio)
        try:
            if "what type of posting is this" in driver.page_source.lower():
                radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                if len(radios) >= 6:
                    radios[5].click()
                    print("DEBUG: Clicked 5th radio button (for sale by owner)")
                elif radios:
                    radios[0].click()
                    print("DEBUG: Fewer than 5 radios, clicked first available radio as fallback")
                driver.find_element(By.NAME, "go").click()
                continue
        except Exception:
            pass
        # 4. Category selection (radio)
        try:
            if "please choose a category" in driver.page_source.lower():
                radios = driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
                if len(radios) > CATEGORY_TO_ZBPOS[post['category']]:
                    #radios[21].click()
                    radios[CATEGORY_TO_ZBPOS[post['category']]].click()
                    print("DEBUG: Clicked 21st radio button on category page")
                elif radios:
                    radios[0].click()
                    print("DEBUG: Fewer than 21 radios, clicked first available radio as fallback")
                driver.find_element(By.NAME, "go").click()
                continue
        except Exception:
            pass
        # 5. Post details (title, price, body fields)
        try:
            title_input = driver.find_element(By.NAME, "PostingTitle")
            if title_input:
                print("DEBUG: Detected post details screen")
                title_input.clear()
                title_input.send_keys(title)
                # Fill ZIP code in any possible field
                zip_filled = False
                try:
                    zip_input = driver.find_element(By.NAME, "postal")
                    zip_input.clear()
                    zip_input.send_keys(str(post.get("postal", DEFAULT_ZIP)))
                    print("DEBUG: Filled ZIP code in 'postal' field")
                    zip_filled = True
                except Exception:
                    pass
                if not zip_filled:
                    try:
                        zip_input = driver.find_element(By.NAME, "postal_code")
                        zip_input.clear()
                        zip_input.send_keys(str(post.get("postal", "10001")))
                        print("DEBUG: Filled ZIP code in 'postal_code' field")
                        zip_filled = True
                    except Exception:
                        print("DEBUG: No ZIP/postal field found to fill")
                # Fill email field if present
                try:
                    email_input = driver.find_element(By.NAME, "FromEMail")
                    email_input.clear()
                    email_input.send_keys(email)
                    print("DEBUG: Filled email in 'FromEMail' field")
                except Exception:
                    print("DEBUG: No email field found to fill")
                driver.find_element(By.NAME, "price").send_keys(str(price))
                driver.find_element(By.NAME, "PostingBody").send_keys(body)
                try:
                    driver.find_element(By.NAME, "contact_phone_ok").click()
                    driver.find_element(By.NAME, "contact_text_ok").click()
                except Exception:
                    pass
                driver.find_element(By.NAME, "go").click()
                continue
        except Exception:
            pass
        # 5.5. Re-use data screen
        try:
            if "re-use selected data from your previous posting" in driver.page_source.lower():
                buttons = driver.find_elements(By.TAG_NAME, "button")
                clicked = False
                for btn in buttons:
                    if btn.text.strip().lower() == "skip":
                        btn.click()
                        print("DEBUG: Clicked 'skip' button on re-use data screen")
                        clicked = True
                        break
                if not clicked:
                    print("DEBUG: Could not find 'skip' button on re-use data screen")
                continue
        except Exception:
            pass
        # 6. Location (cross streets, etc.)
        try:
            xstreet0 = driver.find_element(By.NAME, "xstreet0")
            if xstreet0:
                print("DEBUG: Detected location screen")
                xstreet0.send_keys(post.get("location", ""))
                driver.find_element(By.NAME, "go").click()
                continue
        except Exception:
            pass
        # 6.5. Map screen (geoverify)
        try:
            leaflet_form = driver.find_element(By.ID, "leafletForm")
            zip_input = None
            try:
                zip_input = driver.find_element(By.NAME, "postal")
            except Exception:
                try:
                    zip_input = driver.find_element(By.NAME, "postal_code")
                except Exception:
                    pass
            if leaflet_form and zip_input:
                print("DEBUG: Detected map/geoverify screen")
                zip_input.clear()
                zip_input.send_keys(str(post.get("postal", DEFAULT_ZIP)))
                # Optionally fill cross streets/city if needed
                try:
                    city_input = driver.find_element(By.NAME, "city")
                    city_input.clear()
                    city_input.send_keys("New York")
                except Exception:
                    pass
                # Click the 'continue' button (not 'find')
                try:
                    submit_buttons = leaflet_form.find_elements(By.CSS_SELECTOR, "button[type='submit'], .continue")
                    clicked = False
                    for btn in submit_buttons:
                        btn_text = btn.text.strip().lower()
                        if btn_text == "continue":
                            btn.click()
                            clicked = True
                            print("DEBUG: Clicked 'continue' button on map screen")
                            break
                    if not clicked:
                        print("ERROR: Could not find 'continue' button on map screen")
                except Exception:
                    print("ERROR: Exception while trying to click 'continue' button on map screen")
                continue
        except Exception:
            pass
        # 7. Image upload
        try:
            if "images of a maximum 24" in driver.page_source.lower():
                print("DEBUG: Detected image upload screen (by text)")
                file_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"][multiple]')
                if file_inputs:
                    file_input = file_inputs[0]
                    local_images = []
                    for img_url in images[:8]:
                        local_path = downloadImage(img_url)
                        local_images.append(local_path)
                    for img_path in local_images:
                        file_input.send_keys(img_path)
                        print(f"DEBUG: Uploaded image {img_path}")
                        time.sleep(2)
                else:
                    print("DEBUG: No file input found on image upload screen")
                # Click the 'done with images' button to proceed
                time.sleep(2)
                try:
                    done_btn = driver.find_element(By.ID, "doneWithImages")
                    done_btn.click()
                    print("DEBUG: Clicked 'done with images' button")
                except Exception:
                    print("DEBUG: Could not find 'done with images' button, trying to submit form")
                    forms = driver.find_elements(By.CSS_SELECTOR, "form[action*='editimage']")
                    if forms:
                        forms[0].submit()
                continue
        except Exception:
            pass
        # 8. Publish/confirm
        try:
            go_btn = driver.find_element(By.NAME, "go")
            if go_btn:
                print("DEBUG: Detected publish/confirm screen")
                go_btn.click()
                continue
        except Exception:
            pass
        try:
            publish_btn = driver.find_element(By.CSS_SELECTOR, "input[value='publish']")
            if publish_btn:
                print("DEBUG: Detected publish button")
                publish_btn.click()
                continue
        except Exception:
            pass
        # 9. Check for success
        if "thanks for posting!" in page.lower() or "your posting can be seen at" in page:
            print("DEBUG: Detected success screen. Posting complete!")
            done = True
            break
        # 10. Fallback: unknown screen
        print("DEBUG: Unknown screen, dumping page source")
        print(driver.page_source[:5000])
        time.sleep(2)
        # Optionally, break or continue to avoid infinite loop
        break
    if not done:
        print("ERROR: Failed to complete posting flow. See debug output above.")

try:
    login()
    for post in posts:
        try:
            # convert user-friendly string to slug (ex: Musical instruments -> msg, Brooklyn -> brk)
            category_slug = CATEGORY_TO_SLUG[post['category'].lower()]
            borough_slug = BOROUGH_TO_SLUG[post['area'].lower()]

            post_url = f"{city_url}/{borough_slug}/{category_slug}/d/{post['title_slug']}/{post['id']}.html"
            title, price, body, images = extractPostData(post_url)
            time.sleep(1)
            delPost(post['id'])
            postAd(post, title, price, body, images)
        except Exception as e:
            print(f"ERROR: Failed to process post {post.get('id', 'unknown')}: {e}")
            continue
finally:
    driver.quit()
