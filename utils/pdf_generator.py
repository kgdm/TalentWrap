import os
import subprocess
import img2pdf
from pypdf import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Arial (using Liberation Sans as replacement in Linux)
try:
    # Regular
    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Arial', font_path))
    else:
        pdfmetrics.registerFont(TTFont('Arial', 'Helvetica'))
    
    # Bold
    font_bold_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    if os.path.exists(font_bold_path):
        pdfmetrics.registerFont(TTFont('Arial-Bold', font_bold_path))
    else:
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'Helvetica-Bold'))
except Exception:
    pass

def generate_summary_pdf(data, output_path):
    """
    Generates a PDF summary matching the specific table layout.
    """
    # Set small margins to allow more content on the first page
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=letter,
        topMargin=0.3*inch,
        bottomMargin=0.3*inch,
        leftMargin=0.3*inch,
        rightMargin=0.3*inch
    )
    story = []
    styles = getSampleStyleSheet()

    # 1. Header Space (Header is now handled by overlay)
    # Removed spacer to minimize empty space before title
    
    # Title: PROFILE SUMMARY
    title_style = ParagraphStyle(
        'ProfileSummary',
        parent=styles['Heading2'],
        fontSize=16,
        alignment=1, # Center
        spaceAfter=5,
        fontName='Helvetica-Bold',
        textColor=colors.black
    )
    story.append(Paragraph("PROFILE SUMMARY", title_style))
    story.append(Spacer(1, 5))

    # 2. Data Table
    # Columns: SNO, Evaluation Criteria, Detail
    table_data = [
        ["SNO", "Evaluation Criteria", "Detail"] # Header Row
    ]

    # Custom style for table content to increase font size
    table_content_style = ParagraphStyle(
        'TableContent',
        parent=styles['BodyText'],
        fontSize=12,
        leading=13
    )

    # Field Mapping (Order matters)
    all_fields = [
        ("1", "Candidate Name", data.get('candidate_name', '')),
        ("2", "Department/Function", data.get('department', '')),
        ("3", "Phone No", data.get('phone', '')),
        ("4", "Email", data.get('email', '')),
        ("5", "Current location", data.get('location', '')),
        ("6", "Age", data.get('age', '')),
        ("7", "Education Qualification", data.get('education', '')),
        ("8", "Technical Expertise", data.get('tech_expertise', '')),
        ("9", "Industry Exposure", data.get('industry', '')),
        ("10", "Current Company", data.get('current_company', '')),
        ("11", "Product Selling", data.get('product_selling', '')),
        ("12", "Ticket Size", data.get('ticket_size', '')),
        ("13", "Current Company’s Annual\nSales Target", data.get('sales_target', '')),
        ("14", "Achieved Sales Target", data.get('sales_achieved', '')),
        ("15", "Communication", data.get('communication', '')),
        ("16", "Reason for the job change", data.get('reason_change', '')),
        ("17", "Total Experience", data.get('total_exp', '')),
        ("18", "Current salary(Per month)", data.get('current_salary', '')),
        ("19", "Expected Salary (Per month)", data.get('expected_salary', '')),
        ("20", "Notice Period", data.get('notice_period', '')),
        ("21", "Remarks if any", data.get('remarks', ''))
    ]

    # Filter out empty fields (except for required ones, but here we just check if value exists)
    # We re-number them based on visible fields
    visible_fields = []
    counter = 1
    for _, label, value in all_fields:
        if value and str(value).strip():
            visible_fields.append((str(counter), label, value))
            counter += 1

    for sno, label, value in visible_fields:
        # Wrap text
        label_p = Paragraph(label, table_content_style)
        value_p = Paragraph(str(value), table_content_style)
        table_data.append([sno, label_p, value_p])

    # Table Styling
    # Col widths: SNO (0.5), Evaluation Criteria (3.0), Detail (3.5)
    t = Table(table_data, colWidths=[0.5*inch, 3*inch, 3.5*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke), # Header bg
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'), # Center SNO
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7), # Optimized to fit 21 rows on one page
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t)

    # Footer (Now handled by overlay)
    # story.append(Spacer(1, 30))
    
    doc.build(story)

