import streamlit as st
import pandas as pd
from io import BytesIO
from uuid import uuid4
from datetime import datetime

st.set_page_config(page_title="AI FAQ System", page_icon="📚", layout="wide")
st.markdown("""<style>
html, body, [class*="css"] {direction: rtl; text-align: right;}
.stApp {background: #f7f9fc;}
h1,h2,h3 {color:#183153;}
[data-testid="stSidebar"] {background:#eaf0f8;}

.stApp {
    background-color: #F7F9FC;
    color: #182335;
}

.stApp h1, .stApp h2, .stApp h3,
.stApp p, .stApp label,
.stApp span {
    color: #182335;
}

[data-testid="stSidebar"] {
    background-color: #EAF0F8;
}

[data-testid="stSidebar"] * {
    color: #182335;
}

.stAlert p {
    color: inherit;
}
/* الكتابة داخل مربعات الإدخال */
.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] *,
.stFileUploader section,
.stFileUploader section * {
    color: #FFFFFF !important;
}

/* الكتابة داخل الأزرار */
.stButton button,
.stButton button * {
    color: #FFFFFF !important;
}

/* النصوص التوضيحية داخل المربعات */
input::placeholder,
textarea::placeholder {
    color: #D1D5DB !important;
}</style>""", unsafe_allow_html=True)

if "session_id" not in st.session_state: st.session_state.session_id = str(uuid4())[:8]
if "history" not in st.session_state: st.session_state.history = []
if "username" not in st.session_state: st.session_state.username = ""

st.title("📚 نظام الأسئلة الشائعة الذكي")
st.caption("AI FAQ Generation and Answering System — واجهة تجريبية للمهمة الرابعة")
st.info("🧪 وضع تجريبي: لا يوجد اتصال فعلي بالنموذج اللغوي أو قاعدة بيانات SQLite بعد.")

with st.sidebar:
    st.header("⚙️ إعدادات الجلسة")
    username = st.text_input("اسم المستخدم", value=st.session_state.username, placeholder="اكتبي اسمك")
    if st.button("بدء / تحديث الجلسة"):
        if username.strip():
            st.session_state.username = username.strip()
            st.success("تم إعداد الجلسة")
        else: st.warning("الرجاء كتابة اسم المستخدم")
    st.caption("معرّف الجلسة: " + st.session_state.session_id)
    st.divider()
    page = st.radio("القائمة", ["الواجهة الرئيسية", "سجل التفاعلات", "حول المشروع"])

# Demo-only function; replace with team API integration later.
def demo_response(task, question, filename):
    if task == "سؤال عام":
        return "هذه إجابة توضيحية فقط. عند ربط Groq وLangChain ستظهر الإجابة الحقيقية هنا."
    if task == "سؤال من مستند":
        return f"تم استلام السؤال المرتبط بالمستند ({filename}). الاسترجاع والإجابة الفعلية يحتاجان ربط كود الفريق."
    if task == "تلخيص":
        return "هذا موضع عرض الملخص. لا يتم تلخيص المستند فعليًا في الوضع التجريبي."
    return ""

def save_interaction(task, question, answer):
    st.session_state.history.append({"الوقت": datetime.now().strftime("%Y-%m-%d %H:%M"), "المهمة": task, "السؤال": question, "الإجابة": answer})

