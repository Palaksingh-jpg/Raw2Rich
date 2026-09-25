import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

GRAPH_DIR = Path(__file__).parent / "graphs"
GRAPH_DIR.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv("superstore_cleaned.csv")

print("Dataset Shape:", df.shape)
print("\nFirst 5 Rows:")
print(df.head())

# Convert Order_Date to datetime
df["Order_Date"] = pd.to_datetime(df["Order_Date"])

# Extract year and month
df["Year"] = df["Order_Date"].dt.year
df["Month"] = df["Order_Date"].dt.month
df["Month_Name"] = df["Order_Date"].dt.month_name()

# Basic information
print("\nBASIC INFORMATION")
print("\nMissing Values:")
print(df.isnull().sum())

print("\nSummary Statistics:")
print(df[["Sales", "Profit", "Quantity"]].describe())

# Total Sales, Profit and Quantity
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_quantity = df["Quantity"].sum()

print("\nTOTAL SALES, PROFIT AND QUANTITY")
print("Total Sales:", total_sales)
print("Total Profit:", total_profit)
print("Total Quantity Sold:", total_quantity)

# Sales by Category
sales_category = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)

print("\nSales by Category:")
print(sales_category)

plt.figure(figsize=(8, 5))
sales_category.plot(kind="bar")
plt.title("Sales by Category")
plt.xlabel("Category")
plt.ylabel("Sales")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "sales_by_category.png")
plt.close()

# Profit by Category
profit_category = df.groupby("Category")["Profit"].sum().sort_values(ascending=False)

print("\nProfit by Category:")
print(profit_category)

plt.figure(figsize=(8, 5))
profit_category.plot(kind="bar")
plt.title("Profit by Category")
plt.xlabel("Category")
plt.ylabel("Profit")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "profit_by_category.png")
plt.close()

# Quantity by Category
quantity_category = df.groupby("Category")["Quantity"].sum().sort_values(ascending=False)

print("\nQuantity by Category:")
print(quantity_category)

plt.figure(figsize=(8, 5))
quantity_category.plot(kind="bar")
plt.title("Quantity Sold by Category")
plt.xlabel("Category")
plt.ylabel("Quantity")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "quantity_by_category.png")
plt.close()

# Sales by Sub-category
sales_subcategory = df.groupby("Sub_category")["Sales"].sum().sort_values(ascending=False)

print("\nSales by Sub-category:")
print(sales_subcategory)

plt.figure(figsize=(10, 6))
sales_subcategory.plot(kind="bar")
plt.title("Sales by Sub-category")
plt.xlabel("Sub-category")
plt.ylabel("Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "sales_by_subcategory.png")
plt.close()

# Profit by Sub-category
profit_subcategory = df.groupby("Sub_category")["Profit"].sum().sort_values(ascending=False)

print("\nProfit by Sub-category:")
print(profit_subcategory)

plt.figure(figsize=(10, 6))
profit_subcategory.plot(kind="bar")
plt.title("Profit by Sub-category")
plt.xlabel("Sub-category")
plt.ylabel("Profit")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "profit_by_subcategory.png")
plt.close()

# Quantity by Sub-category
quantity_subcategory = df.groupby("Sub_category")["Quantity"].sum().sort_values(ascending=False)

print("\nQuantity by Sub-category:")
print(quantity_subcategory)

plt.figure(figsize=(10, 6))
quantity_subcategory.plot(kind="bar")
plt.title("Quantity by Sub-category")
plt.xlabel("Sub-category")
plt.ylabel("Quantity")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "quantity_by_subcategory.png")
plt.close()

# Sales by Region
sales_region = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)

print("\nSales by Region:")
print(sales_region)

plt.figure(figsize=(10, 6))
sales_region.plot(kind="bar")
plt.title("Sales by Region")
plt.xlabel("Region")
plt.ylabel("Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "sales_by_region.png")
plt.close()

# Profit by Region
profit_region = df.groupby("Region")["Profit"].sum().sort_values(ascending=False)

print("\nProfit by Region:")
print(profit_region)

plt.figure(figsize=(10, 6))
profit_region.plot(kind="bar")
plt.title("Profit by Region")
plt.xlabel("Region")
plt.ylabel("Profit")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "profit_by_region.png")
plt.close()

