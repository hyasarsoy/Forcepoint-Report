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

# Load the ReportBro template from a JSON file
with open('report_template.json') as f:
    report_template = json.load(f)

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
        "modules": []
    }

    # Add each module's questions and answers
    for module in session.get('modules', []):
        report_data["modules"].append({
            "module_name": module,
            "answers": data.get(module, [])
        })

    # Create the Report object with ReportBro
    report = Report(report_template, report_data, 'pdf')

    # Generate and save the PDF file
    if not os.path.exists('reports'):
        os.makedirs('reports')
    pdf_file_path = 'reports/generated_report.pdf'
    with open(pdf_file_path, 'wb') as f:
        f.write(report.generate_pdf())

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
