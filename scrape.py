import time
import getpass
from pathlib import Path
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver import Chrome

# All file types we are interested in keeping. Extend to suit your needs.
accepted_suffixes = ["pdf", "ppt", "pptx", "doc", "docx"]

def download_file(element, path):
	# replace / with - to have a somewhat safe path
	safe_path = [f.replace("/", "-") for f in path]
	path_str = "output/" + "/".join(path[:-1])

	# Create dirs if not already present
	Path(path_str).mkdir(parents=True, exist_ok=True)

	file_path = path_str + "/" + path[-1]
	subprocess.run(["wget", "--load-cookies", "cookie.txt", "-O", file_path, element.get_attribute("href")])

	print(path_str)

def visit_item(driver, url, path):
	driver.get(url)

	item_name = driver.find_element(By.ID, "pageTitleText").text

	directory_urls = []

	for content in driver.find_elements_by_xpath("//ul[@id='content_listContainer']/li"):
		titles = content.find_elements_by_xpath("div/h3//span[@style='color:#000000;']")
		if not titles:
			continue
		title = titles[0].text

		attachments = content.find_elements_by_xpath(".//a")
		for a in attachments:
			file = a.text.strip()
			for suf in accepted_suffixes:
				if file.endswith(suf):
					download_file(a, path + [item_name, title, file])

		# detect directory using img alt
		if content.find_elements_by_xpath(".//img[@alt='Content Folder']"):
			href = titles[0].find_element_by_xpath("..").get_attribute("href")

			directory_urls.append(href)

	# recursively follow directories
	for url in directory_urls:
			visit_item(driver, url, path + [item_name])


	driver.back()

def visit_course(driver, course_name):
	course_menu = driver.find_element(By.ID, "courseMenuPalette_contents")

	items = [c.get_attribute("href") for c in course_menu.find_elements(By.TAG_NAME, "a")]

	for url in items:
		visit_item(driver, url, [course_name])

with Chrome() as driver:
	driver.get("https://blackboard.utwente.nl");

	print("Username:", end="")
	driver.find_element(By.ID, "user_id").send_keys(input())
	driver.find_element(By.ID, "password").send_keys(getpass.getpass())

	driver.find_element(By.ID, "entry-login").click()

	# List of courses doesn't load immediatly
	course_ul = WebDriverWait(driver, 2).until(lambda d: d.find_element(By.CLASS_NAME, "courseListing"))

	# After login, we save the cookies with the session id to a file to be used by wget later
	cookiefile = ""
	for c in driver.get_cookies():
		line = "{}\tFALSE\t{}\tFALSE\t{}\t{}\t{}\n".format(c["domain"], c["path"], c.get("expiry", "0"), c["name"], c["value"])
		cookiefile += line

	with open("cookie.txt", "w") as f:
		f.write(cookiefile)

	courses = [(c.text, c.get_attribute("href")) for c in course_ul.find_elements(By.TAG_NAME, "a")]

	for (name, url) in courses:
		print(name)
		driver.get(url)
		visit_course(driver, name)
		driver.back()

	driver.quit()