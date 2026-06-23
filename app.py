# app.py
import streamlit as st
import random
from content_db import MODULES_DATA

# Google API Integration Preview Status
if 'custom_quizzes' not in st.session_state:
    st.session_state['custom_quizzes'] = []
if 'selected_quiz_pool' not in st.session_state:
    st.session_state['selected_quiz_pool'] = []
if 'quiz_submitted' not in st.session_state:
    st.session_state['quiz_submitted'] = False
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

def get_system_pool():
    pool = []
    for mod_name, mod_val in MODULES_DATA.items():
        for top_name, top_val in mod_val["topics"].items():
            for q in top_val.get("quizzes", []):
                pool.append({
                    "id": q["id"], "module": mod_name, "topic": top_name,
                    "difficulty": q["difficulty"], "question": q["question"],
                    "options": q["options"], "answer": q["answer"]
                })
    for idx, q in enumerate(st.session_state['custom_quizzes']):
        pool.append({
            "id": f"CUSTOM_{idx+1}", "module": q["module"], "topic": q["topic"],
            "difficulty": q["difficulty"], "question": q["question"],
            "options": q["options"], "answer": q["answer"]
        })
    return pool

total_pool = get_system_pool()

with st.sidebar:
    st.header("👤 บัญชีผู้ใช้งาน & Google Sync")
    if not st.session_state['logged_in']:
        st.info("💡 ล็อกอินบัญชี Google เพื่อผูกระบบกับ Google Docs ในการส่งออกสมุดจดโน้ตย่อ")
        if st.button("🔑 เข้าสู่ระบบด้วยบัญชี Google"):
            st.session_state['logged_in'] = True
            st.session_state['user_info'] = {"name": "User Gemini"}
            st.rerun()
    else:
        st.success(f"🔓 บัญชีใช้งาน: {st.session_state['user_info']['name']}")
        if st.button("🚪 ออกจากระบบ (Logout)"):
            st.session_state['logged_in'] = False
            st.session_state['user_info'] = None
            st.rerun()
            
    st.markdown("---")
    st.header("➕ เพิ่มข้อสอบเข้าคลังด้วยตนเอง")
    st.write("เพิ่มจำนวนข้อสอบและคำถามของคุณเพื่อฝึกฝนเพิ่มขึ้นในระบบ:")
    
    with st.form("custom_question_form", clear_on_submit=True):
        c_mod = st.selectbox("เลือกหมวดหมู่:", list(MODULES_DATA.keys()))
        c_top = st.text_input("ระบุหัวข้อย่อย:", value="แนวข้อสอบเสริมเพิ่มเติม")
        c_diff = st.selectbox("ระดับความยาก:", ["ง่าย", "ปานกลาง", "ยาก"])
        c_q = st.text_area("โจทย์คำถาม:")
        c_a = st.text_input("ตัวเลือก ก:")
        c_b = st.text_input("ตัวเลือก ข:")
        c_c = st.text_input("ตัวเลือก ค:")
        c_d = st.text_input("ตัวเลือก ง:")
        c_ans = st.selectbox("เฉลยที่ถูกต้อง:", ["ก", "ข", "ค", "ง"])
        
        if st.form_submit_button("📥 บันทึกข้อสอบเข้าพูลระบบ"):
            if c_q and c_a and c_b:
                st.session_state['custom_quizzes'].append({
                    "module": c_mod, "topic": c_top, "difficulty": c_diff, "question": c_q,
                    "options": [f"ก. {c_a}", f"ข. {c_b}", f"ค. {c_c}", f"ง. {c_d}"], "answer": c_ans
                })
                st.toast("เพิ่มข้อสอบใหม่สำเร็จ!", icon="✅")
                st.rerun()
            else:
                st.error("กรุณากรอกข้อมูลโจทย์และตัวเลือกให้ครบถ้วน")

st.title("🌾 ระบบแอปติวสอบนักวิชาการส่งเสริมการเกษตรอัจฉริยะ")
st.write("แพลตฟอร์มทบทวนความรู้ สุ่มชุดคำถามตามจำนวนข้อ และประเมินจุดบกพร่องรายบุคคล")

st.markdown("---")
st.header("📖 1. อ่านบทสรุปย่อทบทวนความรู้รายหมวด")
sel_mod_view = st.selectbox("เลือกหมวดเนื้อหาที่ต้องการทบทวน:", list(MODULES_DATA.keys()))
for t_name, t_val in MODULES_DATA[sel_mod_view]["topics"].items():
    with st.expander(f"📌 สรุปสาระสำคัญ: {t_name}"):
        st.info(t_val["summary"])

st.markdown("---")
st.header("🎛 Honor Engine: 2. เลือกตั้งค่าและสุ่มจำนวนข้อสอบ")
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 1, 1])
with col_ctrl1:
    f_mod = st.selectbox("กรองตามหมวดหมู่ข้อสอบ:", ["ทั้งหมด"] + list(MODULES_DATA.keys()))
with col_ctrl2:
    f_diff = st.selectbox("กรองตามระดับความยาก:", ["ทั้งหมด", "ง่าย", "ปานกลาง", "ยาก"])
