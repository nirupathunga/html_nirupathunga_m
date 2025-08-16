from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import qrcode
import os
from geocoder import ip
import json

app = Flask(__name__)

# Mock credentials
CREDENTIALS = {
    'user': {'username': 'user', 'password': 'pass', 'role': 'user'},
    'admin': {'username': 'admin', 'password': 'pass', 'role': 'admin'}
}

# Language configuration
LANGUAGES = {
    'en': {
        'name': 'English', 'region': 'Urban India',
        'welcome': 'Welcome to UnityScan AI',
        'ussdTitle': 'USSD Survey', 'qrTitle': 'QR Code Survey',
        'question1': 'Do you use digital payments?', 'question2': 'What is your monthly income?',
        'options': ['Yes', 'No'], 'incomeOptions': ['Below ₹10,000', '₹10,000-25,000', 'Above ₹25,000'],
        'submit': 'Submit', 'back': 'Back', 'next': 'Next', 'login': 'Login',
        'username': 'Username', 'password': 'Password', 'loginError': 'Invalid username or password',
        'qrPrompt': 'Enter a valid Survey ID (numbers only).', 'qrSuccess': 'QR Code Generated!',
        'locationPrompt': 'Allow location access for language selection.'
    },
    'hi': {
        'name': 'हिंदी', 'region': 'North India',
        'welcome': 'UnityScan AI में आपका स्वागत है',
        'ussdTitle': 'USSD सर्वे', 'qrTitle': 'QR कोड सर्वे',
        'question1': 'क्या आप डिजिटल भुगतान का उपयोग करते हैं?', 'question2': 'आपकी मासिक आय क्या है?',
        'options': ['हाँ', 'नहीं'], 'incomeOptions': ['10,000 से कम', '10,000-25,000', '25,000 से अधिक'],
        'submit': 'जमा करें', 'back': 'वापस', 'next': 'आगे', 'login': 'लॉगिन',
        'username': 'उपयोगकर्ता नाम', 'password': 'पासवर्ड', 'loginError': 'अमान्य उपयोगकर्ता नाम या पासवर्ड',
        'qrPrompt': 'वैध सर्वे आईडी (संख्या) दर्ज करें।', 'qrSuccess': 'QR कोड उत्पन्न!',
        'locationPrompt': 'भाषा चयन के लिए स्थान अनुमति दें।'
    },
    'bn': {
        'name': 'বাংলা', 'region': 'West Bengal',
        'welcome': 'UnityScan AI-এ স্বাগতম',
        'ussdTitle': 'USSD জরিপ', 'qrTitle': 'QR কোড জরিপ',
        'question1': 'আপনি ডিজিটাল পেমেন্ট ব্যবহার করেন?', 'question2': 'আপনার মাসিক আয় কত?',
        'options': ['হ্যাঁ', 'না'], 'incomeOptions': ['১০,০০০-এর নিচে', '১০,০০০-২৫,০০০', '২৫,০০০-এর উপরে'],
        'submit': 'জমা দিন', 'back': 'পেছনে', 'next': 'পরবর্তী', 'login': 'লগইন',
        'username': 'ব্যবহারকারীর নাম', 'password': 'পাসওয়ার্ড', 'loginError': 'অবৈধ ব্যবহারকারীর নাম বা পাসওয়ার্ড',
        'qrPrompt': 'একটি বৈধ সর্বে ID (সংখ্যা মাত্র) লিখুন।', 'qrSuccess': 'QR কোড তৈরি হয়েছে!',
        'locationPrompt': 'ভাষা নির্বাচনের জন্য অবস্থানের অনুমতি দিন।'
    }
}

# Mock survey storage (in memory for this demo)
surveys = []

# Location-based language detection
def get_language_by_location():
    try:
        g = ip('me')
        lat, lng = g.lat, g.lng
        if 21.0 <= lat <= 25.0 and 86.0 <= lng <= 90.0:  # West Bengal
            return 'bn'
        elif 8.0 <= lat <= 13.5 and 76.0 <= lng <= 80.5:  # Tamil Nadu
            return 'ta'
        elif 9.0 <= lat <= 11.5 and 75.0 <= lng <= 77.0:  # Kerala
            return 'ml'
        elif 15.0 <= lat <= 18.5 and 78.0 <= lng <= 81.0:  # Andhra Pradesh/Telangana
            return 'te'
        elif 19.0 <= lat <= 23.0 and 72.0 <= lng <= 75.0:  # Urban India (e.g., Mumbai)
            return 'en'
        return 'hi'  # Default to Hindi
    except:
        return 'en'  # Fallback to English

@app.route('/')
def index():
    return render_template('login.html', lang=LANGUAGES['en'])

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = next((u for u in CREDENTIALS.values() if u['username'] == username and u['password'] == password), None)
    if user:
        lang = get_language_by_location()
        return render_template('home.html' if user['role'] == 'user' else 'admin.html', lang=LANGUAGES[lang], role=user['role'])
    return render_template('login.html', lang=LANGUAGES['en'], error=LANGUAGES['en']['loginError'])

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/generate_qr/<survey_id>')
def generate_qr(survey_id):
    if not survey_id.isdigit():
        return jsonify({'error': LANGUAGES['en']['qrPrompt']})
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f'http://localhost:5000/survey/{survey_id}')
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    qr_path = os.path.join('static/qr', f'qr_{survey_id}.png')
    img.save(qr_path)
    return jsonify({'qr_path': qr_path, 'message': LANGUAGES['en']['qrSuccess']})

@app.route('/static/qr/<filename>')
def serve_qr(filename):
    return send_from_directory('static/qr', filename)

@app.route('/admin/create_survey', methods=['POST'])
def create_survey():
    global surveys
    title = request.form['title']
    q1 = request.form['question1']
    q2 = request.form['question2']
    lang = request.form['language']
    survey = {
        'id': len(surveys) + 1,
        'title': title,
        'questions': [
            {'text': q1, 'options': LANGUAGES[lang]['options'], 'key': 'digitalPayment'},
            {'text': q2, 'options': LANGUAGES[lang]['incomeOptions'], 'key': 'income'}
        ],
        'language': lang
    }
    surveys.append(survey)
    return jsonify({'status': 'success', 'surveys': surveys})

@app.route('/ussd')
def ussd():
    survey_id = request.args.get('surveyId')
    lang = get_language_by_location()
    return render_template('ussd.html', lang=LANGUAGES[lang], survey_id=survey_id, surveys=surveys)

@app.route('/survey/<survey_id>')
def survey(survey_id):
    lang = get_language_by_location()
    return render_template('survey.html', lang=LANGUAGES[lang], survey_id=survey_id, surveys=surveys)

@app.route('/complete', methods=['POST'])
def complete():
    data = request.form.to_dict()
    lang = get_language_by_location()
    return render_template('complete.html', lang=LANGUAGES[lang], survey_data=data)

if __name__ == '__main__':
    if not os.path.exists('static/qr'):
        os.makedirs('static/qr')
    app.run(debug=True)
