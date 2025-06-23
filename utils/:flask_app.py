# flask_app.py

import os
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from utils.pdf_parser import parse_pdf
from utils.gemini_processor import process_text
from utils.enhanced_pdf_generator import generate_pdf
from dotenv import load_dotenv

load_dotenv()  # will pull GOOGLE_API_KEY into os.environ

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'change-me')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # handle PDF upload
        file = request.files.get('file')
        if not file or not allowed_file(file.filename):
            flash('Please upload a PDF.')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(path)

        # 1) parse → 2) AI process → 3) generate PDF
        parsed = parse_pdf(path)
        ai_out = process_text(parsed.text, metadata=parsed.metadata)
        output = generate_pdf(ai_out, metadata=parsed.metadata)

        return send_file(
            output,
            as_attachment=True,
            download_name='enhanced_'+filename,
            mimetype='application/pdf'
        )
    return render_template('index.html')