# Sales by Year
sales_year = df.groupby("Year")["Sales"].sum()

print("\nSales by Year:")
print(sales_year)

plt.figure(figsize=(8, 5))
sales_year.plot(kind="line", marker="o")
plt.title("Yearly Sales Trend")
plt.xlabel("Year")
plt.ylabel("Sales")
plt.grid(True)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "sales_by_year.png")
plt.close()

# Profit by Year
profit_year = df.groupby("Year")["Profit"].sum()

print("\nProfit by Year:")
print(profit_year)

plt.figure(figsize=(8, 5))
profit_year.plot(kind="line", marker="o")
plt.title("Yearly Profit Trend")
plt.xlabel("Year")
plt.ylabel("Profit")
plt.grid(True)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "profit_by_year.png")
plt.close()

# Quantity by Year
quantity_year = df.groupby("Year")["Quantity"].sum()

print("\nQuantity by Year:")
print(quantity_year)

plt.figure(figsize=(8, 5))
quantity_year.plot(kind="line", marker="o")
plt.title("Yearly Quantity Trend")
plt.xlabel("Year")
plt.ylabel("Quantity")
plt.grid(True)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "quantity_by_year.png")
plt.close()

# Monthly Sales
monthly_sales = df.groupby(
    df["Order_Date"].dt.to_period("M")
)["Sales"].sum()

print("\nMonthly Sales:")
print(monthly_sales)

plt.figure(figsize=(12, 6))
monthly_sales.plot(kind="line")
plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.grid(True)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "monthly_sales.png")
plt.close()

# Monthly Profit
monthly_profit = df.groupby(
    df["Order_Date"].dt.to_period("M")
)["Profit"].sum()

print("\nMonthly Profit:")
print(monthly_profit)

plt.figure(figsize=(12, 6))
monthly_profit.plot(kind="line")
plt.title("Monthly Profit Trend")
plt.xlabel("Month")
plt.ylabel("Profit")
plt.grid(True)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "monthly_profit.png")
plt.close()

# Category and Sub-category analysis
category_subcategory = df.groupby(
    ["Category", "Sub_category"]
)[["Sales", "Profit", "Quantity"]].sum()

print("\nCategory + Sub-category Analysis:")
print(category_subcategory)

# Sales vs Profit relationship
correlation = df["Sales"].corr(df["Profit"])

print("\nSALES VS PROFIT RELATIONSHIP")
print("Sales-Profit Correlation:", correlation)

plt.figure(figsize=(8, 6))
plt.scatter(df["Sales"], df["Profit"], alpha=0.4)
plt.title("Sales vs Profit")
plt.xlabel("Sales")
plt.ylabel("Profit")
plt.grid(True)
plt.tight_layout()
plt.savefig(GRAPH_DIR / "sales_vs_profit.png")
plt.close()

# Important insights
print("\nIMPORTANT INSIGHTS")

print(
    "\nHighest Sales Category:",
    sales_category.idxmax(),
    "->",
    sales_category.max()
)

print(
    "Highest Profit Category:",
    profit_category.idxmax(),
    "->",
    profit_category.max()
)

print(
    "Highest Quantity Category:",
    quantity_category.idxmax(),
    "->",
    quantity_category.max()
)

print(
    "Highest Sales Sub-category:",
    sales_subcategory.idxmax(),
    "->",
    sales_subcategory.max()
)

print(
    "Lowest Profit Sub-category:",
    profit_subcategory.idxmin(),
    "->",
    profit_subcategory.min()
)

print(
    "Highest Sales Region:",
    sales_region.idxmax(),
    "->",
    sales_region.max()
)

print(
    "Highest Profit Region:",
    profit_region.idxmax(),
    "->",
    profit_region.max()
)

print(
    "Highest Sales Year:",
    sales_year.idxmax(),
    "->",
    sales_year.max()
)

print(
    "Highest Profit Year:",
    profit_year.idxmax(),
    "->",
    profit_year.max()
)

print(
    "\nSales-Profit Correlation:",
    correlation
)