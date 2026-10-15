"""Make synthetic, clearly labeled photography-business transactions for ExpenseLens.

Everything here is invented. Run it once to create data/labeled_transactions.csv.
The fixed seed means you get the exact same file every time.
"""

import csv
import random
from datetime import date, timedelta
from itertools import product
from pathlib import Path

random.seed(42)

OUTPUT = Path(__file__).parent.parent / "data" / "labeled_transactions.csv"
START, END = date(2026, 1, 2), date(2026, 6, 28)


def random_date():
    """Pick a random day between START and END."""
    return START + timedelta(days=random.randint(0, (END - START).days))


def build(template, options, low, high):
    """Fill a description template with each option. Returns (description, low, high)."""
    return [(template.format(o), low, high) for o in options]


def add_expenses(rows, pool, category, count):
    """Pick `count` different descriptions from the pool and add them as outflows."""
    for description, low, high in random.sample(pool, min(count, len(pool))):
        amount = -round(random.uniform(low, high), 2)  # negative = money out
        rows.append([random_date().isoformat(), description, f"{amount:.2f}", category])


# ---------- Descriptions for each category ----------
shops = ["B&H", "Adorama", "KEH Camera", "Best Buy", "Amazon"]
equipment = (
    build("Camera battery - {}", shops, 40, 90)
    + build("Memory card 128GB - {}", shops, 30, 70)
    + build("Tripod - {}", shops, 80, 250)
    + build("Flash speedlight - {}", shops, 150, 400)
    + build("Camera lens - {}", shops, 300, 1400)
    + build("LED light panel - {}", shops, 60, 220)
    + build("Camera bag - {}", shops, 70, 200)
    + build("Lens filter set - {}", shops, 40, 120)
    + build("Light stand and softbox - {}", shops, 60, 180)
    + build("Gimbal stabilizer - {}", shops, 150, 400)
)

software_one_offs = [
    ("Canva Pro annual plan", 100, 120),
    ("QuickBooks Online", 25, 45),
    ("Squarespace website renewal", 150, 220),
    ("Zoom Pro plan", 13, 16),
    ("Capture One license", 180, 300),
    ("Lightroom presets pack", 20, 60),
    ("Domain renewal - GoDaddy", 15, 25),
    ("Backblaze cloud backup", 8, 10),
]

ad_platforms = ["Instagram ads", "Facebook ads", "Google Ads", "TikTok ads", "Yelp ads"]
campaigns = ["spring promo", "grad season", "wedding season", "holiday minis", "brand awareness"]
marketing = (
    [(f"{p} - {c}", 25, 300) for p, c in product(ad_platforms, campaigns)]
    + build("{} - Vistaprint", ["Business cards", "Flyers", "Banner", "Postcards", "Stickers"], 20, 120)
    + [
        ("Wedding expo booth fee", 150, 600),
        ("Thumbtack lead fee", 15, 60),
        ("Giveaway prizes - Instagram contest", 30, 100),
        ("Branded tote bags", 60, 180),
        ("Referral thank-you gifts", 25, 80),
        ("Photographer directory listing", 20, 90),
        ("Facebook group sponsor post", 25, 75),
    ]
)

places = ["client shoot", "wedding venue", "campus event", "concert", "airport", "studio rental"]
travel = (
    build("Uber to {}", places, 12, 45)
    + build("Lyft to {}", places, 12, 45)
    + build("Gas - {}", ["Shell", "Exxon", "QuikTrip", "Chevron", "Buc-ee's"], 35, 80)
    + build("Parking - {}", ["Deep Ellum garage", "Convention center", "Stadium lot", "UNT campus lot", "DFW Airport"], 8, 40)
    + build("Hotel stay - {}", ["Austin", "Houston", "San Antonio", "Oklahoma City"], 120, 260)
    + build("Southwest flight - {}", ["DAL to AUS", "DAL to HOU", "DAL to OKC"], 90, 220)
    + build("NTTA toll - {}", ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], 8, 30)
    + [("Rental car - Enterprise", 90, 220)]
)

office_items = [
    ("Printer paper", 15, 45), ("Printer ink", 30, 90), ("Pens and notebooks", 10, 35),
    ("Shipping envelopes", 12, 40), ("Folders and binders", 10, 30),
    ("Sticky notes and tape", 8, 25), ("Desk organizer", 15, 45), ("Print packaging boxes", 20, 60),
]
office = []
for name, low, high in office_items:
    office += build(name + " - {}", ["Staples", "Office Depot", "Walmart", "Target", "Amazon"], low, high)

# Vague bank-statement style descriptions (no obvious keywords): description, low, high, category
vague = [
    ("AMZN Mktp US*2K4TR9", 40, 300, "equipment"),
    ("AMZN Mktp US*5M7QX2", 50, 250, "equipment"),
    ("PAYPAL *PHOTOGEAR", 80, 400, "equipment"),
    ("AMZN Mktp US*8H1LP3", 12, 60, "office supplies"),
    ("WALMART SUPERCENTER #1234", 15, 70, "office supplies"),
    ("COSTCO WHSE #1098", 20, 90, "office supplies"),
    ("TARGET T-0213", 10, 50, "office supplies"),
    ("PAYPAL *TUCKERDESIGN", 40, 200, "marketing"),
    ("SQ *PRINT SHOP DENTON", 25, 150, "marketing"),
    ("SQ *LOCAL AD CO", 50, 250, "marketing"),
    ("CIRCLE K 04455", 30, 70, "travel"),
    ("SQ *AIRPORT SHUTTLE", 20, 60, "travel"),
    ("APPLE.COM/BILL", 3, 30, "software"),
    ("GOOGLE *SERVICES", 3, 30, "software"),
]

clients = ["Johnson", "Garcia", "Patel", "Nguyen", "Smith", "Williams", "Brown", "Davis"]
inflows = (
    build("Wedding shoot deposit - {}", clients, 300, 800)
    + build("Portrait session - {}", clients, 150, 450)
    + build("Greek life event - {}", ["Sigma Chi", "Kappa Alpha", "Delta Gamma", "Alpha Phi", "Phi Delta Theta"], 400, 1200)
    + build("Concert gallery license - {}", ["House of Blues", "Granada Theater", "Trees", "Dada"], 200, 700)
)

# ---------- Build the rows ----------
rows = []  # each row: date, description, amount, category

add_expenses(rows, equipment, "equipment", 50)
add_expenses(rows, marketing, "marketing", 37)
add_expenses(rows, travel, "travel", 36)
add_expenses(rows, office, "office supplies", 40)
add_expenses(rows, software_one_offs, "software", 8)

# Monthly subscriptions repeat every month (real statements do this too)
subscriptions = [("Adobe Creative Cloud", 59.99), ("Pixieset gallery plan", 20.00),
                 ("Dropbox storage", 11.99), ("Google Workspace", 7.20)]
for month in range(1, 7):
    for name, price in subscriptions:
        rows.append([date(2026, month, 5).isoformat(), name, f"{-price:.2f}", "software"])

for description, low, high, category in vague:
    amount = -round(random.uniform(low, high), 2)
    rows.append([random_date().isoformat(), description, f"{amount:.2f}", category])

# Money coming in has no expense category, so that column stays blank
for description, low, high in random.sample(inflows, 25):
    amount = round(random.uniform(low, high), 2)
    rows.append([random_date().isoformat(), description, f"{amount:.2f}", ""])

rows.sort(key=lambda r: r[0])  # oldest first

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "description", "amount", "category"])
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {OUTPUT}")