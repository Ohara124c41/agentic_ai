import pandas as pd
import numpy as np
import os
import time
import json
import textwrap
import dotenv
import ast
from difflib import get_close_matches
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, Engine
from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool, StructuredDict
from pydantic_ai.settings import ModelSettings

# Create an SQLite database
db_engine = create_engine("sqlite:///munder_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},  # per plate
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},  # per cup
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},  # per napkin
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},  # per cup
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},  # per cover
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},  # per envelope
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},  # per sheet
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},  # per pad
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},  # per card
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},  # per flyer
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},  # per roll
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},  # per roll
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},  # per bag
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},  # per tag
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},  # per folder

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

VOC_BASE_URL = "https://openai.vocareum.com/v1"
CANONICAL_ITEM_NAMES = sorted({item["item_name"] for item in paper_supplies})
LOWER_CANONICAL_ITEM_NAMES = [name.lower() for name in CANONICAL_ITEM_NAMES]
PRICE_LOOKUP = {item["item_name"].lower(): item["unit_price"] for item in paper_supplies}
ITEM_NAME_SYNONYMS = {
    "heavy cardstock": "Cardstock",
    "card stock": "Cardstock",
    "colored cardstock": "Cardstock",
    "glossy a4 paper": "Glossy paper",
    "a4 glossy paper": "Glossy paper",
    "a4 paper": "A4 paper",
    "letter paper": "Letter-sized paper",
    "letter sized paper": "Letter-sized paper",
    "eco paper": "Eco-friendly paper",
    "recycled": "Recycled paper",
    "poster stock": "Poster paper",
    "banner": "Banner paper",
}

