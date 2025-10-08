# import os
# import json
# import random
# import webbrowser
# from pathlib import Path
# from datetime import date, timedelta
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML, CSS
# from config import API_KEY, MODEL_NAME

# # Import OpenAI library
# import openai

# # --- CONFIGURATION ---
# # The API_KEY check is already handled in config.py
# # Initialize OpenAI client globally
# client = openai.OpenAI(api_key=API_KEY)


# def get_structured_data_from_llm(user_query: str):
#     """Uses the OpenAI LLM to extract detailed structured data from a user query."""
    
#     # Prompt adapted for OpenAI's Chat Completions API
#     prompt_messages = [
#         {"role": "system", "content": """
#         You are an expert data extraction AI. Your task is to meticulously analyze a user's request for a price quotation and extract all relevant information into a structured JSON format.

#         **Instructions & Chain-of-Thought:**
#         1.  **Analyze Request:** I will read the user's request.
#         2.  **Extract Customer Details:** I will identify all customer information: name, company name, full address, city, state, zip code, phone number, and email. If a piece of information is missing, I will use an empty string "".
#         3.  **Extract Line Items:** I will find each product/service, its quantity, and unit price. Discounts are separate items with negative prices.
#         4.  **Extract Tax Rates:** I will look for CGST and SGST rates.
#             - If the user gives "9% CGST and 9% SGST", I will set `cgst_rate` to 9.0 and `sgst_rate` to 9.0.
#             - If the user gives a total "18% GST", I will calculate `cgst_rate` as 18/2=9.0 and `sgst_rate` as 18/2=9.0.
#             - If no tax is mentioned, I will set both rates to 0.0.
#         5.  **Extract Currency:** I will identify the currency symbol (e.g., Rs., $, AED). Default to 'Rs.' if not specified.
#         6.  **Construct Final JSON:** I will assemble the data into the precise JSON schema below, without adding extra fields.

#         **JSON Schema to follow:**
#         ```json
#         {{
#             "customer": {{
#                 "name": "string",
#                 "company_name": "string",
#                 "address": "string",
#                 "city": "string",
#                 "state": "string",
#                 "zip": "string",
#                 "phone": "string",
#                 "email": "string"
#             }},
#             "items": [
#                 {{
#                     "description": "string",
#                     "qty": integer,
#                     "unit_price": float
#                 }}
#             ],
#             "cgst_rate": float,
#             "sgst_rate": float,
#             "currency": "string"
#         }}
#         ```
#         Ensure the output is *only* the JSON, no additional text or formatting outside the JSON block.
#         """},
#         {"role": "user", "content": f"User Request: {user_query}"}
#     ]
    
#     try:
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=prompt_messages,
#             response_format={"type": "json_object"} # Instructs the model to return a JSON object
#         )
#         # The content of the response is directly the JSON string
#         cleaned_response = response.choices[0].message.content.strip()
#         return json.loads(cleaned_response)
#     except openai.APIError as e: # Catch OpenAI specific API errors
#         print(f"OpenAI API Error: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"JSON Decode Error: Could not parse LLM response: {e}")
#         print(f"LLM Raw Response: {cleaned_response}")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred while calling the LLM: {e}")
#         return None

# def process_quote_data(structured_data: dict):
#     """Calculates all financial values, including CGST and SGST, for the quote."""
#     items = structured_data.get("items", [])
#     cgst_rate = structured_data.get("cgst_rate", 0)
#     sgst_rate = structured_data.get("sgst_rate", 0)
    
#     subtotal = 0
    
#     for item in items:
#         amount = item['qty'] * item['unit_price']
#         item['amount'] = amount
#         subtotal += amount
            
#     cgst_amount = subtotal * (cgst_rate / 100)
#     sgst_amount = subtotal * (sgst_rate / 100)
#     total = subtotal + cgst_amount + sgst_amount
    
#     summary = {
#         "subtotal": subtotal,
#         "cgst_amount": cgst_amount,
#         "sgst_amount": sgst_amount,
#         "total": total
#     }
#     return items, summary

# def generate_pdf(data: dict, output_filename: str):
#     """Renders the HTML template and converts it to a PDF."""
#     env = Environment(loader=FileSystemLoader('templates'))
#     template = env.get_template('template.html')
#     html_out = template.render(data)
    
#     css = CSS(filename='templates/style.css')
    
#     os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
#     # WeasyPrint needs absolute file URIs for local files like images
#     # The logo_path in data['company'] should already be a file URI (e.g., file:///...)
#     HTML(string=html_out, base_url=Path().cwd().as_uri()).write_pdf(output_filename, stylesheets=[css])
#     print(f"Successfully generated PDF: {output_filename}")
#     return output_filename # Return the path to the generated PDF


