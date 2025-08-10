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
import re

# Should be True in production!
DO_DELETE = True

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
	"arts & crafts": "art",
	"atvs, utvs, snowmobiles": "snw",
	"auto parts": "pts",
	"auto wheels & tires": "wto",
	"aviation": "avo",
	"baby & kid stuff": "bab",
	"barter": "bar",
	"books & magazines": "bks",
	"business/commercial": "bfs",
	"cars & trucks ($5)": "ctd",
	"cds / dvds / vhs": "emd",
	"cell phones": "mob",
	"clothing & accessories": "clo",
	"collectibles": "clt",
	"computer parts": "sop",
	"computers": "sys",
	"electronics": "ele",
	"farm & garden": "grd",
	"free stuff": "zip",
	"furniture": "fuo",
	"garage & moving sales": "gms",
	"general for sale": "for",
	"health and beauty": "hab",
	"heavy equipment": "hvo",
	"household items": "hsh",
	"jewelry": "jwl",
	"materials": "mat",
	"motorcycle parts": "mpo",
	"motorcycles/scooters ($5)": "mcy",
	"musical instruments": "msg",
	"photo/video": "pho",
	"rvs ($5)": "rvs",
	"sporting goods": "spo",
	"tickets": "tid",
	"tools": "tls",
	"toys & games": "tag",
	"trailers": "tro",
	"video gaming": "vgm",
	"wanted": "wan",
	"bicycles": "bik",
	"bicycle parts": "bop",
	"boats": "boa",
	"boat parts": "bpo"
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

CONFIG_YAML = "config.yml"

def loadConfig():
	with open(CONFIG_YAML) as f:
		return yaml.safe_load(f)

config = loadConfig()
cityURL = config["city_url"]
posts = config["posts"]
email = config["email"]

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

def extractPostIdFromHTML(html):
	soup = BeautifulSoup(html, 'html.parser')

	htmlLower = html.lower()
	if "view your post at" in htmlLower:
		print("DEBUG: Found 'view your post at' text in HTML")
		# Find all <a> tags and find the one that comes after "View your post at"
		aTags = soup.find_all("a")
		for aTag in aTags:
			href = aTag.get('href', '')
			# Check if this href contains post ID
			if re.search(r'/(\d+)\.html', href):
				parent_text = aTag.parent.get_text().lower() if aTag.parent else ""
				if "view your post at" in parent_text:
					print(f"DEBUG: Found matching a_tag = {aTag}")
					print(f"DEBUG: href = {href}")
					match = re.search(r'/(\d+)\.html', href)
					if match:
						post_id = match.group(1)
						print(f"DEBUG: Extracted post ID: {post_id}")
						return post_id
	else:
		print(f"DEBUG: Could not find 'view your post at' text in HTML")
		print(f"DUMP: HTML snippet: {html[:1000]}")
	return ""

# id_pairs: List of (oldId, newId) pairs as strings
def updateConfig(idPairs):
	nUpdated = 0
	with open(CONFIG_YAML, 'r') as f:
		config = yaml.safe_load(f)

	# Make a mapping for fast lookup
	idMap = {old: new for old, new in idPairs}

	for post in config.get("posts", []):
		strPostId = str(post.get("id"))
		if strPostId in idMap:
			post["id"] = idMap[strPostId]
			nUpdated += 1

	# Manually construct YAML with unquoted IDs
	yamlLines = []
	yamlLines.append(f"city_url: {config['city_url']}")
	yamlLines.append(f"email: {config['email']}")
	yamlLines.append("posts:")

	for post in config.get("posts", []):
		yamlLines.append("- id: " + str(post["id"]))  # Unquoted ID
		yamlLines.append(f"  title_slug: {post['title_slug']}")
		yamlLines.append(f"  category: {post['category']}")
		yamlLines.append(f"  area: {post['area']}")
		yamlLines.append(f"  postal: {post['postal']}")

	with open(CONFIG_YAML, 'w') as f:
		f.write("\n".join(yamlLines) + "\n")

	if nUpdated > 0:
		print(f"✅SUCCESS: {CONFIG_YAML} updated successfully: {nUpdated} IDs updated.")
	else:
		print(f"DEBUG: Did not update {CONFIG_YAML}.")

def login():
	driver.get(URL_LOGIN)
	print("Waiting for user to log in manually in the browser window, including solving any captcha if present...")
	try:
		# Wait until the account home page is loaded (look for a known element) (600 sec = 10 min)
		WebDriverWait(driver, 600).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/logout']"))
		)
		print("DEBUG: Login detected, proceeding...")
	except Exception:
		print("ERROR: Timed out waiting for manual login.")
		raise

