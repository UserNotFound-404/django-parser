import time
from random import uniform, randint
import re

from celery.utils.log import get_task_logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .models import Image, Property
from .utils import parse_price


logger = get_task_logger(__name__)


def scrape_properties_task(min_price="5000000"):
    parsed_properties = {}

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    link = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93917&minPrice={min_price}"

    try:
        driver.get(link)
        WebDriverWait(driver, 50).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'l-searchResult'))
        )
        try:
            reject_cookies_button = driver.find_element(By.CSS_SELECTOR, '#onetrust-reject-all-handler')
            reject_cookies_button.click()
        except:
            logger.info("Cookies were not asked")

        properties = driver.find_elements(By.CSS_SELECTOR, '.l-searchResult')
        pages_amount = driver.find_element(By.CSS_SELECTOR, '[data-bind="text: total"]').text
        for page_number in range(int(pages_amount)):
            next_page_link = link + "&index=" + str(24 * (page_number + 1))
            for property in properties:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", property)

                    images_set = set()
                    price_text = property.find_element(By.CSS_SELECTOR, '.propertyCard-priceValue').text
                    price = parse_price(price_text)
                    try:
                        price_guidance = property.find_element(By.CLASS_NAME, 'propertyCard-priceQualifier').text
                    except:
                        price_guidance = "No Guidance"

                    address = property.find_element(By.CSS_SELECTOR, '.propertyCard-address').text
                    property_url = property.find_element(By.CSS_SELECTOR, '.propertyCard-details > a').get_attribute('href')
                    description = property.find_element(By.CSS_SELECTOR, '.propertyCard-description').text
                    phone_number = property.find_element(By.CSS_SELECTOR, '.propertyCard-contactsPhoneNumber').text
                    contact_info = property.find_element(By.CSS_SELECTOR, '.propertyCard-branchLogo > a').get_attribute('title')

                    property_information = property.find_element(By.CSS_SELECTOR, '.property-information')
                    property_type = property_information.find_element(By.CSS_SELECTOR, '.text').text

                    carousel = property.find_element(By.CSS_SELECTOR, '.swipe-wrap')

                    while True:
                        previous_set = images_set.copy()
                        next_button = property.find_element(By.CLASS_NAME, 'next-button')
                        images = carousel.find_elements(By.CSS_SELECTOR, '.propertyCard-img > img')
                        for image in images:
                            image_url = image.get_attribute('src')
                            images_set.add(image_url)
                        next_button.click()
                        time.sleep(round(uniform(0, 1), 2))
                        if len(images_set) == len(previous_set):
                            break

                    try:
                        bedrooms = property_information.find_element(By.CSS_SELECTOR,
                                                                     'span.no-svg-bed-icon.bed-icon.seperator > svg > title').get_attribute('textContent')
                        bedrooms_count = bedrooms.split()[0] if bedrooms else None
                    except Exception as e:
                        bedrooms_count = None

                    try:
                        bathrooms = property_information.find_element(By.CSS_SELECTOR,
                                                                      "span.no-svg-bathroom-icon.bathroom-icon.seperator > svg > title").get_attribute("textContent")
                        bathrooms_count = bathrooms.split()[0] if bathrooms else None
                    except Exception as e:
                        bathrooms_count = None
                    logger.info("Adding info about", address)
                    parsed_properties[property_url] = {
                            "address": address,
                            "price": price,
                            "price_guidance": price_guidance,
                            "short_description": description,
                            "property_type": property_type,
                            "bedrooms": bedrooms_count,
                            "bathrooms": bathrooms_count,
                            "phone_number": phone_number,
                            "contact_info": contact_info,
                            "images": [],
                    }
                    for image_url in images_set:
                        parsed_properties[property_url]["images"].append(image_url)

                except Exception as e:
                    logger.info("Error occurred", e)
            time.sleep(randint(0, 3))
            driver.get(next_page_link)
            WebDriverWait(driver, 50).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'l-searchResult'))
            )
            properties = driver.find_elements(By.CSS_SELECTOR, '.l-searchResult')

    except Exception as e:
        logger.info("Error occurred", e)

    finally:
        driver.quit()

    parsed_urls = set(parsed_properties.keys())
    db_urls = set(Property.objects.values_list("url", flat=True))

    urls_to_delete = db_urls - parsed_urls
    if urls_to_delete:
        Property.objects.filter(url__in=urls_to_delete).delete()
        logger.info(f"Deleted {len(urls_to_delete)} records.")

    urls_to_add = parsed_urls - db_urls
    new_properties = [
        Property(
            url=url,
            address=property_data["address"],
            price=property_data["price"],
            property_type=property_data["property_type"],
            bedrooms=property_data.get("bedrooms"),
            bathrooms=property_data.get("bathrooms"),
            phone_number=property_data.get("phone_number"),
            contact_info=property_data.get("contact_info"),
            short_description=property_data.get("short_description", ""),
            price_guidance=property_data.get("price_guidance", ""),
        )
        for url, property_data in parsed_properties.items()
        if url in urls_to_add
    ]
    Property.objects.bulk_create(new_properties)
    logger.info(f"Added {len(new_properties)} new records")

    images_to_create = []

    new_property_objects = Property.objects.filter(url__in=urls_to_add)
    property_url_to_instance = {prop.url: prop for prop in new_property_objects}

    for url, property_data in parsed_properties.items():
        if url in property_url_to_instance:
            property_instance = property_url_to_instance[url]
            for image_url in property_data.get("images", []):
                images_to_create.append(
                    Image(
                        property=property_instance,
                        image_url=image_url,
                        floorplan=False,
                    )
                )
    Image.objects.bulk_create(images_to_create)
    logger.info(f"Added {len(images_to_create)} images")


def scrape_additional_info(link):  # TODO: add description parsing
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(link)
        WebDriverWait(driver, 10)

        info_reel = driver.find_elements(By.CSS_SELECTOR, '#info-reel > div')

        size = None
        tenure = None

        for block in info_reel:
            title_block = block.find_element(By.TAG_NAME, "dt")
            value_block = block.find_element(By.TAG_NAME, "dd")
            if title_block and value_block:
                title = title_block.text
                if "SIZE" in title.upper():
                    size_elements = value_block.find_elements(By.TAG_NAME, 'p')
                    if size_elements:
                        size = [size.text for size in size_elements]
                if "TENURE" in title.upper():
                    tenure = value_block.find_element(By.TAG_NAME, 'p').text

        main_info_block = driver.find_element(By.CSS_SELECTOR, 'article[data-testid="primary-layout"]')
        floorplan_images = main_info_block.find_elements(By.CSS_SELECTOR, 'a[href*="floorplan"] > img')
        floorplan = []
        for image in floorplan_images:
            cleaned_url = re.sub(r"_max_\d+x\d+", "", image.get_attribute('src')).replace("/dir/", "/")
            floorplan.append(cleaned_url)

        property_record = Property.objects.get(url=link)
        property_record.size = ", ".join(size) if size else None
        property_record.tenure = tenure
        property_record.save()

        for image_url in floorplan:
            Image.objects.create(property=property_record, image_url=image_url, floorplan=True)

        logger.info(f"Updated property {link} with additional info.")
    except Exception as e:
        logger.info(f"ERROR - {e}")
    finally:
        driver.quit()