# def create_quotation(user_query: str, company_info: dict, preview_mode=False):
#     """Main function to orchestrate the quotation generation process.
#     Accepts company_info dict with 'name', 'address', 'phone', 'fax', 'email', 'logo_path'."""
#     print("1. Getting structured data from LLM...")
#     structured_data = get_structured_data_from_llm(user_query)
    
#     if not structured_data:
#         print("Could not process the request. Aborting.")
#         return None

#     print("2. Processing calculations...")
#     items, summary = process_quote_data(structured_data)
    
#     # Use the company_info passed into the function
#     company_details = {
#         "name": company_info.get("name", "Your Company Name"),
#         "address": company_info.get("address", "Company Address"),
#         "phone": company_info.get("phone", "Company Phone"),
#         "fax": company_info.get("fax", "Company Fax"),
#         "email": company_info.get("email", "Company Email"),
#         "logo_path": company_info.get("logo_path", "") # This should be a file URI, e.g., file:///path/to/logo.png
#     }
    
#     customer_data = structured_data.get("customer", {})
#     customer_details = {
#         "id": random.randint(100, 999), # Generate a random customer ID for now
#         "name": customer_data.get("name", ""),
#         "company_name": customer_data.get("company_name", ""),
#         "address": customer_data.get("address", ""),
#         "city": customer_data.get("city", ""),
#         "state": customer_data.get("state", ""),
#         "zip": customer_data.get("zip", ""),
#         "phone": customer_data.get("phone", ""),
#         "email": customer_data.get("email", "")
#     }

#     today = date.today()
#     valid_until_date = today + timedelta(days=30)
#     customer_name_for_file = customer_details['name'].replace(' ', '_') if customer_details['name'] else "Customer"
#     quote_number = f"{today.year}-{random.randint(1000, 9999)}"
    
#     # Ensure output directory exists
#     output_dir = "output"
#     os.makedirs(output_dir, exist_ok=True)
#     output_filename = os.path.join(output_dir, f"Quote_{quote_number}_{customer_name_for_file}.pdf")

#     template_data = {
#         "company": company_details,
#         "customer": customer_details,
#         "quote_number": quote_number,
#         "quote_date": f"{today.month}/{today.day}/{today.year}",
#         "valid_until": f"{valid_until_date.month}/{valid_until_date.day}/{valid_until_date.year}",
#         "items": items,
#         "summary": summary,
#         "cgst_rate": structured_data.get("cgst_rate", 0),
#         "sgst_rate": structured_data.get("sgst_rate", 0),
#         "currency": structured_data.get("currency", "Rs.")
#     }
    
#     print("3. Generating PDF...")
#     pdf_path = generate_pdf(template_data, output_filename)
    
#     if preview_mode:
#         print(f"4. Preview mode enabled. Opening {pdf_path}...")
#         try:
#             full_path = Path(pdf_path).resolve()
#             webbrowser.open(full_path.as_uri())
#         except Exception as e:
#             print(f"Could not open PDF for preview. Error: {e}")
            
#     return pdf_path # Return the path to the generated PDF









# import os
# import json
# import random
# import webbrowser
# from pathlib import Path
# from datetime import date, timedelta
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML, CSS
# from config import API_KEY, MODEL_NAME
# import openai

# # Initialize OpenAI client
# client = openai.OpenAI(api_key=API_KEY)

# def get_structured_data_from_llm(user_query: str):
#     """
#     Uses the OpenAI LLM to analyze a complex prompt containing both natural language
#     and a JSON block of raw product data, then extracts structured quote information.
#     """
    
#     # This new prompt empowers the AI to act as a data analyst.
#     prompt_messages = [
#         {"role": "system", "content": """
#         You are an expert data analysis and extraction AI. Your task is to interpret a user's request, which includes both plain text and a JSON data block, and convert it into a structured price quotation.

#         **Your Thought Process:**
#         1.  **Analyze Customer Info:** First, I will read the plain text part of the "User's Request" to extract all customer details (name, company, address, city, state, zip, phone, email) and tax information (CGST/SGST rates). If a detail is missing, I'll use an empty string "". If total GST is given (e.g., 18%), I'll split it equally into CGST and SGST (9% each).
        
#         2.  **Analyze Product Data:** Next, I will look at the "Selected Products Data (JSON)" block. This is an array of raw product objects.
        
#         3.  **Identify Key Columns:** For the entire list of products, I must determine which column holds the main product identifier (like 'Product Name', 'Item', 'description') and which column holds the price (like 'Price', 'Rate', 'cost', 'unit_price', 'MRP'). I will be consistent across all items.
        
