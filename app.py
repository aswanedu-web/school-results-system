import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="نظام النتائج الذكي 2026", layout="wide")

# تخصيص المظهر بالعربي
    <style>
    .main { text-align: right; }
    div.stButton > button:first-child { background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_name_with_html=True)

# --- 2. وظيفة إنشاء شهادة التقدير ---
def create_certificate(name, percentage, rank):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    pdf.set_font('Arial', 'B', 30)
    pdf.cell(0, 60, 'CERTIFICATE OF EXCELLENCE', ln=True, align='C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(0, 20, f'This is to certify that: {name}', ln=True, align='C')
    pdf.cell(0, 20, f'Ranked #{rank} with score {percentage}%', ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- 3. نظام تسجيل الدخول ---
def check_password():
    if "password_correct" not in st.session_state:
        st.sidebar.subheader("🔐 دخول المسؤولين")
        user = st.sidebar.text_input("اسم المستخدم")
        pwd = st.sidebar.text_input("كلمة المرور", type="password")
        if st.sidebar.button("دخول"):
            if user == "admin" and pwd == "12345": # يمكنك تغييرها
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.sidebar.error("❌ بيانات خاطئة")
        return False
    return True

# --- 4. تحميل البيانات ---
# ملاحظة: سنقوم بإنشاء بيانات وهمية إذا لم يتم رفع ملف لتجربة الكود فوراً
st.title("📊 نظام عرض وتحليل نتائج الطلاب الذكي")

uploaded_file = st.sidebar.file_uploader("ارفع ملف نتائج الإكسيل", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # حساب المجموع والنسبة تلقائياً
    subject_cols = df.select_dtypes(include=['number']).columns.drop(['رقم_الجلوس'], errors='ignore')
    df['المجموع'] = df[subject_cols].sum(axis=1)
    df['النسبة'] = (df['المجموع'] / (len(subject_cols) * 100)) * 100

    # --- القسم العام: بحث الطلاب ---
    st.header("🔍 استعلام عن نتيجة")
    search_id = st.number_input("أدخل رقم الجلوس الخاص بك", min_value=0, step=1)
    
    if search_id > 0:
        student = df[df['رقم_الجلوس'] == search_id]
        if not student.empty:
            res = student.iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("اسم الطالب", res['الاسم'])
            c2.metric("المجموع", f"{res['المجموع']}")
            c3.metric("النسبة المئوية", f"{res['النسبة']:.2f}%")
            
            if res['النسبة'] >= 90:
                st.balloons()
                st.success("🎉 تهانينا! أنت من المتفوقين.")
            elif res['النسبة'] >= 50:
                st.info("ناجح - نتمنى لك مزيداً من التوفيق.")
            else:
                st.error("راسب - حظاً أوفر في المرة القادمة.")
        else:
            st.warning("رقم الجلوس غير موجود.")

    # --- القسم الخاص: لوحة تحكم الإدارة ---
    st.divider()
    if check_password():
        st.sidebar.success("مرحباً بك في لوحة الإدارة")
        
        tab1, tab2 = st.tabs(["🏆 أوائل الطلبة", "📈 تحليل أداء المدارس"])
        
        with tab1:
            top_n = st.slider("عرض أفضل:", 5, 20, 10)
            top_df = df.sort_values(by='المجموع', ascending=False).head(top_n)
            
            fig_top = px.bar(top_df, x='الاسم', y='النسبة', color='المدرسة', text_auto='.2f')
            st.plotly_chart(fig_top, use_container_width=True)
            
            st.subheader("🖨️ طباعة الشهادات")
            selected = st.selectbox("اختر الطالب لإصدار شهادته", top_df['الاسم'])
            s_row = top_df[top_df['الاسم'] == selected].iloc[0]
            rank = top_df.index.get_loc(s_row.name) + 1
            pdf_file = create_certificate(selected, round(s_row['النسبة'], 2), rank)
            st.download_button(f"تحميل شهادة {selected}", pdf_file, f"{selected}.pdf", "application/pdf")

        with tab2:
            st.subheader("🧠 رؤية الذكاء الاصطناعي للمدارس")
            school_stats = df.groupby('المدرسة')['النسبة'].mean().reset_index()
            
            fig_school = px.pie(school_stats, values='النسبة', names='المدرسة', hole=0.3)
            st.plotly_chart(fig_school)
            
            best_school = school_stats.loc[school_stats['النسبة'].idxmax()]
            st.info(f"💡 التحليل الذكي: مدرسة **{best_school['المدرسة']}** تتصدر الأداء التعليمي لهذا العام بمتوسط **{best_school['النسبة']:.2f}%**.")

else:
    st.info("👈 من فضلك قم برفع ملف الإكسيل من القائمة الجانبية لبدء تشغيل النظام.")
    st.image("https://via.placeholder.com/800x400.png?text=Waiting+for+Data+File", caption="نظام النتائج جاهز للعمل")
