# Product Specifications & Business Rules

## Discount Rules

- The discount code `SAVE15` applies a **15% discount** to the cart subtotal (before shipping).
- Any other discount code is invalid and must show an inline error message.
- Only one discount code can be applied at a time.

## Shipping Rules

- **Standard shipping** is free.
- **Express shipping** costs **$10**.
- The shipping cost should be added after applying the discount.

## Cart & Pricing Rules

- Each product has a fixed unit price.
- Quantity must be a positive integer (1 or greater).
- The total price is calculated as:  
  `Total = (Sum of item price * quantity) - discount + shipping fee`.

## Payment Rules

- Payment methods: **Credit Card** and **PayPal**.
- The chosen payment method must be submitted along with the order details.