#         4.  **Construct Line Items:** I will iterate through each product object in the JSON data. For each object, I will create a single line item for the final quote.
#             -   The `qty` will be taken directly from the "Quantity" field I added to each product object.
#             -   The `unit_price` will be the value from the price column I identified in step 3.
#             -   The `description` will be a clear, concise summary I create by combining the most important fields from the raw product data. For example, if the data has columns for 'Brand', 'Product Name', and 'Specs', I will combine them into a description like "Apple - iPhone 15 Pro (256GB, Blue)".

#         5.  **Assemble Final JSON:** Finally, I will assemble all the extracted information into the precise JSON schema below, ensuring every field is correct. I will not add any extra commentary or text outside the JSON block.

#         **JSON Schema to follow:**
#         ```json
#         {{
#             "customer": {{
#                 "name": "string",
#                 "company_name": "string",
#                 "address": "string",
#                 "city": "string",
#                 "state": "string",
#                 "zip": "string",
#                 "phone": "string",
#                 "email": "string"
#             }},
#             "items": [
#                 {{
#                     "description": "string",
#                     "qty": integer,
#                     "unit_price": float
#                 }}
#             ],
#             "cgst_rate": float,
#             "sgst_rate": float,
#             "currency": "string"
#         }}
#         ```
#         """},
#         {"role": "user", "content": user_query} # The user_query now contains the combined text and JSON data
#     ]
    
#     try:
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=prompt_messages,
#             response_format={"type": "json_object"}
#         )
#         cleaned_response = response.choices[0].message.content.strip()
#         return json.loads(cleaned_response)
#     except openai.APIError as e:
#         print(f"OpenAI API Error: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"JSON Decode Error: Could not parse LLM response: {e}")
#         print(f"LLM Raw Response: {cleaned_response}")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred while calling the LLM: {e}")
#         return None

# # --- The rest of the generator.py file (process_quote_data, generate_pdf, create_quotation) remains exactly the same. ---
# def process_quote_data(structured_data: dict):
#     """Calculates all financial values, including CGST and SGST, for the quote."""
#     items = structured_data.get("items", [])
#     cgst_rate = structured_data.get("cgst_rate", 0)
#     sgst_rate = structured_data.get("sgst_rate", 0)
    
#     subtotal = 0
    
#     for item in items:
#         # Ensure qty and unit_price are valid numbers before calculation
#         qty = item.get('qty', 0)
#         unit_price = item.get('unit_price', 0)
#         amount = qty * unit_price
#         item['amount'] = amount
#         subtotal += amount
            
#     cgst_amount = subtotal * (cgst_rate / 100)
#     sgst_amount = subtotal * (sgst_rate / 100)
#     total = subtotal + cgst_amount + sgst_amount
    
#     summary = {
#         "subtotal": subtotal,
#         "cgst_amount": cgst_amount,
#         "sgst_amount": sgst_amount,
#         "total": total
#     }
#     return items, summary

# def generate_pdf(data: dict, output_filename: str):
#     """Renders the HTML template and converts it to a PDF."""
#     env = Environment(loader=FileSystemLoader('templates'))
#     template = env.get_template('template.html')
#     html_out = template.render(data)
    
#     css = CSS(filename='templates/style.css')
    
#     os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
#     HTML(string=html_out, base_url=Path().cwd().as_uri()).write_pdf(output_filename, stylesheets=[css])
#     print(f"Successfully generated PDF: {output_filename}")
#     return output_filename

# def create_quotation(user_query: str, company_info: dict, preview_mode=False):
#     """Main function to orchestrate the quotation generation process."""
#     print("1. Getting structured data from LLM (Intelligent Analysis)...")
#     structured_data = get_structured_data_from_llm(user_query)
    
#     if not structured_data:
#         print("Could not process the request. Aborting.")
#         return None

#     print("2. Processing calculations...")
#     items, summary = process_quote_data(structured_data)
    
#     company_details = {
#         "name": company_info.get("name", "Your Company Name"),
#         "address": company_info.get("address", "Company Address"),
#         "phone": company_info.get("phone", "Company Phone"),
#         "fax": company_info.get("fax", "Company Fax"),
#         "email": company_info.get("email", "Company Email"),
#         "logo_path": company_info.get("logo_path", "")
#     }
    
