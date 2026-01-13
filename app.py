
import streamlit as st

# ======================
# GLOBAL CONFIG
# ======================

st.set_page_config(page_title="GITAM Grade & CGPA Calculator", layout="centered")

GRADE_POINT_MAP = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "P": 4,
    "L": 0,   # Learning engagement not met
    "I": 0    # Incomplete
} 

# ======================
# CORE LOGIC
# ======================

def marks_to_gp(marks, max_marks):
    percent = (marks / max_marks) * 100
    if percent >= 90: return 10
    if percent >= 80: return 9
    if percent >= 70: return 8
    if percent >= 60: return 7
    if percent >= 50: return 6
    if percent >= 40: return 5
    if percent >= 33: return 4
    return 0

def wgp_to_grade(wgp):
    if wgp > 9: return "O"
    if wgp > 8: return "A+"
    if wgp > 7: return "A"
    if wgp > 6: return "B+"
    if wgp > 5: return "B"
    if wgp > 4: return "C"
    if wgp == 4: return "P"
    return "F"

def calculate_final_grade(s1, le_grade, s2):
    s1_gp = marks_to_gp(s1, 30)
    s2_gp = marks_to_gp(s2, 45)
    le_gp = GRADE_POINT_MAP[le_grade]

    wgp = (0.30 * s1_gp) + (0.25 * le_gp) + (0.45 * s2_gp)
    final_grade = wgp_to_grade(wgp)

    return round(wgp, 2), final_grade

def required_s2_for_target(s1, le, target):
    s1_gp = marks_to_gp(s1, 30)
    le_gp = GRADE_POINT_MAP[le]
    target_gp = GRADE_POINT_MAP[target]

    req_gp = (target_gp - (0.3*s1_gp) - (0.25*le_gp)) / 0.45

    if req_gp > 10:
        return None

    marks = (req_gp / 10) * 45
    if marks > 45:
        return None

    return round(max(0, marks), 2)

def calculate_cgpa(courses):
    completed = [c for c in courses if c["grade"] != "I"]

    if not completed:
        return None, ["All courses are incomplete."]

    total_credits = sum(c["credits"] for c in completed)
    weighted_sum = sum(
        GRADE_POINT_MAP[c["grade"]] * c["credits"]
        for c in completed
    )

    cgpa = round(weighted_sum / total_credits, 2)

    incomplete_courses = [c["name"] for c in courses if c["grade"] == "I"]

    return cgpa, incomplete_courses


# ======================
# UI
# ======================

st.title("🎓 GITAM Grade & CGPA Calculator")
st.caption("No departments. No semesters. Just grades and math.")

mode = st.radio(
    "Choose what you want to calculate:",
    ["📘 Course Grade Predictor", "📊 CGPA Calculator"]
)

# --------------------------------------------------
# MODE 1: COURSE GRADE PREDICTOR
# --------------------------------------------------

if mode == "📘 Course Grade Predictor":

    st.header("📘 Course Grade Predictor")

    s1 = st.number_input("Sessional 1 Marks (out of 30)", 0.0, 30.0)
    le = st.selectbox("Learning Engagement Grade", list(GRADE_POINT_MAP.keys()))
    if le == "L":
        st.warning("⚠️ Learning Engagement = L severely impacts final grade.")

    st.subheader("🔮 Required Sessional 2 Marks")

    for g in ["P","C","B","B+","A","A+","O"]:
        req = required_s2_for_target(s1, le, g)
        if req is None:
            st.write(f"**{g}** → ❌ Not achievable")
        else:
            st.write(f"**{g}** → ~{req}/45")

    st.divider()

    st.subheader("📊 Already have Sessional 2 marks?")
    s2 = st.number_input("Sessional 2 Marks (out of 45)", 0.0, 45.0)

    if st.button("Calculate Final Grade"):
        wgp, grade = calculate_final_grade(s1, le, s2)
        st.success(f"🎯 Final Grade: **{grade}**")
        st.info(f"Weighted Grade Point: **{wgp}**")

# --------------------------------------------------
# MODE 2: CGPA CALCULATOR
# --------------------------------------------------

if mode == "📊 CGPA Calculator":

    st.header("📊 CGPA Calculator")
    st.caption("Add as many courses as you want. Only grade + credits matter.")

    if "courses" not in st.session_state:
        st.session_state.courses = []

    with st.form("add_course_form"):
        course_name = st.text_input("Course name (optional)")
        credits = st.number_input("Credits", min_value=1, step=1)
        grade = st.selectbox(
    "Final Grade",
    ["O","A+","A","B+","B","C","P","I"]
)
        submitted = st.form_submit_button("➕ Add course")

        if submitted:
            st.session_state.courses.append({
                "name": course_name if course_name else "Unnamed course",
                "credits": credits,
                "grade": grade
            })

    if st.session_state.courses:
        st.subheader("📚 Courses added")

        for i, c in enumerate(st.session_state.courses):
            st.write(
                f"{i+1}. **{c['name']}** — {c['credits']} credits — Grade {c['grade']}"
            )

        if st.button("Calculate CGPA"):
    result = calculate_cgpa(st.session_state.courses)

    cgpa, incomplete = result

    if cgpa is None:
        st.error("❌ No completed courses yet.")
    else:
        st.success(f"🎯 Current CGPA: **{cgpa}**")

        if incomplete:
            st.warning(
                f"📌 {len(incomplete)} course(s) incomplete: "
                + ", ".join(incomplete)
            )
            st.info("You’re almost there — finish strong 💪")
        else:
            st.balloons()
            st.success("🔥 All courses completed. Proud of you.")

        if st.button("Clear all courses"):
            st.session_state.courses = []

st.caption(
    "⚠️ This is an unofficial student-built tool for guidance only. "
    "It is not affiliated with or endorsed by GITAM University."
)
