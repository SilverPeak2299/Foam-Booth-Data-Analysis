from google import genai
from google.genai import types

def generate(csv_data: str, key):
    client = genai.Client(
        api_key=key,
    )

    model = "gemini-2.5-flash-preview-04-17"
    
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            properties = {
                "Line": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["Type", "invoice number"],
                        properties = {
                            "Type": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "Price": genai.types.Schema(
                                type = genai.types.Type.NUMBER,
                            ),
                            "Dimentions": genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                properties = {
                                    "Height": genai.types.Schema(
                                        type = genai.types.Type.NUMBER,
                                    ),
                                    "Width": genai.types.Schema(
                                        type = genai.types.Type.NUMBER,
                                    ),
                                    "Length": genai.types.Schema(
                                        type = genai.types.Type.NUMBER,
                                    ),
                                },
                            ),
                            "invoice number": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "fabric_length": genai.types.Schema(
                                type = genai.types.Type.NUMBER,
                            ),
                            "fabric_name": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                        },
                    ),
                ),
            },
        ),

        system_instruction=[
            types.Part.from_text(text="""CSV Processing Instructions

Input Format
CSV columns: Invoice number, Item number, Description, Quantity, Price, Total

Processing Rules

General Guidelines
Process each line individually (processing 10 lines total)
Skip lines that are too difficult to parse correctly
Split lines into multiple entries only when pricing per piece is clear
Skip non-item lines (discounts, invoice balancing, banking details)

Product Type Classification

Foam Products:
HD, High Density, Seating Foam → Type: 29/200
MD, Medium Density → Type: 23/130
Premium Medium Density, Mattress Foam → Type: 30/130
Outdoor, Dryflow, Dricell → Type: 31/200R
Outdoor Soft, Dryflow Soft, Dricell → Type: 27/120R

Other Products:
Fabrics: Quantity represents length in meters, put the type as Fabric and store the fabric name
Covers, sewing, and related items → Category: Upholstery

Formatting Requirements
All dimensions must be in millimeters (mm)
Foam format: density/firmness (add R suffix for outdoor foam)

Items to Skip
Discount entries
Invoice balancing entries
Banking details
Any non-product line items
 """),
        ],
    )

    response = client.models.generate_content(
        model=model,
        contents= csv_data,
        config=generate_content_config
    )
    
    return response.candidates[0].content.parts[0].text
    
    