#     customer_data = structured_data.get("customer", {})
#     customer_details = {
#         "id": random.randint(100, 999),
#         "name": customer_data.get("name", ""),
#         "company_name": customer_data.get("company_name", ""),
#         "address": customer_data.get("address", ""),
#         "city": customer_data.get("city", ""),
#         "state": customer_data.get("state", ""),
#         "zip": customer_data.get("zip", ""),
#         "phone": customer_data.get("phone", ""),
#         "email": customer_data.get("email", "")
#     }

#     today = date.today()
#     valid_until_date = today + timedelta(days=30)
#     customer_name_for_file = customer_details['name'].replace(' ', '_') if customer_details['name'] else "Customer"
#     quote_number = f"{today.year}-{random.randint(1000, 9999)}"
    
#     output_dir = "output"
#     os.makedirs(output_dir, exist_ok=True)
#     output_filename = os.path.join(output_dir, f"Quote_{quote_number}_{customer_name_for_file}.pdf")

#     template_data = {
#         "company": company_details,
#         "customer": customer_details,
#         "quote_number": quote_number,
#         "quote_date": f"{today.month}/{today.day}/{today.year}",
#         "valid_until": f"{valid_until_date.month}/{valid_until_date.day}/{valid_until_date.year}",
#         "items": items,
#         "summary": summary,
#         "cgst_rate": structured_data.get("cgst_rate", 0),
#         "sgst_rate": structured_data.get("sgst_rate", 0),
#         "currency": structured_data.get("currency", "Rs.")
#     }
    
#     print("3. Generating PDF...")
#     pdf_path = generate_pdf(template_data, output_filename)
    
#     if preview_mode:
#         print(f"4. Preview mode enabled. Opening {pdf_path}...")
#         try:
#             full_path = Path(pdf_path).resolve()
#             webbrowser.open(full_path.as_uri())
#         except Exception as e:
#             print(f"Could not open PDF for preview. Error: {e}")
            
#     return pdf_path



























# import os
# import json
# import random
# import webbrowser
# from pathlib import Path
# from datetime import date, timedelta
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML, CSS
# from config import API_KEY, MODEL_NAME
# import openai

# # Initialize OpenAI client
# client = openai.OpenAI(api_key=API_KEY)

# def get_structured_data_from_llm(user_query: str):
#     """
#     Uses the OpenAI LLM to interpret a complex prompt with separate JSON for customer and products,
#     plus a natural language query for discounts, to generate structured quote data.
#     """
    
#     # The new prompt is highly specific about its inputs and discount handling.
#     prompt_messages = [
#         {"role": "system", "content": """
#         You are an advanced financial data extraction AI for creating price quotations. You will receive a multi-part prompt and must follow these steps meticulously.

#         **Your Thought Process:**
#         1.  **Customer Data:** I will find the `Customer Data (JSON)` block. I will use this data *directly* for the customer's name, company, address, phone, and email. I will not try to find this information anywhere else.

#         2.  **Product Data Analysis:** I will find the `Selected Products Data (JSON)` block. This is a list of all products the user wants in the quote. My first task is to analyze this list to identify the main 'description' column and the 'price' column. I will then create a standard line item for EACH product in this list, using its identified description, price, and the specified 'Quantity'.

#         3.  **Discount & Modification Analysis:** I will find the `Modification Query` text. This is the most critical step. I will analyze this text for any commands, especially for DISCOUNTS.
#             -   If I find a **percentage discount** for a specific product (e.g., "10% off the iMac" which costs 150000), I will calculate that discount (15000) and create a **NEW, SEPARATE line item**. This item's description will be like 'Discount (10%) on iMac' and its `unit_price` will be a **NEGATIVE** value (`-15000.0`). The quantity will be 1.
#             -   If I find a **flat discount** (e.g., "Rs. 500 off the mouse"), I will create a new line item with a description like 'Discount on mouse' and a `unit_price` of `-500.0`.
#             -   If no specific product is mentioned for a discount, I will apply it to the most logical item or as a general discount on the whole order.

#         4.  **Final Assembly:** I will combine the product line items and the discount line items into a single list under the `items` key. I will also look for any tax information in the `Modification Query` (e.g., "Apply 18% GST"). If found, I will set `cgst_rate` and `sgst_rate` by dividing the total by 2. If not found, they will be 0.0. I will then construct the final JSON object according to the schema below without any extra text.

#         **JSON Schema to follow:**
#         ```json
#         {{
#             "customer": {{
#                 "name": "string",
#                 "company_name": "string",
#                 "address": "string",
#                 "city": "string",
#                 "state": "string",
#                 "zip": "string",
#                 "phone": "string",
#                 "email": "string"
#             }},
#             "items": [
#                 {{
#                     "description": "string",
#                     "qty": integer,
#                     "unit_price": float
#                 }}
#             ],
#             "cgst_rate": float,
#             "sgst_rate": float,
#             "currency": "string"
#         }}
#         ```
#         """},
#         {"role": "user", "content": user_query}
#     ]
    