if page == "الواجهة الرئيسية":
    st.subheader("اختاري المهمة")
    task = st.selectbox("نوع المهمة", ["سؤال عام", "سؤال من مستند", "توليد أسئلة شائعة", "تلخيص"])
    upload_needed = task in ["سؤال من مستند", "توليد أسئلة شائعة", "تلخيص"]
    uploaded = st.file_uploader("رفع مستند (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"], disabled=not upload_needed)
    filename = uploaded.name if uploaded else "لا يوجد ملف"
    valid_file = False
    if uploaded:
        size = uploaded.size
        if size == 0: st.error("الملف فارغ، الرجاء اختيار ملف يحتوي على بيانات.")
        elif size > 10 * 1024 * 1024: st.error("حجم الملف أكبر من الحد التجريبي (10 MB).")
        else:
            valid_file = True
            st.success(f"تم اختيار الملف: {uploaded.name} — {size / 1024:.1f} KB")
            st.caption("الملف لم يُعالج بواسطة LangChain بعد؛ هذه واجهة تجريبية.")
    if task == "توليد أسئلة شائعة":
        count = st.slider("عدد الأسئلة المطلوبة", min_value=5, max_value=20, value=10)
        if st.button("توليد الأسئلة الشائعة", type="primary"):
            if not st.session_state.username: st.warning("أدخلي اسم المستخدم أولًا من القائمة الجانبية.")
            elif not valid_file: st.warning("ارفعي ملفًا صالحًا أولًا.")
            else:
                st.warning("لم يتم ربط مولّد الأسئلة الحقيقي بعد. الجدول التالي بيانات عرض توضيحية فقط.")
                rows = [{"السؤال": f"سؤال تجريبي {i}", "الإجابة": "إجابة تجريبية — ليست من المستند", "التصنيف": "تجريبي"} for i in range(1, count+1)]
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("تصدير CSV تجريبي", df.to_csv(index=False).encode("utf-8-sig"), "demo_faq.csv", "text/csv")
                save_interaction(task, f"توليد {count} أسئلة من {filename}", "جدول تجريبي — لا توجد معالجة حقيقية")
    else:
        prompt_label = "اكتبي النص المراد تلخيصه" if task == "تلخيص" else "اكتبي سؤالك"
        question = st.text_area(prompt_label, height=130, placeholder="اكتبي هنا...")
        if st.button("إرسال", type="primary"):
            if not st.session_state.username: st.warning("أدخلي اسم المستخدم أولًا من القائمة الجانبية.")
            elif not question.strip() and not (task == "تلخيص" and valid_file): st.warning("الرجاء إدخال نص قبل الإرسال.")
            elif upload_needed and not valid_file and task == "سؤال من مستند": st.warning("يجب رفع مستند صالح لهذا النوع من الأسئلة.")
            elif task == "تلخيص" and len(question.strip()) < 30 and not valid_file: st.warning("النص قصير جدًا للتلخيص؛ اكتبي نصًا أطول أو ارفعي مستندًا.")
            else:
                with st.spinner("جارٍ تجهيز نتيجة العرض..."):
                    answer = demo_response(task, question, filename)
                st.subheader("النتيجة")
                st.write(answer)
                save_interaction(task, question or f"تلخيص {filename}", answer)
                st.success("اكتمل العرض التجريبي")

elif page == "سجل التفاعلات":
    st.subheader("🕘 سجل التفاعلات")
    st.caption("السجل محفوظ مؤقتًا في جلسة Streamlit الحالية فقط، وليس في SQLite.")
    if not st.session_state.history: st.info("لا يوجد سجل بعد.")
    else:
        term = st.text_input("بحث في السجل", placeholder="اكتبي كلمة للبحث")
        rows = [r for r in st.session_state.history if term.strip().lower() in str(r).lower()]
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else: st.info("لا توجد نتائج مطابقة.")
        if st.button("مسح السجل التجريبي"):
            st.session_state.history = []
            st.rerun()
else:
    st.subheader("عن النظام")
    st.write("واجهة لنظام توليد الأسئلة الشائعة والإجابة عنها من المستندات باستخدام LangChain وGroq وSQLite بعد التكامل مع أكواد الفريق.")
    st.write("الوظائف المخططة: سؤال عام، سؤال من مستند، توليد FAQ، تلخيص، رفع ملفات، وسجل قابل للبحث.")
    st.warning("هذه النسخة تثبت شكل الواجهة والتفاعل المحلي فقط، ولا تثبت صحة نتائج الذكاء الاصطناعي.")

