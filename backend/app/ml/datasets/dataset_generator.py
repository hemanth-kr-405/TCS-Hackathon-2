"""
Synthetic Retail Feedback Dataset Generator — Phase 1
======================================================
Generates reproducible, clearly-labelled synthetic retail customer feedback
for development / demo purposes.

IMPORTANT: All records are marked is_synthetic=True. Never present as real data.
"""
import random
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import os


# ─── Template Banks ──────────────────────────────────────────────────────────

POSITIVE_TEMPLATES = [
    ("The {product} exceeded all my expectations! Highly durable and very easy to use.", "Praise", "Joy", "Product Quality & Build"),
    ("Super fast delivery for my {product}. Arrived two days early in perfect condition!", "Order Tracking", "Satisfaction", "Delivery Speed & Packaging"),
    ("Customer service was extremely helpful resolving my issue with the {product}. Excellent!", "Praise", "Satisfaction", "Customer Support Service"),
    ("Really good value for money. The {product} works seamlessly and looks premium.", "Praise", "Joy", "Pricing & Value"),
    ("Impressed with the sleek design of the {product}. Will definitely recommend to my friends.", "Praise", "Joy", "Product Quality & Build"),
    ("Packaging was fantastic and the {product} worked right out of the box!", "Praise", "Satisfaction", "Delivery Speed & Packaging"),
    ("Smooth exchange process when I needed a different size for {product}. Thank you!", "Refund / Return", "Satisfaction", "Refunds & Exchanges"),
    ("Outstanding quality of materials in the {product}. TCS Retail really delivers!", "Praise", "Joy", "Product Quality & Build"),
    ("Great battery life and build quality on the {product}. Very satisfied buyer.", "Praise", "Satisfaction", "Product Quality & Build"),
    ("Easy checkout and quick response to my query about {product}.", "General Inquiry", "Satisfaction", "Usability & Features"),
    ("My {product} arrived in pristine condition. The courier handled it with care.", "Order Tracking", "Joy", "Delivery Speed & Packaging"),
    ("Five stars for the {product}! Setup was straightforward and it performs flawlessly.", "Praise", "Joy", "Usability & Features"),
    ("Just received my {product} and I am absolutely thrilled. Highly recommended.", "Praise", "Joy", "Product Quality & Build"),
    ("The support team resolved my {product} issue in under 10 minutes. Fantastic service.", "Praise", "Satisfaction", "Customer Support Service"),
    ("Got a full refund for my defective {product} within 48 hours. Impressed with the policy.", "Refund / Return", "Satisfaction", "Refunds & Exchanges"),
]

NEUTRAL_TEMPLATES = [
    ("The {product} arrived on time. Does the job adequately, nothing extraordinary.", "General Inquiry", "Neutral", "Product Quality & Build"),
    ("Standard packaging. The {product} is fine for everyday basic use.", "General Inquiry", "Neutral", "Delivery Speed & Packaging"),
    ("Required a firmware update before using the {product}. Works as described now.", "Technical Support", "Neutral", "Usability & Features"),
    ("Average delivery time for {product}. Took 5 business days as estimated.", "Order Tracking", "Neutral", "Delivery Speed & Packaging"),
    ("The colour of {product} is slightly lighter than shown on website, otherwise fine.", "Product Inquiry", "Neutral", "Product Quality & Build"),
    ("Customer support responded within 24 hours regarding {product} specifications.", "General Inquiry", "Neutral", "Customer Support Service"),
    ("Price for {product} is fair, but delivery charges could be lower.", "Product Inquiry", "Neutral", "Pricing & Value"),
    ("Setup instructions for {product} are adequate. Took about 15 minutes to configure.", "Technical Support", "Neutral", "Usability & Features"),
    ("Return window for {product} is 14 days according to the policy. Standard policy.", "Refund / Return", "Neutral", "Refunds & Exchanges"),
    ("Decent performance for {product}, though the user manual could be more detailed.", "General Inquiry", "Neutral", "Usability & Features"),
    ("The {product} does what it says. Not exceptional but meets basic requirements.", "General Inquiry", "Neutral", "Product Quality & Build"),
    ("Received {product} in the estimated window. No complaints, no praise.", "Order Tracking", "Neutral", "Delivery Speed & Packaging"),
]

NEGATIVE_TEMPLATES = [
    ("Extremely disappointed with the {product}. Stopped working after just 3 days!", "Complaint", "Frustration", "Product Quality & Build"),
    ("Package for {product} arrived damaged and torn! Horrible delivery handling.", "Complaint", "Anger", "Delivery Speed & Packaging"),
    ("Been waiting 2 weeks for my {product} refund. Customer support keeps ignoring me!", "Refund / Return", "Anger", "Refunds & Exchanges"),
    ("The {product} size chart is completely wrong. Fits 2 sizes smaller than stated.", "Refund / Return", "Frustration", "Product Quality & Build"),
    ("Charged twice for my {product} order! Unacceptable billing error.", "Complaint", "Anger", "Pricing & Value"),
    ("The {product} feels extremely cheap and flimsy. Not worth even half the price.", "Complaint", "Disappointment", "Product Quality & Build"),
    ("App crashed multiple times while trying to track my {product} shipment.", "Technical Support", "Frustration", "Usability & Features"),
    ("Customer service agent was rude and unhelpful when I asked for {product} replacement.", "Complaint", "Anger", "Customer Support Service"),
    ("Received wrong item instead of {product}! Painful return process with no updates.", "Refund / Return", "Frustration", "Refunds & Exchanges"),
    ("The {product} overheats severely during regular use. This is a safety hazard!", "Complaint", "Anger", "Product Quality & Build"),
    ("No one from support has contacted me about my {product} complaint for a week.", "Complaint", "Frustration", "Customer Support Service"),
    ("My {product} was shipped to the wrong address. Total logistics failure.", "Complaint", "Anger", "Delivery Speed & Packaging"),
    ("The {product} subscription was auto-renewed without my consent. Terrible practice.", "Complaint", "Anger", "Pricing & Value"),
    ("Waited 3 weeks for {product} to arrive, then it arrived broken. Absolutely unacceptable.", "Complaint", "Anger", "Delivery Speed & Packaging"),
]

