import streamlit as st
from datetime import datetime

# Color options for sections (re-import or make global if many pages use them)
COLOR_PALETTE = {
    "Blau": "#00859c",
    "Grün": "#00784f",
    "Rot": "#fc4024",
    "Orange": "#f8991d",
    "Lila": "#8552a0",
    "Gelb": "#f7ce15",
    "Rosa": "#ef4782",
    "Grau": "#aaaaaa"
}

# Priority labels (re-import or make global)
PRIORITY_LABELS = {
    3: "★★★",
    2: "★★",
    1: "★"
}

# Ensure "Erledigte Tasks" section exists (crucial for accessing its data)
DONE_SECTION_ID = "done_tasks"
if DONE_SECTION_ID not in st.session_state.sections:
    st.session_state.sections[DONE_SECTION_ID] = {
        "name": "Erledigte Tasks",
        "color": "Grau",
        "tasks": [],
        "shared_with": [],
        "id": DONE_SECTION_ID
    }

# --- Task cleanup for completed tasks (after due date + 30 days) ---
now = datetime.now()
tasks_to_keep_in_done = []
for task in st.session_state.sections[DONE_SECTION_ID]["tasks"]:
    if "due" in task and (now - task["due"]).days > 30:
        continue
    tasks_to_keep_in_done.append(task)
st.session_state.sections[DONE_SECTION_ID]["tasks"] = tasks_to_keep_in_done
# --- End Task cleanup ---

st.markdown("""
<div style='text-align: center; font-size: 80px; font-family: "Source Sans Pro", sans-serif; font-weight: 800;'>
    Erledigte Tasks
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

section = st.session_state.sections[DONE_SECTION_ID]
section_border_color = COLOR_PALETTE[section['color']]

# Container for the "Erledigte Tasks" section
st.markdown(
    f"<div style='border: 8px solid {section_border_color}; padding: 0px; border-radius: 10px; margin-bottom: 20px; margin-top: 70px;'>",
    unsafe_allow_html=True
)

st.markdown(f"### <span style='color:{COLOR_PALETTE[section['color']]};'>{section['name']}</span>", unsafe_allow_html=True)

# Display tasks in "Erledigte Tasks"
tasks_sorted = sorted(section["tasks"], key=lambda x: (x["due"], -x["priority"]))
for i, task in enumerate(tasks_sorted):
    col1, col2, col3, col4 = st.columns([11.5, 4.5, 5, 4.5])

    with col1:
        days_left = (task["due"].date() - datetime.now().date()).days
        due_str = task["due"].strftime("%d.%m.%Y %H:%M")

        days_left_display = ""
        if days_left < 0:
            days_left_display = f"<span style='color:red;'>({abs(days_left)} Tage überfällig)</span>"
        elif days_left == 0:
            days_left_display = f"<span style='color:red;'>(Heute fällig)</span>"
        else:
            days_left_display = f"({days_left} Tage)"

        st.markdown(f"**{PRIORITY_LABELS[task['priority']]}** \n{task['content']}  \n{due_str} {days_left_display}  \n  \n**Zugeordnet:** {task.get('assigned_to', 'Nicht zugewiesen')}", unsafe_allow_html=True)
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    with col3:
        # Display color circle in "Erledigte Tasks" section
        color = COLOR_PALETTE.get(task.get("done_color", "Grau"), "#cccccc")
        st.markdown(f"<div style='width:20px;height:20px;background-color:{color};border-radius:50%;'></div>", unsafe_allow_html=True)
    with col4:
        if st.button("🗑️ Löschen", key=f"delete_done_task_{task['id']}"):
            section["tasks"].remove(task)
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True) # End of the Section container