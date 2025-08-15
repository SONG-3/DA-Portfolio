import pandas as pd 
import streamlit as st
import matplotlib.pyplot as plt
import koreanize_matplotlib

df = pd.read_csv('/Users/SongKG/Downloads/bakery_sales_revised.csv')

# 날짜 및 시간 파싱
df['date'] = pd.to_datetime(df['date_time']).dt.date
df['date'] = pd.to_datetime(df['date'])
df['hour'] = pd.to_datetime(df['date_time']).dt.hour

# 거래 수 집계
daily_transactions = df.groupby('date')['Transaction'].nunique()
today = daily_transactions.index.max() # 가장 최근 날짜 
yesterday = today - pd.Timedelta(days=1) # 오늘 날짜 - 1

# 사이드바에 필터 UI 구성
with st.sidebar:
    st.markdown("### 📅 날짜 기준 필터링")
    date_filter = st.selectbox("기준 선택", ["일별", "주별", "월별"])

    if date_filter == "일별":
        selected_date = st.date_input(
            "날짜 선택",
            value=df['date'].max().date(),
            min_value=df['date'].min().date(),
            max_value=df['date'].max().date(),
            key="daily_filter"
        )
        filtered_df = df[df['date'].dt.date == selected_date]

    elif date_filter == "주별":
        df['week'] = df['date'].dt.isocalendar().week
        min_week = int(df['week'].min())
        max_week = int(df['week'].max())
        selected_week = st.slider(
            "주 선택)",
            min_value=min_week,
            max_value=max_week,
            value=max_week,
            step=1,
            key="weekly_slider"
        )
        filtered_df = df[df['week'] == selected_week]

    else:  # "월별"
        df['month'] = df['date'].dt.month
        min_month = int(df['month'].min())
        max_month = int(df['month'].max())
        selected_month = st.slider(
            "월 선택",
            min_value=min_month,
            max_value=max_month,
            value=max_month,
            step=1,
            key="monthly_slider"
        )
        filtered_df = df[df['month'] == selected_month]

    # download_button에 고유 key 지정!
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 필터링된 데이터 다운로드(.csv)",
            data=csv,
            file_name='filtered_sales_data.csv',
            mime='text/csv',
            key="filtered_download"  # 고유 key
        )
    st.caption('필터링된 기간의 데이터 확인이 가능합니다.')


# 총 거래 수
daily_transactions = filtered_df.groupby('date')['Transaction'].nunique()
today_count = daily_transactions.sum()  # 필터링된 범위 내 전체 합산

# 피크 타임
filtered_df['hour'] = pd.to_datetime(filtered_df['date_time']).dt.hour
hourly_sales = filtered_df.groupby('hour')['Item'].count()
peak_hour = hourly_sales.idxmax()
peak_count = hourly_sales.max()

if not hourly_sales.empty:
    peak_hour = hourly_sales.idxmax()
    peak_count = hourly_sales.max()
else:
    peak_hour = "-"
    peak_count = 0

# 인기 상품
top_items = filtered_df['Item'].value_counts().head(5)
top_items_df = top_items.reset_index()
top_items_df.columns = ['상품명', '판매 수량']


# ❌ 예외 처리: 필터링 후 데이터가 없는 경우
if filtered_df.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다. 다른 날짜나 범위를 선택해주세요.")
    st.stop()


# 레이아웃: 3단 상단 요약

st.title('🍞베이커리 운영 대시보드')
st.write("""
         - 본 대시보드는 인기 제품 관리 및 재고 배치 등 운영 전략에 활용할 수 있습니다.
         - 데이터가 2016년 10월부터 2017년 4월까지 존재하여 해당 기간만 필터링 기능이 가능합니다.
         """)
st.caption('주별/월별 증감율은 필터링X🥹')
col1, col2, col3 = st.columns(3)

with col1:
    # 이전 날짜와 비교
    df['date'] = pd.to_datetime(df['date'])
    prev_day = df['date'].max() - pd.Timedelta(days=1)
    prev_day_count = df[df['date'].dt.date == prev_day.date()]['Transaction'].nunique()
    # 예외 처리 포함하여 성장률 계산
    growth_rate = ((today_count - prev_day_count) / prev_day_count) * 100 if prev_day_count != 0 else 0

    st.metric('총 거래 수 (오늘)', today_count, f'{growth_rate:.2f}%')

with col2:
    st.metric("🔥 피크 타임", f"{peak_hour}시", f"{peak_count}개 판매")

with col3:
    st.write("📦 오늘의 인기 상품 TOP5")
    st.dataframe(top_items_df, use_container_width=True, height=220)


# 거래 단위로 묶기 
basket_df = df.groupby('Transaction')['Item'].apply(list).reset_index()
# st.dataframe(basket_df.head())
from mlxtend.preprocessing import TransactionEncoder 

basket = basket_df['Item'].tolist()

te = TransactionEncoder() 
te_ary = te.fit_transform(basket) 

te_df = pd.DataFrame(te_ary, columns=te.columns_)