#     try:
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=prompt_messages,
#             response_format={"type": "json_object"}
#         )
#         cleaned_response = response.choices[0].message.content.strip()
#         # A small fix to handle potential LLM errors where it might return a string for a number field
#         data = json.loads(cleaned_response)
#         for item in data.get("items", []):
#             if isinstance(item.get("unit_price"), str):
#                 item["unit_price"] = float(item["unit_price"].replace(",", ""))
#             if isinstance(item.get("qty"), str):
#                 item["qty"] = int(item["qty"])
#         return data
#     except openai.APIError as e:
#         print(f"OpenAI API Error: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"JSON Decode Error: Could not parse LLM response: {e}")
#         print(f"LLM Raw Response: {cleaned_response}")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred while calling the LLM: {e}")
#         return None

# # --- The rest of the generator.py file (process_quote_data, generate_pdf, create_quotation) remains exactly the same. ---
# def process_quote_data(structured_data: dict):
#     # This function already handles negative prices correctly, so no changes are needed.
#     items = structured_data.get("items", [])
#     cgst_rate = structured_data.get("cgst_rate", 0)
#     sgst_rate = structured_data.get("sgst_rate", 0)
    
#     subtotal = 0
    
#     for item in items:
#         qty = item.get('qty', 0)
#         unit_price = item.get('unit_price', 0)
#         amount = qty * unit_price
#         item['amount'] = amount
#         subtotal += amount
            
#     cgst_amount = subtotal * (cgst_rate / 100)
#     sgst_amount = subtotal * (sgst_rate / 100)
#     total = subtotal + cgst_amount + sgst_amount
    
#     summary = {
#         "subtotal": subtotal,
#         "cgst_amount": cgst_amount,
#         "sgst_amount": sgst_amount,
#         "total": total
#     }
#     return items, summary

# def generate_pdf(data: dict, output_filename: str):
#     """Renders the HTML template and converts it to a PDF."""
#     env = Environment(loader=FileSystemLoader('templates'))
#     template = env.get_template('template.html')
#     html_out = template.render(data)
    
#     css = CSS(filename='templates/style.css')
    
#     os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
#     HTML(string=html_out, base_url=Path().cwd().as_uri()).write_pdf(output_filename, stylesheets=[css])
#     print(f"Successfully generated PDF: {output_filename}")
#     return output_filename

# def create_quotation(user_query: str, company_info: dict, preview_mode=False):
#     """Main function to orchestrate the quotation generation process."""
#     print("1. Getting structured data from LLM (Intelligent Analysis)...")
#     structured_data = get_structured_data_from_llm(user_query)
    
#     if not structured_data:
#         print("Could not process the request. Aborting.")
#         return None

#     print("2. Processing calculations (Discounts are handled as negative items)...")
#     items, summary = process_quote_data(structured_data)
    
#     company_details = {
#         "name": company_info.get("name", "Your Company Name"),
#         "address": company_info.get("address", "Company Address"),
#         "phone": company_info.get("phone", "Company Phone"),
#         "fax": company_info.get("fax", "Company Fax"),
#         "email": company_info.get("email", "Company Email"),
#         "logo_path": company_info.get("logo_path", "")
#     }
    
#     customer_data = structured_data.get("customer", {})
#     # This now gets city/state/zip by parsing the address, which the AI is instructed to do.
#     customer_details = {
#         "id": random.randint(100, 999),
#         "name": customer_data.get("name", ""),
#         "company_name": customer_data.get("company_name", ""),
#         "address": customer_data.get("address", ""),
#         "city": customer_data.get("city", ""),
#         "state": customer_data.get("state", ""),
#         "zip": customer_data.get("zip", ""),
#         "phone": customer_data.get("phone", ""),
#         "email": customer_data.get("email", "")
#     }

#     today = date.today()
#     valid_until_date = today + timedelta(days=30)
#     customer_name_for_file = customer_details['name'].replace(' ', '_') if customer_details['name'] else "Customer"
#     quote_number = f"{today.year}-{random.randint(1000, 9999)}"
    
#     output_dir = "output"
#     os.makedirs(output_dir, exist_ok=True)
#     output_filename = os.path.join(output_dir, f"Quote_{quote_number}_{customer_name_for_file}.pdf")

