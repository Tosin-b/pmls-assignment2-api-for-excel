# FastAPI app for the skin clinic campaign analysis.
# Run locally with: uvicorn main:app --reload

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

df = pd.read_csv("skin clinic campaign.csv")
df["Responded"] = df["Response_to_Campaign"].map({"Yes": 1, "No": 0})
df["Products"] = pd.cut(df["Unique_Products_Purchased"], bins=[0, 4, 8, 1000], labels=["1-4", "5-8", ">8"])


@app.get("/")
def home():
    return {"message": "API is running. Go to /campaign-analysis"}


@app.get("/campaign-analysis", response_class=HTMLResponse)
def campaign_analysis():
    html = "<h1>Skin Clinic Campaign Analysis</h1>"

    for col in ["Gender", "AgeGroup", "Purchase_Last_Quarter", "Products"]:
        table = df.groupby(col, observed=True)["Responded"].mean().mul(100).round(2)
        table = table.reset_index(name="Response_Rate_%")
        html += f"<h2>{col} vs Response Rate</h2>"
        html += table.to_html(index=False)

    return html