def extractPostData(postURL):
	res = requests.get(postURL)
	soup = BeautifulSoup(res.text, "html.parser")
	print(f"DEBUG: Fetching {postURL}")

	titleTag = soup.find("span", id="titletextonly")
	if not titleTag:
		raise Exception(f"Could not find title for post at {postURL}")
	title = titleTag.text.strip()
	print(f"DEBUG: Got title {title}")

	priceTag = soup.find("span", class_="price")
	price = priceTag.text.strip().replace("$", "").replace(",", "") if priceTag else ""
	print(f"DEBUG: Got price ${price}")

	bodyElem = soup.find("section", id="postingbody")
	if not bodyElem:
		raise Exception(f"Could not find body for post at {postURL}")
	body = bodyElem.get_text("\n").strip().replace("QR Code Link to This Post", "").strip()
	print(f"DEBUG: Got body text starting w/:\t{body[0:60]}...")

	try:
		conditionElem = soup.find("span", class_="valu")
		condition = conditionElem.get_text("\n").strip() # Condition of the item (new, used, etc.)
		print(f"DEBUG: Got item condition {condition}")
	except Exception:
		condition = ""
		print(f"DEBUG: No condition provided")
		pass # There may not be a condition, skip

	images = []
	# Find the <script> tag containing 'imgList'
	for script in soup.find_all("script"):
		if script.string and "imgList" in script.string:
			try:
				# Extract the JSON array from the JS assignment
				imgJSON = script.string.split("var imgList = ", 1)[1].split(";", 1)[0]
				imgList = json.loads(imgJSON)
				for img in imgList:
					if "url" in img:
						images.append(img["url"])
				print(f"DEBUG: Extracted {len(images)} images from imgList")
				print(f"DEBUG: {images}")
			except Exception as e:
				print(f"WARNING: Failed to parse imgList: {e}")
			break
	# Fallback: scrape <img> tags in the gallery
	if not images:
		for imgTag in soup.select("figure.iw img, div.swipe-wrap img"):
			imgURL = imgTag.get("src")
			if imgURL and imgURL.startswith("http"):
				images.append(imgURL)
		print(f"DEBUG: Fallback extracted {len(images)} images from <img> tags")
	return title, price, body, images, condition

def delPost(postId):
	print(f"DEBUG: delPost({postId})")
	driver.get(URL_DEL_POST)
	wait = WebDriverWait(driver, 10)
	try:
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.manage.delete")))
		form = driver.find_element(By.CSS_SELECTOR, f"form.manage.delete[data-posting-id='{postId}']")
		delete_button = form.find_element(By.CSS_SELECTOR, "input[type='submit'][value='delete']")
		delete_button.click()
		try:
			confirm_button = wait.until(EC.element_to_be_clickable((By.NAME, "go")))
			# Don't want to undo the delete
			if confirm_button.text == "Undelete this Posting":
				return
			confirm_button.click()
		except Exception:
			pass
		print(f"DEBUG: Post {postId} deleted.")
	except Exception as e:
		print(f"WARNING: Failed to delete post {postId}: {e}")

def downloadImage(url):
	res = requests.get(url)
	filename = os.path.join("/tmp", os.path.basename(url.split('?')[0]))
	with open(filename, "wb") as f:
		f.write(res.content)
	return filename

