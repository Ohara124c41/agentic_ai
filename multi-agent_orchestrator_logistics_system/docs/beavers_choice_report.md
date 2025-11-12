# Beaver's Choice Multi-Agent System Report

## 1. Starter Helper Function Notes
- generate_sample_inventory(paper_supplies, coverage=0.4, seed=137): builds a repeatable subset of the canonical paper catalog with randomized stock/minimum levels for initializing the SQLite tables.
- init_database(db_engine, seed=137): creates and seeds the SQLite schema (	ransactions, quote_requests, quotes, inventory) plus starter cash/stock transactions using the generated inventory snapshot.
- create_transaction(item_name, transaction_type, quantity, price, date): inserts a single stock order or sales record into 	ransactions, returning the new row id.
- get_all_inventory(as_of_date): aggregates stock orders and sales up to a date to compute on-hand units for every item that still has positive stock.
- get_stock_level(item_name, as_of_date): similar to get_all_inventory but scoped to one item, returning a tiny DataFrame with the net stock number.
- get_supplier_delivery_date(input_date_str, quantity): provides a deterministic lead-time estimate based on requested quantity buckets to help plan replenishment.
- get_cash_balance(as_of_date): subtracts cumulative stock purchases from cumulative sales to get the available cash on a date.
- generate_financial_report(as_of_date): wraps cash balance, inventory valuation, and best sellers into a single dictionary for executive-style dashboards.
- search_quote_history(search_terms, limit=5): mines both quote_requests and quotes tables for similar past deals so agents can ground new quotes in precedent.

## 2. Architecture Overview (to be completed)

**Workflow diagram:** `docs/beavers_choice_workflow.png` captures the high-level routing logic. Customer text flows through the **NorthStar Orchestrator** agent, which parses intent, aligns it with our SKU catalog, and flags which of the downstream workers should run.

**Agent roster (max five as required):**
- **NorthStar Orchestrator** – `pydantic-ai` agent that produces a structured plan per inquiry (items, urgency, due dates, delegation flags). It ensures all downstream calls stay under the five-agent cap.
- **Stock Sentinel** – inventory & replenishment agent backed by tools that wrap `get_all_inventory`, `get_stock_level`, `get_supplier_delivery_date`, and `create_transaction`. It decides if we can fulfill from stock or need to reorder without breaking cash or lead-time policies.
- **Quote Engineer** – pricing strategist that mixes `search_quote_history`, `get_cash_balance`, and a deterministic `price_builder` tool to output transparent quotes (per-line math + rationale).
- **Fulfillment Ranger** – closes the loop by logging approved sales via `create_transaction`, auditing the books with `generate_financial_report`, and producing customer-facing confirmations or polite rejections.

**Data flow summary:**
- Orchestrator consumes text + metadata and outputs normalized items and delegation notes.
- Items that require validation are sent to Stock Sentinel, which in turn may book supplier orders (future-dated) via helper functions.
- Quote Engineer only prices items cleared by the inventory agent and always annotates quotes with the historical context it retrieved from `search_quote_history`.
- Fulfillment Ranger records the final sale when quotes are accepted and embeds `generate_financial_report` snapshots into the final narrative so customers see the operational status they care about (cash remains internal).

## 3. Evaluation Summary (to be completed)

`project_starter.py` ships with `run_test_scenarios()`, which loops through `quote_requests_sample.csv`, routes every request via the four-agent stack, and logs the resulting balances plus customer-facing responses into `test_results.csv`. Running it requires the Udacity/Vocareum key because each agent is a `pydantic-ai` OpenAI client. (Set `UDACITY_OPENAI_API_KEY` in `.env` and execute `python project_starter.py`.)

- Our recorded run (`logs/run_full.txt`, `test_results.csv`) shows **20 total requests processed** between 2025‑04‑01 and 2025‑04‑17. The system finished with **cash $43,394.40** (down from $45,000) and **inventory $5,438.10**, demonstrating real sales and purchase orders flowing through the helper functions.
- **At least five requests changed the cash balance** via sales transactions (IDs 7, 8, 15, 16, 20), while many others only triggered restock orders, satisfying the rubric requirement of ≥3 cash movements.
- **Four quotes cleared with non-zero totals** (requests 7, 8, 15, 20) and the CSV clearly records partial or declined outcomes for the rest (e.g., request 8 declines the 2,000-unit A5 line, request 20 declines Flyers entirely). This ensures “not all requests fulfilled” is both traceable and explained.
- Strengths observed: Stock Sentinel consistently initiated supplier orders (e.g., envelopes, disposable cups) without overspending cash; Quote Engineer cited availability and discounts in every response; Fulfillment Ranger never exposed raw balances, instead using qualitative delivery commitments. Improvement areas: we still return empty `fulfilled_items` strings in the CSV (IDs are stored internally), and negotiations stop after the first decline rather than proposing substitutes.

## 4. Improvement Ideas (to be completed)

1. **Negotiation & upsell agent** – add a fifth (optional) agent that monitors historical win rates, suggests package alternatives, and loops back into the orchestrator when it detects a probable decline (e.g., offer recycled stock when glossy paper is unavailable).
2. **Simulation-grade testing** – extend `run_test_scenarios()` with a seed parameter and pytest hook so CI can replay deterministic prompts using stored model responses; pair it with fixtures for additional CSV test suites (enterprise vs. SMB) to stress different inventory mixes.
3. **Lead-time aware inventory model** – persist supplier delivery dates inside a separate table and have Stock Sentinel aggregate outstanding purchase orders, preventing over-ordering an item whose replenishment is already en route.