#     template_data = {
#         "company": company_details,
#         "customer": customer_details,
#         "quote_number": quote_number,
#         "quote_date": f"{today.month}/{today.day}/{today.year}",
#         "valid_until": f"{valid_until_date.month}/{valid_until_date.day}/{valid_until_date.year}",
#         "items": items,
#         "summary": summary,
#         "cgst_rate": structured_data.get("cgst_rate", 0),
#         "sgst_rate": structured_data.get("sgst_rate", 0),
#         "currency": structured_data.get("currency", "Rs.")
#     }
    
#     print("3. Generating PDF...")
#     pdf_path = generate_pdf(template_data, output_filename)
    
#     if preview_mode:
#         webbrowser.open(Path(pdf_path).resolve().as_uri())
            
#     return pdf_path





























# import os
# import json
# import random
# import webbrowser
# from pathlib import Path
# from datetime import date, timedelta
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML, CSS
# from config import API_KEY, MODEL_NAME
# import openai

# # Initialize OpenAI client
# client = openai.OpenAI(api_key=API_KEY)

# def get_structured_data_from_llm(user_query: str):
#     """
#     Uses the OpenAI LLM to interpret a complex prompt, calculate per-item discounts,
#     and return structured data with a new 'discount_amount' field.
#     """
    
#     # The new prompt instructs the AI to modify items directly, not add new ones.
#     prompt_messages = [
#         {"role": "system", "content": """
#         You are a highly precise financial data extraction AI. Your task is to process a multi-part user request and generate a structured JSON output for a price quotation.

#         **Your Thought Process:**
#         1.  **Customer Data:** I will parse the `Customer Data (JSON)` block directly for all customer information.
        
#         2.  **Product Analysis:** I will analyze the `Selected Products Data (JSON)` to understand the product details and create a base list of line items. For each item, I will identify its description, quantity, and unit price.
        
#         3.  **Discount Allocation (Critical Change):** I will carefully read the `Modification Query`. When I find a discount command (e.g., "10% off product X", "Rs. 500 discount on item Y"), I will perform the following actions:
#             -   I will **NOT** create a new line item for the discount.
#             -   Instead, I will find the corresponding product in my list of line items.
#             -   I will calculate the discount amount. For a 10% discount on a 150,000 item, the amount is 15000.0.
#             -   I will add a new key, `discount_amount`, to that **specific item's JSON object**. The value will be the calculated positive discount amount (e.g., `15000.0`).
#             -   If an item has no discount, its `discount_amount` will be 0.0.

#         4.  **Final Assembly:** I will assemble the final JSON. The `items` array will now contain objects that may have a `discount_amount`. I will find tax details in the `Modification Query` as before. I will then output *only* the final JSON object, adhering strictly to the schema.

#         **JSON Schema to follow:**
#         ```json
#         {{
#             "customer": {{
#                 "name": "string", "company_name": "string", "address": "string",
#                 "city": "string", "state": "string", "zip": "string",
#                 "phone": "string", "email": "string"
#             }},
#             "items": [
#                 {{
#                     "description": "string",
#                     "qty": integer,
#                     "unit_price": float,
#                     "discount_amount": float
#                 }}
#             ],
#             "cgst_rate": float,
#             "sgst_rate": float,
#             "currency": "string"
#         }}
#         ```
#         """},
#         {"role": "user", "content": user_query}
#     ]
    
#     try:
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=prompt_messages,
#             response_format={"type": "json_object"}
#         )
#         cleaned_response = response.choices[0].message.content.strip()
#         return json.loads(cleaned_response)
#     except Exception as e:
#         print(f"An unexpected error occurred while calling the LLM: {e}")
#         return None

# def process_quote_data(structured_data: dict):
#     """
#     Calculates all financial values, now factoring in the per-item discount.
#     """
#     items = structured_data.get("items", [])
#     cgst_rate = structured_data.get("cgst_rate", 0)
#     sgst_rate = structured_data.get("sgst_rate", 0)
    
#     subtotal = 0
    
#     for item in items:
#         qty = item.get('qty', 0)
#         unit_price = item.get('unit_price', 0)
#         # --- LOGIC CHANGE HERE ---
#         # Get the per-item discount, default to 0 if not present
#         discount = item.get('discount_amount', 0.0)
        
#         # The final amount for the row is calculated after discount
#         final_unit_price = unit_price - discount
#         amount = qty * final_unit_price
        
#         item['amount'] = amount
#         # Subtotal is based on the final price after discount
#         subtotal += amount
            
#     cgst_amount = subtotal * (cgst_rate / 100)
#     sgst_amount = subtotal * (sgst_rate / 100)
#     total = subtotal + cgst_amount + sgst_amount
    
