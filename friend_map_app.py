import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

# --- Firebase init ---
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://home-be9db-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

ref = db.reference('friend_houses')


# --- Data functions ---
def load_data():
    data = ref.get()
    return data or {}


def add_friend(name, x, y):
    new_ref = ref.push()
    new_ref.set({'name': name, 'x': x, 'y': y})


def delete_friend(key):
    ref.child(key).delete()


# --- Web UI ---
st.set_page_config(layout="wide")
st.title("🏠 Friend Houses Map")

# Custom CSS for better appearance
st.markdown("""
    <style>
    /* Main form styling */
    .stForm {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }

    /* Input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #333333 !important;
        font-weight: bold;
        font-size: 14px;
    }

    /* Input fields */
    .stTextInput input, .stNumberInput input {
        background-color: #f8f9fa !important;
        color: #333333 !important;
    }

    /* Button styling */
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 4px;
        font-weight: bold;
        width: 100%;
        padding: 0.5rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        padding: 20px;
    }

    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .stForm {
            background-color: #1a1a1a;
            border-color: #444;
        }
        .stTextInput label, .stNumberInput label {
            color: #f0f0f0 !important;
        }
        .stTextInput input, .stNumberInput input {
            background-color: #2d2d2d !important;
            color: #f0f0f0 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #1a1a1a;
        }
    }

    /* Container styling */
    .stContainer {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 15px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for adding new friends
with st.sidebar:
    st.header("Add New Friend House")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name", placeholder="Enter friend's name")
        col1, col2 = st.columns(2)
        with col1:
            x = st.number_input("X coordinate", min_value=0, max_value=500, step=10, value=250)
        with col2:
            y = st.number_input("Y coordinate", min_value=0, max_value=500, step=10, value=250)

        submitted = st.form_submit_button("➕ Add Location")
        if submitted and name.strip():
            add_friend(name.strip(), int(x), int(y))
            st.success(f"Added {name} at ({x}, {y})")
            st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Plot the map
    data = load_data()

    if data:
        # Prepare data
        x_coords = [info['x'] for info in data.values()]
        y_coords = [info['y'] for info in data.values()]
        names = [info['name'] for info in data.values()]

        # Create figure with better styling
        fig, ax = plt.subplots(figsize=(10, 8), facecolor='#f8f9fa')
        fig.set_facecolor('#f8f9fa')

        # Set limits and aspect ratio
        ax.set_xlim(0, 500)
        ax.set_ylim(0, 500)
        ax.set_aspect('equal')

        # Custom grid and ticks
        major_ticks = MultipleLocator(50)
        minor_ticks = MultipleLocator(10)
        ax.xaxis.set_major_locator(major_ticks)
        ax.yaxis.set_major_locator(major_ticks)
        ax.xaxis.set_minor_locator(minor_ticks)
        ax.yaxis.set_minor_locator(minor_ticks)

        # Grid styling
        ax.grid(which='major', linestyle='-', linewidth=0.7, alpha=0.7, color='#cccccc')
        ax.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.5, color='#dddddd')

        # Plot points with better styling
        scatter = ax.scatter(
            x_coords, y_coords,
            c='#4285F4',
            s=40,
            edgecolors='white',
            linewidths=1.5,
            alpha=0.9,
            zorder=5
        )

        # Annotate points
        for name, x, y in zip(names, x_coords, y_coords):
            ax.annotate(
                name,
                (x, y),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center',
                fontsize=8,
                weight='bold',
                color='#333333'
            )

        # Labels and title
        ax.set_title('Friend Houses Location Map', pad=20, fontsize=14, weight='bold', color='#333333')
        ax.set_xlabel('X Coordinate', labelpad=10, fontsize=10)
        ax.set_ylabel('Y Coordinate', labelpad=10, fontsize=10)

        # Remove spines
        for spine in ['top', 'right', 'bottom', 'left']:
            ax.spines[spine].set_visible(False)

        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No friend houses added yet. Add some locations to see them on the map!")

with col2:
    st.header("Current Locations")
    if not data:
        st.info("No friend houses yet. Add your first location using the sidebar!")
    else:
        for key, info in data.items():
            with st.container(border=True):
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(f"**{info['name']}**  \n"
                                f"Coordinates: ({info['x']}, {info['y']})")
                with cols[1]:
                    if st.button("🗑️", key=key, help=f"Delete {info['name']}'s location"):
                        delete_friend(key)
                        st.rerun()