import pandas as pd
import streamlit as st
import datetime

# --- Rooms and tasks ---
rooms = {
    1: "kitchen",
    2: "living room",
    3: "half bath",
    4: "full bath",
    5: "master bedroom",
    6: "guest bedroom",
    7: "hall"
}

tasks = {
    "kitchen": ["Wash dishes", "Wipe counters", "Sweep floor", "Mop", "Put away dishes"],
    "living room": ["Dust", "Vacuum carpet", "Mop", "Declutter and Organize"],
    "half bath": ["Clean sink", "Wipe mirror", "Mop floor","Vacuum"],
    "full bath": ["Scrub shower", "Clean toilet", "Mop floor", "Vacuum", "Litter Changeout"],
    "master bedroom": ["Make bed", "Laundry", "Change Bedding", "Swiffer"],
    "guest bedroom": ["Vacuum", "Declutter and Organize"],
    "hall": ["Mop floor", "Vacuum"]
}

# --- Weekly reset logic ---
today = datetime.date.today()
week_number = today.isocalendar()[1]

if "week_number" not in st.session_state or st.session_state.week_number != week_number:
    st.session_state.clear()
    st.session_state.week_number = week_number

# --- Streamlit UI ---
st.title("🏠 Cleaning Routine Dashboard")

# --- Global reset button ---
if st.button("🔄 Reset ALL Rooms and Tasks"):
    for seq, room in rooms.items():
        for task in tasks[room]:
            st.session_state.pop(f"{room}_{task}", None)
            st.session_state.pop(f"{room}_{task}_date", None)

progress_data = []
task_log = []

for seq, room in rooms.items():
    with st.expander(f"{seq}. {room.capitalize()}", expanded=False):
        completed = 0
        total = len(tasks[room])

        # Reset button per room
        if st.button(f"Reset {room}", key=f"reset_{room}"):
            for task in tasks[room]:
                st.session_state.pop(f"{room}_{task}", None)
                st.session_state.pop(f"{room}_{task}_date", None)

        # Dropdown for each task
        for task in tasks[room]:
            key = f"{room}_{task}"
            status = st.selectbox(
                f"{task}",
                ["Not Started", "In Progress", "Done"],
                key=key
            )

            # Handle completion date
            if status == "Done":
                completed += 1
                if f"{key}_date" not in st.session_state:
                    st.session_state[f"{key}_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                st.write(f"✅ Completed on {st.session_state[f'{key}_date']}")
                completed_date = st.session_state[f"{key}_date"]
            else:
                completed_date = None
                if f"{key}_date" in st.session_state:
                    st.session_state.pop(f"{key}_date", None)

            # Log task status and date
            task_log.append({
                "room": room,
                "task": task,
                "status": status,
                "completed_date": completed_date
            })

        # Progress bar + metric
        progress = completed / total if total > 0 else 0
        st.progress(progress)
        st.metric(label="Completed", value=f"{completed}/{total}")

        progress_data.append({"room": room, "completed": completed, "total": total})

# --- Summary dashboard ---
st.header("📊 Overall Progress")
summary_df = pd.DataFrame(progress_data)
summary_df["percent"] = (summary_df["completed"] / summary_df["total"]) * 100
st.dataframe(summary_df)

overall_progress = summary_df["completed"].sum() / summary_df["total"].sum()
st.progress(overall_progress)
st.metric(label="Overall Completion", value=f"{summary_df['completed'].sum()}/{summary_df['total'].sum()}")

# --- Bar chart visualization ---
st.subheader("📈 Completion by Room")
chart_data = summary_df.set_index("room")["percent"]
st.bar_chart(chart_data)

# --- Task log summary ---
st.subheader("📝 Task Status Log")
task_df = pd.DataFrame(task_log)
st.dataframe(task_df)



