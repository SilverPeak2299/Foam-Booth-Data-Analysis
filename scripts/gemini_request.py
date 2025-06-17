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
                        required = ["Type", "invoice number", "Price"],
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
            types.Part.from_text(text="""
                CSV Processing Instructions
                
                Input Format:
                CSV columns: Invoice number, Item number, Description, Quantity, Price, Total
                
                Processing Rules:
                
                General Guidelines:
                1. Process each line individually (processing up to 10 lines total).
                2. Skip lines that are too difficult to parse correctly.
                3. Split lines into multiple entries only when pricing per piece is clear.
                4. Skip non-item lines (e.g., discounts, invoice balancing, banking details).
                
                Product Type Classification:
                1. Foam Products:
                   - Use the following shorthand for common foam types:
                     - HD, High Density, Seating Foam → Type: 29/200
                     - MD, Medium Density → Type: 23/130
                     - Premium Medium Density, Mattress Foam → Type: 30/130
                     - Outdoor, Dryflow, Dricell → Type: 31/200R
                     - Outdoor Soft, Dryflow Soft, Dricell → Type: 27/120R
                   - For foam products that match the density/firmness convention but are not explicitly listed above, classify them using their density/firmness (e.g., Type: 25/150) and include the "R" suffix for outdoor foam types.
                   - Ensure all foam products matching the convention are processed.
                
                2. Fabrics:
                   - Quantity represents length in meters.
                   - Type: Fabric.
                   - Store the fabric name explicitly in the fabric_name field.
                   - Only classify items as Fabric if the description explicitly mentions fabric-related terms (e.g., fabric, textile, cloth). Do not classify unrelated items as Fabric.
                
                3. Other Products:
                   - Covers, sewing, and related items → Category: Upholstery.
                   - Dacron → Category: Dacron.
                
                Formatting Requirements:
                1. All dimensions must be in millimeters (mm).
                2. Invoice number must be an integer.
                3. Foam format: density/firmness (add "R" suffix for outdoor foam).
                
                Items to Skip:
                1. Discount entries.
                2. Invoice balancing entries.
                3. Banking details.
                4. Any non-product line items.
                
                Chain of Thought Reasoning:
                For each line in the CSV:
                1. Step 1: Parse the line and extract relevant fields (Invoice number, Item number, Description, Quantity, Price, Total).
                2. Step 2: Check if the line matches any of the predefined categories (Foam Products, Fabrics, Other Products).
                   - If it matches a Foam Product, apply the shorthand or fallback classification based on density/firmness.
                   - If it matches a Fabric, ensure the description explicitly mentions fabric-related terms.
                   - If it matches Other Products, classify accordingly.
                3. Step 3: If the line does not fit into any category, classify it as "Unknown Type."
                4. Step 4: Format the output according to the requirements (e.g., dimensions in mm, integer invoice number).
                5. Step 5: Log skipped lines with reasons for skipping (e.g., ambiguous description, non-product line item).
                6. Step 6: Return the processed line in JSON format.
                
                Additional Notes:
                - Ensure strict adherence to the classification rules.
                - Prioritize processing all foam products, using shorthand for common types and density/firmness for others.
                - Provide detailed reasoning for each step to ensure transparency and accuracy. """),
        ],
    )

    response = client.models.generate_content(
        model=model,
        contents= csv_data,
        config=generate_content_config
    )
    
    return response.candidates[0].content.parts[0].text
    
    

