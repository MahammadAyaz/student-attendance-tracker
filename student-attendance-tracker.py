import json
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# CONFIGURATION & PAGE SETUP
# ============================================================

DATA_FILE = Path(__file__).parent / "attendance_data.json"

st.set_page_config(
    page_title="Student Attendance Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# JSON FILE FUNCTIONS
# ============================================================

def save_data(data):
    """Save application data to the local JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return True
    except OSError as error:
        st.error(f"Could not save data: {error}")
        return False


def create_data_file():
    """Create the JSON file if it does not exist."""
    if not DATA_FILE.exists():
        save_data({
            "students": [],
            "attendance": []
        })


def load_data():
    """Load data from the JSON file."""
    create_data_file()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            data = {}

        data.setdefault("students", [])
        data.setdefault("attendance", [])

        return data

    except (json.JSONDecodeError, OSError):
        data = {
            "students": [],
            "attendance": []
        }
        save_data(data)
        return data


# ============================================================
# STUDENT FUNCTIONS
# ============================================================

def add_student(name, roll_number, branch, year):
    """Validate and add a new student."""
    name = name.strip()
    roll_number = roll_number.strip()
    branch = branch.strip()

    if not name:
        return False, "Student name cannot be empty."

    if not roll_number:
        return False, "Roll number cannot be empty."

    if not branch:
        return False, "Branch cannot be empty."

    data = load_data()

    # Check duplicate roll number
    for student in data["students"]:
        if student["roll_number"].strip().lower() == roll_number.lower():
            return False, "A student with this roll number already exists."

    data["students"].append({
        "name": name,
        "roll_number": roll_number,
        "branch": branch,
        "year": year
    })

    if save_data(data):
        st.session_state.data = data
        return True, "Student added successfully."

    return False, "Student could not be saved."


# ============================================================
# ATTENDANCE FUNCTIONS
# ============================================================

def save_attendance(roll_number, attendance_date, status):
    """Save or update attendance for a student on a specific date."""
    if not roll_number:
        return False, "Please select a student."

    data = load_data()

    student_exists = any(
        student["roll_number"] == roll_number
        for student in data["students"]
    )

    if not student_exists:
        return False, "Selected student was not found."

    date_string = attendance_date.isoformat()

    # Only one attendance record per student per date.
    for record in data["attendance"]:
        if (
            record["roll_number"] == roll_number
            and record["date"] == date_string
        ):
            record["status"] = status

            if save_data(data):
                st.session_state.data = data
                return True, "Attendance updated successfully."

            return False, "Attendance could not be saved."

    data["attendance"].append({
        "roll_number": roll_number,
        "date": date_string,
        "status": status
    })

    if save_data(data):
        st.session_state.data = data
        return True, "Attendance saved successfully."

    return False, "Attendance could not be saved."


# ============================================================
# ATTENDANCE CALCULATIONS
# ============================================================

def get_attendance_summary(roll_number):
    """Return total, present, absent and attendance percentage."""
    records = [
        record
        for record in st.session_state.data["attendance"]
        if record["roll_number"] == roll_number
    ]

    total_classes = len(records)

    present_classes = sum(
        1
        for record in records
        if record["status"] == "Present"
    )

    absent_classes = sum(
        1
        for record in records
        if record["status"] == "Absent"
    )

    percentage = (
        (present_classes / total_classes) * 100
        if total_classes > 0
        else 0
    )

    return (
        total_classes,
        present_classes,
        absent_classes,
        percentage
    )


def get_student_name(roll_number):
    """Return student name from roll number."""
    for student in st.session_state.data["students"]:
        if student["roll_number"] == roll_number:
            return student["name"]

    return "Unknown Student"


# ============================================================
# CUSTOM CSS & THEME DESIGN
# ============================================================

st.markdown(
    """
<style>
/* Main Background with Indigo-Blue-Cyan theme */
.stApp {
    background:
        radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.12), transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(6, 182, 212, 0.12), transparent 40%),
        linear-gradient(135deg, #f8fafc 0%, #e0e7ff 50%, #cffaff 100%);
    min-height: 100vh;
}

