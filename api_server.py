# # api_server.py

# import os
# import threading
# import time
# from flask import Flask, request, jsonify, send_from_directory
# from generator import create_quotation
# from werkzeug.utils import secure_filename
# from pathlib import Path
# from flask_cors import CORS # Import CORS

# # Initialize the Flask application
# app = Flask(__name__)
# # Apply CORS to the app. For local development, '*' allows all origins.
# # In production, you'd specify your Streamlit app's origin, e.g., origins=["http://localhost:8501"]
# CORS(app) 

# # Global in-memory storage for company data
# # This data will persist as long as the Flask server is running.
# # Default values are provided for initial startup.
# temp_company_data = {
#     "name": "Motm Tech",
#     "address": "Pune, Maharashtra",
#     "phone": "98765432456",
#     "fax": "23453221",
#     "email": "motm.tech@gmail.com",
#     "logo_path": "" # Will store absolute URI of the logo file
# }

# # Directory for uploaded static files (e.g., logos)
# UPLOAD_FOLDER = 'static'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure the directory exists
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Global variable to store the path of the last generated PDF for download via API
# last_generated_pdf_path = ""

# def quotation_generation_thread(user_query, company_info, preview_mode):
#     """
#     Function to run PDF generation in a separate thread.
#     Updates the global last_generated_pdf_path upon completion.
#     """
#     global last_generated_pdf_path
#     try:
#         pdf_path = create_quotation(user_query, company_info, preview_mode)
#         if pdf_path:
#             last_generated_pdf_path = pdf_path
#             print(f"PDF generated successfully in thread: {pdf_path}")
#         else:
#             print("PDF generation failed in thread.")
#     except Exception as e:
#         print(f"Error in quotation_generation_thread: {e}")

# @app.route('/upload-company-data', methods=['POST'])
# def upload_company_data():
#     """
#     API endpoint to receive company details and logo from Streamlit.
#     Stores them in temp_company_data.
#     """
#     global temp_company_data
#     print("Received request to upload company data.")
    
#     # Extract text data from form (Streamlit sends form-data for file uploads)
#     temp_company_data["name"] = request.form.get("name", "Your Company")
#     temp_company_data["address"] = request.form.get("address", "Address Not Set")
#     temp_company_data["phone"] = request.form.get("phone", "Phone Not Set")
#     temp_company_data["fax"] = request.form.get("fax", "Fax Not Set")
#     temp_company_data["email"] = request.form.get("email", "Email Not Set")

#     # Handle file upload for logo
#     if 'logo' in request.files:
#         logo_file = request.files['logo']
#         if logo_file.filename != '':
#             filename = secure_filename(logo_file.filename)
#             logo_path_on_server = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             logo_file.save(logo_path_on_server)
#             temp_company_data["logo_path"] = Path(logo_path_on_server).resolve().as_uri()
#             print(f"Logo saved to: {temp_company_data['logo_path']}")
#         else:
#             temp_company_data["logo_path"] = ""
#             print("No logo file provided or filename empty.")
#     else:
#         temp_company_data["logo_path"] = ""
#         print("No logo field in request.")

#     print(f"Company data updated: {temp_company_data}")
#     return jsonify({"status": "success", "message": "Company data uploaded successfully!"})


# @app.route('/generate-quote', methods=['POST'])
# def handle_quote_generation():
#     """
#     API endpoint to generate a quote without previewing.
#     The generation runs in a separate thread.
#     """
#     data = request.get_json()
    
#     if not data or 'query' not in data:
#         return jsonify({"status": "error", "message": "Missing 'query' in request body"}), 400

#     user_query = data['query']
#     print(f"\nReceived API request to generate: '{user_query}'")

#     try:
#         thread = threading.Thread(target=quotation_generation_thread, args=(user_query, temp_company_data, False))
#         thread.start()
        
#         return jsonify({
#             "status": "success", 
#             "message": "Quotation generation started. The PDF will be created in the 'output' folder."
#         }), 202
        
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return jsonify({"status": "error", "message": f"An internal error occurred: {e}"}), 500


# @app.route('/generate-and-preview-quote', methods=['POST'])
# def handle_generate_and_preview():
#     """
#     API endpoint to generate a quote AND automatically open it for preview (server-side).
#     This endpoint is not directly used by the updated Streamlit app for client-side preview.
#     """
#     data = request.get_json()
    