# postAd: return ID of ad posted as string or "" on failure
def postAd(post, title, price, body, images, condition):
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
	CONDITION_MAP = {
		"": 3,
		"new": 4,
		"like new": 5,
		"excellent": 6,
		"good": 7,
		"fair": 8,
		"salvage": 9
	}

	driver.get(URL_POST_AD)
	if "/manage/" in driver.current_url:
		print(f"ERROR: SHOULD NOT BE ON MANAGE PAGE WHEN MAKING NEW POST!!!!!!!!!!")
		print(f"DEBUG: {driver.current_url}")
		x = input("")

	print(f"DEBUG: Loaded post URL, URL: {driver.current_url}") # why is this the manage page?
	print(driver.page_source[:1000])

	done = False
	maxSteps = 20
	steps = 0
	while not done and steps < maxSteps:
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
			labelTexts = [l.text.strip().lower() for l in labels]
			areaKey = post.get('area', '').lower()
			areaLabel = AREA_MAP.get(areaKey, areaKey).lower()
			if any(areaLabel == t for t in labelTexts):
				print("DEBUG: Detected subarea/borough selection screen")
				for radio, label in zip(radios, labelTexts):
					if label == areaLabel:
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
					radios[5].click() # MAGIC NUMBER: but this is unlikely to change
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
				radioZbPos = CATEGORY_TO_ZBPOS[post['category']]
				if len(radios) > radioZbPos:
					radios[radioZbPos].click()
					print(f"DEBUG: Clicked radio {radioZbPos+1} (one-based) button on category page corresponding to {post['category']}")
				elif radios:
					radios[0].click()
					print(f"DEBUG: Fewer than {radioZbPos} radios, clicked first available radio as fallback")
				driver.find_element(By.NAME, "go").click()
				continue
		except Exception:
			pass
		# 5. Post details (title, price, body fields, condition)
		try:
			titleInput = driver.find_element(By.NAME, "PostingTitle")
			if titleInput:
				print("DEBUG: Detected post details screen")
				titleInput.clear()
				titleInput.send_keys(title)
				# Fill ZIP code in any possible field
				isZipFilled = False
				try:
					zipInput = driver.find_element(By.NAME, "postal")
					zipInput.clear()
					zipInput.send_keys(str(post.get("postal", DEFAULT_ZIP)))
					print("DEBUG: Filled ZIP code in 'postal' field")
					isZipFilled = True
				except Exception:
					pass
				if not isZipFilled:
					try:
						zipInput = driver.find_element(By.NAME, "postal_code")
						zipInput.clear()
						zipInput.send_keys(str(post.get("postal", DEFAULT_ZIP)))
						print("DEBUG: Filled ZIP code in 'postal_code' field")
						isZipFilled = True
					except Exception:
						print("DEBUG: No ZIP/postal field found to fill")
				# Fill email field if present
				try:
					emailInput = driver.find_element(By.NAME, "FromEMail")
					emailInput.clear()
					emailInput.send_keys(email)
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

				# Fill condition (used, new, etc.) field if present
				if condition == "":
					print(f"DEBUG: No condition provided, so field won't be filled")
				else:
					print(f"DEBUG: Condition = {condition}")
					try:
						ariaId = f"ui-id-{CONDITION_MAP[condition]}"

						dropdownBtn = wait.until(EC.element_to_be_clickable((By.ID, "ui-id-1-button")))
						dropdownBtn.click()

						# Wait for menu to appear
						wait.until(EC.visibility_of_element_located((By.ID, "ui-id-1-menu")))

						# Click the correct option
						liOption = wait.until(EC.element_to_be_clickable((By.ID, ariaId)))
						liOption.click()
						print("DEBUG: Selected condition:", condition)
					except Exception as e:
						print(f"ERROR: Problem with condition: {e}")
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
			leafletForm = driver.find_element(By.ID, "leafletForm")
			zipInput = None
			try:
				zipInput = driver.find_element(By.NAME, "postal")
			except Exception:
				try:
					zipInput = driver.find_element(By.NAME, "postal_code")
				except Exception:
					pass
			if leafletForm and zipInput:
				print("DEBUG: Detected map/geoverify screen")
				zipInput.clear()
				zipInput.send_keys(str(post.get("postal", DEFAULT_ZIP)))
				# Optionally fill cross streets/city if needed
				try:
					cityInput = driver.find_element(By.NAME, "city")
					cityInput.clear()
					cityInput.send_keys("New York")
				except Exception:
					pass
				# Click the 'continue' button (not 'find')
				try:
					submitButtons = leafletForm.find_elements(By.CSS_SELECTOR, "button[type='submit'], .continue")
					clicked = False
					for btn in submitButtons:
						btnText = btn.text.strip().lower()
						if btnText == "continue":
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
				fileInputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"][multiple]')
				if fileInputs:
					fileInput = fileInputs[0]
					localImages = []
					for imgURL in images[:8]:
						localPath = downloadImage(imgURL)
						localImages.append(localPath)
					for imgPath in localImages:
						fileInput.send_keys(imgPath)
						print(f"DEBUG: Uploaded image {imgPath}")
						time.sleep(2)
				else:
					print("DEBUG: No file input found on image upload screen")
				# Click the 'done with images' button to proceed
				time.sleep(2)
				try:
					doneBtn = driver.find_element(By.ID, "doneWithImages")
					doneBtn.click()
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
			done = True
			retval = extractPostIdFromHTML(page)
			print("✅SUCCESS: Detected success screen. Posting complete")
			print(f"DEBUG: Page = {page}")
			print(f"DEBUG: retval = {retval}")
			return retval
		# 10. Fallback: unknown screen
		print("DEBUG: Unknown screen, dumping page source")
		print(driver.page_source[:5000])
		time.sleep(2)
		break
	if not done:
		print("ERROR: Failed to complete posting flow. See debug output above.")
	return ""

idPairs = []
try:
	login()
	print(f"DEBUG: Num of posts = {len(posts)}")

	for post in posts:
		try:
			# convert user-friendly string to slug (ex: Musical instruments -> msg, Brooklyn -> brk)
			categorySlug = CATEGORY_TO_SLUG[post['category'].lower()]
			boroughSlug = BOROUGH_TO_SLUG[post['area'].lower()]
			print(f"DEBUG: category_slug = {categorySlug}")
			print(f"DEBUG: borough_slug = {boroughSlug}")

			post_url = f"{cityURL}/{boroughSlug}/{categorySlug}/d/{post['title_slug']}/{post['id']}.html"
			title, price, body, images, condition = extractPostData(post_url)
			time.sleep(1)
			if DO_DELETE:
				delPost(post['id'])
			oldId = str(post['id'])
			time.sleep(2)
			newId = postAd(post, title, price, body, images, condition)
			if newId != "":
				idPairs.append((oldId, newId))
			else:
				print(f"ERROR: Post {oldId} failed to repost. Will leave config as-is for this post.")
		except Exception as e:
			print(f"ERROR: Failed to process post {post.get('id', 'unknown')}: {e}")
			continue

	print(f"DEBUG: Updating {CONFIG_YAML} with new post IDs:")
	print(f"DEBUG: idPairs = {idPairs}")
	updateConfig(idPairs)
finally:
	driver.quit()