.block-container {
    max-width: 1200px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255, 255, 255, 0.5);
}

/* Hero Section */
.hero-container {
    background: linear-gradient(135deg, #4338ca 0%, #2563eb 50%, #0891b2 100%);
    padding: 32px 28px;
    border-radius: 20px;
    color: white;
    box-shadow: 0 12px 30px rgba(37, 99, 235, 0.25);
    margin-bottom: 24px;
}

.hero-container h1 {
    margin: 0;
    color: #ffffff !important;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 800;
    letter-spacing: -0.5px;
}

.hero-container p {
    margin: 8px 0 0 0;
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.05rem;
}

/* Stat Cards */
.stat-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
    text-align: center;
    transition: transform 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-card .val {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4338ca 0%, #0891b2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-card .lbl {
    font-size: 0.9rem;
    color: #475569;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Glass Panels */
.glass-panel {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    margin-bottom: 24px;
}

/* Form Styling */
div[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.8);
    padding: 24px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

/* Primary Buttons */
.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.6rem 1.2rem;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    transition: all 0.2s ease;
}

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(135deg, #4338ca 0%, #1d4ed8 100%);
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
}

/* Table Customization */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(226, 232, 240, 0.8);
}

/* Mobile Responsive Tweaks */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .hero-container {
        padding: 20px 16px;
    }
}
</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE
# ============================================================

if "data" not in st.session_state:
    st.session_state.data = load_data()

create_data_file()
st.session_state.data = load_data()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    st.title("🎓 Navigation")
    st.write("Manage attendance seamlessly.")
    
    selected_page = st.radio(
        "Go to",
        ["📊 Dashboard", "👨‍🎓 Students", "📝 Attendance", "📈 Reports"],
        index=0
    )
    
    st.markdown("---")
    st.caption("🔒 Storage: **Local JSON**")
    st.caption("🚫 Database: **None**")


# ============================================================
# HERO HEADER SECTION
# ============================================================

st.markdown(
    f"""
    <div class="hero-container">
        <h1>🎨 Student Attendance Tracker</h1>
        <p>Current Section: <b>{selected_page}</b></p>
    </div>
    """,
    unsafe_allow_html=True
)

students = st.session_state.data["students"]
attendance = st.session_state.data["attendance"]


# ============================================================
# PAGE 1: DASHBOARD
# ============================================================

if selected_page == "📊 Dashboard":
    st.subheader("📊 System Overview")

    # Global Stats Calculation
    total_students = len(students)
    total_records = len(attendance)
    total_present = sum(1 for r in attendance if r["status"] == "Present")
    overall_percentage = (total_present / total_records * 100) if total_records > 0 else 0.0

    # Modern Dashboard Stat Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="val">{total_students}</div><div class="lbl">Total Students</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="val">{total_records}</div><div class="lbl">Attendance Records</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="val">{total_present}</div><div class="lbl">Total Present</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="val">{overall_percentage:.1f}%</div><div class="lbl">Avg Attendance</div></div>', unsafe_allow_html=True)

    st.write("")
    
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.subheader("💡 Quick Actions & Status")
    if not students:
        st.info("👋 Welcome! Start by navigating to the **Students** section to register your first student.")
    else:
        st.success(f"System actively tracking {total_students} student(s) across {total_records} logged sessions.")
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PAGE 2: STUDENTS
# ============================================================

