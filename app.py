import streamlit as st
from datetime import date
from io import BytesIO

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

# 登录注册逻辑
def login_user(username, password):
    if username in st.session_state.users and st.session_state.users[username] == password:
        # ✅ 清空旧数据（模拟用户隔离）
        st.session_state.selected_product = None
        st.session_state.current_user = username
        st.session_state.logged_in = True
        return True
    return False

def register_user(username, password):
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = password
    return True
    
# 主页面入口
def main_page():
    st.sidebar.success(f"👋 Welcome, {st.session_state.current_user}")

    pages = ["Welcome", "Search Equipment", "List Equipment", "My Account", "Customer Support"]
    selected = st.sidebar.radio("Navigation", pages)

    # 页面切换后清空内容
    if "active_page" not in st.session_state:
        st.session_state.active_page = selected
    elif st.session_state.active_page != selected:
        # 清除旧页面状态（按需可加更多）
        st.session_state.selected_product = None
        st.session_state.get("search_input", None)
        st.session_state.active_page = selected
        st.experimental_rerun()

    st.sidebar.button("Log out", on_click=lambda: st.session_state.update({'logged_in': False, 'current_user': None}))

    # 页面调用
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

        
def welcome_page():
    st.title("🎉 Welcome to SHERS!")
    st.write("SHERS (Second-Hand Equipment Rental Service) is designed to help you easily rent and lend sports equipment.")
    st.markdown("**Key Features:**")
    st.markdown("- 🛠️ List your unused equipment")
    st.markdown("- 🔍 Search and rent nearby gear")
    st.markdown("- 🚚 Support pickup delivery")
    st.markdown("- 💬 Chat with owners")
    st.markdown("- ✅ Easy returns and personal tracking")
    st.markdown("---")
    st.metric("♻️ 已节省 CO₂ 排放", "102.9 吨")
    st.metric("📦 累计器材租借次数", "10,993 次")
    st.metric("👥 平台用户人数", "4,000+")
    st.info("Use the sidebar to start exploring!")
# 平台首页
def homepage():
    st.title("🏋️ SHERS Rent an equipment")

    # 搜索栏保留输入，不强依赖按钮
    search = st.text_input("Feel free to explore and find the device that best suits your preferences.", key="search_input")

    # 如果处于“查看详情模式”
    if st.session_state.selected_product:
        detail_view(st.session_state.selected_product)
        if st.button("🔙 Search results"):
            st.session_state.selected_product = None
            st.rerun()
        return  # 提前退出，避免再渲染搜索结果列表

    # 常驻搜索结果
    results = [p for p in st.session_state.products if search.lower() in p['name'].lower()]
    st.success(f"There are {len(results)} search results")
    for idx, item in enumerate(results):
        st.image(item['images'][0], width=200)
        st.write(f"**{item['name']}** - €{item['price']}/day")
        if st.button(f"Details {idx}", key=f"detail_{idx}"):
            st.session_state.selected_product = item
            st.rerun()



# 发布器材
def publish_page():
    st.title("📦 Rent out your equipment")
    name = st.text_input("Name of equipment")
    desc = st.text_area("Description")
    price = st.number_input("Rent price (€)", min_value=1)
    images = st.file_uploader("Add pictures for your equipment", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if st.button("Upload"):
        if not name or not images:
            st.warning("Please add at least one picture")
        else:
            st.session_state.products.append({
                'name': name,
                'desc': desc,
                'price': price,
                'location': location,
                'images': [img.read() for img in images],
                'owner': st.session_state.current_user,  # 👈 标记设备的主人是谁
                'borrower': None,
                'returned': False
            })
            st.success("Successfully uploaded")

# 器材详情
def detail_view(product):
    st.title(f"📄 Details：{product['name']}")
    st.image(product['images'], width=300)
    st.write(product['desc'])
    st.write(f"💰 Daily price：€{product['price']}")

    st.subheader("💳 Pay")
    if st.button("Simulated paymentv"):
        st.success("✅ Payment successful! Thank you for your contribution to protecting the environment.")
        product['borrower'] = st.session_state.current_user
        st.session_state.orders.append({
            'user': st.session_state.current_user,
            'item': product['name'],
            'price': product['price'],
            'returned': False
        })

    st.subheader("💬 Messages")
    if product['name'] not in st.session_state.messages:
        st.session_state.messages[product['name']] = []
    msg = st.text_input("Send a message to renter")
    if st.button("Send"):
        st.session_state.messages[product['name']].append((st.session_state.current_user, msg))
    for sender, text in st.session_state.messages[product['name']]:
        st.info(f"**{sender}**：{text}")

# 客服中心
def support_page():
    st.title("🛎️ Customer service")
    question = st.text_area("Your problems/feedback")
    if st.button("Send"):
        st.session_state.support_messages.append((st.session_state.current_user, question))
        st.success("Successfully sent. The customer service will reply within 24 hours")

    if st.session_state.current_user == "admin":
        st.subheader("📬 客服收件箱（管理员可见）")
        for user, msg in st.session_state.support_messages:
            st.warning(f"{user} 留言：{msg}")

# 我的个人中心
def profile_page():
    st.title("🧍 My information")

    st.subheader("📦 My rented equipment")
    owned = [p for p in st.session_state.products if p['owner'] == st.session_state.current_user]
    for item in owned:
        st.write(f"**{item['name']}** - €{item['price']}/天")
        st.image(item['images'][0], width=150)
        st.write("Status：" + ("Rented" if item['borrower'] else "Not rented yet"))

    st.subheader("🛒 My order")
    my_orders = [o for o in st.session_state.orders if o['user'] == st.session_state.current_user]
    for order in my_orders:
        st.write(f"Equipment：{order['item']}，Price：€{order['price']}，Return status：{'✅ Returned' if order['returned'] else '❌ Not returned'}")
        if not order['returned'] and st.button(f"Return {order['item']}", key=f"return_{order['item']}"):
            order['returned'] = True
            st.success(f"You have successfully returned {order['item']}")

# 登录 / 注册界面
if not st.session_state.logged_in:
    st.title("🔐 Welcome to the SHERS platform")
    tab1, tab2 = st.tabs(["Log in", "Sign up"])
    with tab1:
        user = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Log in"):
            if login_user(user, pwd):
                st.rerun()
            else:
                st.error("Your username or password is incorrect. Please try again.")
    with tab2:
        new_user = st.text_input("Username")
        new_pwd = st.text_input("Password", type="password")
        if st.button("Sign up"):
            if register_user(new_user, new_pwd):
                st.success("Registration successful! Please log in.")
            else:
                st.error("The user name already exists.")
else:
    main_page()
