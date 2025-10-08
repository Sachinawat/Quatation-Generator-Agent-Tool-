
# 🧾 Quotation Generation System

A simple and efficient Quotation Generator built with Python that automates the process of creating professional PDF quotations for clients — dynamically filling details like client name, product, price, and tax, and generating a final branded quotation document.

🚀 Features

✅ Auto-generates quotations in PDF format
✅ Customizable company name, logo, and client details
✅ Dynamic item list, quantity, and pricing
✅ Auto-calculates subtotal, tax, and grand total
✅ Clean, professional quotation design
✅ Lightweight and easy to integrate with other systems

🛠️ Tech Stack
Component	Technology Used
Language	Python 🐍
PDF Generation	reportlab / fpdf
Data Source	JSON / CSV / API / Manual Input
Output Format	PDF / Email Attachment
📦 Project Structure
quotation-generator/
│
├── main.py                  # Main Python script
├── templates/               # Folder for templates or logos
│   └── company_logo.png
├── data/
│   └── client_data.json
├── output/
│   └── quotation_001.pdf
└── README.md

⚙️ How It Works

The system reads client and product details from a data source (like JSON, CSV, or API).

Automatically calculates totals, taxes, and discounts.

Fills a PDF template with your company logo, header, and details.

Generates and saves the quotation in the /output folder.

🧩 Example Usage
from quotation_generator import generate_quotation

generate_quotation(
    client_name="ABC Pvt Ltd",
    items=[
        {"name": "CNC Machine", "qty": 2, "price": 150000},
        {"name": "Cutting Tool Set", "qty": 5, "price": 8000},
    ],
    tax_rate=18,
    quotation_no="QTN-2025-001"
)


Output:
✅ Generates quotation_QTN-2025-001.pdf in /output/ folder.

📄 Sample Output

Here’s a glimpse of a generated quotation:


💡 Future Enhancements

Add email sending functionality 📧

Integrate database (MySQL/MongoDB) support

Web dashboard for quotation tracking

Multi-language PDF generation 🌍

👨‍💻 Author

Sachin Awati
📧 awatisachin021@gmail.com

🔗 LinkedIn : https://www.linkedin.com/in/sachin-awati-7b886b1a1/
