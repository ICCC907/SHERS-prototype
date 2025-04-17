import streamlit as st
from datetime import date
from io import BytesIO
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# 初始化状态
if 'users' not in st.session_state:
    st.session_state.users = {"admin": "admin123"}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'products' not in st.session_state:
    st.session_state.products = []
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'messages' not in st.session_state:
    st.session_state.messages = {}
if 'support_messages' not in st.session_state:
    st.session_state.support_messages = []
if 'orders' not in st.session_state:
    st.session_state.orders = []

geolocator = Nominatim(user_agent="shers_app")

def get_coords(location_name):
    try:
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude)
    except:
        return None
    return None

def login_user(username, password):
    if username in st.session_state.users and st.session_state.users[username] == password:
        st.session_state.logged_in = True
        st.session_state.current_user = username
        return True
    return False

def register_user(username, password):
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = password
    return True

def main_page():
    st.sidebar.success(f"👋 Welcome, {st.session_state.current_user}")
    page = st.sidebar.radio("Navigation", ["Home", "List Equipment", "Customer Support", "My Account"])
    st.sidebar.button("Log out", on_click=lambda: st.session_state.update({'logged_in': False, 'current_user': None}))
    if page == "Home":
        homepage()
    elif page == "List Equipment":
        publish_page()
    elif page == "Customer Support":
        support_page()
    elif page == "My Account":
        profile_page()

def homepage():
    st.title("🏋️ SHERS - Search for Equipment")
    search = st.text_input("Search equipment", key="search_input")
    if st.session_state.selected_product:
        detail_view(st.session_state.selected_product)
        if st.button("🔙 Back to results"):
            st.session_state.selected_product = None
            st.rerun()
        return

    results = [p for p in st.session_state.products if search.lower() in p['name'].lower()]
    st.success(f"{len(results)} results found")
    for idx, item in enumerate(results):
        st.image(item['images'][0], width=200)
        st.write(f"**{item['name']}** - €{item['price']}/day - 📍 {item.get('location', 'No location')}")
        if st.button(f"View Details {idx}", key=f"detail_{idx}"):
            st.session_state.selected_product = item
            st.rerun()

def publish_page():
    st.title("📦 List Your Equipment")
    name = st.text_input("Equipment Name")
    desc = st.text_area("Description")
    price = st.number_input("Daily Price (€)", min_value=1)
    location = st.text_input("📍 Equipment Location")
    images = st.file_uploader("Upload Photos (multiple allowed)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if st.button("Submit"):
        if not name or not images or not location:
            st.warning("Please provide name, address and at least one image.")
        else:
            st.session_state.products.append({
                'name': name,
                'desc': desc,
                'price': price,
                'location': location,
                'images': [img.read() for img in images],
                'owner': st.session_state.current_user,
                'borrower': None,
                'returned': False
            })
            st.success("Your equipment is now listed!")
