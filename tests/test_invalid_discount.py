from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os


def main():
    # Initialize Chrome with webdriver-manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)

    try:
        # 👉 Load the local checkout.html file instead of localhost:8501
        html_path = os.path.abspath(os.path.join("assets", "checkout.html"))
        url = "file:///" + html_path.replace("\\", "/")
        print(f"Opening {url}")
        driver.get(url)

        # Step 1: Cart is empty by default (no action needed)

        # Step 2: Enter discount code SAVE15
        discount_code_input = driver.find_element(By.ID, "discount-code")
        discount_code_input.send_keys("SAVE15")

        # Step 3: Trigger discount event
        discount_code_input.send_keys("")

        # Wait for the error message
        wait.until(EC.visibility_of_element_located((By.ID, "discount-error")))

        # Verify error text
        discount_error_message = driver.find_element(By.ID, "discount-error").text
        assert discount_error_message == "Invalid discount code.", "Expected error message not displayed."

        # Total must still be 0.00
        total_price = driver.find_element(By.ID, "total-price").text
        assert total_price == "0.00", "Total price should remain $0.00."

        print("❌ Negative Discount Test Passed — SAVE15 rejected with empty cart.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
