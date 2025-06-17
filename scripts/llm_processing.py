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
df = pd.read_csv("./data/stage_1_output.txt", skiprows=[i for i in range(1, starting_point)], nrows=CHUNK_SIZE)

to_send = df[["Invoice #", "Item Number", "Description", "Quantity", "Price", "Total"]].to_csv()

gemini_response = generate(to_send, GEMINI_API_KEY)

results = json.loads(str(gemini_response))

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


foam = re.compile(r"\w+/\w+R?")
def validate_llm_output(line):
    try:
        if "invoice number" in line:
            line["invoice number"] = int(float(line["invoice number"]))
        if "Price" in line:
            line["Price"] = float(line["Price"])

        # Validation checks
        required_fields = ["invoice number", "Type", "Price"]
        for field in required_fields:
            if field not in line or line[field] is None:
                return False, f"Missing or null field: {field}"

        if not isinstance(line["invoice number"], int):
            return False, "Invoice number must be an integer."

        if not isinstance(line["Price"], (int, float)):
            return False, "Price must be a number."

        if line["Type"] == "Fabric":
            if "fabric_name" not in line or "fabric_length" not in line:
                return False, "Fabric entries must include fabric_name and fabric_length."

        return True, None
    except ValueError as e:
        return False, f"Type-casting error: {str(e)}"


for line in results["Line"]:
    is_valid, error_message = validate_llm_output(line)
    if not is_valid:
        with open("failed_inserts.txt", "a") as f:
            f.write(f"Invalid entry: {line}\n")
            f.write(f"Error: {error_message}\n")
            f.write("-" * 80 + "\n")
        continue

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
            f.write(f"Failed to insert: {insert_dict}\n")
            f.write(f"Error: {str(e)}\n")
            f.write("-" * 80 + "\n")
 

progress['last_processed_chunk'] += 1
with open("progress.json", "w") as f:
    json.dump(progress, f, indent=4)



    