#     if not data or 'query' not in data:
#         return jsonify({"status": "error", "message": "Missing 'query' in request body"}), 400

#     user_query = data['query']
#     print(f"\nReceived API request to generate and preview: '{user_query}'")

#     try:
#         thread = threading.Thread(target=quotation_generation_thread, args=(user_query, temp_company_data, True))
#         thread.start()
        
#         return jsonify({
#             "status": "success", 
#             "message": "Quotation generation and preview started."
#         }), 202
        
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return jsonify({"status": "error", "message": f"An internal error occurred: {e}"}), 500

# @app.route('/get-last-generated-pdf', methods=['GET'])
# def get_last_generated_pdf():
#     """
#     API endpoint for Streamlit to inquire about the filename of the last generated PDF.
#     """
#     if last_generated_pdf_path and os.path.exists(last_generated_pdf_path):
#         return jsonify({
#             "status": "success", 
#             "filename": os.path.basename(last_generated_pdf_path)
#         }), 200
#     else:
#         return jsonify({
#             "status": "error", 
#             "message": "No PDF has been generated yet, or file not found on server."
#         }), 404

# @app.route('/download/<filename>', methods=['GET'])
# def download_file(filename):
#     """
#     API endpoint to allow Streamlit to download or view a specific generated PDF.
#     """
#     output_dir = "output"
#     if filename in os.listdir(output_dir):
#         # IMPORTANT FIX: Removed as_attachment=True to allow inline viewing in iframe.
#         # Explicitly set mimetype to ensure browsers know it's a PDF.
#         return send_from_directory(output_dir, filename, mimetype="application/pdf")
#     else:
#         return jsonify({"status": "error", "message": "File not found or unauthorized access."}), 404

# if __name__ == "__main__":
#     print("--- Quotation API Server ---")
#     print("Starting server on http://127.0.0.1:5000")
#     app.run(host='0.0.0.0', port=5000, debug=False)














import os
import threading
from flask import Flask, request, jsonify, send_from_directory
from generator import create_quotation
from werkzeug.utils import secure_filename
from pathlib import Path
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

temp_company_data = {
    "name": "", "address": "", "phone": "",
    "fax": "", "email": "", "logo_path": ""
}

UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

last_generated_pdf_path = ""

def quotation_generation_thread(user_query, company_info):
    global last_generated_pdf_path
    try:
        pdf_path = create_quotation(user_query, company_info, preview_mode=False)
        if pdf_path:
            last_generated_pdf_path = pdf_path
            print(f"PDF generated successfully in thread: {pdf_path}")
        else:
            print("PDF generation failed in thread.")
    except Exception as e:
        print(f"Error in quotation_generation_thread: {e}")

@app.route('/upload-company-data', methods=['POST'])
def upload_company_data():
    global temp_company_data
    temp_company_data["name"] = request.form.get("name", "Your Company")
    temp_company_data["address"] = request.form.get("address", "Address Not Set")
    temp_company_data["phone"] = request.form.get("phone", "Phone Not Set")
    temp_company_data["fax"] = request.form.get("fax", "Fax Not Set")
    temp_company_data["email"] = request.form.get("email", "Email Not Set")

    if 'logo' in request.files:
        logo_file = request.files['logo']
        if logo_file.filename != '':
            filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logo_file.save(logo_path)
            temp_company_data["logo_path"] = Path(logo_path).resolve().as_uri()
    
    return jsonify({"status": "success", "message": "Company data uploaded successfully!"})

@app.route('/generate-quote', methods=['POST'])
def handle_quote_generation():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    # The user_query is now a structured JSON object from the frontend
    user_query = data

    thread = threading.Thread(target=quotation_generation_thread, args=(user_query, temp_company_data))
    thread.start()
    return jsonify({"status": "success", "message": "Quotation generation started."}), 202

@app.route('/get-last-generated-pdf', methods=['GET'])
def get_last_generated_pdf():
    if last_generated_pdf_path and os.path.exists(last_generated_pdf_path):
        return jsonify({"status": "success", "filename": os.path.basename(last_generated_pdf_path)})
    else:
        return jsonify({"status": "error", "message": "No PDF generated yet."}), 404

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    output_dir = "output"
    return send_from_directory(output_dir, filename, mimetype="application/pdf")

if __name__ == "__main__":
    print("--- Quotation API Server ---")
    print("Starting server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)





