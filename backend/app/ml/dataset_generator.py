import random
import pandas as pd
from datetime import datetime, timedelta

def generate_retail_dataset(n_samples: int = 500) -> pd.DataFrame:
    """
    Generates a rich, realistic synthetic retail feedback dataset with 500+ items.
    Covers reviews, chat transcripts, and survey responses across retail product lines and customer interactions.
    """
    random.seed(42)

    categories = ["Electronics", "Fashion", "Home & Kitchen", "Shipping & Delivery", "Customer Support", "Billing & Refunds"]
    channels = ["review", "chat", "survey"]

    # Sample template sets for realistic text generation
    positive_templates = [
        ("The {product} exceeded all my expectations! Highly durable and easy to use.", "Praise", "Joy", "Product Quality", 5),
        ("Super fast delivery for my {product}. Arrived two days early in perfect condition!", "Order Tracking", "Satisfaction", "Delivery Speed", 5),
        ("Customer service agent was extremely helpful resolving my issue with {product}. Excellent support!", "Product Query", "Satisfaction", "Customer Support", 5),
        ("Really good value for money. The {product} works seamlessly and looks premium.", "Praise", "Joy", "Pricing", 4),
        ("Impressed with the sleek design of {product}. Will definitely recommend to my friends.", "Praise", "Joy", "Design", 5),
        ("Packaging was fantastic and the {product} worked right out of the box!", "Praise", "Satisfaction", "Packaging", 5),
        ("Smooth exchange process when I needed a different size for {product}. Thank you!", "Refund/Return", "Satisfaction", "Exchange Process", 4),
        ("The quality of materials in this {product} is outstanding. TCS retail really delivers!", "Praise", "Joy", "Product Quality", 5),
        ("Great battery life and build quality on this {product}. Very satisfied buyer.", "Praise", "Satisfaction", "Performance", 5),
        ("Easy checkout experience and quick response to my query about {product}.", "General Inquiry", "Satisfaction", "Checkout Experience", 4)
    ]

    neutral_templates = [
        ("The {product} arrived on time. It does the job adequately, nothing extraordinary.", "General Inquiry", "Neutral", "Product Quality", 3),
        ("Standard packaging. The {product} is fine for basic daily use.", "General Inquiry", "Neutral", "Packaging", 3),
        ("Required a firmware update before using the {product}. Works as described now.", "Technical Support", "Neutral", "Setup", 3),
        ("Average delivery time for {product}. Took 5 business days as estimated.", "Order Tracking", "Neutral", "Delivery Speed", 3),
        ("The fabric of {product} is okay, but color is slightly lighter than shown on website.", "Product Query", "Neutral", "Product Appearance", 3),
        ("Customer support responded within 24 hours regarding {product} specs.", "Customer Support", "Neutral", "Support Response Time", 3),
        ("Price for {product} is fair, but delivery charges could be lower.", "Product Query", "Neutral", "Pricing", 3),
        ("Clear instructions included with {product}. Setup took about 15 minutes.", "Technical Support", "Neutral", "Usability", 3),
        ("The return window for {product} is 14 days according to the policy.", "Refund/Return", "Neutral", "Return Policy", 3),
        ("Decent performance for {product}, though manual could be more detailed.", "Technical Support", "Neutral", "Documentation", 3)
    ]

    negative_templates = [
        ("Extremely disappointed with the {product}. Stopped working after just 3 days!", "Complaint", "Frustration", "Product Failure", 1),
        ("Package for {product} arrived damaged and torn! Horrible delivery handling.", "Complaint", "Anger", "Damaged Item", 1),
        ("Been waiting 2 weeks for my {product} refund. Customer support keeps ignoring me!", "Refund/Return", "Anger", "Refund Delay", 1),
        ("The {product} size chart is completely wrong. Fits 2 sizes smaller than stated.", "Refund/Return", "Frustration", "Sizing Issue", 2),
        ("Charged twice for my {product} order! Unacceptable billing glitch.", "Billing Glitch", "Anger", "Overcharging", 1),
        ("The quality of {product} feels cheap and flimsy. Not worth half the price.", "Complaint", "Disappointment", "Low Quality", 1),
        ("App crashed multiple times trying to track my {product} shipment.", "Technical Support", "Frustration", "App Bug", 2),
        ("Customer service for {product} was rude and unhelpful when I asked for a replacement.", "Complaint", "Anger", "Rude Service", 1),
        ("Received the wrong item instead of {product}! Now I have to go through painful returns.", "Refund/Return", "Frustration", "Wrong Item", 1),
        ("The {product} overheats severely during regular usage. Potential safety risk!", "Complaint", "Anger", "Safety Hazard", 1)
    ]

    products = {
        "Electronics": ["Noise Cancelling Headphones", "Smartwatch Ultra", "4K OLED TV", "Wireless Mechanical Keyboard", "Bluetooth Speaker"],
        "Fashion": ["Leather Denim Jacket", "Slim Fit Chino Pants", "Breathable Running Shoes", "Cotton Polo Shirt", "Designer Sunglasses"],
        "Home & Kitchen": ["Air Fryer XL", "Espresso Coffee Machine", "Robotic Vacuum Cleaner", "Memory Foam Pillow", "Stainless Steel Cookware Set"],
        "Shipping & Delivery": ["Express Delivery Package", "Standard Ground Order", "Same-Day Courier Delivery", "Overseas Parcel"],
        "Customer Support": ["Warranty Claim Ticket", "Account Access Help", "Order Modification Request", "Loyalty Rewards Inquiry"],
        "Billing & Refunds": ["Credit Card Payment", "Gift Card Redemption", "Auto-Renewal Subscription", "Store Credit Adjustment"]
    }

    data = []
    base_date = datetime.now() - timedelta(days=60)

    for i in range(n_samples):
        # Choose sentiment with balanced weight (35% Positive, 30% Neutral, 35% Negative)
        sentiment_choice = random.choices(["Positive", "Neutral", "Negative"], weights=[0.35, 0.30, 0.35])[0]
        category = random.choice(categories)
        product = random.choice(products[category])
        channel = random.choice(channels)

        if sentiment_choice == "Positive":
            tmpl, intent, emotion, aspect, rating = random.choice(positive_templates)
            sentiment_score = round(random.uniform(0.5, 0.98), 2)
        elif sentiment_choice == "Neutral":
            tmpl, intent, emotion, aspect, rating = random.choice(neutral_templates)
            sentiment_score = round(random.uniform(-0.15, 0.15), 2)
        else:
            tmpl, intent, emotion, aspect, rating = random.choice(negative_templates)
            sentiment_score = round(random.uniform(-0.98, -0.4), 2)

        text = tmpl.format(product=product)
        created_at = base_date + timedelta(days=random.randint(0, 60), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        customer_name = f"Customer_{random.randint(100, 999)}"

        data.append({
            "text": text,
            "customer_name": customer_name,
            "channel": channel,
            "category": category,
            "product_name": product,
            "rating": rating,
            "sentiment": sentiment_choice,
            "sentiment_score": sentiment_score,
            "confidence": round(random.uniform(0.82, 0.99), 2),
            "intent": intent,
            "emotion": emotion,
            "aspect": aspect,
            "created_at": created_at
        })

    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_retail_dataset(500)
    print(f"Generated {len(df)} samples.")
    print(df["sentiment"].value_counts())
