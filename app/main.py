# FastAPI app for the skin clinic campaign analysis.
# Returns the four response rate tables as an HTML page so they show up as real tables
# in the browser, and so Excel Power Query can pick them up with "From Web".

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Skin Clinic Campaign Analysis")

DATA_FILE = "skin clinic campaign.csv"

# load once at startup, the file never changes while the app is running
df = pd.read_csv(DATA_FILE)
df["Responded"] = df["Response_to_Campaign"].map({"Yes": 1, "No": 0})

# keep the age groups in a sensible order instead of alphabetical
df["AgeGroup"] = pd.Categorical(df["AgeGroup"], categories=["<30", "30-50", ">50"], ordered=True)

# same product bins as the notebook
df["ProductGroup"] = pd.cut(df["Unique_Products_Purchased"],
                            bins=[0, 4, 8, float("inf")],
                            labels=["1-4", "5-8", ">8"])


def response_table(group_col):
    out = df.groupby(group_col, observed=True).agg(
        Customers=("Responded", "size"),
        Responded=("Responded", "sum")
    ).reset_index()
    out["Response_Rate_%"] = (out["Responded"] / out["Customers"] * 100).round(2)
    return out


@app.get("/")
def home():
    return {"message": "Campaign analysis API is running. Go to /campaign-analysis for the tables."}


@app.get("/campaign-analysis", response_class=HTMLResponse)
def campaign_analysis():
    tables = [
        ("1. Gender vs Response Rate", response_table("Gender")),
        ("2. Age Group vs Response Rate", response_table("AgeGroup")),
        ("3. Purchase Last Quarter vs Response Rate", response_table("Purchase_Last_Quarter")),
        ("4. Unique Products Purchased vs Response Rate", response_table("ProductGroup")),
    ]

    overall = round(df["Responded"].mean() * 100, 2)

    html = """<html>
<head>
  <title>Skin Clinic Campaign Analysis</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 30px; }
    table { border-collapse: collapse; margin-bottom: 30px; }
    th, td { border: 1px solid #999; padding: 6px 14px; text-align: left; }
    th { background: #eee; }
  </style>
</head>
<body>
"""
    html += "<h1>Skin Clinic Campaign Analysis</h1>"
    html += f"<p>{len(df):,} customers, overall response rate {overall}%.</p>"

    for title, table in tables:
        html += f"<h2>{title}</h2>"
        html += table.to_html(index=False)

    html += "</body></html>"
    return html
