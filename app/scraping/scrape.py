import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to ChromeDriver executable
chrome_driver_path = 'chromedriver-linux64/chromedriver'

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode

# Initialize the WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL of the webpage to scrape
nutritonal_data_url = os.environ.get('NUTRITONAL_DATA_URL')
food_slug = "paneer"
url = f"{nutritonal_data_url}{food_slug}"  # Replace with the actual URL

# Load the webpage
driver.get(url)
print("\nFetched URL!")

# Define function to extract text with specific wait


def extract_text(wait, locator):
    element = wait.until(EC.visibility_of_element_located(locator))
    return element.text.strip() if element else "Data not available"


print("\nWaiting for the element")
# Wait for the nutrition info to be present
wait = WebDriverWait(driver, 2)
nutrition_info = wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, 'nf')))
print("\nWaiting for the element complete")

print("\nExtracting information")
# Define locators for required macros
macros_locators = {
    'single_serving_size': (By.CLASS_NAME, 'nf-serving-unit-name'),
    'calories': (By.CSS_SELECTOR, 'span.nf-pr[itemprop="calories"]'),
    'total_fat': (By.XPATH, '//span[contains(text(), "Total Fat")]/following-sibling::span'),
    'total_carbohydrates': (By.XPATH, '//span[contains(text(), "Total Carbohydrates")]/following-sibling::span'),
    'dietary_fiber': (By.XPATH, '//span[contains(text(), "Dietary Fiber")]/following-sibling::span'),
    'protein': (By.XPATH, '//span[contains(text(), "Protein")]/following-sibling::span')
}

# Extract all the required macros
macros_data = {}
for key, locator in macros_locators.items():
    macros_data[key] = extract_text(wait, locator)

print("\nExtracting information finished")

# Extract serving size
single_serving_weight = float(
    macros_data['single_serving_size'].split('(')[-1].split('g')[0])

# Calculate the ratio to convert to 100 grams
ratio_per_100g = 100 / single_serving_weight

# Calculate values per 100 grams
macros_100g = {}
for key, value in macros_data.items():
    if key != 'single_serving_size' and 'g' in value:
        macros_100g[f"{key}_100g"] = round(
            float(value.split('g')[0]) * ratio_per_100g, 1)
    else:
        try:
            float_value = float(value)
            # If convertible, add it to the macros_100g dictionary
            macros_100g[key] = float_value
        except ValueError:
            # If not convertible, keep the value unchanged
            macros_100g[key] = value

# Preserve serving size
macros_100g['single_serving_size'] = single_serving_weight

# Print the processed data
print(f"\nSingle serving size: {single_serving_weight}")
print("\nMacros per 100g:")
print(macros_100g)

# Close the WebDriver
driver.quit()


# selenium timeout error, need to handled:

# raise TimeoutException(message, screen, stacktrace)
# selenium.common.exceptions.TimeoutException: Message:


# fetching data workflow
# 1. check if the database has the macros data, if yes return it
# 2. if there is no macros data in db, scrape the macros data, save it db and return the same
# 3. if there is no macros data on the web to scrape, use llm knowledge to predict (better than no data)

# probably cache the frequently queried info