# Given below are some utility functions you can use to implement your multi-agent system

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """
    Generate inventory for exactly a specified percentage of items from the full paper supply list.

    This function randomly selects exactly `coverage` × N items from the `paper_supplies` list,
    and assigns each selected item:
    - a random stock quantity between 200 and 800,
    - a minimum stock level between 50 and 150.

    The random seed ensures reproducibility of selection and stock levels.

    Args:
        paper_supplies (list): A list of dictionaries, each representing a paper item with
                               keys 'item_name', 'category', and 'unit_price'.
        coverage (float, optional): Fraction of items to include in the inventory (default is 0.4, or 40%).
        seed (int, optional): Random seed for reproducibility (default is 137).

    Returns:
        pd.DataFrame: A DataFrame with the selected items and assigned inventory values, including:
                      - item_name
                      - category
                      - unit_price
                      - current_stock
                      - min_stock_level
    """
    # Ensure reproducible random output
    np.random.seed(seed)

    # Calculate number of items to include based on coverage
    num_items = int(len(paper_supplies) * coverage)

    # Randomly select item indices without replacement
    selected_indices = np.random.choice(
        range(len(paper_supplies)),
        size=num_items,
        replace=False
    )

    # Extract selected items from paper_supplies list
    selected_items = [paper_supplies[i] for i in selected_indices]

    # Construct inventory records
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),  # Realistic stock range
            "min_stock_level": np.random.randint(50, 150)  # Reasonable threshold for reordering
        })

    # Return inventory as a pandas DataFrame
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine, seed: int = 137) -> Engine:    
    """
    Set up the Munder Difflin database with all required tables and initial records.

    This function performs the following tasks:
    - Creates the 'transactions' table for logging stock orders and sales
    - Loads customer inquiries from 'quote_requests.csv' into a 'quote_requests' table
    - Loads previous quotes from 'quotes.csv' into a 'quotes' table, extracting useful metadata
    - Generates a random subset of paper inventory using `generate_sample_inventory`
    - Inserts initial financial records including available cash and starting stock levels

    Args:
        db_engine (Engine): A SQLAlchemy engine connected to the SQLite database.
        seed (int, optional): A random seed used to control reproducibility of inventory stock levels.
                              Default is 137.

    Returns:
        Engine: The same SQLAlchemy engine, after initializing all necessary tables and records.

    Raises:
        Exception: If an error occurs during setup, the exception is printed and raised.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        # Unpack metadata fields (job_type, order_size, event_type) if present
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

        # Retain only relevant columns
        quotes_df = quotes_df[[
            "request_id",
            "total_amount",
            "quote_explanation",
            "order_date",
            "job_type",
            "order_size",
            "event_type"
        ]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def create_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: Union[str, datetime],
) -> int:
    """
    This function records a transaction of type 'stock_orders' or 'sales' with a specified
    item name, quantity, total price, and transaction date into the 'transactions' table of the database.

    Args:
        item_name (str): The name of the item involved in the transaction.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units involved in the transaction.
        price (float): Total price of the transaction.
        date (str or datetime): Date of the transaction in ISO 8601 format.

    Returns:
        int: The ID of the newly inserted transaction.

    Raises:
        ValueError: If `transaction_type` is not 'stock_orders' or 'sales'.
        Exception: For other database or execution errors.
    """
    try:
        # Convert datetime to ISO string if necessary
        date_str = date.isoformat() if isinstance(date, datetime) else date

        # Validate transaction type
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        # Prepare transaction record as a single-row DataFrame
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])

        # Insert the record into the database
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        # Fetch and return the ID of the inserted row
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])

    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """
    Retrieve a snapshot of available inventory as of a specific date.

    This function calculates the net quantity of each item by summing 
    all stock orders and subtracting all sales up to and including the given date.

    Only items with positive stock are included in the result.

    Args:
        as_of_date (str): ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff.

    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    # SQL query to compute stock levels per item as of the given date
    query = """
        SELECT
            item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL
        AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """

    # Execute the query with the date parameter
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})

    # Convert the result into a dictionary {item_name: stock}
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """
    Retrieve the stock level of a specific item as of a given date.

    This function calculates the net stock by summing all 'stock_orders' and 
    subtracting all 'sales' transactions for the specified item up to the given date.

    Args:
        item_name (str): The name of the item to look up.
        as_of_date (str or datetime): The cutoff date (inclusive) for calculating stock.

    Returns:
        pd.DataFrame: A single-row DataFrame with columns 'item_name' and 'current_stock'.
    """
    # Convert date to ISO string format if it's a datetime object
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # SQL query to compute net stock level for the item
    stock_query = """
        SELECT
            item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name
        AND transaction_date <= :as_of_date
    """

    # Execute query and return result as a DataFrame
    return pd.read_sql(
        stock_query,
        db_engine,
        params={"item_name": item_name, "as_of_date": as_of_date},
    )

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date based on the requested order quantity and a starting date.

    Delivery lead time increases with order size:
        - ≤10 units: same day
        - 11–100 units: 1 day
        - 101–1000 units: 4 days
        - >1000 units: 7 days

    Args:
        input_date_str (str): The starting date in ISO format (YYYY-MM-DD).
        quantity (int): The number of units in the order.

    Returns:
        str: Estimated delivery date in ISO format (YYYY-MM-DD).
    """
    # Debug log (comment out in production if needed)
    print(f"FUNC (get_supplier_delivery_date): Calculating for qty {quantity} from date string '{input_date_str}'")

    # Attempt to parse the input date
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        # Fallback to current date on format error
        print(f"WARN (get_supplier_delivery_date): Invalid date format '{input_date_str}', using today as base.")
        input_date_dt = datetime.now()

    # Determine delivery delay based on quantity
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    # Add delivery days to the starting date
    delivery_date_dt = input_date_dt + timedelta(days=days)

    # Return formatted delivery date
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """
    Calculate the current cash balance as of a specified date.

    The balance is computed by subtracting total stock purchase costs ('stock_orders')
    from total revenue ('sales') recorded in the transactions table up to the given date.

    Args:
        as_of_date (str or datetime): The cutoff date (inclusive) in ISO format or as a datetime object.

    Returns:
        float: Net cash balance as of the given date. Returns 0.0 if no transactions exist or an error occurs.
    """
    try:
        # Convert date to ISO format if it's a datetime object
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()

        # Query all transactions on or before the specified date
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine,
            params={"as_of_date": as_of_date},
        )

        # Compute the difference between sales and stock purchases
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)

        return 0.0

    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """
    Generate a complete financial report for the company as of a specific date.

    This includes:
    - Cash balance
    - Inventory valuation
    - Combined asset total
    - Itemized inventory breakdown
    - Top 5 best-selling products

    Args:
        as_of_date (str or datetime): The date (inclusive) for which to generate the report.

    Returns:
        Dict: A dictionary containing the financial report fields:
            - 'as_of_date': The date of the report
            - 'cash_balance': Total cash available
            - 'inventory_value': Total value of inventory
            - 'total_assets': Combined cash and inventory value
            - 'inventory_summary': List of items with stock and valuation details
            - 'top_selling_products': List of top 5 products by revenue
    """
    # Normalize date input
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # Get current cash balance
    cash = get_cash_balance(as_of_date)

    # Get current inventory snapshot
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    # Compute total inventory value and summary by item
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value

        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })

    # Identify top-selling products by revenue
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")

    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Retrieve a list of historical quotes that match any of the provided search terms.

    The function searches both the original customer request (from `quote_requests`) and
    the explanation for the quote (from `quotes`) for each keyword. Results are sorted by
    most recent order date and limited by the `limit` parameter.

    Args:
        search_terms (List[str]): List of terms to match against customer requests and explanations.
        limit (int, optional): Maximum number of quote records to return. Default is 5.

    Returns:
        List[Dict]: A list of matching quotes, each represented as a dictionary with fields:
            - original_request
            - total_amount
            - quote_explanation
            - job_type
            - order_size
            - event_type
            - order_date
    """
    conditions = []
    params = {}

    # Build SQL WHERE clause using LIKE filters for each search term
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"

    # Combine conditions; fallback to always-true if no terms provided
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Final SQL query to join quotes with quote_requests
    query = f"""
        SELECT
            qr.response AS original_request,
            q.total_amount,
            q.quote_explanation,
            q.job_type,
            q.order_size,
            q.event_type,
            q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """

    # Execute parameterized query
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row) for row in result]

