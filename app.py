from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "secret123"  # لتفعيل الفلاشات في لوحة التحكم

# مسار ملف النتائج
RESULT_FILE = 'results.xlsx'

# تحميل البيانات
def load_results():
    if os.path.exists(RESULT_FILE):
        df = pd.read_excel(RESULT_FILE)
        return df
    else:
        return pd.DataFrame(columns=['seat','name','school','arabic','english','math','science','social','total','grade'])

# صفحة الطلاب
@app.route('/', methods=['GET', 'POST'])
def home():
    df = load_results()
    result = None
    if request.method == 'POST':
        seat = request.form['seat'].strip()
        student = df[df['seat'] == int(seat)] if seat.isdigit() else pd.DataFrame()
        if not student.empty:
            result = student.to_dict(orient='records')[0]
        else:
            result = 'not_found'
    return render_template('index.html', result=result)

# لوحة التحكم - تسجيل دخول بسيط
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == 'admin' and pwd == 'admin123':
            return redirect(url_for('dashboard'))
        else:
            flash("اسم المستخدم أو كلمة المرور خاطئة")
    return render_template('admin_login.html')

# لوحة التحكم الرئيسية
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        # رفع ملف Excel جديد
        file = request.files.get('file')
        if file:
            file.save(RESULT_FILE)
            flash("تم رفع الملف بنجاح!")
            return redirect(url_for('dashboard'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