PRODUCTS = {
    "Electronics": [
        "Noise Cancelling Headphones", "Smartwatch Ultra", "4K OLED TV",
        "Wireless Mechanical Keyboard", "Bluetooth Speaker", "Laptop Stand Pro",
    ],
    "Fashion": [
        "Leather Denim Jacket", "Slim Fit Chino Pants", "Breathable Running Shoes",
        "Cotton Polo Shirt", "Designer Sunglasses", "Wool Blend Scarf",
    ],
    "Home & Kitchen": [
        "Air Fryer XL", "Espresso Coffee Machine", "Robotic Vacuum Cleaner",
        "Memory Foam Pillow", "Stainless Steel Cookware Set", "Bamboo Cutting Board",
    ],
    "Shipping & Delivery": [
        "Express Delivery Package", "Standard Ground Order",
        "Same-Day Courier Delivery", "Overseas Parcel",
    ],
    "Customer Support": [
        "Warranty Claim Ticket", "Account Access Help",
        "Order Modification Request", "Loyalty Rewards Inquiry",
    ],
    "Billing & Refunds": [
        "Credit Card Payment", "Gift Card Redemption",
        "Auto-Renewal Subscription", "Store Credit Adjustment",
    ],
}

CHANNELS = ["review", "chat", "survey"]
CUSTOMER_NAMES = [f"Customer_{i:04d}" for i in range(1, 1001)]


def generate_retail_dataset(n_samples: int = 800, seed: int = 42) -> pd.DataFrame:
    """
    Generate a reproducible synthetic retail feedback dataset.

    Args:
        n_samples: Number of records to generate.
        seed: Random seed for reproducibility.

    Returns:
        pd.DataFrame with columns matching FeedbackItem schema.
        All rows have is_synthetic=True.
    """
    random.seed(seed)
    categories = list(PRODUCTS.keys())
    data = []
    base_date = datetime.now() - timedelta(days=90)

    for i in range(n_samples):
        sentiment_choice = random.choices(
            ["Positive", "Neutral", "Negative"], weights=[0.35, 0.30, 0.35]
        )[0]
        category = random.choice(categories)
        product = random.choice(PRODUCTS[category])
        channel = random.choice(CHANNELS)

        if sentiment_choice == "Positive":
            tmpl, intent, emotion, aspect = random.choice(
                [(t, i, e, a) for t, i, e, a in
                 [x[:4] for x in POSITIVE_TEMPLATES]]
            )
            sentiment_score = round(random.uniform(0.45, 0.98), 3)
            rating = random.choice([4, 5])
            confidence = round(random.uniform(0.78, 0.99), 3)
        elif sentiment_choice == "Neutral":
            tmpl, intent, emotion, aspect = random.choice(
                [(t, i, e, a) for t, i, e, a in
                 [x[:4] for x in NEUTRAL_TEMPLATES]]
            )
            sentiment_score = round(random.uniform(-0.15, 0.20), 3)
            rating = 3
            confidence = round(random.uniform(0.65, 0.88), 3)
        else:
            tmpl, intent, emotion, aspect = random.choice(
                [(t, i, e, a) for t, i, e, a in
                 [x[:4] for x in NEGATIVE_TEMPLATES]]
            )
            sentiment_score = round(random.uniform(-0.98, -0.40), 3)
            rating = random.choice([1, 2])
            confidence = round(random.uniform(0.75, 0.97), 3)

        text = tmpl.format(product=product)
        created_at = base_date + timedelta(
            days=random.randint(0, 90),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        customer_id = random.choice(CUSTOMER_NAMES)

        data.append({
            "text": text,
            "customer_id": customer_id,
            "source": channel,
            "product": product,
            "category": category,
            "sentiment": sentiment_choice,
            "sentiment_score": sentiment_score,
            "confidence": confidence,
            "intent": intent,
            "emotion": emotion,
            "aspect": aspect,
            "rating": rating,
            "is_synthetic": True,
            "created_at": created_at,
        })

    return pd.DataFrame(data)


def save_dataset(df: pd.DataFrame, path: str) -> None:
    """Save generated dataset to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[dataset] Saved {len(df)} synthetic records → {path}")


if __name__ == "__main__":
    df = generate_retail_dataset(800)
    save_dataset(df, "data/synthetic/retail_feedback.csv")
    print(df["sentiment"].value_counts())
    print(df["category"].value_counts())
