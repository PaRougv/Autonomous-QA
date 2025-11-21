from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the Chrome driver
driver = webdriver.Chrome()

try:
    # Navigate to the checkout page
    driver.get("http://127.0.0.1:5500/assets/checkout.html")

    # Step 1: Leave required fields empty
    name_field = driver.find_element(By.ID, "name")
    email_field = driver.find_element(By.ID, "email")
    address_field = driver.find_element(By.ID, "address")

    # Step 2: Click 'Pay Now' button
    pay_now_button = driver.find_element(By.ID, "pay-now")
    pay_now_button.click()

    # Wait for the error message to be displayed
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "payment-message"))
    )

    # Assert the expected result
    payment_message = driver.find_element(By.ID, "payment-message").text
    assert "Please fix the errors above." in payment_message, "Expected error message not found."

    print("Yaay , the test was performed successfully")

finally:
    # Close the browser
    driver.quit()
