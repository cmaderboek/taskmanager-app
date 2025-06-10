import streamlit as st
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# Color options (needs to be consistent across files)
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

st.set_page_config(page_title="TaskBuddy Kalender", layout="wide")

st.title("Kalender")

# Retrieve sections and tasks from session_state
if "sections" not in st.session_state:
    st.session_state.sections = {}

# Prepare events for the calendar
calendar_events = []

# Iterate through all sections to gather tasks, including 'Erledigte Tasks'
for section_id, section_data in st.session_state.sections.items():
    section_color = COLOR_PALETTE.get(section_data["color"], "#cccccc") # Default to grey if color not found

    for task in section_data["tasks"]:
        # Ensure 'due' is a datetime object
        if isinstance(task.get("due"), datetime):
            due_datetime = task["due"]
        else:
            # Attempt to convert if it's not already datetime (e.g., if loaded from a different format)
            try:
                # Assuming 'due' might be a date object, combine with a default time
                if isinstance(task.get("due"), (datetime.date, datetime.time)):
                    due_datetime = datetime.combine(task["due"], datetime.min.time()) # Use min.time if only date
                else:
                    due_datetime = datetime.now() # Fallback
            except:
                due_datetime = datetime.now() # Fallback if conversion fails

        # Define event title based on task details
        event_title = f"{task['content']}"
        if task.get('assigned_to') and task['assigned_to'] != "Nicht zugewiesen":
            event_title += f" ({task['assigned_to']})"

        # Add priority to the title for easy viewing
        priority_label = ""
        if task.get('priority') == 3:
            priority_label = "★★★ "
        elif task.get('priority') == 2:
            priority_label = "★★ "
        elif task.get('priority') == 1:
            priority_label = "★ "

        event_title = priority_label + event_title

        # Determine event class name for styling if needed, or just use background color
        event_class_name = ""
        if section_id == "done_tasks":
            event_class_name = "event-done"
            # For done tasks, use their original section's color if available, otherwise default to Grau
            done_task_color = COLOR_PALETTE.get(task.get("done_color", "Grau"), "#aaaaaa")
            event_color = done_task_color
        else:
            event_color = section_color
            if task.get("status") == "In Bearbeitung":
                event_class_name = "event-inprogress"
                event_color = COLOR_PALETTE["Gelb"] # Special color for in-progress on calendar

        end_datetime = due_datetime + timedelta(hours=1)

        calendar_events.append(
            {
                "title": event_title,
                "start": due_datetime.isoformat(), # FullCalendar expects ISO 8601 string
                "end": end_datetime.isoformat(), # Assume 1 hour duration for visualization
                "extendedProps": {
                    "section_name": section_data["name"],
                    "status": task.get("status", "Offen"),
                    "priority": task.get("priority", 3),
                    "assigned_to": task.get("assigned_to", "Nicht zugewiesen"),
                },
                "color": event_color, # Event background color
                "classNames": [event_class_name] # Optional class for custom CSS
            }
        )

# Calendar options
calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "dayGridMonth",
    "editable": False, # Prevent drag-and-drop editing from calendar
    "selectable": True, # Allow selecting dates/times (though we don't use it yet)
    "navLinks": True, # Allow clicks on day/week names to navigate views
    "eventClick": "function(info) { Streamlit.setComponentValue('calendar_event_click', info.event.extendedProps); }",
    "eventDidMount": """
        function(info) {
            // Add a tooltip for more details
            var tooltip = new Tooltip(info.el, {
                title: info.event.title + ' (Section: ' + info.event.extendedProps.section_name + ')<br>Status: ' + info.event.extendedProps.status + '<br>Zugeordnet: ' + info.event.extendedProps.assigned_to,
                placement: 'top',
                trigger: 'hover',
                container: 'body',
                html: true // Allow HTML in tooltip
            });
        }
    """
}

# Load FullCalendar's external plugins for tooltips if you wish
# You'll need to add 'fullcalendar-tooltip' to your pip install
# For now, let's keep it simple without external tooltip library dependency unless specifically asked.
# The 'eventDidMount' is a placeholder if you wanted to implement a custom tooltip.

# Custom CSS for calendar (optional, but good for distinction)
custom_css = """
    .fc-event {
        cursor: pointer;
    }
    .fc-event-main-frame {
        padding: 5px;
    }
    .event-done {
        text-decoration: line-through;
        opacity: 0.7;
    }
    .event-inprogress {
        border: 2px dashed #333; /* Example styling for in-progress */
    }
"""

# Render the calendar
calendar_response = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css,
    key="full_calendar",
)

# You can add logic here to handle event clicks if you want details to show up
# For example, to show details of a clicked event:
# if calendar_response and "eventClick" in calendar_response:
#    st.write("Clicked Event:", calendar_response["eventClick"])

if calendar_response and calendar_response.get("eventClick"):
    st.subheader("Details des angeklickten Tasks:")
    clicked_props = calendar_response["eventClick"]
    st.write(f"**Task:** {clicked_props.get('title', 'N/A')}")
    st.write(f"**Section:** {clicked_props.get('section_name', 'N/A')}")
    st.write(f"**Status:** {clicked_props.get('status', 'N/A')}")
    st.write(f"**Zugeordnet zu:** {clicked_props.get('assigned_to', 'N/A')}")
    st.write(f"**Priorität:** {clicked_props.get('priority', 'N/A')}")

st.markdown("---")
st.markdown("Tasks, die erledigt wurden, sind in ihrer ursprünglichen Section-Farbe und durchgestrichen.")
st.markdown(f"Tasks in Bearbeitung haben eine {COLOR_PALETTE['Gelb']} gelbe Markierung.")