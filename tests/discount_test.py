from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

try:
    driver.get("http://127.0.0.1:5500/assets/checkout.html")
    add_to_cart_buttons = driver.find_elements(By.CLASS_NAME, "add-to-cart")
    for button in add_to_cart_buttons[:3]:
        button.click()

    time.sleep(1)
    total_before = float(driver.find_element(By.ID, "total-price").text)

    discount_code_input = driver.find_element(By.ID, "discount-code")
    discount_code_input.clear()
    discount_code_input.send_keys("SAVE15")

    discount_code_input.send_keys("")

    def total_changed(driver):
        try:
            new_total = float(driver.find_element(By.ID, "total-price").text)
            return new_total != total_before
        except:
            return False

    WebDriverWait(driver, 10).until(total_changed)

    total_after = float(driver.find_element(By.ID, "total-price").text)

    expected_total = 110 * 0.85  # 15% discount

    assert abs(total_after - expected_total) < 0.01, (
        f"Expected total: {expected_total}, got: {total_after}"
    )

    print("Test Passed: SAVE15 applied correctly")

finally:
    driver.quit()
