import streamlit as st
from datetime import datetime, timedelta
import uuid

# Farboptionen für Sections
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

# Prioritäten festlegen
PRIORITY_LABELS = { 
    3: "★★★",
    2: "★★",
    1: "★"
}

# Initialisierung
if "sections" not in st.session_state:
    st.session_state.sections = {}

if "add_section_mode" not in st.session_state:
    st.session_state.add_section_mode = False

if "new_task_inputs" not in st.session_state:
    st.session_state.new_task_inputs = {}

if "delete_section_id" not in st.session_state:
    st.session_state.delete_section_id = None

# Stelle sicher, dass die "Erledigte Tasks"-Section existiert
DONE_SECTION_ID = "done_tasks"
if DONE_SECTION_ID not in st.session_state.sections:
    st.session_state.sections[DONE_SECTION_ID] = {
        "name": "Erledigte Tasks",
        "color": "Grau",
        "tasks": [],
        "shared_with": [],
        "id": DONE_SECTION_ID
    }

# Titel
st.markdown("""
<div style='text-align: center; font-size: 80px; font-family: "Source Sans Pro", sans-serif; font-weight: 800;'>
    TaskBuddy
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# UI: Neue Section anlegen
if not st.session_state.add_section_mode:
    col1, col2, col3 = st.columns([3, 3, 3])
    with col2:
        if st.button("➕ Neue Section anlegen"):
            st.session_state.add_section_mode = True
            st.rerun()
else:
    st.markdown("""
    <div style='font-size: 1.75rem; font-family: "Source Sans Pro", sans-serif; font-weight: 600; margin-bottom: 1.25rem;'>
        Neue Section
    </div>
    """, unsafe_allow_html=True)
    section_name = st.text_input("Name der neuen Section")
    section_color = st.selectbox("Farbe der neuen Section wählen", list(COLOR_PALETTE.keys())[:-1])  # Grau ausgeschlossen

    col1, col2 = st.columns([13, 3])  
    with col1:
        if st.button("✔️ Fertig"):
            if section_name.strip():
                section_id = str(uuid.uuid4())
                st.session_state.sections[section_id] = {
                    "name": section_name.strip(),
                    "color": section_color,
                    "tasks": [],
                    "shared_with": [],
                    "id": section_id
                }
                st.session_state.new_task_inputs[section_id] = {}
                st.session_state.add_section_mode = False
                st.rerun()
            else:
                st.warning("Bitte gib einen Namen ein.")
    with col2:
        if st.button("✖️ Abbrechen"):
            st.session_state.add_section_mode = False
            st.rerun()

st.markdown("---")

# Stelle sicher, dass "Erledigte Tasks" zuletzt kommt
section_ids = list(st.session_state.sections.keys())
if DONE_SECTION_ID in section_ids:
    section_ids.remove(DONE_SECTION_ID)
    section_ids.append(DONE_SECTION_ID)


# UI: Sections und Tasks anzeigen
# UI: Sections und Tasks anzeigen
for section_id in section_ids:
    section = st.session_state.sections[section_id]

    if f"task_form_open_{section_id}" not in st.session_state:
        st.session_state[f"task_form_open_{section_id}"] = False

    section_color = COLOR_PALETTE[section["color"]]
    section_name = section["name"]

    with st.expander(" ", expanded=True):  # Platzhalter, wird überschrieben
        # Eigener Titel in Farbe & Format
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(
                f"<div style='font-size:24px; font-weight:700; color:{section_color}; margin-top:-35px; margin-bottom:10px;'>{section_name}</div>",
                unsafe_allow_html=True)
        with col2:
            if section_id != DONE_SECTION_ID:
                if st.button("🗑", key=f"delete_section_{section_id}"):
                    st.session_state.delete_section_id = section_id
                    st.rerun()

        # ➕ Neuer Task Button
        if section_id != DONE_SECTION_ID:
            if st.button("➕ Neuen Task hinzufügen", key=f"show_task_form_btn_{section_id}"):
                st.session_state[f"task_form_open_{section_id}"] = not st.session_state[f"task_form_open_{section_id}"]

        # Task-Formular
        if st.session_state[f"task_form_open_{section_id}"]:
            with st.form(key=f"task_form_{section_id}"):
                content = st.text_input("Task-Beschreibung", key=f"task_input_{section_id}")
                due_date = st.date_input("Fälligkeitsdatum", value=datetime.now().date(), key=f"task_due_{section_id}")
                due_time = st.time_input("Fällige Uhrzeit", value=datetime.now().time(), key=f"time_{section_id}")
                priority = st.selectbox("Priorität", options=[3, 2, 1],
                                        format_func=lambda x: PRIORITY_LABELS[x], key=f"task_priority_{section_id}")

                submitted = st.form_submit_button("Speichern")
                if submitted:
                    if content.strip():
                        task = {
                            "content": content.strip(),
                            "due": datetime.combine(due_date, due_time),
                            "priority": priority,
                            "assigned_to": [],
                            "from_section": section_id
                        }
                        section["tasks"].append(task)
                        st.session_state[f"task_form_open_{section_id}"] = False
                        st.rerun()
                    else:
                        st.warning("Bitte gib eine Task-Beschreibung ein.")

        # Aufgaben anzeigen
        tasks_sorted = sorted(section["tasks"], key=lambda x: (x["due"], -x["priority"]))
        for i, task in enumerate(tasks_sorted):
            col1, col2, col3 = st.columns([16, 4, 4])
            with col1:
                days_left = (task["due"].date() - datetime.now().date()).days
                due_str = task["due"].strftime("%d.%m.%Y %H:%M")
                st.markdown(f"{PRIORITY_LABELS[task['priority']]}  \n{task['content']}  \n{due_str} ({days_left} Tage)")
            with col2:
                if section_id != DONE_SECTION_ID:
                    if st.button("✔ Erledigt", key=f"done_{section_id}_{i}"):
                        task["done_color"] = section["color"]
                        st.session_state.sections[DONE_SECTION_ID]["tasks"].append(task)
                        section["tasks"].pop(i)
                        st.rerun()
            with col3:
                if section_id != DONE_SECTION_ID:
                    if st.button("🗑 Löschen", key=f"delete_task_{section_id}_{i}"):
                        section["tasks"].pop(i)
                        st.rerun()
                else:
                    color = COLOR_PALETTE.get(task.get("done_color", "Grau"), "#cccccc")
                    st.markdown(
                        f"<div style='width:20px;height:20px;background-color:{color};border-radius:50%;'></div>",
                        unsafe_allow_html=True
                    )
                    if st.button("🗑 Löschen", key=f"delete_done_task_{section_id}_{i}"):
                        section["tasks"].pop(i)
                        st.rerun()





st.markdown("---")

# Section wirklich löschen
if st.session_state.delete_section_id:
    del st.session_state.sections[st.session_state.delete_section_id]
    st.session_state.delete_section_id = None
    st.rerun()

# Teilen
st.markdown("Teilen")
share_link = f"https://mein-taskmanager.de/invite/{section_id}"
st.code(share_link)
st.text("Versende den Link z.B. per WhatsApp oder E-Mail.")
if section["shared_with"]:
    st.markdown("👥 Geteilt mit: " + ", ".join(section["shared_with"]))
