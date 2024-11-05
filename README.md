Here’s a `README.md` file to guide users on setting up and using the application.

---

# Forcepoint Report Generator

This is a web-based application for generating Forcepoint reports based on customer-specific details and modules. The app enables L1 support staff to input customer information, select relevant Forcepoint modules, answer dynamic questions, and generate reports in Excel and PDF formats.

## Features

- Collect customer information (name, date, selected modules)
- Dynamic module-based questions
- Export data to Excel and PDF for easy sharing
- User-friendly web interface

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/forcepoint-report-generator.git
   cd forcepoint-report-generator
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
forcepoint_app/
├── app.py               # Main application logic
├── templates/           # HTML templates for web pages
│   ├── base.html        # Base layout template
│   ├── index.html       # Home page for customer info
│   ├── modules.html     # Module selection page
│   ├── questions_*.html # Individual question pages for each module
│   └── summary.html     # Summary review and export page
├── static/
│   └── styles.css       # CSS styling
├── reports/             # Generated reports (Excel and PDF)
│   ├── report.xlsx      
│   └── report.pdf       
└── requirements.txt     # Dependencies
```

## Usage

1. **Run the Application:**

   ```bash
   python app.py
   ```

2. **Access the Web Interface:**
   Open your browser and go to `http://127.0.0.1:5000/`.

3. **Steps in the Web App:**
   - **Step 1:** Enter customer details on the home page (Customer Name, Date, and Modules).
   - **Step 2:** Select the relevant modules, which will load module-specific questions on the next pages.
   - **Step 3:** Review all answers on the summary page.
   - **Step 4:** Export the report in Excel and PDF formats by clicking the export button.

4. **Find Reports:**
   The generated reports will be saved in the `reports/` folder as `report.xlsx` and `report.pdf`.

## Technologies Used

- **Flask** - Web framework for the application
- **Flask-WTF** - Form handling for customer inputs
- **pandas** - Data processing and Excel export
- **FPDF** - PDF generation for reports

## License

This project is licensed under the MIT License.

---

## Contributing

Feel free to fork this repository and submit pull requests if you have any improvements or bug fixes.

## Contact

For any questions or feedback, please contact [Your Name](mailto:your-email@example.com).

---

Enjoy generating your Forcepoint reports! 😊
