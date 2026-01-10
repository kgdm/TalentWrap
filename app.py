from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
import uuid
from werkzeug.utils import secure_filename
from utils.pdf_generator import generate_summary_pdf, convert_to_pdf, merge_pdfs

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        # Use environment variable for password, fallback to 'admin'
        correct_password = os.environ.get('APP_PASSWORD', 'admin')
        if password == correct_password:
            session['logged_in'] = True
            return redirect(url_for('form'))
        else:
            return render_template('login.html', error="Invalid password")
    return render_template('login.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # 1. Collect Form Data
            form_data = {
                'candidate_name': request.form.get('candidate_name'),
                'department': request.form.get('department'),
                'phone': request.form.get('phone'),
                'email': request.form.get('email'),
                'location': request.form.get('location'),
                'age': request.form.get('age'),
                'education': request.form.get('education'),
                'tech_expertise': request.form.get('tech_expertise'),
                'industry': request.form.get('industry'),
                'current_company': request.form.get('current_company'),
                'product_selling': request.form.get('product_selling'),
                'ticket_size': request.form.get('ticket_size'),
                'sales_target': request.form.get('sales_target'),
                'sales_achieved': request.form.get('sales_achieved'),
                'communication': request.form.get('communication'),
                'reason_change': request.form.get('reason_change'),
                'total_exp': request.form.get('total_exp'),
                'current_salary': request.form.get('current_salary'),
                'expected_salary': request.form.get('expected_salary'),
                'notice_period': request.form.get('notice_period'),
                'remarks': request.form.get('remarks')
            }

            # 2. Handle File Upload
            if 'resume_file' not in request.files:
                return "No file uploaded", 400
            
            file = request.files['resume_file']
            if file.filename == '':
                return "No file selected", 400

            # Generate unique session ID for filenames
            session_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
            file.save(upload_path)

            # 3. Generate Summary PDF
            summary_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_summary.pdf")
            generate_summary_pdf(form_data, summary_pdf_path)

            # 4. Convert Uploaded Resume to PDF
            converted_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_converted.pdf")
            try:
                convert_to_pdf(upload_path, converted_pdf_path)
            except RuntimeError as e:
                return f"Error converting file: {str(e)}. Please try uploading a PDF.", 500

            # 5. Merge PDFs
            final_pdf_name = f"TalentWrap_Profile_{session_id}.pdf"
            final_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], final_pdf_name)
            merge_pdfs(summary_pdf_path, converted_pdf_path, final_pdf_path)

            # Cleanup temp files (optional, keeping final one)
            # os.remove(upload_path)
            # os.remove(summary_pdf_path)
            # os.remove(converted_pdf_path)

            return redirect(url_for('download', filename=final_pdf_name))

        except Exception as e:
            return f"An error occurred: {str(e)}", 500
        
    return render_template('form.html')

@app.route('/download/<filename>')
def download(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('download.html', filename=filename)

@app.route('/files/<filename>')
def serve_file(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
