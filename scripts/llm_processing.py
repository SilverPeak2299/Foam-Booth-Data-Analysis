from gemini_request import generate
import os
import json
from dotenv import load_dotenv
import pandas as pd
from supabase import create_client, Client
import re

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API"]

CHUNK_SIZE = 10

if os.path.exists("progress.json"):
    with open("progress.json") as f:
        progress = json.load(f)
else:
    progress = {'last_processed_chunk': -1}

starting_point = progress['last_processed_chunk'] * CHUNK_SIZE + 1
df = pd.read_csv("./data/data.TXT", skiprows=[i for i in range(1, starting_point)], nrows=CHUNK_SIZE)

to_send = df[["Invoice #", "Item Number", "Description", "Quantity", "Price", "Total"]].to_csv()

gemini_response = generate(to_send, GEMINI_API_KEY)

results = json.loads(str(gemini_response))

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


foam = re.compile(r"\w+/\w+R?")
for line in results["Line"]:
    existing_tables = (supabase
              .table("invoice")
              .select("invoice_id")
              .eq("invoice_id", str(line["invoice number"]))
              .execute()
              )

    if existing_tables.data == []:

        invoice_number = int(line["invoice number"])
        row = df[df["Invoice #"].astype(int) == invoice_number].iloc[0]
        date = row["Date"]
        customer_name = row["Co./Last Name"]

        supabase.table("invoice").insert(
            {
                "invoice_id": str(line["invoice number"]),
                "customer_name": customer_name,
                "date": date
            }
        ).execute()
    
    insert_dict = {
        "invoice_id": line["invoice number"],
        "type": line["Type"],
        "price": line["Price"],
        "item_desc": None
    }

    if foam.match(line["Type"]):
        insert_dict["item_desc"] = json.dumps(line["Dimentions"])
        

    elif line["Type"] == "Fabric":
        insert_dict["item_desc"] = {
            "fabric_name": line["fabric_name"],
            "fabric_length": line["fabric_length"]
            }

    try:
        response =(supabase
        .table("invoice_item")
        .insert(
            insert_dict
        ).execute()
        )

    except Exception as e:
        with open("failed_inserts.txt", "a") as f:
            f.write(f"{insert_dict}: {e}")
 

progress['last_processed_chunk'] += 1
with open("progress.json", "w") as f:
    json.dump(progress, f, indent=4)



    