#st.write('One-Hot Encoding 결과')
#st.dataframe(te_df.head())

from mlxtend.frequent_patterns import apriori 

# 빈발 항목 추출 
frequent_items = apriori(te_df, min_support=0.02, use_colnames=True)

# support 기준 내림차순 정렬
frequent_items = frequent_items.sort_values(by='support', ascending=False) 

#st.subheader('자주 등장한 상품 조합')
#st.dataframe(frequent_items.head(10))

from mlxtend.frequent_patterns import association_rules
use_cols = [
    'antecedents',
    'consequents',
    'support',
    'confidence',
    'lift'
]
# 1. 연관 규칙 생성 
fp_rules = association_rules(frequent_items, metric='confidence', min_threshold=0.2)[use_cols]

#st.dataframe(fp_rules.head(10))

# 조건에 맞는 연관 규칙 필터링
filtered_rules = fp_rules[
    (fp_rules['lift'] > 1.1) & (fp_rules['confidence'] > 0.2)
].sort_values(by='lift', ascending=False)

# frozenset → 보기 좋게 문자열로 변환
filtered_rules['antecedents'] = filtered_rules['antecedents'].apply(lambda x: ', '.join(map(str, list(x))))
filtered_rules['consequents'] = filtered_rules['consequents'].apply(lambda x: ', '.join(map(str, list(x))))

# 제품별 판매량 집계
item_sales = filtered_df['Item'].value_counts().head(10).sort_values(ascending=False)

st.subheader("📊 오늘의 판매 현황")


viz_col1, viz_col2 = st.columns(2)

# 왼쪽: 시간대별 판매량
with viz_col1:
    st.markdown("#### ⏰ 시간대별 판매량")
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    bars = ax1.bar(hourly_sales.index, hourly_sales.values)
    for bar in bars:
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        ax1.text(x, y + 0.5, f'{int(y)}', ha='center', va='bottom', fontsize=9)
    ax1.set_xlabel('시간 (시)')
    ax1.set_ylabel('판매 수')
    ax1.set_title('시간대별 판매량')
    ax1.set_xticks(hourly_sales.index)
    st.pyplot(fig1)

# 오른쪽: 카테고리별 판매량
with viz_col2:
    st.markdown("#### 🧁 제품별 판매량")
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    bars = ax2.bar(item_sales.index, item_sales.values, color='orange')
    for bar in bars:
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        ax2.text(x, y + 0.5, f'{int(y)}', ha='center', va='bottom', fontsize=9)
    ax2.set_xlabel('카테고리')
    ax2.set_ylabel('판매 수')
    ax2.set_title('제품별 판매량')
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)

# 전략 제안은 아래쪽에 세로로
st.markdown("---")
st.subheader("🕵🏻‍♂️ 장바구니 속 조합으로 전략을 세워보자!")
st.info("""
        - 세트 상품 개발 및 상품 배치에 효과적인 장바구니 분석에 기반한 마케팅 전략입니다.
        - 의미있는 연관 규칙 도출하기 위해 빈도 수가 낮은 거래는 제외하였습니다.""")
st.markdown("""
- 향상도(Lift) **1.2 이상**: 세트 구성 후 프로모션 적용 및 전면 진열  
- 향상도(Lift) **1.2 이하**: 테마존 구성하여 **단독 진열 또는 추천 및 업셀링 전략**
""")

# 전략 생성 함수
def generate_strategy(from_item, to_item):
    pair = (from_item, to_item)
    if pair == ('Cake', 'Tea'):
        return "Tea와 잘 어울리는 디저트 세트로 구성하여 티타임존에 진열"
    elif pair == ('Toast', 'Coffee'):
        return "모닝 세트로 구성하여 할인 프로모션 적용 또는 아침 시간대(8~11시) 추천 상품존 진열"
    elif pair == ('Medialuna', 'Coffee'):
        return "브런치 코너 구성하여 Medialuna 전면 진열"
    elif pair == ('Pastry', 'Coffee'):
        return "'오늘의 추천'으로 제시 또는 SNS공유 유도"
    elif pair == ('Juice', 'Coffee'):
        return "고객 맞춤형 주스/커피 선택 옵션 제공"
    else:
        return f"{from_item} + {to_item} 세트 상품 구성"

# 전략 카드 반복 출력
for idx, row in filtered_rules.head(5).iterrows():
    from_item = row['antecedents']
    to_item = row['consequents']
    confidence = row['confidence'] * 100
    lift = row['lift']
    strategy_text = generate_strategy(from_item, to_item)

    st.markdown(f"""
    <div style="background-color:#333;padding:15px;border-radius:10px;margin-bottom:10px;color:white">
    <b>🔄 {from_item}</b>를 구매한 고객의 <b>{confidence:.1f}%</b>가 <b>{to_item}</b>도 함께 구매했습니다.<br>
    👉 추천 전략: <b>{strategy_text}</b> (Lift: <b>{lift:.2f}</b>)
    </div>
    """, unsafe_allow_html=True)
