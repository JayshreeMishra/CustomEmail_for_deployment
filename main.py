import os, sys
import json
from flask import Flask, render_template, request, flash, jsonify
from werkzeug.utils import secure_filename
import email

from app.email_sender import send_email
from ml.pipeline.predict_pipeline_spam_detection import SpamPredictPipeline
from ml.pipeline.predict_pipeline_spelling_corrector import SpellingPredictPipeline
from config.logging_config import logger
from config.exception import CustomException

template_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'templates')

app= Flask(__name__, static_folder='app/static', template_folder=template_folder_path)
app.secret_key = os.environ.get('SECRET_KEY', 'mysecretkey') 
is_production = os.environ.get('FLASK_ENV') == 'production'

spelling_pipeline = SpellingPredictPipeline()
spam_pipeline = SpamPredictPipeline()

# File upload folder
upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload')
os.makedirs(upload_folder, exist_ok=True) 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            sender_email = request.form.get('sender_email')
            sender_password = request.form.get('sender_app_password')
            recipient_input = request.form.get('recipients')
            recipient_names_input = request.form.get('recipient_names')
            recipient_company_input = request.form.get('recipient_companies')
            subject = request.form.get('subject')
            message = request.form.get('message')

            # Process recipients
            recipients = [email.strip() for email in recipient_input.split('\n') if email.strip()]
            recipient_names = [name.strip() for name in recipient_names_input.split('\n') if name.strip()]
            recipient_companies = [company.strip() for company in recipient_company_input.split('\n') if company.strip()]

            # Ensures the lists are of the same length
            if len(recipients) != len(recipient_names) or len(recipients) != len(recipient_companies):
                logger.error("The number of recipients, names, and companies must match.")
                flash("The number of recipients, names, and companies must match.", "danger")
                return render_template('email_form.html', error=True)

            # File upload
            file = request.files.get('file')
            attachment = None

            if file and file.filename != '':
                # Save the file temporarily
                file_path = os.path.join(upload_folder, file.filename)
                file.save(file_path)
                attachment = file_path  # Store the file path for sending email

            if recipients and subject and message:
                try:
                    result = send_email(sender_email, sender_password, recipients, subject, message, recipient_names, recipient_companies, attachment)
                except Exception as e:
                    result = f"Error sending email: {str(e)}"
            else:
                result = "All fields are required!"

            flash(result, "success" if "successfully" in result else "danger")

            # Delete the file after processing
            if attachment and os.path.exists(attachment):
                os.remove(attachment)

        except Exception as e:
            print(f"Unexpected error: {str(e)}") 
            flash('Internal Server Error', 'danger')

    return render_template('email_form.html')

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/spelling_correction', methods=['POST'])
def spelling_corrector():
    try:
        data = request.json
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        corrected_text, changed_words = spelling_pipeline.predict(text)

        # Ensure `changed_words` is always a list of lists (not tuples)
        if isinstance(changed_words, list):
            changed_words = [[original, corrected] for original, corrected in changed_words]

        return jsonify({
            "corrected_text": corrected_text,
            "changed_words": changed_words
        })

    except CustomException as e:
        app.logger.error(f"CustomException: {str(e)}")
        return jsonify(e.to_dict()), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/spam_detection', methods=['POST'])
def spam_detection():
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        text = data['text']
        is_spam = spam_pipeline.predict(text)

        # Log the output before returning
        app.logger.info(f"Prediction output: {is_spam}")

        # Convert NumPy boolean to Python boolean
        return jsonify({'is_spam': bool(is_spam[0])})  

    except CustomException as e:
        app.logger.error(f"CustomException: {str(e)}")
        return jsonify(e.to_dict()), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

#Use Render's assigned port for deployment
if __name__ == '__main__':
    port = os.environ.get("PORT", "Not Set")
    print(f"🚀 Starting server on port: {port}")  # Debugging log
    port = int(port) if port.isdigit() else 10000  # Default to 10000 if missing
    app.run(host="0.0.0.0", port=port)
