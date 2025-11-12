import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1600, 1000
BG_COLOR = (252, 253, 255)
BOX_FILL = (235, 241, 252)
BOX_OUTLINE = (54, 95, 140)
ARROW_COLOR = (54, 95, 140)
TEXT_COLOR = (20, 20, 20)
TITLE_COLOR = (23, 55, 94)

img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

try:
    title_font = ImageFont.truetype("arial.ttf", 28)
    body_font = ImageFont.truetype("arial.ttf", 18)
    small_font = ImageFont.truetype("arial.ttf", 16)
except OSError:
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()
    small_font = ImageFont.load_default()


def draw_box(x0, y0, x1, y1, title, lines):
    draw.rectangle([(x0, y0), (x1, y1)], fill=BOX_FILL, outline=BOX_OUTLINE, width=3)
    draw.text((x0 + 12, y0 + 12), title, font=title_font, fill=TITLE_COLOR)
    y = y0 + 48
    for line in lines:
        draw.text((x0 + 12, y), f"- {line}", font=body_font, fill=TEXT_COLOR)
        y += 24


def draw_arrow(start, end, label=None):
    draw.line([start, end], fill=ARROW_COLOR, width=4)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    arrow_length = 18
    angle1 = angle + math.pi / 7
    angle2 = angle - math.pi / 7
    point1 = (end[0] - arrow_length * math.cos(angle1), end[1] - arrow_length * math.sin(angle1))
    point2 = (end[0] - arrow_length * math.cos(angle2), end[1] - arrow_length * math.sin(angle2))
    draw.polygon([end, point1, point2], fill=ARROW_COLOR)
    if label:
        lx = (start[0] + end[0]) / 2
        ly = (start[1] + end[1]) / 2
        draw.text((lx + 10, ly - 20), label, font=small_font, fill=TEXT_COLOR)

# Customer intake box
draw_box(30, 80, 280, 220, "Customer Input", [
    "Request text + metadata",
    "Strictly text IO",
    "quote_requests_sample.csv"
])

# Orchestrator box
draw_box(520, 40, 1080, 240, "NorthStar Orchestrator", [
    "Parses demand + due dates",
    "Routes items to at most 3 workers",
    "Shares canonical SKU list",
    "Produces structured plan JSON"
])

# Inventory agent box
draw_box(60, 320, 500, 610, "Stock Sentinel (Inventory)", [
    "Tools: inventory_snapshot -> get_all_inventory",
    "item_probe -> get_stock_level",
    "restock_planner -> get_supplier_delivery_date + create_transaction",
    "Guards reorder rules & lead times"
])

# Quoting agent box
draw_box(560, 320, 1000, 610, "Quote Engineer", [
    "Tools: quote_lookup -> search_quote_history",
    "cash_window -> get_cash_balance",
    "price_builder -> deterministic quote math",
    "Crafts transparent pricing"
])

# Fulfillment agent box
draw_box(1060, 320, 1500, 610, "Fulfillment Ranger", [
    "Tools: log_sale -> create_transaction",
    "financial_snapshot -> generate_financial_report",
    "Confirms delivery windows",
    "Provides final response"
])

# Data layer box
draw_box(400, 680, 1200, 920, "SQLite Helper Layer", [
    "create_transaction, get_all_inventory, get_stock_level,",
    "get_supplier_delivery_date, get_cash_balance,",
    "generate_financial_report, search_quote_history",
    "Powered by project_starter utilities"
])

# Arrows
draw_arrow((280, 150), (520, 150), "requests")
draw_arrow((800, 240), (360, 320), "inventory needs")
draw_arrow((800, 240), (780, 320), "quote brief")
draw_arrow((800, 240), (1280, 320), "fulfillment criteria")

# Worker outputs back to orchestrator
draw_arrow((360, 610), (800, 660), "stock & reorder plan")
draw_arrow((780, 610), (800, 660), "pricing package")
draw_arrow((1280, 610), (800, 660), "final transaction")

# Customer response arrow
draw_arrow((800, 660), (800, 900), "final narrative")

draw.text((640, 950), "Diagram: Beaver's Choice Multi-Agent Workflow", font=small_font, fill=TITLE_COLOR)

Path("docs").mkdir(exist_ok=True)
output_path = Path("docs") / "beavers_choice_workflow.png"
img.save(output_path)
print(f"Diagram saved to {output_path}")