#     summary = {
#         "subtotal": subtotal,
#         "cgst_amount": cgst_amount,
#         "sgst_amount": sgst_amount,
#         "total": total
#     }
#     return items, summary

# # --- The generate_pdf and create_quotation functions remain exactly the same ---
# def generate_pdf(data: dict, output_filename: str):
#     env = Environment(loader=FileSystemLoader('templates'))
#     template = env.get_template('template.html')
#     html_out = template.render(data)
#     css = CSS(filename='templates/style.css')
#     os.makedirs(os.path.dirname(output_filename), exist_ok=True)
#     HTML(string=html_out, base_url=Path().cwd().as_uri()).write_pdf(output_filename, stylesheets=[css])
#     print(f"Successfully generated PDF: {output_filename}")
#     return output_filename

# def create_quotation(user_query: str, company_info: dict, preview_mode=False):
#     print("1. Getting structured data from LLM (Per-Item Discount Logic)...")
#     structured_data = get_structured_data_from_llm(user_query)
    
#     if not structured_data:
#         print("Could not process the request. Aborting.")
#         return None

#     print("2. Processing calculations (Applying discounts to each item)...")
#     items, summary = process_quote_data(structured_data)
    
#     # (The rest of this function is unchanged)
#     company_details = {
#         "name": company_info.get("name", "Your Company Name"),
#         "address": company_info.get("address", "Company Address"),
#         "phone": company_info.get("phone", "Company Phone"),
#         "fax": company_info.get("fax", "Company Fax"),
#         "email": company_info.get("email", "Company Email"),
#         "logo_path": company_info.get("logo_path", "")
#     }
#     customer_data = structured_data.get("customer", {})
#     customer_details = {
#         "id": random.randint(100, 999), "name": customer_data.get("name", ""),
#         "company_name": customer_data.get("company_name", ""), "address": customer_data.get("address", ""),
#         "city": customer_data.get("city", ""), "state": customer_data.get("state", ""),
#         "zip": customer_data.get("zip", ""), "phone": customer_data.get("phone", ""),
#         "email": customer_data.get("email", "")
#     }
#     today = date.today()
#     valid_until_date = today + timedelta(days=30)
#     customer_name_for_file = customer_details['name'].replace(' ', '_') if customer_details['name'] else "Customer"
#     quote_number = f"{today.year}-{random.randint(1000, 9999)}"
#     output_dir = "output"
#     os.makedirs(output_dir, exist_ok=True)
#     output_filename = os.path.join(output_dir, f"Quote_{quote_number}_{customer_name_for_file}.pdf")
#     template_data = {
#         "company": company_details, "customer": customer_details, "quote_number": quote_number,
#         "quote_date": f"{today.month}/{today.day}/{today.year}",
#         "valid_until": f"{valid_until_date.month}/{valid_until_date.day}/{valid_until_date.year}",
#         "items": items, "summary": summary, "cgst_rate": structured_data.get("cgst_rate", 0),
#         "sgst_rate": structured_data.get("sgst_rate", 0), "currency": structured_data.get("currency", "Rs.")
#     }
#     print("3. Generating PDF...")
#     pdf_path = generate_pdf(template_data, output_filename)
#     if preview_mode:
#         webbrowser.open(Path(pdf_path).resolve().as_uri())
#     return pdf_path














import os
import json
import random
import webbrowser
from pathlib import Path
from datetime import date, timedelta
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from config import API_KEY, MODEL_NAME
import openai

client = openai.OpenAI(api_key=API_KEY)

def get_structured_data_from_llm(user_query: str):
    prompt_messages = [
        {"role": "system", "content": """
        You are a hyper-precise financial data AI. You will receive a multi-part prompt and must generate a structured JSON for a price quote.

        **Your Thought Process:**
        1.  **Customer & Currency:** I will parse `Customer Data (JSON)` for customer details. I will find the `Currency to Use` instruction (e.g., "$", "₹") and use this symbol for the `currency` field in my final output.

        2.  **Product Analysis & Item Creation:** I will analyze `Selected Products Data (JSON)`. For each product object, I will identify two key columns: one that serves as the main **product name/title** and one that is the **unit price**. I will create a line item object for each product.
            - This object will have a `product_name` field (e.g., "iPhone 15 Pro").
            - It will have a `description` field, which can be a more detailed summary from other columns (e.g., "256GB, Blue Titanium"). If no other details exist, the description can be the same as the product name.
            - It will have `qty`, `unit_price`, and `discount_amount` (initialized to 0.0).

        3.  **Discount Allocation:** I will read the `Modification Query`. When I find a discount command (e.g., "10% off iPhones"), I will find the relevant item(s) in my list and update their `discount_amount` key with the calculated positive discount value. I will not create new line items for discounts.

        4.  **Final Assembly:** I will assemble the final JSON object, ensuring it strictly follows the schema below.

        **JSON Schema to follow:**
        ```json
        {{
            "customer": {
                "name": "string", "company_name": "string", "address": "string",
                "city": "string", "state": "string", "zip": "string",
                "phone": "string", "email": "string"
            },
            "items": [
                {{
                    "product_name": "string",
                    "description": "string",
                    "qty": integer,
                    "unit_price": float,
                    "discount_amount": float
                }}
            ],
            "cgst_rate": float,
            "sgst_rate": float,
            "currency": "string"
        }}
        ```
        """},
        {"role": "user", "content": user_query}
    ]
    
    try:
        response = client.chat.completions.create(model=MODEL_NAME, messages=prompt_messages, response_format={"type": "json_object"})
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"LLM Error: {e}")
        return None