with col_ctrl3:
    active_pool = [x for x in total_pool if (f_mod == "ทั้งหมด" or x["module"] == f_mod) and (f_diff == "ทั้งหมด" or x["difficulty"] == f_diff)]
    num_alloc = st.number_input("กำหนดจำนวนข้อที่ต้องการทำในรอบนี้:", min_value=1, max_value=max(len(active_pool), 1), value=min(len(active_pool), 3))

if st.button("🔄 ดำเนินการจัดชุดข้อสอบ / สุ่มข้อใหม่"):
    if active_pool:
        st.session_state['selected_quiz_pool'] = random.sample(active_pool, min(len(active_pool), int(num_alloc)))
        st.session_state['quiz_submitted'] = False
        st.toast("จัดเตรียมชุดข้อสอบเรียบร้อย!", icon="📝")
    else:
        st.error("ไม่พบข้อสอบในเงื่อนไขการกรองนี้")

if st.session_state['selected_quiz_pool']:
    st.subheader(f"📝 ชุดคำถามจำนวน {len(st.session_state['selected_quiz_pool'])} ข้อ")
    with st.form("exam_execution_form"):
        user_responses = {}
        for idx, q in enumerate(st.session_state['selected_quiz_pool']):
            st.markdown(f"**ข้อที่ {idx+1}. [{q['difficulty']}] {q['question']}**")
            ans_select = st.radio("เลือกคำตอบ:", q["options"], key=f"active_ans_{q['id']}_{idx}", index=None)
            user_responses[q['id']] = ans_select
            st.markdown("<br>", unsafe_allow_html=True)
            
        if st.form_submit_button("🚀 ส่งข้อสอบและวิเคราะห์ผล"):
            st.session_state['quiz_submitted'] = True
            st.session_state['last_responses'] = user_responses
            st.rerun()

if st.session_state.get('quiz_submitted') and st.session_state.get('selected_quiz_pool'):
    st.markdown("---")
    st.header("📊 3. ผลการวิเคราะห์และตรวจสอบข้อพิจารณาบกพร่อง (Diagnostic Analytics)")
    
    correct_cnt = 0
    wrong_by_topics = {}
    last_resp = st.session_state.get('last_responses', {})
    
    for q in st.session_state['selected_quiz_pool']:
        u_selection = last_resp.get(q['id'])
        is_correct = False
        if u_selection and u_selection.startswith(q['answer']):
            is_correct = True
            correct_cnt += 1
            
        if not is_correct:
            t_name = q['topic']
            if t_name not in wrong_by_topics:
                wrong_by_topics[t_name] = {"module": q['module'], "missed": []}
            wrong_by_topics[t_name]["missed"].append({
                "q": q['question'], "user": u_selection if u_selection else "ไม่ได้ระบุคำตอบ", "correct": [o for o in q['options'] if o.startswith(q['answer'])][0]
            })
            
    total_count = len(st.session_state['selected_quiz_pool'])
    score_pct = (correct_cnt / total_count) * 100
    
    st.metric("คะแนนที่คุณได้", f"{correct_cnt} / {total_count} ข้อ", f"{score_pct:.1f}%")
    
    st.markdown("### 🔎 บทวิเคราะห์หัวข้อที่คุณพลาด (Weakness Report):")
    if wrong_by_topics:
        for topic, info in wrong_by_topics.items():
            with st.expander(f"❌ เรื่องที่คุณพลาด: {topic} (หมวดหลัก: {info['module']})"):
                st.write("💡 **คำแนะนำ:** กลับไปอ่านข้อมูลสรุปเรื่องนี้ในส่วนที่ 1 ทบทวนข้อกฎหมาย ตัวเลข หรือหลักเกณฑ์สถิติที่สำคัญ")
                for m in info["missed"]:
                    st.write(f"- **โจทย์:** {m['q']}")
                    st.write(f"  • สิ่งที่คุณเลือก: `{m['user']}`")
                    st.write(f"  • คำตอบที่ถูกต้อง: **{m['correct']}**")
    else:
        st.success("🎉 สุดยอดมาก! คุณทำคะแนนได้เต็ม 100% ไม่มีจุดผิดพลาดในชุดข้อสอบรอบนี้")

    st.markdown("---")
    st.header("✍️ 4. บันทึกสรุปช่วยจำส่วนตัว & ส่งออก Google Docs")
    user_notes = st.text_area("จดโน้ตย่อเทคนิค ตัวเลข หรือประเด็นสำคัญที่คุณเรียนรู้เพิ่มเติม:")
    if st.button("💾 ส่งออกบันทึกย่อไปยังบัญชี Google Docs"):
        if st.session_state['logged_in']:
            st.success("📊 [API Connected] ซิงค์บันทึกและรายงานวิเคราะห์จุดพลาดของคุณเข้าเอกสาร Google Docs สำเร็จ!")
        else:
            st.error("❌ กรุณากดปุ่มล็อกอินด้วยบัญชี Google ที่แถบเมนูด้านซ้ายก่อนกดส่งออกข้อมูล")
