import streamlit as st
from datetime import datetime, timedelta
import uuid

# Color options for sections
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

# Priority labels
PRIORITY_LABELS = {
    3: "★★★",
    2: "★★",
    1: "★"
}

# Initialization
if "sections" not in st.session_state:
    st.session_state.sections = {}

if "add_section_mode" not in st.session_state:
    st.session_state.add_section_mode = False

if "new_task_inputs" not in st.session_state:
    st.session_state.new_task_inputs = {}

if "delete_section_id" not in st.session_state:
    st.session_state.delete_section_id = None

if "edit_section_id" not in st.session_state:
    st.session_state.edit_section_id = None

if "edit_task_id" not in st.session_state:
    st.session_state.edit_task_id = None

# Ensure "Erledigte Tasks" section exists
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
    # Only delete if 'due' date exists and 30 days after due have passed
    if "due" in task and (now - task["due"]).days > 30:
        continue # Task is 30 days overdue, skipped (deleted)
    tasks_to_keep_in_done.append(task)
st.session_state.sections[DONE_SECTION_ID]["tasks"] = tasks_to_keep_in_done
# --- End Task cleanup ---


# Title
st.markdown("""
<div style='text-align: center; font-size: 80px; font-family: "Source Sans Pro", sans-serif; font-weight: 800;'>
    TaskBuddy
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# UI: Create new section
if not st.session_state.add_section_mode and not st.session_state.edit_section_id:
    col1, col2, col3 = st.columns([3, 3, 3])
    with col2:
        if st.button("➕ Neue Section anlegen"):
            st.session_state.add_section_mode = True
            st.rerun()
elif st.session_state.add_section_mode:
    st.markdown("""
    <div style='font-size: 1.75rem; font-family: "Source Sans Pro", sans-serif; font-weight: 600; margin-bottom: 1.25rem;'>
        Neue Section
    </div>
    """, unsafe_allow_html=True)
    section_name = st.text_input("Name der neuen Section")
    section_color = st.selectbox("Farbe der neuen Section wählen", list(COLOR_PALETTE.keys())[:-1])  # Grau excluded

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
                # Initialize new_task_inputs for the newly created section
                st.session_state.new_task_inputs[section_id] = {
                    "content": "",
                    "assigned_to": "",
                    "status": "Offen",
                    "due_date": datetime.now().date(),
                    "due_time": datetime.now().time(),
                    "priority": 3
                }
                st.session_state.add_section_mode = False
                st.rerun()
            else:
                st.warning("Bitte gib einen Namen ein.")
    with col2:
        if st.button("✖️ Abbrechen"):
            st.session_state.add_section_mode = False
            st.rerun()

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# Ensure "Erledigte Tasks" comes last
section_ids = list(st.session_state.sections.keys())
if DONE_SECTION_ID in section_ids:
    section_ids.remove(DONE_SECTION_ID)
    section_ids.append(DONE_SECTION_ID)


# UI: Display sections and tasks
for section_id in section_ids:
    section = st.session_state.sections[section_id]
    section_border_color = COLOR_PALETTE[section['color']]

    if section_id != DONE_SECTION_ID:
        # Container for each section with colored border
        st.markdown(
            f"<div style='border: 8px solid {section_border_color}; padding: 0px; border-radius: 10px; margin-bottom: 20px; margin-top: 70px;'>",
            unsafe_allow_html=True
        )

    if section_id == DONE_SECTION_ID:
        st.markdown("---")

    # Title row with delete and edit buttons
    col1, col2, col3 = st.columns([10, 1, 1])
    with col1:
        st.markdown(f"### <span style='color:{COLOR_PALETTE[section['color']]};'>{section['name']}</span>", unsafe_allow_html=True)
    with col2:
        if section_id != DONE_SECTION_ID:
            if st.button("✏️", key=f"edit_section_{section_id}"):
                st.session_state.edit_section_id = section_id
                st.session_state.add_section_mode = False # Exit add mode if in it
                st.rerun()
    with col3:
        if section_id != DONE_SECTION_ID:
            if st.button("🗑️", key=f"delete_section_{section_id}"):
                st.session_state.delete_section_id = section_id
                st.rerun()

    # Edit section mode
    if st.session_state.edit_section_id == section_id:
        st.markdown(f"#### Section bearbeiten: {section['name']}")
        edited_section_name = st.text_input("Neuer Name", value=section["name"], key=f"edit_section_name_{section_id}")
        edited_section_color = st.selectbox("Neue Farbe", list(COLOR_PALETTE.keys())[:-1], index=list(COLOR_PALETTE.keys())[:-1].index(section["color"]), key=f"edit_section_color_{section_id}")

        col_edit1, col_edit2 = st.columns([22, 4])
        with col_edit1:
            if st.button("Änderungen speichern", key=f"save_edit_section_{section_id}"):
                if edited_section_name.strip():
                    section["name"] = edited_section_name.strip()
                    section["color"] = edited_section_color
                    st.session_state.edit_section_id = None
                    st.rerun()
                else:
                    st.warning("Bitte gib einen Namen ein.")
        with col_edit2:
            if st.button("✖️ Abbrechen", key=f"cancel_edit_section_{section_id}"):
                st.session_state.edit_section_id = None
                st.rerun()
    else:
        # New task creation (only if not in edit section mode)
        if section_id != DONE_SECTION_ID:
            input_key = f"task_input_{section_id}"
            due_key = f"task_due_{section_id}"
            time_key = f"time_{section_id}"
            priority_key = f"task_priority_{section_id}"
            assigned_to_key = f"task_assigned_to_{section_id}"
            status_key = f"task_status_{section_id}"

            # Initialize new_task_inputs for the current section if not already present
            if section_id not in st.session_state.new_task_inputs:
                st.session_state.new_task_inputs[section_id] = {
                    "content": "",
                    "assigned_to": "",
                    "status": "Offen",
                    "due_date": datetime.now().date(),
                    "due_time": datetime.now().time(),
                    "priority": 3
                }

            with st.expander("➕ Neuer Task"):
                # Use session_state to store and retrieve input values
                content = st.text_input(
                    "Task-Beschreibung",
                    value=st.session_state.new_task_inputs[section_id]["content"],
                    key=input_key
                )
                assigned_to = st.text_input(
                    "Zugeordnet zu (optional)",
                    value=st.session_state.new_task_inputs[section_id]["assigned_to"],
                    key=assigned_to_key
                )
                status = st.selectbox(
                    "Status",
                    options=["Offen", "In Bearbeitung"],
                    index=["Offen", "In Bearbeitung"].index(st.session_state.new_task_inputs[section_id]["status"]),
                    key=status_key
                )
                due_date = st.date_input(
                    "Fälligkeitsdatum",
                    value=st.session_state.new_task_inputs[section_id]["due_date"],
                    key=due_key
                )
                due_time = st.time_input(
                    "Fällige Uhrzeit",
                    value=st.session_state.new_task_inputs[section_id]["due_time"],
                    key=time_key
                )
                priority = st.selectbox(
                    "Priorität",
                    options=[3, 2, 1],
                    format_func=lambda x: PRIORITY_LABELS[x],
                    index=[3, 2, 1].index(st.session_state.new_task_inputs[section_id]["priority"]),
                    key=priority_key
                )

                # Update session_state with current input values on change
                st.session_state.new_task_inputs[section_id]["content"] = content
                st.session_state.new_task_inputs[section_id]["assigned_to"] = assigned_to
                st.session_state.new_task_inputs[section_id]["status"] = status
                st.session_state.new_task_inputs[section_id]["due_date"] = due_date
                st.session_state.new_task_inputs[section_id]["due_time"] = due_time
                st.session_state.new_task_inputs[section_id]["priority"] = priority

                if st.button("Speichern", key=f"save_{section_id}"):
                    if content.strip():
                        task = {
                            "id": str(uuid.uuid4()), # Assign a unique ID to each task
                            "content": content.strip(),
                            "due": datetime.combine(due_date, due_time),
                            "priority": priority,
                            "assigned_to": assigned_to.strip() if assigned_to.strip() else "Nicht zugewiesen",
                            "status": status,
                            "from_section": section_id
                        }
                        section["tasks"].append(task)
                        # Clear the inputs after saving
                        st.session_state.new_task_inputs[section_id] = {
                            "content": "",
                            "assigned_to": "",
                            "status": "Offen",
                            "due_date": datetime.now().date(),
                            "due_time": datetime.now().time(),
                            "priority": 3
                        }
                        st.rerun()
                    else:
                        st.warning("Bitte gib eine Task-Beschreibung ein.")

    # Display tasks
    tasks_sorted = sorted(section["tasks"], key=lambda x: (x["due"], -x["priority"]))
    for i, task in enumerate(tasks_sorted):
        # Check if this task is currently being edited
        is_editing_task = (st.session_state.edit_task_id == task["id"])

        if is_editing_task:
            st.markdown("---")
            st.markdown(f"#### Task bearbeiten: {task['content']}")
            edited_content = st.text_input("Task-Beschreibung", value=task["content"], key=f"edit_content_{task['id']}")
            edited_assigned_to = st.text_input("Zugeordnet zu", value=task["assigned_to"], key=f"edit_assigned_to_{task['id']}")
            edited_status = st.selectbox("Status", options=["Offen", "In Bearbeitung"], index=["Offen", "In Bearbeitung"].index(task["status"]), key=f"edit_status_{task['id']}")
            edited_due_date = st.date_input("Fälligkeitsdatum", value=task["due"].date(), key=f"edit_due_date_{task['id']}")
            edited_due_time = st.time_input("Fällige Uhrzeit", value=task["due"].time(), key=f"edit_due_time_{task['id']}")
            edited_priority = st.selectbox("Priorität", options=[3, 2, 1], format_func=lambda x: PRIORITY_LABELS[x], index=[3, 2, 1].index(task["priority"]), key=f"edit_priority_{task['id']}")

            col_task_edit1, col_task_edit2 = st.columns([22, 4])
            with col_task_edit1:
                if st.button("Änderungen speichern", key=f"save_edit_task_{task['id']}"):
                    if edited_content.strip():
                        task["content"] = edited_content.strip()
                        task["assigned_to"] = edited_assigned_to.strip() if edited_assigned_to.strip() else "Nicht zugewiesen"
                        task["status"] = edited_status
                        task["due"] = datetime.combine(edited_due_date, edited_due_time)
                        task["priority"] = edited_priority
                        st.session_state.edit_task_id = None
                        st.rerun()
                    else:
                        st.warning("Bitte gib eine Task-Beschreibung ein.")
            with col_task_edit2:
                if st.button("✖️ Abbrechen", key=f"cancel_edit_task_{task['id']}"):
                    st.session_state.edit_task_id = None
                    st.rerun()
            st.markdown("---")

        else: # Display task if not in edit mode
            # Adjust column widths for better alignment
            col1, col2, col3, col4 = st.columns([11.5, 4.5, 5, 4.5])

            with col1:
                days_left = (task["due"].date() - datetime.now().date()).days
                due_str = task["due"].strftime("%d.%m.%Y %H:%M")

                # Color highlighting for overdue tasks
                days_left_display = ""
                if days_left < 0:
                    days_left_display = f"<span style='color:red;'>({abs(days_left)} Tage überfällig)</span>"
                elif days_left == 0:
                    days_left_display = f"<span style='color:red;'>(Heute fällig)</span>"
                else:
                    days_left_display = f"({days_left} Tage)"

                st.markdown(f"**{PRIORITY_LABELS[task['priority']]}** \n{task['content']}  \n{due_str} {days_left_display}  \n  \n**Zugeordnet:** {task.get('assigned_to', 'Nicht zugewiesen')}", unsafe_allow_html=True)


                # Display "In Bearbeitung" status
                if section_id != DONE_SECTION_ID:
                    if task.get("status") == "In Bearbeitung":
                        st.markdown(
                            f"<div style='display:inline-block; background-color:{COLOR_PALETTE['Gelb']}; color:black; padding: 4px 10px; border-radius: 10px; font-size: 0.75em;'>In Bearbeitung</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
            with col3:
                if section_id != DONE_SECTION_ID: # Edit button for active tasks
                    if st.button("✏️ Bearbeiten", key=f"edit_task_{section_id}_{task['id']}"):
                        st.session_state.edit_task_id = task["id"]
                        st.rerun()
                if section_id == DONE_SECTION_ID:
                    # Display color circle in "Erledigte Tasks" section
                    color = COLOR_PALETTE.get(task.get("done_color", "Grau"), "#cccccc")
                    st.markdown(f"<div style='width:20px;height:20px;background-color:{color};border-radius:50%;'></div>", unsafe_allow_html=True)
            with col4:
                if section_id != DONE_SECTION_ID:
                    if st.button("🗑️ Löschen", key=f"delete_task_{section_id}_{task['id']}"):
                        section["tasks"].remove(task)
                        st.rerun()
                if section_id == DONE_SECTION_ID: # Delete button for done tasks
                    if st.button("🗑️ Löschen", key=f"delete_done_task_{section_id}_{task['id']}"):
                        section["tasks"].remove(task)
                        st.rerun()
                if section_id != DONE_SECTION_ID:
                    if st.button("✔️ Erledigt", key=f"done_{section_id}_{task['id']}"):
                        task["done_color"] = section["color"]
                        st.session_state.sections[DONE_SECTION_ID]["tasks"].append(task)
                        section["tasks"].remove(task) # Remove the task by its reference
                        st.rerun()
            #st.markdown("---") # Add a separator between tasks

    if section_id != DONE_SECTION_ID:
        st.markdown("</div>", unsafe_allow_html=True) # End of the Section container


# Really delete section
if st.session_state.delete_section_id:
    del st.session_state.sections[st.session_state.delete_section_id]
    # Also delete the corresponding new_task_inputs if a section is deleted
    if st.session_state.delete_section_id in st.session_state.new_task_inputs:
        del st.session_state.new_task_inputs[st.session_state.delete_section_id]
    st.session_state.delete_section_id = None
    st.rerun()