def process_quote_data(structured_data: dict):
    items = structured_data.get("items", [])
    subtotal = 0
    for item in items:
        qty = item.get('qty', 0)
        unit_price = item.get('unit_price', 0)
        discount = item.get('discount_amount', 0.0)
        item['amount'] = qty * (unit_price - discount)
        subtotal += item['amount']
            
    cgst_rate = structured_data.get("cgst_rate", 0)
    sgst_rate = structured_data.get("sgst_rate", 0)
    cgst_amount = subtotal * (cgst_rate / 100)
    sgst_amount = subtotal * (sgst_rate / 100)
    total = subtotal + cgst_amount + sgst_amount
    
    summary = {"subtotal": subtotal, "cgst_amount": cgst_amount, "sgst_amount": sgst_amount, "total": total}
    return items, summary

def generate_pdf(data: dict, output_filename: str, template_name: str):
    # The FileSystemLoader now points to the 'new' subdirectory
    env = Environment(loader=FileSystemLoader('templates/new'))
    template = env.get_template(f'{template_name}.html')
    html_out = template.render(data)
    
    # We will use a generic style for all templates for now
    css = CSS(filename='templates/style.css')
    
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    HTML(string=html_out, base_url=Path().cwd().as_uri()).write_pdf(output_filename, stylesheets=[css])
    print(f"Successfully generated PDF: {output_filename}")
    return output_filename

def create_quotation(user_data: dict, company_info: dict, preview_mode=False):
    """
    Creates a quotation directly from the structured data provided by the frontend.
    """
    print("1. Received structured data from frontend...")
    
    # No LLM call needed. The data is already structured.
    structured_data = user_data
    
    print("2. Processing calculations...")
    items, summary = process_quote_data(structured_data)
    
    # The company_info is still relevant for details not in the form
    company_details = {
        "name": structured_data.get("company", {}).get("name"),
        "address": structured_data.get("company", {}).get("address"),
        "phone": company_info.get("phone"), # Assuming these are not in the form
        "fax": company_info.get("fax"),
        "email": company_info.get("email"),
        "logo_path": company_info.get("logo_path", "")
    }
    
    customer_details = structured_data.get("customer", {})
    
    today = date.today()
    quote_id = structured_data.get("quote", {}).get("id", f"{today.year}-{random.randint(1000, 9999)}")
    validation_date_str = structured_data.get("quote", {}).get("validationDate")
    
    if validation_date_str:
        valid_until = validation_date_str
    else:
        valid_until_date = today + timedelta(days=30)
        valid_until = f"{valid_until_date.month}/{valid_until_date.day}/{valid_until_date.year}"

    customer_name_for_file = customer_details.get('name', 'Customer').replace(' ', '_')
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"Quote_{quote_id}_{customer_name_for_file}.pdf")

    template_data = {
        "company": company_details,
        "customer": customer_details,
        "quote_number": quote_id,
        "quote_date": f"{today.month}/{today.day}/{today.year}",
        "valid_until": valid_until,
        "items": items,
        "summary": summary,
        "terms": structured_data.get("terms", []),
        # These fields might not be in the new UI, so we default them
        "cgst_rate": structured_data.get("cgst_rate", 0),
        "sgst_rate": structured_data.get("sgst_rate", 0),
        "currency": structured_data.get("currency", "Rs.")
    }
    
    selected_template = structured_data.get("template", "template1")
    
    print(f"3. Generating PDF using template: {selected_template}...")
    pdf_path = generate_pdf(template_data, output_filename, selected_template)
    
    if preview_mode:
        webbrowser.open(Path(pdf_path).resolve().as_uri())
        
    return pdf_path