import streamlit as st
from datetime import date

st.set_page_config(page_title="SHERS 平台原型", layout="centered")

st.title("🏋️ SHERS 二手运动器材租赁平台")
st.caption("环保 · 实惠 · 共享 —— 为留学生和短住居民提供经济便捷的运动器材租赁服务")

tab1, tab2 = st.tabs(["🎯 租借者入口", "🚲 出借者入口"])

with tab1:
    st.header("🔍 搜索可租器材")
    search = st.text_input("搜索关键词（如：自行车、瑜伽垫）")
    max_price = st.slider("期望租金上限 (€)", 0, 100, 20)
    rent_date = st.date_input("选择期望租用日期", value=date.today())
    if st.button("开始搜索"):
        st.success(f"搜索结果：找到符合“{search}”的器材，价格不超过 €{max_price}")

with tab2:
    st.header("📦 发布你的器材")
    name = st.text_input("器材名称")
    desc = st.text_area("器材描述（品牌/使用情况）")
    price = st.number_input("建议租金 (€)", min_value=0)
    available_date = st.date_input("可租日期")
    if st.button("提交出租"):
        st.success("✅ 你的器材已发布！系统将为你匹配感兴趣的租借者")

st.markdown("---")
st.metric("♻️ 已节省 CO₂ 排放", "102.9 吨")
st.metric("📦 累计器材租借次数", "10,993 次")
st.metric("👥 平台用户人数", "4,000+")