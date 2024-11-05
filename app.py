from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd
from fpdf import FPDF
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

class InfoForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    modules = SelectMultipleField('Modules', choices=[
        ('fsm', 'Forcepoint Security Manager'),
        ('dlp_protector', 'DLP Protector'),
        ('dlp_irr', 'DLP IRR'),
        ('dlp_icap', 'DLP ICAP'),
        ('dlp_esg', 'DLP ESG'),
        ('web_appliance', 'Web Appliance'),
        ('web_hybrid', 'Web Hybrid')
    ], validators=[DataRequired()])
    submit = SubmitField('Next')

# Route to the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = InfoForm()
    if form.validate_on_submit():
        session['customer_name'] = form.customer_name.data
        session['date'] = form.date.data.strftime('%Y-%m-%d')
        session['modules'] = form.modules.data
        return redirect(url_for('module_questions'))
    return render_template('index.html', form=form)

# Route to dynamically load question pages based on selected modules
@app.route('/module_questions', methods=['GET', 'POST'])
def module_questions():
    modules = session.get('modules', [])
    if request.method == 'POST':
        for module in modules:
            session[module] = request.form.getlist(module)
        return redirect(url_for('summary'))
    return render_template('modules.html', modules=modules)

# Summary and export route
@app.route('/summary', methods=['GET', 'POST'])
def summary():
    data = {
        'Customer Name': session.get('customer_name'),
        'Date': session.get('date'),
    }
    data.update({module: session.get(module) for module in session.get('modules', [])})
    
    if request.method == 'POST':
        export_to_excel(data)
        export_to_pdf(data)
        return "Reports generated successfully!"
    
    return render_template('summary.html', data=data)

def export_to_excel(data):
    df = pd.DataFrame([data])
    if not os.path.exists('reports'):
        os.makedirs('reports')
    df.to_excel('reports/report.xlsx', index=False)

def export_to_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for key, value in data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    pdf.output("reports/report.pdf")

if __name__ == '__main__':
    app.run(debug=True)
