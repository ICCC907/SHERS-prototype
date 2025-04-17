import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

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

def welcome_page():
    st.title("🎉 Welcome to SHERS!")
    st.write("SHERS (Second-Hand Equipment Rental Service) is designed to help you easily rent sports equipment.")
    st.markdown("- 🛠️ List your unused equipment")
    st.markdown("- 🔍 Search and rent nearby gear")
    st.markdown("- 🚚 Pickup support")
    st.markdown("- 💬 Chat with owners")
    st.markdown("- ✅ Easy return and order tracking")
    st.markdown("---")
    st.metric("♻️ 已节省 CO₂ 排放", "102.9 吨")
    st.metric("📦 累计器材租借次数", "10,993 次")
    st.metric("👥 平台用户人数", "4,000+")

def homepage():
    st.title("🔍 Search Equipment")
    search = st.text_input("Feel free to explore and find the device that best suits your preferences", key="search_input")
    if st.session_state.selected_product:
        detail_view(st.session_state.selected_product)
        if st.button("🔙 Search results"):
            st.session_state.selected_product = None
            st.rerun()
        return
    results = [p for p in st.session_state.products if search.lower() in p['name'].lower()]
    st.write(f"{len(results)} results found.")
    for idx, item in enumerate(results):
        st.image(item['images'][0], width=200)
        st.write(f"**{item['name']}** - €{item['price']}/day - 📍 {item['location']}")
        if st.button(f"View Details {item['name']}", key=f"view_{idx}"):
            st.session_state.selected_product = item
            st.rerun()

def publish_page():
    st.title("📦 Rent Out Your Equipment")
    name = st.text_input("Name of equipment")
    desc = st.text_area("Description")
    price = st.number_input("Rent Price per day (€)", min_value=1)
    location = st.text_input("📍 Location")
    images = st.file_uploader("Upload photos", type=["png", "jpg"], accept_multiple_files=True)
    if st.button("Upload"):
        if not name or not images or not location:
            st.warning("Please fill all fields.")
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
            st.success("✅ Successfully uploaded! Thank you for your contribution to protecting the environment.")

def detail_view(product):
    st.title(product['name'])
    st.image(product['images'], width=300)
    st.write(product['desc'])
    st.write(f"📍 {product['location']}")
    st.write(f"💰 €{product['price']}/day")
    user_loc = st.text_input("📍 Your address")
    if user_loc:
        coords1 = get_coords(product['location'])
        coords2 = get_coords(user_loc)
        if coords1 and coords2:
            distance = geodesic(coords1, coords2).km
            st.info(f"Estimated distance: {distance:.2f} km")
    st.subheader("💳 Pay")
    if st.button("Simulate Payment"):
        if not user_loc:
            st.warning("Enter pickup address.")
        else:
            product['borrower'] = st.session_state.current_user
            st.session_state.orders.append({
                'user': st.session_state.current_user,
                'item': product['name'],
                'price': product['price'],
                'returned': False,
                'pickup_location': user_loc
            })
            st.success("✅ Payment successful! Thank you for your contribution to protecting the environment.")
    st.subheader("💬 Messages")
    if product['name'] not in st.session_state.messages:
        st.session_state.messages[product['name']] = []
    msg = st.text_input("Send a message to renter")
    if st.button("Send"):
        st.session_state.messages[product['name']].append((st.session_state.current_user, msg))
    for sender, text in st.session_state.messages[product['name']]:
        st.info(f"{sender}: {text}")

def support_page():
    st.title("🛎️ Support")
    msg = st.text_area("Your problems/feedback")
    if st.button("Send"):
        st.session_state.support_messages.append((st.session_state.current_user, msg))
        st.success("Successfully sent. The customer service will reply within 24 hours")
    if st.session_state.current_user == "admin":
        st.subheader("📬 Support Inbox")
        for u, m in st.session_state.support_messages:
            st.warning(f"{u}: {m}")

def profile_page():
    st.title("🧍 My information")

    st.subheader("📦 My rented equipment")
    owned = [p for p in st.session_state.products if p['owner'] == st.session_state.current_user]
    for item in owned:
        st.write(f"**{item['name']}** - €{item['price']}/day")
        st.image(item['images'][0], width=150)
        st.write("Status：" + ("Rented" if item['borrower'] else "Not rented yet"))

    st.subheader("🛒 My order")
    my_orders = [o for o in st.session_state.orders if o['user'] == st.session_state.current_user]
    for order in my_orders:
        st.write(f"Equipment：{order['item']}，Price：€{order['price']}，Return status：{'✅ Returned' if order['returned'] else '❌ Not returned'}")
        if not order['returned'] and st.button(f"Return {order['item']}", key=f"return_{order['item']}"):
            order['returned'] = True
            st.success(f"You have successfully returned {order['item']}")

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def main_page():
    st.sidebar.success(f"👋 Welcome, {st.session_state.current_user}")
    pages = ["Welcome", "Search Equipment", "List Equipment", "My Account", "Customer Support"]
    selected = st.sidebar.radio("Navigation", pages)
    if "active_page" not in st.session_state:
        st.session_state.active_page = selected
    elif st.session_state.active_page != selected:
        st.session_state.selected_product = None
        st.session_state.active_page = selected
        st.rerun()
    st.sidebar.button("Log out", on_click=logout)

    if selected == "Welcome":
        welcome_page()
    elif selected == "Search Equipment":
        homepage()
    elif selected == "List Equipment":
        publish_page()
    elif selected == "My Account":
        profile_page()
    elif selected == "Customer Support":
        support_page()

# 登录界面
if not st.session_state.logged_in:
    st.title("🔐 Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        user = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            if user in st.session_state.users and st.session_state.users[user] == pwd:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("Incorrect username or password.")
    with tab2:
        new_user = st.text_input("New Username")
        new_pwd = st.text_input("New Password", type="password")
        if st.button("Register"):
            if new_user in st.session_state.users:
                st.error("Username already exists.")
            else:
                st.session_state.users[new_user] = new_pwd
                st.success("Registration successful!")
else:
    main_page()
