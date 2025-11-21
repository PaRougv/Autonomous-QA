from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize the Chrome driver
driver = webdriver.Chrome()

try:
    # Navigate to the checkout page
    driver.get("http://127.0.0.1:5500/assets/checkout.html")

    # Step 1: Add items to the cart (only once each!)
    add_to_cart_buttons = driver.find_elements(By.CLASS_NAME, "add-to-cart")

    # Click only the first 3 product buttons
    for button in add_to_cart_buttons[:3]:
        button.click()

    time.sleep(1)  # allow JS UI update

    # Getting total BEFORE discount
    total_before = float(driver.find_element(By.ID, "total-price").text)

    # Step 2: Enter discount code
    discount_code_input = driver.find_element(By.ID, "discount-code")
    discount_code_input.clear()
    discount_code_input.send_keys("SAVE15")

    # Trigger apply (input change event)
    discount_code_input.send_keys("")

    # Wait for total to change
    def total_changed(driver):
        try:
            new_total = float(driver.find_element(By.ID, "total-price").text)
            return new_total != total_before
        except:
            return False

    WebDriverWait(driver, 10).until(total_changed)

    # Step 3: Validate new total
    total_after = float(driver.find_element(By.ID, "total-price").text)

    expected_total = 110 * 0.85  # 15% discount

    assert abs(total_after - expected_total) < 0.01, (
        f"Expected total: {expected_total}, got: {total_after}"
    )

    print("🎉 Test Passed: SAVE15 applied correctly")

finally:
    driver.quit()