def convert_to_pdf(input_path, output_path):
    """
    Converts the input file (Image or Docx) to PDF.
    """
    ext = os.path.splitext(input_path)[1].lower()

    if ext == '.pdf':
        if input_path != output_path:
             reader = PdfReader(input_path)
             writer = PdfWriter()
             for page in reader.pages:
                 writer.add_page(page)
             with open(output_path, "wb") as f:
                 writer.write(f)
        return

    if ext in ['.jpg', '.jpeg', '.png']:
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(input_path))
        return

    if ext in ['.docx', '.doc']:
        try:
            out_dir = os.path.dirname(output_path)
            cmd = ['soffice', '--headless', '--convert-to', 'pdf', input_path, '--outdir', out_dir]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            generated_pdf = os.path.join(out_dir, base_name + '.pdf')
            
            if generated_pdf != output_path:
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(generated_pdf, output_path)
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("LibreOffice not found or failed. Please run in Docker for Word support.")
        return

    raise ValueError(f"Unsupported file format: {ext}")

    with open(output_path, "wb") as f:
        writer.write(f)

def create_overlay(output_path):
    """
    Creates a single-page PDF with the Header (Logo) and Footer.
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Header (Logo)
    logo_path = os.path.abspath("static/images/logo.jpg")
    if os.path.exists(logo_path):
        # Draw image at top left (x=30, y=height-100)
        # Reduced size to prevent pixelation: Width 1.5 inch
        c.drawImage(logo_path, 30, height - 90, width=1.5*inch, height=0.8*inch, preserveAspectRatio=True, mask='auto')
    else:
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.HexColor('#2563eb'))
        c.drawString(30, height - 50, "Triumph Consultants")

    # Footer
    footer_text = "Triumph consultants"
    # Use Arial-Bold for a bolder look
    c.setFont("Arial-Bold", 13)
    c.setFillColor(colors.HexColor('#222222')) # Grayish black
    c.setStrokeColor(colors.HexColor('#00008B')) # Darker Blue underline
    c.setLineWidth(3) # 3/4th of 5.0pt as requested
    
    text_width = c.stringWidth(footer_text, "Arial-Bold", 13)
    c.drawString(30, 30, footer_text)
    # Draw the underline slightly below the text
    c.line(30, 24, 30 + text_width, 24) 
    
    c.save()

def merge_pdfs(summary_path, resume_path, output_path):
    """
    Merges summary and resume, applying header/footer overlay to ALL pages.
    Scales content pages to fit within margins to avoid overlap.
    """
    from pypdf import Transformation

    writer = PdfWriter()
    
    # Generate Overlay
    overlay_path = os.path.join(os.path.dirname(output_path), "overlay.pdf")
    create_overlay(overlay_path)
    reader_overlay = PdfReader(overlay_path)
    overlay_page = reader_overlay.pages[0]

    # Helper to process and add pages
    def add_pages_with_overlay(reader):
        target_w, target_h = 612, 792 # Letter size
        for page in reader.pages:
            # Create a blank Letter-sized page
            new_page = writer.add_blank_page(width=target_w, height=target_h)
            
            # Original dimensions and origin
            orig_w = float(page.mediabox.width)
            orig_h = float(page.mediabox.height)
            orig_left = float(page.mediabox.left)
            orig_bottom = float(page.mediabox.bottom)

            # 1. Normalize origin to (0,0)
            page.add_transformation(Transformation().translate(tx=-orig_left, ty=-orig_bottom))
            
            # 2. Calculate scale to fit width (maintaining user's 0.83 proportion)
            # This ensures that even if the input is A4 or other sizes, it scales to the same width as the summary
            scale_factor = 0.83 * (target_w / orig_w)
            
            # 3. Calculate tx to center horizontally
            tx = (target_w - (orig_w * scale_factor)) / 2
            ty = 35 # User's preferred vertical position
            
            # Apply transformation
            op = Transformation().scale(scale_factor).translate(tx=tx, ty=ty)
            page.add_transformation(op)
            
            # Merge scaled content
            new_page.merge_page(page)
            
            # Merge overlay (header/footer) on top
            new_page.merge_page(overlay_page)

    # Add Summary (Already has header/footer from generate_summary_pdf, 
    # but user wants "Every page". 
    # Actually, generate_summary_pdf already adds them using ReportLab. 
    # If we overlay again, it will double up.
    # So for summary, we might NOT need to scale/overlay if it's already correct.
    # BUT, to be consistent, maybe we should remove header/footer from generate_summary_pdf 
    # and use this global overlay? 
    # Let's keep generate_summary_pdf as is for now, assuming it's Page 1 and looks good.
    # The user said "Every page". 
    # Let's apply the overlay ONLY to the resume pages.
    
    # Add Summary (With Overlay and Scaling)
    reader_summary = PdfReader(summary_path)
    add_pages_with_overlay(reader_summary)

    # Add Resume (With Overlay and Scaling)
    reader_resume = PdfReader(resume_path)
    add_pages_with_overlay(reader_resume)

    with open(output_path, "wb") as f:
        writer.write(f)
    
    # Cleanup
    if os.path.exists(overlay_path):
        os.remove(overlay_path)
