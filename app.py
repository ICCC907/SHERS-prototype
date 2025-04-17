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
def detail_view(product):
    st.title(f"📄 {product['name']}")
    st.image(product['images'], width=300)
    st.write(product['desc'])
    st.write(f"📍 Location: {product.get('location', 'Not provided')}")
    st.write(f"💰 Price: €{product['price']} per day")

    st.subheader("💳 Rent + Delivery Info")
    user_location = st.text_input("📍 Your location for pickup service")
    if user_location and product.get('location'):
        from_coords = get_coords(product['location'])
        to_coords = get_coords(user_location)
        if from_coords and to_coords:
            dist = geodesic(from_coords, to_coords).km
            st.info(f"🚚 Distance: approx. {dist:.2f} km")
        else:
            st.warning("⚠️ Location not recognized.")

    if st.button("Simulate Payment"):
        if not user_location:
            st.warning("Enter your pickup location.")
        else:
            st.success("✅ Payment simulated successfully.")
            product['borrower'] = st.session_state.current_user
            st.session_state.orders.append({
                'user': st.session_state.current_user,
                'item': product['name'],
                'price': product['price'],
                'returned': False,
                'pickup_location': user_location
            })

    st.subheader("💬 Message the Lender")
    if product['name'] not in st.session_state.messages:
        st.session_state.messages[product['name']] = []
    msg = st.text_input("Write a message")
    if st.button("Send Message"):
        st.session_state.messages[product['name']].append((st.session_state.current_user, msg))
    for sender, text in st.session_state.messages[product['name']]:
        st.info(f"**{sender}**: {text}")

def support_page():
    st.title("🛎️ Customer Support")
    question = st.text_area("Submit a question or issue")
    if st.button("Send to Support"):
        st.session_state.support_messages.append((st.session_state.current_user, question))
        st.success("Submitted successfully!")

    if st.session_state.current_user == "admin":
        st.subheader("📬 Admin Support Inbox")
        for user, msg in st.session_state.support_messages:
            st.warning(f"{user} said: {msg}")

def profile_page():
    st.title("🧍 My Account")
    st.subheader("📦 My Listed Equipment")
    owned = [p for p in st.session_state.products if p['owner'] == st.session_state.current_user]
    for item in owned:
        st.write(f"**{item['name']}** - €{item['price']}/day")
        st.image(item['images'][0], width=150)
        st.write("Location: " + item.get('location', 'N/A'))
        st.write("Status: " + ("Rented" if item['borrower'] else "Available"))

    st.subheader("🛒 My Rentals")
    my_orders = [o for o in st.session_state.orders if o['user'] == st.session_state.current_user]
    for order in my_orders:
        st.write(f"Item: {order['item']}, Price: €{order['price']}, Returned: {'✅' if order['returned'] else '❌'}")
        st.write(f"Pickup address: {order.get('pickup_location', 'Not provided')}")
        if not order['returned'] and st.button(f"Return {order['item']}", key=f"return_{order['item']}"):
            order['returned'] = True
            st.success(f"Marked {order['item']} as returned.")

# 登录注册流程
if not st.session_state.logged_in:
    st.title("🔐 Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        user = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            if login_user(user, pwd):
                st.rerun()
            else:
                st.error("Incorrect username or password.")
    with tab2:
        new_user = st.text_input("New Username")
        new_pwd = st.text_input("New Password", type="password")
        if st.button("Register"):
            if register_user(new_user, new_pwd):
                st.success("Registration successful!")
            else:
                st.error("Username already exists.")
else:
    main_page()

