# Menyiapkan seluruh library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })

    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_byorder_items_df(df):
    product_sales = all_df.groupby('product_category_name_english').agg({
     "order_id":"count"})
    product_sales = product_sales.reset_index()
    product_sales.rename(columns={
        "order_id": "order_count"
    }, inplace=True)
    product_sales = product_sales.sort_values("order_count", ascending=False)

    return product_sales

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    bystate_df = bystate_df.sort_values(by="customer_count", ascending=False)
    
    return bystate_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_unique_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)
    bycity_df = bycity_df.sort_values(by="customer_count", ascending=False)

    return bycity_df

def create_bypercentage_review_df(df):
    bypercentage_df = df.groupby(by="review_score").order_id.count().reset_index()
    bypercentage_df.rename(columns={
        "order_id": "review_count"
    }, inplace=True)
    bypercentage_df = bypercentage_df.sort_values(by="review_count", ascending=False)
    bypercentage_df["percentage"] = bypercentage_df["review_count"].apply(lambda x: x / bypercentage_df["review_count"].sum() *100)
    bypercentage_df.index = bypercentage_df.index.astype(int)
    return bypercentage_df

def create_bypayment_type_df(df):
    bypayment_type = df.groupby(by="payment_type").order_id.nunique().reset_index()
    bypayment_type.rename(columns={
        "order_id": "number_of_users"
    }, inplace=True)
    bypayment_type = bypayment_type.sort_values(by="number_of_users", ascending=False)
    return bypayment_type

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "order_purchase_timestamp", "frequency", "monetary"]
    
    rfm_df["order_purchase_timestamp"] = rfm_df["order_purchase_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["order_purchase_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("order_purchase_timestamp", axis=1, inplace=True)
    rfm_df.sort_values(by="recency", ascending=True).head(5)
    
    return rfm_df


# Load cleaned data
all_df = pd.read_csv("https://drive.google.com/u/0/uc?id=1n1kNHwHm4WqfqiwLEI6PLEQmPTRyWVRH&export=download")


datetime_columns = ["order_purchase_timestamp", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.title('Dashboard Analisis Data')
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# Menyiapkan berbagai dataframe
daily_orders_df = create_daily_orders_df(main_df)
product_sales_df = create_byorder_items_df(main_df)
customer_state_df = create_bystate_df(main_df)
customer_city_df = create_bycity_df(main_df)
customer_review_scores_df = create_bypercentage_review_df(main_df)
customer_payment_type_df = create_bypayment_type_df(main_df)
rfm_df = create_rfm_df(main_df)


# plot number of daily orders and revenue
st.title('E-COMMERCE PUBLIC :sparkles:')
st.header('Daily Orders and Revenue')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders in (2016 - 2018)", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue in (2016 - 2018)", value=total_revenue)

tab1, tab2 = st.tabs(["Orders", "Revenue"])
 
with tab1:
    st.subheader("Grafik Penjualan")
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_orders_df["order_purchase_timestamp"],
        daily_orders_df["order_count"],
        marker='o', 
        linewidth=2,
        color="#90CAF9"
    )
    ax.set_title(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)
 
with tab2:
    st.subheader("Grafik Pendapatan")
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_orders_df["order_purchase_timestamp"],
        daily_orders_df["revenue"],
        marker='o', 
        linewidth=2,
        color="#90CAF9"
    )
    ax.set_title(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)
 

# bar chart untuk Produk dengan penjualan tertinggi dan terendah
st.header('Produk Dengan Penjualan Tertinggi dan Terendah')

tab1, tab2 = st.tabs(["Penjualan Tertinggi", "Penjualan Terendah"])

# Membuat bar chart untuk 10 produk dengan penjualan tertinggi
with tab1:
    fig, ax = plt.subplots(figsize=(12, 6))
    colors1 = ["#2986cc","#a9ceea","#a9ceea","#a9ceea","#a9ceea","#a9ceea","#a9ceea","#a9ceea","#a9ceea","#a9ceea"]
    
    st.subheader("Top 10 Products by sales")
    sns.barplot(
        x="order_count", 
        y="product_category_name_english", 
        data=product_sales_df.head(10), 
        palette=colors1)
    
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis ='y', labelsize=12)

    # Menampilkan plot
    st.pyplot(fig)

# Membuat bar chart untuk 10 produk dengan penjualan terendah
with tab2:
    fig, ax = plt.subplots(figsize=(12, 6))
    colors2 = ["#f44336","#ea9999","#ea9999","#ea9999","#ea9999","#ea9999","#ea9999","#ea9999","#ea9999","#ea9999"]

    st.subheader("Lowest 10 Products by sales")
    sns.barplot(
        x="order_count", 
        y="product_category_name_english", 
        data=product_sales_df.sort_values(by="order_count", ascending=True).head(10), 
        palette=colors2)
    
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=12)

    # Menampilkan plot
    st.pyplot(fig)


# Membuat bar chart untuk Negara dengan jumlah pelanggan terbesar
st.header('Jumlah Pelanggan Terbesar Berdasarkan Kota dan Negara')

tab1, tab2 = st.tabs(["Berdasarkan Kota", "Berdasarkan Negara"])

