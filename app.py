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
        st.session_state.logged_in = True
        st.session_state.current_user = username
        return True
    return False

def register_user(username, password):
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = password
    return True

# 主页面入口
def main_page():
    st.sidebar.success(f"👋 Welcome，{st.session_state.current_user}")
    page = st.sidebar.radio("SHERS", ["Rent", "Rent out", "Customer service", "My information"])
    st.sidebar.button("Sign out", on_click=lambda: st.session_state.update({'logged_in': False, 'current_user': None}))

    if page == "Rent":
        homepage()
    elif page == "Rent out":
        publish_page()
    elif page == "Customer service":
        support_page()
    elif page == "My information":
        profile_page()

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
        st.write(f"**{item['name']}** - €{item['price']}/天")
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

    if st.button("提交发布"):
        if not name or not images:
            st.warning("Please add at least one picture")
        else:
            st.session_state.products.append({
                'name': name,
                'desc': desc,
                'price': price,
                'images': [img.read() for img in images],
                'owner': st.session_state.current_user,
                'borrower': None,
                'returned': False
            })
            st.success("Successfully uploaded")

# 器材详情
def detail_view(product):
    st.title(f"📄 器材详情：{product['name']}")
    st.image(product['images'], width=300)
    st.write(product['desc'])
    st.write(f"💰 日租金：€{product['price']}")

    st.subheader("💳 支付租金")
    if st.button("模拟支付"):
        st.success("✅ 支付成功！感谢你的租借。")
        product['borrower'] = st.session_state.current_user
        st.session_state.orders.append({
            'user': st.session_state.current_user,
            'item': product['name'],
            'price': product['price'],
            'returned': False
        })

    st.subheader("💬 留言板")
    if product['name'] not in st.session_state.messages:
        st.session_state.messages[product['name']] = []
    msg = st.text_input("发送消息给出租者")
    if st.button("发送消息"):
        st.session_state.messages[product['name']].append((st.session_state.current_user, msg))
    for sender, text in st.session_state.messages[product['name']]:
        st.info(f"**{sender}**：{text}")

# 客服中心
def support_page():
    st.title("🛎️ 客服中心")
    question = st.text_area("你遇到的问题 / 意见")
    if st.button("发送给客服"):
        st.session_state.support_messages.append((st.session_state.current_user, question))
        st.success("已发送，客服将在24小时内回复（模拟）")

    if st.session_state.current_user == "admin":
        st.subheader("📬 客服收件箱（管理员可见）")
        for user, msg in st.session_state.support_messages:
            st.warning(f"{user} 留言：{msg}")

# 我的个人中心
def profile_page():
    st.title("🧍 我的个人中心")

    st.subheader("📦 我的出租器材")
    owned = [p for p in st.session_state.products if p['owner'] == st.session_state.current_user]
    for item in owned:
        st.write(f"**{item['name']}** - €{item['price']}/天")
        st.image(item['images'][0], width=150)
        st.write("状态：" + ("已出租" if item['borrower'] else "空闲"))

    st.subheader("🛒 我的订单")
    my_orders = [o for o in st.session_state.orders if o['user'] == st.session_state.current_user]
    for order in my_orders:
        st.write(f"器材：{order['item']}，租金：€{order['price']}，归还状态：{'✅ 已归还' if order['returned'] else '❌ 未归还'}")
        if not order['returned'] and st.button(f"确认归还 {order['item']}", key=f"return_{order['item']}"):
            order['returned'] = True
            st.success(f"你已归还 {order['item']}")

# 登录 / 注册界面
if not st.session_state.logged_in:
    st.title("🔐 登录 / 注册")
    tab1, tab2 = st.tabs(["登录", "注册"])
    with tab1:
        user = st.text_input("用户名", key="login_user")
        pwd = st.text_input("密码", type="password", key="login_pwd")
        if st.button("登录"):
            if login_user(user, pwd):
                st.rerun()
            else:
                st.error("用户名或密码错误")
    with tab2:
        new_user = st.text_input("新用户名")
        new_pwd = st.text_input("新密码", type="password")
        if st.button("注册"):
            if register_user(new_user, new_pwd):
                st.success("注册成功！请登录")
            else:
                st.error("用户名已存在")
else:
    main_page()

