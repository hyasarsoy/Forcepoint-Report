from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd
from reportbro import Report
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Function to export data to Excel
def export_to_excel(data):
    # Flatten the data for better readability in Excel
    flattened_data = []
    for module in data['Modules']:
        flattened_data.append({
            'Customer Name': data['Customer Name'],
            'Date': data['Date'],
            'Module Name': module['module_name'],
            'Answers': ', '.join(module['answers']) if module['answers'] else "No answers provided"
        })
    
    # Convert the flattened data to a DataFrame
    df = pd.DataFrame(flattened_data)
    
    # Ensure 'reports' directory exists
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # Save data to an Excel file in the 'reports' directory
    df.to_excel('reports/report.xlsx', index=False)

# Load the ReportBro template from a JSON file with validation
template_path = 'report_template.json'
if os.path.exists(template_path):
    with open(template_path) as f:
        report_template = json.load(f)
else:
    report_template = None
    print("Warning: 'report_template.json' not found. Please check the file path.")

# Validate the structure of the report template
if report_template is None or 'pageFormat' not in report_template or 'documentProperties' not in report_template:
    raise ValueError("The report_template.json is invalid or missing required properties like 'pageFormat' or 'documentProperties'.")

class InfoForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Next')

# Route to the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = InfoForm()
    if form.validate_on_submit():
        session['customer_name'] = form.customer_name.data
        session['date'] = form.date.data.strftime('%Y-%m-%d')
        session['modules'] = request.form.getlist('modules')  # Store list of selected modules
        session['current_module_index'] = 0  # Initialize index for question navigation
        return redirect(url_for('module_questions'))
    return render_template('index.html', form=form)

# Route to display questions for each module
@app.route('/module_questions', methods=['GET', 'POST'])
def module_questions():
    modules = session.get('modules', [])
    current_index = session.get('current_module_index', 0)
    
    # If we've gone through all modules, go to the summary
    if current_index >= len(modules):
        return redirect(url_for('summary'))
    
    current_module = modules[current_index]
    
    if request.method == 'POST':
        # Save answers for the current module
        session[current_module] = request.form.getlist(current_module)
        # Move to the next module
        session['current_module_index'] += 1
        return redirect(url_for('module_questions'))
    
    # Render the questions page for the current module
    return render_template(f'questions_{current_module}.html')

# Summary and export route
@app.route('/summary', methods=['GET', 'POST'])
def summary():
    data = {
        'Customer Name': session.get('customer_name'),
        'Date': session.get('date'),
        'Modules': []
    }
    
    # Add each module's questions and answers
    for module in session.get('modules', []):
        module_data = {
            "module_name": module,
            "answers": session.get(module, [])
        }
        data['Modules'].append(module_data)

    if request.method == 'POST':
        export_to_excel(data)
        export_to_pdf(data)
        return "Reports generated successfully!"
    
    return render_template('summary.html', data=data)

# Use ReportBro to generate a PDF with a more sophisticated template
def export_to_pdf(data):
    report_data = {
        "customer_name": data['Customer Name'],
        "report_date": data['Date'],
        "health_check_results": [
            {"parameter": "Version and Hotfix Details", "observation": "No issues found with version 8.5.5.44."},
            {"parameter": "System Health Interface", "observation": "No error messages detected."},
            {"parameter": "Resource Utilization", "observation": "Resource utilization is stable."},
            {"parameter": "AV Exclusions, DEP, UAC", "observation": "Data Execution Prevention is disabled."},
            {"parameter": "Backup & Restoration", "observation": "No scheduled backups found for Forcepoint Web system."},
            # Add more parameters as needed based on your findings
        ]
    }

    # Ensure 'reports' directory exists
    if not os.path.exists('reports'):
        os.makedirs('reports')

    # Create the Report object with ReportBro and generate PDF
    try:
        report = Report(report_template, report_data, 'pdf')
        pdf_file_path = 'reports/generated_report.pdf'
        with open(pdf_file_path, 'wb') as f:
            f.write(report.generate_pdf())
    except Exception as e:
        print(f"Error generating PDF: {e}")


# Optional route to download the generated PDF
@app.route('/download_report')
def download_report():
    pdf_file_path = 'reports/generated_report.pdf'
    if os.path.exists(pdf_file_path):
        return send_file(pdf_file_path, as_attachment=True)
    else:
        return "Report not found. Please generate the report first.", 404

if __name__ == '__main__':
    app.run(debug=True)