with tab1:
    # bar chart untuk Kota dengan jumlah pelanggan terbesar
    st.write('10 Kota Teratas')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="customer_count", 
        y="customer_city",
        data=customer_city_df.sort_values(by="customer_count", ascending=False).head(10),
        palette="Blues_r")
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=11)

    # Menampilkan plot
    st.pyplot(fig)

with tab2:
    # bar chart untuk Kota dengan jumlah pelanggan terbesar
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="customer_count", 
        y="customer_state",
        data=customer_state_df.sort_values(by="customer_count", ascending=False),
        palette="Blues_r")
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=11)

    # Menampilkan plot
    st.pyplot(fig)


# Membuat pie chart persentase kepuasan pelanggan terhadap produk yang dibeli berdasarkan skor ulasan
with st.container():
    st.header('Persentase Kepuasan Pelanggan')
    st.write('Persentase kepuasan pelanggan terhadap produk yang dibeli berdasarkan skor ulasan')

    customer_review_scores_df['review_score'] = customer_review_scores_df['review_score'].astype(int)

    values = customer_review_scores_df['percentage']
    labels = customer_review_scores_df['review_score'].tolist()
    pie_color=["#86aad2","#d7e3f1","#ecc196","#d25865","#aa3840"]
    explodes = [0.05, 0.05, 0.05, 0.05, 0.06]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(values, labels=labels, colors=pie_color, explode=explodes, autopct='%1.1f%%', startangle=90)
    ax.legend(loc='upper left')

    # Menampilkan pie chart di streamlit
    st.pyplot(fig)


# Membuat bar chart tipe pembayaran yang paling sering digunakan oleh pelanggan
st.header('Tipe pembayaran Terpopuler')
st.write('Tipe pembayaran yang sering digunakan oleh pelanggan')
fig, ax = plt.subplots(figsize=(10, 5))

colors = ["#2986cc","#a9ceea","#a9ceea","#a9ceea","#a9ceea"]

sns.barplot(
    y="number_of_users", 
    x="payment_type",
    data=customer_payment_type_df.sort_values(by="number_of_users", ascending=False),
    palette=colors)
plt.title("Number of Customer by State", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)

# Menampilkan plot
st.pyplot(fig)


# visualisasi hasil Analisis RFM
# Pelanggan Terbaik Berdasarkan Analisis RFM
st.header("Pelanggan Terbaik Berdasarkan Analisis RFM")
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency", value=avg_recency)
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Customer ID", fontsize=30)
ax[0].set_title("By Recency", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35, rotation=90)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Customer ID", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=30)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35, rotation=90)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Customer ID", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=30)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35, rotation=90)

st.pyplot(fig)


# RFM Scores
st.subheader('Segmentasi Pelanggan Berdasarkan Skor RFM')
# Mengurutkan Customer berdasarkan RFM scores
rfm_df['r_rank'] = rfm_df['recency'].rank(ascending=False)
rfm_df['f_rank'] = rfm_df['frequency'].rank(ascending=True)
rfm_df['m_rank'] = rfm_df['monetary'].rank(ascending=True)

# menormalkan peringkat pelanggan
rfm_df['r_rank_norm'] = (rfm_df['r_rank'] / rfm_df['r_rank'].max()) * 100
rfm_df['f_rank_norm'] = (rfm_df['f_rank'] / rfm_df['f_rank'].max()) * 100
rfm_df['m_rank_norm'] = (rfm_df['m_rank'] / rfm_df['m_rank'].max()) * 100
rfm_df.drop(columns=['r_rank', 'f_rank', 'm_rank'], inplace=True)

# Hitung skor RFM
rfm_df['RFM_score'] = 0.15 * rfm_df['r_rank_norm'] + 0.28 * rfm_df['f_rank_norm'] + 0.57 * rfm_df['m_rank_norm']
rfm_df['RFM_score'] *= 0.05
rfm_df = rfm_df.round(2)

# menentukan segmen pelanggan berdasarkan skor RFM
rfm_df["customer_segment"] = np.where(
    rfm_df['RFM_score'] > 4.5, "Top customers", (np.where(
        rfm_df['RFM_score'] > 4, "High-value customer", (np.where(
            rfm_df['RFM_score'] > 3, "Medium-value customer", np.where(
                rfm_df['RFM_score'] > 1.6, 'Low-value customers', 'Lost customers'))))))

# Menampilkan bar chart yang menunjukkan jumlah pelanggan di setiap segmen
customer_segment_df = rfm_df.groupby(by="customer_segment", as_index=False).customer_id.nunique()
customer_segment_df['customer_segment'] = pd.Categorical(customer_segment_df['customer_segment'], [
    "Lost customers", "Low-value customers", "Medium-value customer",
    "High-value customer", "Top customers"
])

plt.figure(figsize=(10, 5))
colors = ["#bedaef", "#539ed6", "#bedaef", "#bedaef", "#bedaef"]
sns.barplot(
    x="customer_id",
    y="customer_segment",
    data=customer_segment_df.sort_values(by="customer_segment", ascending=False),
    palette=colors
)
plt.title(None)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=12)
st.pyplot(plt)

st.caption('Copyright (c) Analisis Data E-Commerce 2023 :sparkles:')