########################
########################
########################
# YOUR MULTI AGENT STARTS HERE
########################
########################
########################


dotenv.load_dotenv()


def configure_openai_environment() -> str:
    """
    Ensure that pydantic-ai routes through the Vocareum proxy by setting OPENAI env vars.
    """
    key = (
        os.getenv("UDACITY_OPENAI_API_KEY")
        or os.getenv("VOC_OPENAI_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )
    if not key:
        raise RuntimeError(
            "Missing UDACITY_OPENAI_API_KEY in your environment or .env file."
        )
    os.environ["OPENAI_API_KEY"] = key
    os.environ.setdefault("OPENAI_BASE_URL", VOC_BASE_URL)
    return key


def canonicalize_item_name(raw_name: str) -> str:
    """Map arbitrary text to the closest Beaver's Choice SKU."""
    if not raw_name:
        return ""
    key = raw_name.strip().lower()
    if key in ITEM_NAME_SYNONYMS:
        return ITEM_NAME_SYNONYMS[key]
    if key in PRICE_LOOKUP:
        idx = LOWER_CANONICAL_ITEM_NAMES.index(key)
        return CANONICAL_ITEM_NAMES[idx]
    for sku in CANONICAL_ITEM_NAMES:
        if sku.lower() in key:
            return sku
    matches = get_close_matches(key, LOWER_CANONICAL_ITEM_NAMES, n=1, cutoff=0.72)
    if matches:
        matched = matches[0]
        idx = LOWER_CANONICAL_ITEM_NAMES.index(matched)
        return CANONICAL_ITEM_NAMES[idx]
    return ""


class PlannedItem(BaseModel):
    requested_name: str
    normalized_item: str
    quantity: int = Field(ge=0)
    urgency: str
    notes: Optional[str] = None


class OrchestrationPlan(BaseModel):
    summary: str
    due_date: Optional[str] = None
    customer_priority: str
    discount_strategy: str
    needs_inventory: bool
    needs_reorder: bool
    needs_quote: bool
    needs_fulfillment: bool
    items: List[PlannedItem]


class InventoryLine(BaseModel):
    item_name: str
    requested_units: int
    available_units: int
    ready_units: int
    status: str
    action: str
    eta: Optional[str] = None
    notes: Optional[str] = None


class InventoryAssessment(BaseModel):
    lines: List[InventoryLine]
    decision_notes: str


class QuoteLine(BaseModel):
    item_name: str
    quantity: int
    unit_price: float
    line_total: float
    discount_pct: float
    status: str
    notes: str


class QuoteDecision(BaseModel):
    quote_lines: List[QuoteLine]
    declined_items: List[str]
    total_amount: float
    quote_explanation: str
    can_fulfill: bool


class FulfillmentSummary(BaseModel):
    fulfilled_items: List[str]
    recorded_transactions: List[int]
    delivery_notes: str
    customer_message: str


ORCHESTRATOR_OUTPUT = StructuredDict(OrchestrationPlan.model_json_schema())
INVENTORY_OUTPUT = StructuredDict(InventoryAssessment.model_json_schema())
QUOTE_OUTPUT = StructuredDict(QuoteDecision.model_json_schema())
FULFILLMENT_OUTPUT = StructuredDict(FulfillmentSummary.model_json_schema())


def tool_inventory_snapshot(as_of_date: str) -> Dict[str, Any]:
    """Return company-wide stock levels as of the supplied ISO date."""
    return {"as_of_date": as_of_date, "inventory": get_all_inventory(as_of_date)}


def tool_item_stock_probe(item_name: str, as_of_date: str) -> Dict[str, Any]:
    """Inspect a single SKU's stock position."""
    canonical = canonicalize_item_name(item_name)
    if not canonical:
        return {"item_name": item_name, "error": "unrecognized SKU"}
    stock_df = get_stock_level(canonical, as_of_date)
    stock_value = int(stock_df["current_stock"].iloc[0]) if not stock_df.empty else 0
    return {"item_name": canonical, "current_stock": stock_value, "as_of_date": as_of_date}


def tool_plan_restock_purchase(item_name: str, units: int, as_of_date: str) -> Dict[str, Any]:
    """Create a supplier order transaction dated on the delivery date."""
    canonical = canonicalize_item_name(item_name)
    if not canonical or units <= 0:
        return {"status": "skipped", "reason": "invalid sku or units"}
    unit_price = PRICE_LOOKUP.get(canonical.lower())
    if unit_price is None:
        return {"status": "skipped", "reason": "missing price"}
    estimated_cost = round(unit_price * units, 2)
    available_cash = get_cash_balance(as_of_date)
    if estimated_cost > max(available_cash * 0.85, 1.0):
        return {
            "status": "deferred",
            "reason": f"cost ${estimated_cost:.2f} exceeds safe cash window ${available_cash:.2f}",
        }
    delivery_date = get_supplier_delivery_date(as_of_date, units)
    transaction_id = create_transaction(
        canonical,
        "stock_orders",
        units,
        estimated_cost,
        delivery_date,
    )
    return {
        "status": "ordered",
        "item_name": canonical,
        "units": units,
        "cost": estimated_cost,
        "expected_delivery": delivery_date,
        "transaction_id": transaction_id,
    }


def tool_lookup_quote_history(keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch relevant historical quotes."""
    keywords = [kw for kw in keywords if kw]
    return search_quote_history(keywords, limit=limit)


def tool_cash_window(as_of_date: str) -> Dict[str, Any]:
    """Expose cash balance for budgeting decisions."""
    cash = get_cash_balance(as_of_date)
    return {"as_of_date": as_of_date, "cash_balance": round(cash, 2)}


def tool_price_builder(
    item_name: str,
    quantity: int,
    discount_pct: float = 0.0,
    expedite: bool = False,
) -> Dict[str, Any]:
    """Deterministic pricing helper used by the quote agent."""
    canonical = canonicalize_item_name(item_name)
    if not canonical or quantity <= 0:
        return {"error": "invalid input"}
    unit_price = PRICE_LOOKUP.get(canonical.lower())
    if unit_price is None:
        return {"error": "price lookup failed"}
    volume_markup = 0.28 if quantity < 500 else 0.18
    if quantity >= 2000:
        volume_markup = 0.12
    base_price = unit_price * (1 + volume_markup)
    capped_discount = max(min(discount_pct, 15.0), 0.0)
    discounted_price = base_price * (1 - capped_discount / 100)
    if expedite:
        discounted_price *= 1.02
    final_unit = round(max(discounted_price, unit_price * 0.8), 4)
    line_total = round(final_unit * quantity, 2)
    return {
        "item_name": canonical,
        "unit_price": final_unit,
        "line_total": line_total,
        "discount_pct": capped_discount,
        "applied_markup": volume_markup,
        "expedite": expedite,
    }


def tool_record_sale(
    item_name: str,
    units: int,
    unit_price: float,
    as_of_date: str,
    note: str = "",
) -> Dict[str, Any]:
    """Create a sales transaction and return the id."""
    canonical = canonicalize_item_name(item_name)
    if not canonical or units <= 0:
        return {"status": "skipped", "reason": "invalid sale payload"}
    total_price = round(unit_price * units, 2)
    transaction_id = create_transaction(
        canonical,
        "sales",
        units,
        total_price,
        as_of_date,
    )
    return {
        "status": "recorded",
        "item_name": canonical,
        "units": units,
        "unit_price": unit_price,
        "total_price": total_price,
        "note": note,
        "transaction_id": transaction_id,
    }


def tool_financial_snapshot(as_of_date: str) -> Dict[str, Any]:
    """Return a lightweight financial report for customer-facing transparency."""
    return generate_financial_report(as_of_date)


class BeaverChoiceSystem:
    """Encapsulates the Beaver's Choice multi-agent workflow."""

    def __init__(self, model_name: str = "gpt-4o-mini") -> None:
        configure_openai_environment()
        model_ref = f"openai:{model_name}"
        orchestration_settings = ModelSettings(temperature=0.2, max_output_tokens=800)
        worker_settings = ModelSettings(temperature=0.15, max_output_tokens=900)

        self.orchestrator = Agent(
            model_ref,
            name="northstar_orchestrator",
            instructions=self._build_orchestrator_instructions(),
            output_type=ORCHESTRATOR_OUTPUT,
            model_settings=orchestration_settings,
        )
        self.inventory_agent = Agent(
            model_ref,
            name="stock_sentinel",
            instructions=self._build_inventory_instructions(),
            tools=[
                Tool(tool_inventory_snapshot),
                Tool(tool_item_stock_probe),
                Tool(tool_plan_restock_purchase),
            ],
            output_type=INVENTORY_OUTPUT,
            model_settings=worker_settings,
        )
        self.quote_agent = Agent(
            model_ref,
            name="quote_engineer",
            instructions=self._build_quote_instructions(),
            tools=[
                Tool(tool_lookup_quote_history),
                Tool(tool_cash_window),
                Tool(tool_price_builder),
            ],
            output_type=QUOTE_OUTPUT,
            model_settings=worker_settings,
        )
        self.fulfillment_agent = Agent(
            model_ref,
            name="fulfillment_ranger",
            instructions=self._build_fulfillment_instructions(),
            tools=[
                Tool(tool_record_sale),
                Tool(tool_financial_snapshot),
            ],
            output_type=FULFILLMENT_OUTPUT,
            model_settings=worker_settings,
        )

    def process_request(self, request_row: Dict[str, Any]) -> Dict[str, Any]:
        payload = self._prepare_payload(request_row)
        try:
            plan = self.orchestrator.run_sync(self._orchestrator_prompt(payload)).output
        except Exception as exc:
            message = (
                "We encountered an internal routing issue while drafting your plan. "
                "Please retry shortly or contact your account rep."
            )
            print(f"[WARN] Orchestrator failure: {exc}")
            return {"customer_message": message, "error": str(exc)}

        actionable_items = [
            item
            for item in plan.get("items", [])
            if item["normalized_item"] and item["normalized_item"] != "UNSUPPORTED" and item["quantity"] > 0
        ]

        inventory_result = None
        if actionable_items and plan.get("needs_inventory", True):
            inventory_payload = {
                "items": actionable_items,
                "request_date": payload["request_date"],
                "due_date": plan.get("due_date") or payload["request_date"],
                "need_size": payload["need_size"],
            }
            try:
                inventory_result = self.inventory_agent.run_sync(
                    self._inventory_prompt(inventory_payload)
                ).output
            except Exception as exc:
                print(f"[WARN] Inventory agent failure: {exc}")

        quote_result = None
        if actionable_items and plan.get("needs_quote", True):
            quote_payload = {
                "items": actionable_items,
                "inventory": inventory_result["lines"] if inventory_result else [],
                "request_date": payload["request_date"],
                "customer_context": payload,
                "discount_strategy": plan.get("discount_strategy", "balanced"),
            }
            try:
                quote_result = self.quote_agent.run_sync(
                    self._quote_prompt(quote_payload)
                ).output
            except Exception as exc:
                print(f"[WARN] Quote agent failure: {exc}")

        fulfillment_result = None
        ready_lines = []
        if quote_result:
            ready_lines = [
                line
                for line in quote_result["quote_lines"]
                if line["status"].lower() in {"ready", "partial"}
            ]
        if ready_lines and plan.get("needs_fulfillment", True):
            fulfillment_payload = {
                "lines": ready_lines,
                "request_date": payload["request_date"],
                "due_date": plan.get("due_date") or payload["request_date"],
                "quote_total": quote_result.get("total_amount", 0.0) if quote_result else 0.0,
                "inventory": inventory_result["lines"] if inventory_result else [],
            }
            try:
                fulfillment_result = self.fulfillment_agent.run_sync(
                    self._fulfillment_prompt(fulfillment_payload)
                ).output
            except Exception as exc:
                print(f"[WARN] Fulfillment agent failure: {exc}")

        final_message = self._final_customer_message(
            payload,
            plan,
            inventory_result,
            quote_result,
            fulfillment_result,
        )

        return {
            "plan": plan,
            "inventory": inventory_result,
            "quote": quote_result,
            "fulfillment": fulfillment_result,
            "customer_message": final_message,
            "quote_total": quote_result.get("total_amount", 0.0) if quote_result else 0.0,
            "fulfilled_items": fulfillment_result["fulfilled_items"] if fulfillment_result else [],
        }

    def _prepare_payload(self, row: Dict[str, Any]) -> Dict[str, Any]:
        request_date = row["request_date"]
        if isinstance(request_date, datetime):
            request_iso = request_date.strftime("%Y-%m-%d")
        else:
            request_iso = str(request_date)
        return {
            "job": row.get("job", "customer"),
            "need_size": row.get("need_size", ""),
            "event": row.get("event", ""),
            "request": row.get("request", ""),
            "request_date": request_iso,
        }

    def _build_orchestrator_instructions(self) -> str:
        allowed = ", ".join(CANONICAL_ITEM_NAMES[:20]) + ", ..."
        return textwrap.dedent(
            f"""
            You are NorthStar, Beaver's Choice orchestrator. Map customer text to <=4 SKUs using
            this catalog (examples: {allowed}). Any unsupported item should get normalized_item = "UNSUPPORTED".
            Produce structured JSON that flags which downstream agents (inventory, reorder, quote, fulfillment) must run.
            Always include at least one actionable line when you detect a valid SKU and estimate urgency (high/medium/low).
            """
        ).strip()

    def _build_inventory_instructions(self) -> str:
        return textwrap.dedent(
            """
            You are Stock Sentinel. Steps:
            1. Call inventory_snapshot first to see overall stock for the given request date.
            2. For each requested item call item_stock_probe before deciding status.
            3. If stock is insufficient but reordering is allowed, call plan_restock_purchase with the missing units.
            4. Produce JSON with a line per item describing the decision. ready_units represents what can ship by the due date.
            """
        ).strip()

    def _build_quote_instructions(self) -> str:
        return textwrap.dedent(
            """
            You are Quote Engineer. Always ground your rationale in:
            - quote_lookup with relevant keywords (call it at least once);
            - cash_window to ensure we do not overdiscount;
            - price_builder for every approved line to compute the actual price.
            Decline lines that inventory marked as unavailable and justify them in quote_explanation.
            """
        ).strip()

    def _build_fulfillment_instructions(self) -> str:
        return textwrap.dedent(
            """
            You are Fulfillment Ranger. For each ready line:
            - Call log_sale to record the confirmed transaction on the request date.
            - Summarize logistics referencing delivery windows from the inventory notes.
            Pull a financial_snapshot to mention overall readiness (do not expose cash balances exactly;
            speak qualitatively in customer_message).
            """
        ).strip()

    def _orchestrator_prompt(self, payload: Dict[str, Any]) -> str:
        return textwrap.dedent(
            f"""
            Customer role: {payload['job']}
            Event: {payload['event']} (size: {payload['need_size']})
            Request date: {payload['request_date']}
            Full text:
            {payload['request']}
            """
        ).strip()

    def _inventory_prompt(self, payload: Dict[str, Any]) -> str:
        return textwrap.dedent(
            f"""
            Request date: {payload['request_date']}
            Due by: {payload['due_date']}
            Need size: {payload['need_size']}
            Items:
            {json.dumps(payload['items'], indent=2)}
            """
        ).strip()

    def _quote_prompt(self, payload: Dict[str, Any]) -> str:
        return textwrap.dedent(
            f"""
            Request date: {payload['request_date']}
            Customer metadata: job {payload['customer_context']['job']}, event {payload['customer_context']['event']}
            Discount strategy: {payload['discount_strategy']}
            Inventory context:
            {json.dumps(payload['inventory'], indent=2)}
            Requested items:
            {json.dumps(payload['items'], indent=2)}
            Use quote_lookup keywords extracted from the request narrative and event type.
            """
        ).strip()

    def _fulfillment_prompt(self, payload: Dict[str, Any]) -> str:
        return textwrap.dedent(
            f"""
            Request date: {payload['request_date']}
            Promised delivery date: {payload['due_date']}
            Quote total: {payload['quote_total']}
            Ready lines:
            {json.dumps(payload['lines'], indent=2)}
            Inventory notes:
            {json.dumps(payload['inventory'], indent=2)}
            """
        ).strip()

    def _final_customer_message(
        self,
        payload: Dict[str, Any],
        plan: Dict[str, Any],
        inventory: Optional[Dict[str, Any]],
        quote: Optional[Dict[str, Any]],
        fulfillment: Optional[Dict[str, Any]],
    ) -> str:
        if fulfillment and fulfillment.get("customer_message"):
            return fulfillment["customer_message"]
        if quote:
            return f"{quote['quote_explanation']} Total quoted amount: ${quote['total_amount']:.2f}."
        if inventory:
            return inventory.get("decision_notes", "Inventory review complete.")
        return (
            f"We received your request for the {payload['event']} and will follow up with a quote shortly."
        )


# Run your test scenarios by writing them here. Make sure to keep track of them.

def run_test_scenarios():
    
    print("Initializing Database...")
    init_database(db_engine)
    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    ############
    ############
    ############
    # INITIALIZE YOUR MULTI AGENT SYSTEM HERE
    ############
    ############
    ############
    system = BeaverChoiceSystem()

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        # Process request
        request_payload = row.to_dict()
        request_payload["request_date"] = row["request_date"]
        agent_result = system.process_request(request_payload)
        response = agent_result.get("customer_message", "No response generated.")

        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "quote_total": agent_result.get("quote_total", 0.0),
                "fulfilled_items": ";".join(agent_result.get("fulfilled_items", [])),
                "response": response,
            }
        )

        time.sleep(1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    # Save results
    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


if __name__ == "__main__":
    results = run_test_scenarios()
