import streamlit as st
import uuid
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

# ---------- Hilfsfunktionen ----------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.sections, f, indent=2)

# ---------- Initialisierung ----------
if "sections" not in st.session_state:
    st.session_state.sections = load_data()

if "add_section_mode" not in st.session_state:
    st.session_state.add_section_mode = False

# Farben und Prioritäten
color_options = {
    "🔵 Blau": "#3498db",
    "🟢 Grün": "#2ecc71",
    "🟡 Gelb": "#f1c40f",
    "🟣 Lila": "#9b59b6",
    "🔴 Rot": "#e74c3c"
}
priority_icons = {
    "Hoch (!!!)": "!!!",
    "Mittel (!!)": "!!",
    "Niedrig (!)": "!"
}

# ---------- UI ----------
st.title("🗂 Task Manager")

# Section hinzufügen
if not st.session_state.add_section_mode:
    if st.button("➕ Neue Section"):
        st.session_state.add_section_mode = True
        # st.experimental_rerun()

if st.session_state.add_section_mode:
    with st.form("add_section", clear_on_submit=True):
        name = st.text_input("Section-Name")
        color_choice = st.selectbox("Farbe", list(color_options.keys()))
        submit = st.form_submit_button("✅ Fertig")
    if submit and name:
        new_id = str(uuid.uuid4())
        st.session_state.sections[new_id] = {
            "name": name,
            "color": color_options[color_choice],
            "tasks": [],
            "id": new_id
        }
        st.session_state.add_section_mode = False
        save_data()
        # st.experimental_rerun()

# Erledigte Tasks Section sicherstellen
DONE_ID = "done"
if DONE_ID not in st.session_state.sections:
    st.session_state.sections[DONE_ID] = {
        "name": "✅ Erledigte Tasks",
        "color": "#bdc3c7",
        "tasks": [],
        "id": DONE_ID
    }

# Sections anzeigen
for sec_id, sec in st.session_state.sections.items():
    with st.expander(f"{sec['name']} ({len(sec['tasks'])})", expanded=True):
        sorted_tasks = sorted(
            sec["tasks"],
            key=lambda t: (t.get("due_date") or "", t.get("priority", 2))
        )
        for idx, task in enumerate(sorted_tasks):
            due_str = ""
            if task.get("due_date"):
                due = datetime.strptime(task["due_date"], "%Y-%m-%dT%H:%M")
                days_left = (due - datetime.now()).days
                due_str = f"🗓 {due.strftime('%d.%m.%Y %H:%M')} ({days_left} Tage)"

            prio = priority_icons.get(task.get("priority_label", ""), "")
            color = task.get("original_color", sec["color"])

            st.markdown(
                f"<div style='border-left: 5px solid {color}; padding: 8px; margin-bottom: 5px;'>"
                f"<b>{prio}</b> {task['content']}<br><small>{due_str}</small></div>",
                unsafe_allow_html=True
            )

            if sec_id != DONE_ID:
                if st.button("✅ Erledigt", key=f"{sec_id}_{idx}"):
                    task["original_color"] = sec["color"]
                    st.session_state.sections[DONE_ID]["tasks"].append(task)
                    st.session_state.sections[sec_id]["tasks"].remove(task)
                    save_data()
                    # st.experimental_rerun()

        if sec_id != DONE_ID:
            with st.form(f"task_form_{sec_id}", clear_on_submit=True):
                content = st.text_input("Task", key=f"content_{sec_id}")
                due_date = st.date_input("Fällig am", key=f"due_date_{sec_id}")
                due_time = st.time_input("Uhrzeit", key=f"due_time_{sec_id}")
                prio_label = st.selectbox("Priorität", list(priority_icons.keys()), key=f"prio_{sec_id}")
                submit_task = st.form_submit_button("➕ Task speichern")
            if submit_task and content:
                due_combined = datetime.combine(due_date, due_time)
                st.session_state.sections[sec_id]["tasks"].append({
                    "content": content,
                    "due_date": due_combined.isoformat(),
                    "priority": list(priority_icons).index(prio_label),
                    "priority_label": prio_label
                })
                save_data()


# Teilen
    st.markdown("🔗 Teilen:")
    share_link = f"https://mein-taskmanager.de/invite/{section_id}"
    st.code(share_link)
    st.text("Versende den Link z. B. per WhatsApp oder E-Mail.")

    if section["shared_with"]:
        st.markdown("👥 Geteilt mit: " + ", ".join(section["shared_with"]))
                # st.experimental_rerun()