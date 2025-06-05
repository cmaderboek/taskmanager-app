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

# --- Task-Bereinigung für erledigte Tasks (nach Fälligkeit + 30 Tage) ---
now = datetime.now()
tasks_to_keep_in_done = []
for task in st.session_state.sections[DONE_SECTION_ID]["tasks"]:
    # Nur löschen, wenn 'due' Datum vorhanden ist und 30 Tage nach Fälligkeit vergangen sind
    if "due" in task and (now - task["due"]).days > 30:
        continue # Task ist 30 Tage nach Fälligkeit überfällig, wird übersprungen (gelöscht)
    tasks_to_keep_in_done.append(task)
st.session_state.sections[DONE_SECTION_ID]["tasks"] = tasks_to_keep_in_done
# --- Ende Task-Bereinigung ---


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

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
#st.markdown("---")

# Stelle sicher, dass "Erledigte Tasks" zuletzt kommt
section_ids = list(st.session_state.sections.keys())
if DONE_SECTION_ID in section_ids:
    section_ids.remove(DONE_SECTION_ID)
    section_ids.append(DONE_SECTION_ID)


# UI: Sections und Tasks anzeigen
for section_id in section_ids:
    section = st.session_state.sections[section_id]
    section_border_color = COLOR_PALETTE[section['color']]

    if section_id != DONE_SECTION_ID:
    # Container für jede Section mit farbigem Rahmen
        st.markdown(
            f"<div style='border: 8px solid {section_border_color}; padding: 0px; border-radius: 10px; margin-bottom: 20px; margin-top: 70px;'>",
            unsafe_allow_html=True
        )

    if section_id == DONE_SECTION_ID:
        st.markdown("---")

    # Titelzeile mit Lösch-Button
    col1, col2 = st.columns([12, 1])
    with col1:
        st.markdown(f"### <span style='color:{COLOR_PALETTE[section['color']]};'>{section['name']}</span>", unsafe_allow_html=True)
    with col2:
        if section_id != DONE_SECTION_ID:
            if st.button("🗑️", key=f"delete_section_{section_id}"):
                st.session_state.delete_section_id = section_id
                st.rerun()

    # Neue Task anlegen
    if section_id != DONE_SECTION_ID:
        input_key = f"task_input_{section_id}"
        due_key = f"task_due_{section_id}"
        time_key = f"time_{section_id}"
        priority_key = f"task_priority_{section_id}"
        assigned_to_key = f"task_assigned_to_{section_id}"
        status_key = f"task_status_{section_id}"

        with st.expander("➕ Neuer Task"):
            content = st.text_input("Task-Beschreibung", key=input_key)
            assigned_to = st.text_input("Zugeordnet zu (optional)", key=assigned_to_key)
            status = st.selectbox("Status", options=["Offen", "In Bearbeitung"], key=status_key)
            due_date = st.date_input("Fälligkeitsdatum", value=datetime.now().date(), key=due_key)
            due_time = st.time_input("Fällige Uhrzeit", value=datetime.now().time(), key=time_key)
            priority = st.selectbox("Priorität", options=[3, 2, 1], format_func=lambda x: PRIORITY_LABELS[x], key=priority_key)


            if st.button("Speichern", key=f"save_{section_id}"):
                if content.strip():
                    task = {
                        "content": content.strip(),
                        "due": datetime.combine(due_date, due_time),
                        "priority": priority,
                        "assigned_to": assigned_to.strip() if assigned_to.strip() else "Nicht zugewiesen", # Speichert zugewiesene Person
                        "status": status, # Speichert den Status
                        "from_section": section_id
                    }
                    section["tasks"].append(task)
                    st.rerun()
                else:
                    st.warning("Bitte gib eine Task-Beschreibung ein.")

    # Tasks anzeigen
    tasks_sorted = sorted(section["tasks"], key=lambda x: (x["due"], -x["priority"]))
    for i, task in enumerate(tasks_sorted):
        col1, col2, col3, col4 = st.columns([14, 6, 6, 6]) # Eine Spalte mehr für Status oder Aktion

        with col1:
            days_left = (task["due"].date() - datetime.now().date()).days
            due_str = task["due"].strftime("%d.%m.%Y %H:%M")

            # Farbliche Hervorhebung für überfällige Tasks
            days_left_display = ""
            if days_left < 0:
                days_left_display = f"<span style='color:red;'>({abs(days_left)} Tage überfällig)</span>"
            elif days_left == 0:
                days_left_display = f"<span style='color:red;'>(Heute fällig)</span>"
            else:
                days_left_display = f"({days_left} Tage)"

            st.markdown(f"**{PRIORITY_LABELS[task['priority']]}**  \n{task['content']}  \n{due_str} {days_left_display}  \n  \n**Zugeordnet:** {task.get('assigned_to', 'Nicht zugewiesen')}", unsafe_allow_html=True)

            # Status "In Bearbeitung" anzeigen
            if task.get("status") == "In Bearbeitung":
                st.markdown(
                    f"<div style='display:inline-block; background-color:{COLOR_PALETTE['Gelb']}; color:black; padding: 2px 8px; border-radius: 10px; font-size: 0.75em;'>In Bearbeitung</div>",
                    unsafe_allow_html=True
                )

        with col2:
            if section_id != DONE_SECTION_ID:
                if st.button("✔️ Erledigt", key=f"done_{section_id}_{i}"):
                    task["done_color"] = section["color"]
                    # 'completed_at' wird hier nicht mehr benötigt, da das Löschen an 'due' hängt
                    st.session_state.sections[DONE_SECTION_ID]["tasks"].append(task)
                    section["tasks"].pop(i)
                    st.rerun()
        with col3:
            if section_id != DONE_SECTION_ID:
                if st.button("🗑️ Löschen", key=f"delete_task_{section_id}_{i}"):
                    section["tasks"].pop(i)
                    st.rerun()
            if section_id == DONE_SECTION_ID: # Löschen-Button für erledigte Tasks
                if st.button("🗑️ Löschen", key=f"delete_done_task_{section_id}_{i}"):
                    section["tasks"].pop(i)
                    st.rerun()
        with col4:
            if section_id == DONE_SECTION_ID:
                # In der "Erledigte Tasks" Section nur die Farbkugel anzeigen
                color = COLOR_PALETTE.get(task.get("done_color", "Grau"), "#cccccc")
                st.markdown(f"<div style='width:20px;height:20px;background-color:{color};border-radius:50%;'></div>", unsafe_allow_html=True)


st.markdown("</div>", unsafe_allow_html=True) # Ende des Section-Containers


#st.markdown("---")

# Section wirklich löschen
if st.session_state.delete_section_id:
    del st.session_state.sections[st.session_state.delete_section_id]
    st.session_state.delete_section_id = None
    st.rerun()

