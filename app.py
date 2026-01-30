import streamlit as st
from streamlit_gsheets import GSheetsConnection

# إعداد الاتصال بجوجل شيت
url = "https://docs.google.com/spreadsheets/d/1VYDWk4rU71gX85j6KYHhvhRjCLEb4OOMc16Rm2cw4mc/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

# قراءة البيانات مباشرة
df = conn.read(spreadsheet=url)

# إخفاء خيار رفع الملف اليدوي واستبداله بالتحديث التلقائي
if st.button('تحديث البيانات الآن 🔄'):
    st.cache_data.clear()
    st.rerun()
# إعدادات الصفحة
st.set_page_config(page_title="نظام تحليل النتائج الذكي", layout="wide")

    # حساب المجموع والنسبة (تلقائياً)
    subject_cols = df.select_dtypes(include=['number']).columns.drop(['رقم_الجلوس'], errors='ignore')
    df['المجموع'] = df[subject_cols].sum(axis=1)
    df['النسبة'] = (df['المجموع'] / (len(subject_cols) * 100)) * 100

    # --- القسم الأول: البحث برقم الجلوس ---
    st.header("🔍 البحث عن نتيجة طالب")
    search_id = st.number_input("أدخل رقم الجلوس", min_value=0, step=1)
    
    if search_id in df['رقم_الجلوس'].values:
        student_data = df[df['رقم_الجلوس'] == search_id].iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("الاسم", student_data['الاسم'])
        col2.metric("المجموع", f"{student_data['المجموع']}")
        col3.metric("النسبة المئوية", f"{student_data['النسبة']:.2f}%")
        st.success(f"حالة الطالب: {'ناجح' if student_data['النسبة'] >= 50 else 'راسب'}")
    else:
        st.info("الرجاء إدخال رقم جلوس صحيح.")

    # --- القسم الثاني: أوائل الطلبة ---
    st.divider()
    st.header("🏆 لوحة شرف الأوائل")
    top_n = st.slider("عدد الأوائل المطلوب عرضهم", 5, 20, 10)
    top_students = df.sort_values(by='المجموع', ascending=False).head(top_n)
    
    fig_top = px.bar(top_students, x='الاسم', y='النسبة', color='المدرسة', 
                     text_auto='.2f', title=f"أعلى {top_n} طلاب على مستوى النظام")
    st.plotly_chart(fig_top, use_container_width=True)
    st.table(top_students[['الاسم', 'المدرسة', 'المجموع', 'النسبة']])

    # --- القسم الثالث: تحليل الذكاء الاصطناعي للمدارس ---
    st.divider()
    st.header("🧠 تحليل أداء المدارس (AI Insights)")
    
    school_analysis = df.groupby('المدرسة').agg({
        'النسبة': 'mean',
        'الاسم': 'count'
    }).rename(columns={'الاسم': 'عدد الطلاب', 'النسبة': 'متوسط الدرجات'}).reset_index()

    col_a, col_b = st.columns(2)
    
    with col_a:
        fig_pie = px.pie(school_analysis, values='متوسط الدرجات', names='المدرسة', hole=0.4,
                         title="توزيع كفاءة المدارس")
        st.plotly_chart(fig_pie)

    with col_b:
        best_school = school_analysis.loc[school_analysis['متوسط الدرجات'].idxmax()]
        st.subheader("تحليل ذكي:")
        st.info(f"المدرسة الأكثر تميزاً هي **{best_school['المدرسة']}** بمتوسط درجات **{best_school['متوسط الدرجات']:.2f}%**.")
        st.write(f"إجمالي عدد الطلاب المسجلين في النظام: **{len(df)}** طالب.")

else:
    st.warning("بانتظار رفع ملف البيانات لبدء التحليل...")
