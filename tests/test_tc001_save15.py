from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os


def main():
    # Initialize Chrome driver with webdriver-manager (auto-handles chromedriver)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)

    try:
        # Navigate to the local checkout page (assets/checkout.html)
        html_path = os.path.abspath(os.path.join("assets", "checkout.html"))
        url = "file:///" + html_path.replace("\\", "/")
        print(f"Opening {url}")
        driver.get(url)

        # Step 1: Add items to the cart (all visible "add-to-cart" buttons)
        add_to_cart_buttons = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "add-to-cart"))
        )
        assert len(add_to_cart_buttons) >= 1, "No 'add-to-cart' buttons found."

        # Click all of them once (Mouse, Keyboard, USB-C Cable)
        for button in add_to_cart_buttons:
            button.click()

        # Read total BEFORE discount
        total_price_element = wait.until(
            EC.visibility_of_element_located((By.ID, "total-price"))
        )
        total_before_text = total_price_element.text
        total_before = float(total_before_text)
        print(f"Total before discount: {total_before}")

        # Optional sanity check: 20 + 80 + 10 = 110
        expected_subtotal = 110.0
        assert abs(total_before - expected_subtotal) < 0.01, (
            f"Expected subtotal {expected_subtotal}, but got {total_before}"
        )

        # Step 2: Enter discount code SAVE15
        discount_code_input = wait.until(
            EC.visibility_of_element_located((By.ID, "discount-code"))
        )
        discount_code_input.clear()
        discount_code_input.send_keys("SAVE15")

        # Step 3: Trigger discount application (input event is used in JS)
        discount_code_input.send_keys("")  # minimal change to fire event

        # Wait for the total price to change from the previous value
        def total_changed(driver_instance):
            try:
                current_total = float(
                    driver_instance.find_element(By.ID, "total-price").text
                )
                return abs(current_total - total_before) > 0.01
            except Exception:
                return False

        wait.until(total_changed)

        # Get the total price after applying the discount
        total_after_text = driver.find_element(By.ID, "total-price").text
        total_after = float(total_after_text)
        print(f"Total after discount: {total_after}")

        # Expected total: 110 * 0.85 = 93.5 (15% discount, standard shipping)
        expected_total = 110 * 0.85  # 93.5

        # Assert the expected result: Total is reduced by 15%
        assert abs(total_after - expected_total) < 0.01, (
            f"Expected total after discount {expected_total}, but got {total_after}"
        )

        print("✅ TC-001 passed: SAVE15 reduces total by 15% on full cart.")

    finally:
        # Close the browser
        driver.quit()


if __name__ == "__main__":
    main()