elif selected_page == "👨‍🎓 Students":
    st.subheader("👨‍🎓 Student Management")

    st.markdown("### Add New Student")
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            student_name = st.text_input(
                "Student Name",
                placeholder="Enter student name"
            )

            roll_number = st.text_input(
                "Roll Number",
                placeholder="Enter roll number"
            )

        with col2:
            branch = st.text_input(
                "Branch",
                placeholder="Example: CSE"
            )

            year = st.selectbox(
                "Year",
                [
                    "1st Year",
                    "2nd Year",
                    "3rd Year",
                    "4th Year"
                ]
            )

        add_button = st.form_submit_button(
            "➕ Add Student",
            use_container_width=True
        )

    if add_button:
        success, message = add_student(
            student_name,
            roll_number,
            branch,
            year
        )

        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    st.markdown("---")
    st.markdown("### 📋 Registered Students Directory")

    if students:
        student_table = []

        for student in students:
            total, present, absent, percentage = get_attendance_summary(
                student["roll_number"]
            )

            student_table.append({
                "Name": student["name"],
                "Roll Number": student["roll_number"],
                "Branch": student["branch"],
                "Year": student["year"],
                "Total Classes": total,
                "Present": present,
                "Absent": absent,
                "Attendance %": f"{percentage:.2f}%"
            })

        st.dataframe(
            student_table,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No students registered yet. Fill in the form above to add one.")


# ============================================================
# PAGE 3: ATTENDANCE
# ============================================================

elif selected_page == "📝 Attendance":
    st.subheader("📝 Attendance Entry")

    if students:
        student_options = {
            f"{student['name']} ({student['roll_number']})":
            student["roll_number"]
            for student in students
        }

        with st.form("attendance_form"):
            selected_student = st.selectbox(
                "Select Student",
                options=list(student_options.keys()),
                index=None,
                placeholder="Choose a student"
            )

            attendance_date = st.date_input(
                "Attendance Date",
                value=date.today()
            )

            attendance_status = st.radio(
                "Attendance Status",
                ["Present", "Absent"],
                horizontal=True
            )

            save_attendance_button = st.form_submit_button(
                "💾 Save Attendance Record",
                use_container_width=True
            )

        if save_attendance_button:
            if not selected_student:
                st.error("Please select a student before saving attendance.")
            else:
                selected_roll_number = student_options[selected_student]

                success, message = save_attendance(
                    selected_roll_number,
                    attendance_date,
                    attendance_status
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.warning("⚠️ Add at least one student in the **Students** tab before marking attendance.")


# ============================================================
# PAGE 4: REPORTS
# ============================================================

elif selected_page == "📈 Reports":
    st.subheader("📈 Analytics & Student Reports")

    if students:
        tab1, tab2 = st.tabs(["📊 Class Summary", "🔎 Individual Student Search"])

        with tab1:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown("### Class Attendance Summary")
            summary_table = []

            for student in students:
                total, present, absent, percentage = get_attendance_summary(
                    student["roll_number"]
                )

                summary_table.append({
                    "Name": student["name"],
                    "Roll Number": student["roll_number"],
                    "Total Classes": total,
                    "Present": present,
                    "Absent": absent,
                    "Attendance Percentage": f"{percentage:.2f}%"
                })

            st.dataframe(
                summary_table,
                use_container_width=True,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            detail_options = {
                f"{student['name']} ({student['roll_number']})":
                student["roll_number"]
                for student in students
            }

            selected_detail = st.selectbox(
                "Select a student to view details",
                options=list(detail_options.keys()),
                index=None,
                placeholder="Choose a student"
            )

            if selected_detail:
                roll_number = detail_options[selected_detail]
                student_name = get_student_name(roll_number)

                total, present, absent, percentage = get_attendance_summary(
                    roll_number
                )

                metric1, metric2, metric3, metric4 = st.columns(4)

                metric1.metric("Total Classes", total)
                metric2.metric("Present", present)
                metric3.metric("Absent", absent)
                metric4.metric("Attendance Rate", f"{percentage:.2f}%")

                records = [
                    record
                    for record in st.session_state.data["attendance"]
                    if record["roll_number"] == roll_number
                ]

                if records:
                    details_table = []

                    for record in sorted(
                        records,
                        key=lambda item: item["date"],
                        reverse=True
                    ):
                        details_table.append({
                            "Date": record["date"],
                            "Student": student_name,
                            "Status": record["status"]
                        })

                    st.dataframe(
                        details_table,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No attendance records found for this student.")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("No registered students found. Register students to unlock reports.")


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("🔒 All records stored locally in `attendance_data.json`. No external database required.")