import os
from utils.pdf_generator import generate_summary_pdf, merge_pdfs
from reportlab.pdfgen import canvas

# Ensure uploads dir exists
os.makedirs('uploads', exist_ok=True)

# 1. Test Summary Generation with NEW fields
print("Testing Summary Generation...")
data = {
    'full_name': 'Nandeeshwar Talari',
    'role': 'Sales Executive',
    'email': 'talarinandu82@gmail.com',
    'phone': '7799162580',
    'dob': '1998-08-19',
    'gender': 'Male',
    'marital_status': 'Single',
    'nationality': 'Indian',
    'religion': 'Hindu',
    'passport': 'No',
    'address': 'Hyderabad, India',
    'languages': 'English, Hindi, Telugu',
    'website': 'linkedin.com/in/nandu',
    'summary': 'Experienced sales executive...',
    'skills': 'Sales, Negotiation, CRM',
    'edu_degree': 'Bachelor of Arts',
    'edu_university': 'Osmania University',
    'edu_year': '2021',
    'edu_grade': '7.8'
}
summary_path = 'uploads/test_summary_refined.pdf'
generate_summary_pdf(data, summary_path)
if os.path.exists(summary_path):
    print(f"PASS: Summary PDF created at {summary_path}")
else:
    print("FAIL: Summary PDF not created")

# 2. Create a dummy resume PDF for merging
print("\nCreating dummy resume PDF...")
resume_path = 'uploads/test_resume.pdf'
c = canvas.Canvas(resume_path)
c.drawString(100, 750, "This is a dummy resume page.")
c.save()

# 3. Test Merging
print("\nTesting PDF Merging...")
merged_path = 'uploads/test_merged_refined.pdf'
merge_pdfs(summary_path, resume_path, merged_path)
if os.path.exists(merged_path):
    print(f"PASS: Merged PDF created at {merged_path}")
else:
    print("FAIL: Merged PDF not created")

print("\nVerification Complete.")
