import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import openai
import numpy as np
from openai_utils import OpenAIAssistant

# Hàm đọc dữ liệu từ file Excel
def load_data_excel(file_path):
    return pd.read_excel(file_path, engine='openpyxl')

# Hàm hiển thị dữ liệu mẫu
def display_data(data):
    if not data.empty:
        st.write("Dữ liệu mẫu:")
        rows_per_page = 20
        total_rows = len(data)
        num_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)
        page = st.number_input("Chọn trang: ", min_value=1, max_value=num_pages, step=1)
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        st.write(data.iloc[start_idx:end_idx])

# Hàm thực thi mã với phần nhận xét
def execute_code(code, data):
    try:
        local_scope = {'np': np, 'data': data, 'plt': plt}
        exec(code, {}, local_scope)
        if 'plt' in local_scope:
            st.pyplot(local_scope['plt'].gcf())  # Hiển thị biểu đồ đã tạo
            
            # Hiển thị nhận xét nếu có
            if 'comment' in local_scope:
                st.write("**Nhận xét:**")
                st.write(local_scope['comment'])
        else:
            st.error("Không tìm thấy đối tượng plt để hiển thị biểu đồ.")
    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi thực thi mã: {e}")



# CSS để định dạng giao diện và hộp hiển thị biểu đồ
st.markdown(
    """
    <style>
    .box {
        padding: 20px;
        margin: 10px;
        background-color: #f9f9f9;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Tạo banner hiển thị tiêu đề của trang dashboard
st.markdown(
    """
    <div style="background-color:lightblue; padding:10px">
    <h1 style="color:black; text-align:center;">Hotel Review Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Menu sidebar cho người dùng chọn chức năng
menu = ["Home", "1.Phân Tích Đánh Giá và Số Lượng Đánh Giá", "2.So Sánh Đánh Giá Giữa Khách Sạn 4 Sao và 5 Sao", "3.Phân Tích Nội Dung và Phản Hồi Từ Chủ Khách Sạn",
        "4.Tương Tác của Người Đánh Giá", "5.So Sánh Các Khía Cạnh Khu Vực Địa Lý", "6.Xu Hướng và Thay Đổi Theo Thời Gian", "7.Test"]
choice = st.sidebar.selectbox("Select a Function", menu)

#1
# Hàm tạo biểu đồ cột cho phân tích đánh giá
@st.cache_resource
def average_rating_by_city_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Trung bình đánh giá theo thành phố (Biểu đồ cột)")
    # Tính trung bình đánh giá theo thành phố cho từng loại khách sạn
    avg_rating_4star = df_4star.groupby('city')['rating'].mean()
    avg_rating_5star = df_5star.groupby('city')['rating'].mean()
    # Tạo DataFrame để dễ dàng so sánh
    avg_ratings = pd.DataFrame({
        '4 Sao': avg_rating_4star,
        '5 Sao': avg_rating_5star
    }).dropna()  # Loại bỏ các thành phố không có dữ liệu ở cả 2 loại
    # Vẽ biểu đồ
    avg_ratings.plot(kind='bar', figsize=(14, 6))
    plt.xlabel('Thành phố')
    plt.ylabel('Trung bình đánh giá')
    plt.title('So sánh xếp hạng trung bình theo thành phố giữa khách sạn 4 sao và 5 sao')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ này cho thấy sự khác biệt về xếp hạng trung bình giữa các thành phố cho khách sạn 4 sao và 5 sao.
        Các thành phố có mức đánh giá cao có thể cho thấy dịch vụ tốt và sự hài lòng của khách hàng. Ngược lại, các thành phố
        với xếp hạng thấp cần cải thiện chất lượng dịch vụ. Biểu đồ cột này cho thấy rằng các khách sạn 5 sao ở thành phố Hà Nội 
        có điểm đánh giá trung bình cao hơn so với các khách sạn 4 sao, điều này có thể cho thấy sự khác biệt về chất lượng dịch vụ 
        giữa các phân khúc khách sạn. Trong khi đó, ở thành phố Đà Nẵng, điểm đánh giá trung bình của khách sạn 4 sao và 5 sao khá gần 
        nhau, gợi ý rằng dịch vụ của cả hai loại khách sạn có thể tương đương nhau. Thành phố Hải Phòng có điểm đánh giá trung bình thấp 
        nhất ở cả hai loại khách sạn, cho thấy có thể cần cải thiện chất lượng dịch vụ tại đây.
    """)

    # Hàm tạo biểu đồ histogram cho phân tích phân phối đánh giá
@st.cache_resource
def rating_distribution_histogram(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Phân phối số lượng đánh giá (Biểu đồ Histogram)")
    # Vẽ histogram cho cả 2 loại khách sạn
    plt.figure(figsize=(14, 6))
    # Histogram cho 4 sao
    plt.hist(df_4star['rating'], bins=5, alpha=0.5, label='Khách sạn 4 Sao', color='blue', edgecolor='black')
    # Histogram cho 5 sao
    plt.hist(df_5star['rating'], bins=5, alpha=0.5, label='Khách sạn 5 Sao', color='orange', edgecolor='black')

    plt.xlabel('Thang điểm đánh giá')
    plt.ylabel('Số lượng đánh giá')
    plt.title('Phân phối số lượng đánh giá theo thang điểm')
    plt.legend(loc='upper right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ này hiển thị sự phân bố số lượng đánh giá theo thang điểm. Điều này giúp xác định
        mức độ hài lòng của khách hàng với dịch vụ tại các khách sạn 4 sao và 5 sao. Số lượng lớn các đánh giá ở mức 4 và 5 sao
        thường cho thấy sự hài lòng cao, trong khi nhiều đánh giá ở mức thấp (1-2 sao) là dấu hiệu của dịch vụ cần cải thiện.
        Biểu đồ histogram cho thấy rằng phần lớn các đánh giá tập trung ở mức 4 và 5 sao, chứng tỏ khách hàng thường hài lòng với dịch 
        vụ của cả khách sạn 4 sao và 5 sao. Tuy nhiên, có một số đánh giá ở mức 1 và 2 sao, đặc biệt là ở các khách sạn 4 sao, gợi ý 
        rằng vẫn có một số trường hợp khách hàng không hài lòng. Phân phối lệch về phía đánh giá tích cực cho thấy phần lớn trải nghiệm 
        khách hàng là tốt, nhưng sự hiện diện của các đánh giá thấp có thể là một dấu hiệu cần chú ý để cải thiện dịch vụ. 
    """)

# Hàm tạo biểu đồ đường để hiển thị số lượng đánh giá theo thời gian
@st.cache_resource
def review_count_over_time_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Số lượng đánh giá theo thời gian (Biểu đồ đường)")
    
    # Chuyển đổi cột 'published_at_date' sang định dạng datetime
    df_4star['published_at_date'] = pd.to_datetime(df_4star['published_at_date'], errors='coerce')
    df_5star['published_at_date'] = pd.to_datetime(df_5star['published_at_date'], errors='coerce')
    
    # Tính số lượng đánh giá theo tháng/năm
    review_count_4star = df_4star['published_at_date'].dt.to_period('M').value_counts().sort_index()
    review_count_5star = df_5star['published_at_date'].dt.to_period('M').value_counts().sort_index()

    # Vẽ biểu đồ đường
    plt.figure(figsize=(14, 6))
    plt.plot(review_count_4star.index.astype(str), review_count_4star.values, marker='o', label='Khách sạn 4 Sao', color='blue')
    plt.plot(review_count_5star.index.astype(str), review_count_5star.values, marker='o', label='Khách sạn 5 Sao', color='orange')
    
    plt.xlabel('Thời gian (Tháng/Năm)')
    plt.ylabel('Số lượng đánh giá')
    plt.title('Xu hướng thay đổi số lượng đánh giá theo thời gian')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(loc='upper left')
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ này hiển thị xu hướng số lượng đánh giá qua các tháng/năm, giúp nhận biết các khoảng thời gian có sự gia tăng
        hoặc giảm sút đáng kể về lượng đánh giá. Các đỉnh trong biểu đồ có thể gợi ý về các sự kiện hoặc giai đoạn đặc biệt
        như mùa du lịch cao điểm hoặc các chương trình khuyến mãi. Biểu đồ đường minh họa xu hướng số lượng đánh giá theo thời gian cho
        thấy rằng có một sự tăng vọt trong số lượng đánh giá vào mùa du lịch cao điểm như tháng 6 và tháng 7. Điều này có thể liên 
        quan đến lượng khách du lịch tăng lên trong kỳ nghỉ hè. Ngược lại, số lượng đánh giá giảm đáng kể vào các tháng mùa đông như 
        tháng 12 và tháng 1, có thể đây những tháng này có nhiều dịp lễ tết mọi người hay ở nhà hơn.
    """)

#2
# Hàm tạo biểu đồ cột phân kỳ để so sánh tỷ lệ đánh giá tích cực và tiêu cực
@st.cache_resource
def sentiment_divergence_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Tỷ lệ đánh giá tích cực và tiêu cực (Biểu đồ cột phân kỳ)")
    
    # Phân loại đánh giá
    df_4star['sentiment'] = pd.cut(df_4star['rating'], bins=[0, 2, 3, 5], labels=['Tiêu cực', 'Trung lập', 'Tích cực'])
    df_5star['sentiment'] = pd.cut(df_5star['rating'], bins=[0, 2, 3, 5], labels=['Tiêu cực', 'Trung lập', 'Tích cực'])

    # Tính tỷ lệ đánh giá cho mỗi loại khách sạn
    sentiment_counts_4star = df_4star['sentiment'].value_counts(normalize=True) * 100
    sentiment_counts_5star = df_5star['sentiment'].value_counts(normalize=True) * 100

    # Ghép dữ liệu thành một DataFrame
    sentiment_df = pd.DataFrame({
        '4 Sao': sentiment_counts_4star,
        '5 Sao': sentiment_counts_5star
    }).reindex(['Tiêu cực', 'Trung lập', 'Tích cực'])

    # Vẽ biểu đồ cột phân kỳ
    plt.figure(figsize=(10, 6))
    sentiment_df.plot(kind='bar', stacked=True, color=['red', 'gray', 'green'], alpha=0.7, width=0.8)
    plt.xlabel('Loại đánh giá')
    plt.ylabel('Tỷ lệ (%)')
    plt.title('Tỷ lệ đánh giá tích cực và tiêu cực giữa khách sạn 4 sao và 5 sao')
    plt.xticks(rotation=0)
    plt.legend(loc='upper right')
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ cột phân kỳ này cho thấy rằng khách sạn 5 sao có tỷ lệ đánh giá tích cực cao hơn rõ rệt so với khách sạn 4 sao,
        trong khi đó, khách sạn 4 sao lại có tỷ lệ đánh giá tiêu cực cao hơn. Kết quả này có thể phản ánh sự chênh lệch về chất lượng dịch vụ 
        và mức độ hài lòng giữa hai loại khách sạn, đặc biệt trong các mùa du lịch cao điểm, khi khách sạn 5 sao có thể đáp ứng nhu cầu tốt hơn.
    """)

# Hàm tạo biểu đồ cột kép để so sánh số lượng đánh giá có phản hồi từ chủ khách sạn
@st.cache_resource
def response_interaction_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Số lượng đánh giá có phản hồi từ chủ khách sạn (Biểu đồ cột kép)")
    
    # Kiểm tra xem đánh giá có phản hồi không
    df_4star['has_response'] = df_4star['response_from_owner_text'].notna()
    df_5star['has_response'] = df_5star['response_from_owner_text'].notna()

    # Tính tỷ lệ đánh giá có phản hồi cho mỗi loại khách sạn
    response_rate_4star = df_4star['has_response'].mean() * 100
    response_rate_5star = df_5star['has_response'].mean() * 100

    # Dữ liệu cho biểu đồ
    response_rates = pd.DataFrame({
        '4 Sao': [response_rate_4star],
        '5 Sao': [response_rate_5star]
    })

    # Vẽ biểu đồ cột kép
    plt.figure(figsize=(8, 6))
    response_rates.plot(kind='bar', color=['blue', 'orange'], alpha=0.7)
    plt.xlabel('Loại khách sạn')
    plt.ylabel('Tỷ lệ phản hồi (%)')
    plt.title('So sánh tỷ lệ phản hồi của chủ khách sạn trên các đánh giá')
    plt.xticks(ticks=[0], labels=['Phản hồi từ chủ khách sạn'], rotation=0)
    plt.legend(loc='upper right')
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ cột kép cho thấy sự khác biệt rõ rệt về tỷ lệ phản hồi giữa khách sạn 4 sao và 5 sao. Khách sạn 5 sao có xu hướng
        phản hồi đánh giá của khách hàng thường xuyên hơn, thể hiện sự quan tâm cao đến trải nghiệm của khách. Ngược lại, khách sạn 4 sao có tỷ lệ
        phản hồi thấp hơn, có thể là do nguồn lực hạn chế hoặc ít đầu tư vào dịch vụ chăm sóc khách hàng, đặc biệt trong mùa cao điểm khi số lượng
        đánh giá tăng cao.
    """)

#3
# Hàm tạo biểu đồ cột để hiển thị tỷ lệ phản hồi từ chủ khách sạn
@st.cache_resource
def owner_response_rate_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Tỷ lệ phản hồi từ chủ khách sạn (Biểu đồ cột)")
    
    # Tính tỷ lệ phản hồi cho mỗi loại khách sạn
    response_rate_4star = df_4star['response_from_owner_text'].notna().mean() * 100
    response_rate_5star = df_5star['response_from_owner_text'].notna().mean() * 100

    # Dữ liệu cho biểu đồ
    response_rates = pd.DataFrame({
        'Loại khách sạn': ['4 Sao', '5 Sao'],
        'Tỷ lệ phản hồi (%)': [response_rate_4star, response_rate_5star]
    })

    # Vẽ biểu đồ cột
    plt.figure(figsize=(8, 6))
    plt.bar(response_rates['Loại khách sạn'], response_rates['Tỷ lệ phản hồi (%)'], color=['blue', 'orange'], alpha=0.7)
    plt.xlabel('Loại khách sạn')
    plt.ylabel('Tỷ lệ phản hồi (%)')
    plt.title('Tỷ lệ phản hồi từ chủ khách sạn trên các đánh giá')
    plt.ylim(0, 100)
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ này thể hiện sự khác biệt trong mức độ phản hồi giữa khách sạn 4 sao và 5 sao. Khách sạn 5 sao có tỷ lệ phản hồi cao hơn đáng kể so với khách sạn 4 sao, cho thấy mức độ đầu tư cao hơn vào chăm sóc khách hàng và sự quan tâm đến trải nghiệm khách hàng. Điều này có thể giúp duy trì uy tín cho khách sạn 5 sao, đặc biệt khi khách hàng thường có kỳ vọng cao hơn ở dịch vụ cao cấp.
    """)

# Hàm tạo biểu đồ phân tán để minh họa thời gian trung bình phản hồi từ khi có đánh giá
@st.cache_resource
def response_time_scatter_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Thời gian phản hồi từ chủ khách sạn (Biểu đồ phân tán)")
    
    # Chuyển đổi cột 'published_at_date' và 'response_from_owner_date' sang định dạng datetime
    df_4star['published_at_date'] = pd.to_datetime(df_4star['published_at_date'], errors='coerce')
    df_4star['response_from_owner_date'] = pd.to_datetime(df_4star['response_from_owner_date'], errors='coerce')
    df_5star['published_at_date'] = pd.to_datetime(df_5star['published_at_date'], errors='coerce')
    df_5star['response_from_owner_date'] = pd.to_datetime(df_5star['response_from_owner_date'], errors='coerce')

    # Tính thời gian phản hồi (số ngày)
    df_4star['response_time'] = (df_4star['response_from_owner_date'] - df_4star['published_at_date']).dt.days
    df_5star['response_time'] = (df_5star['response_from_owner_date'] - df_5star['published_at_date']).dt.days

    # Lọc các giá trị hợp lệ (loại bỏ thời gian phản hồi âm hoặc NaN)
    valid_response_4star = df_4star[df_4star['response_time'] >= 0]
    valid_response_5star = df_5star[df_5star['response_time'] >= 0]

    # Vẽ biểu đồ phân tán
    plt.figure(figsize=(14, 6))
    plt.scatter(valid_response_4star['published_at_date'], valid_response_4star['response_time'], color='blue', alpha=0.6, label='Khách sạn 4 Sao')
    plt.scatter(valid_response_5star['published_at_date'], valid_response_5star['response_time'], color='orange', alpha=0.6, label='Khách sạn 5 Sao')
    
    plt.xlabel('Ngày đánh giá')
    plt.ylabel('Thời gian phản hồi (ngày)')
    plt.title('Thời gian phản hồi từ khi có đánh giá')
    plt.legend(loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ phân tán này cho thấy sự khác biệt trong thời gian phản hồi từ chủ khách sạn giữa khách sạn 4 sao và 5 sao. Khách sạn 5 sao có xu hướng phản hồi nhanh hơn và ổn định hơn, điều này có thể giúp tạo lòng tin cho khách hàng. Ngược lại, khách sạn 4 sao có thời gian phản hồi dài hơn và biến động lớn hơn, có thể là do nguồn lực giới hạn hoặc quy trình phản hồi chậm trễ. Sự khác biệt này có thể trở nên rõ ràng hơn trong các mùa cao điểm hoặc ngày lễ.
    """)

#4
# Hàm tạo biểu đồ cột để thể hiện tỷ lệ đánh giá từ Local Guide
@st.cache_resource
def local_guide_review_rate_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Tỷ lệ đánh giá từ Local Guide (Biểu đồ cột)")
    
    # Tính tỷ lệ đánh giá từ Local Guide cho mỗi loại khách sạn
    local_guide_4star = df_4star['is_local_guide'].sum()
    local_guide_5star = df_5star['is_local_guide'].sum()
    total_reviews_4star = len(df_4star)
    total_reviews_5star = len(df_5star)
    
    # Tính tỷ lệ
    ratio_4star = local_guide_4star / total_reviews_4star * 100 if total_reviews_4star > 0 else 0
    ratio_5star = local_guide_5star / total_reviews_5star * 100 if total_reviews_5star > 0 else 0

    # Dữ liệu cho biểu đồ
    categories = ['4 Sao', '5 Sao']
    ratios = [ratio_4star, ratio_5star]

    # Vẽ biểu đồ cột
    plt.figure(figsize=(10, 6))
    plt.bar(categories, ratios, color=['blue', 'orange'], alpha=0.7)
    plt.xlabel('Loại khách sạn')
    plt.ylabel('Tỷ lệ đánh giá từ Local Guide (%)')
    plt.title('Tỷ lệ đánh giá từ Local Guide giữa khách sạn 4 sao và 5 sao')
    plt.ylim(0, 100)
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ này cho thấy rằng khách sạn 5 sao có tỷ lệ đánh giá từ Local Guide cao hơn so với khách sạn 4 sao.
        Điều này có thể cho thấy rằng khách sạn 5 sao thu hút nhiều người dùng Local Guide hơn, có thể là do chất lượng dịch vụ hoặc 
        các tiện ích nổi bật hơn. Khách sạn 4 sao có tỷ lệ thấp hơn, có thể phản ánh sự quan tâm ít hơn từ nhóm người dùng này.
    """)

# Hàm tạo biểu đồ dot plot để thể hiện sự phân bố số lượt thích trên các đánh giá
@st.cache_resource
def review_likes_distribution_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Phân bố số lượt thích trên các đánh giá (Dot Plot)")
    
    # Lấy dữ liệu lượt thích từ các đánh giá
    likes_4star = df_4star['review_likes_count'].dropna()
    likes_5star = df_5star['review_likes_count'].dropna()

    # Vẽ biểu đồ dot plot
    plt.figure(figsize=(14, 6))
    plt.plot(likes_4star, [1] * len(likes_4star), 'bo', alpha=0.6, label='Khách sạn 4 Sao')
    plt.plot(likes_5star, [2] * len(likes_5star), 'ro', alpha=0.6, label='Khách sạn 5 Sao')
    
    # Cài đặt biểu đồ
    plt.yticks([1, 2], ['4 Sao', '5 Sao'])
    plt.xlabel('Số lượt thích')
    plt.title('Phân bố số lượt thích trên các đánh giá')
    plt.legend(loc='upper right')
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ dot plot này cho thấy sự phân bố số lượt thích trên các đánh giá cho khách sạn 4 sao và 5 sao.
        Các đánh giá của khách sạn 5 sao có xu hướng nhận được nhiều lượt thích hơn so với khách sạn 4 sao, điều này có thể
        chỉ ra rằng các đánh giá tại khách sạn 5 sao nhận được sự quan tâm cao hơn từ cộng đồng. Khách sạn 4 sao có phân bố
        lượt thích thấp hơn, có thể phản ánh mức độ ảnh hưởng của các đánh giá ít hơn so với khách sạn 5 sao.
    """)

#5
# Hàm tạo biểu đồ cột để so sánh xếp hạng trung bình theo vùng
@st.cache_resource
def average_rating_by_region_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Xếp hạng trung bình theo vùng (Biểu đồ cột)")
    
    # Tính xếp hạng trung bình theo vùng cho mỗi loại khách sạn
    avg_rating_4star = df_4star.groupby('region')['rating'].mean()
    avg_rating_5star = df_5star.groupby('region')['rating'].mean()

    # Ghép dữ liệu từ hai loại khách sạn thành một DataFrame
    avg_ratings = pd.DataFrame({
        '4 Sao': avg_rating_4star,
        '5 Sao': avg_rating_5star
    }).reset_index()

    # Vẽ biểu đồ cột
    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    regions = avg_ratings['region']
    
    plt.bar(regions, avg_ratings['4 Sao'], width=bar_width, label='Khách sạn 4 Sao', color='blue', alpha=0.7)
    plt.bar(regions, avg_ratings['5 Sao'], width=bar_width, label='Khách sạn 5 Sao', color='orange', alpha=0.7, bottom=avg_ratings['4 Sao'])

    # Cài đặt biểu đồ
    plt.xlabel('Vùng')
    plt.ylabel('Xếp hạng trung bình')
    plt.title('So sánh xếp hạng trung bình theo vùng')
    plt.legend(loc='upper right')
    plt.ylim(0, 5)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ này cho thấy sự khác biệt về xếp hạng trung bình giữa các vùng Bắc, Trung và Nam cho hai loại khách sạn.
        Khách sạn 5 sao tại các vùng thường có xếp hạng trung bình cao hơn khách sạn 4 sao, đặc biệt là ở vùng Bắc, nơi mức độ hài lòng của khách
        hàng tại khách sạn 5 sao có xu hướng cao nhất. Sự khác biệt này có thể liên quan đến chất lượng dịch vụ hoặc sự khác biệt trong yêu cầu
        của khách hàng tại mỗi vùng.
    """)

# Hàm tạo heat map để hiển thị số lượng đánh giá theo thành phố
@st.cache_resource
def review_count_by_city_heatmap(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Số lượng đánh giá theo thành phố (Heatmap)")
    
    # Đếm số lượng đánh giá cho từng thành phố trong mỗi loại khách sạn
    city_counts_4star = df_4star['city'].value_counts()
    city_counts_5star = df_5star['city'].value_counts()
    
    # Kết hợp dữ liệu vào một DataFrame
    city_counts = pd.DataFrame({
        '4 Sao': city_counts_4star,
        '5 Sao': city_counts_5star
    }).fillna(0)  # Điền giá trị NaN bằng 0 nếu thành phố chỉ có đánh giá từ một loại khách sạn

    # Vẽ heatmap với chú thích lớn hơn và khoảng cách giữa các ô
    plt.figure(figsize=(20, 16))  # Tăng kích thước biểu đồ
    sns.heatmap(
        city_counts,
        annot=True,
        annot_kws={"size": 12},  # Điều chỉnh kích thước chữ số trong ô
        cmap="YlGnBu",
        fmt=".0f",
        cbar=True,
        linewidths=1,  # Tăng độ rộng đường kẻ
        linecolor='black'
    )
    plt.xlabel('Loại khách sạn', fontsize=14)
    plt.ylabel('Thành phố', fontsize=14)
    plt.title('Số lượng đánh giá theo thành phố cho khách sạn 4 sao và 5 sao', fontsize=16)
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Heatmap này minh họa sự khác biệt về số lượng đánh giá giữa các thành phố lớn cho hai loại khách sạn.
        Các thành phố lớn như Hà Nội và Hồ Chí Minh thường có số lượng đánh giá cao hơn cho cả khách sạn 4 sao và 5 sao, cho
        thấy nhu cầu dịch vụ khách sạn ở những khu vực này cao hơn hẳn so với các thành phố khác. Điều này có thể phản ánh
        sự phổ biến của các điểm đến du lịch và cơ sở hạ tầng tại các thành phố lớn.
    """)

#6
#Hàm tạo biểu đồ line chart để theo dõi sự biến động của đánh giá theo thời gian
@st.cache_resource
def review_trend_over_time_chart(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Xu hướng thay đổi đánh giá qua các năm/tháng (Biểu đồ line chart)")

    # Chuyển đổi cột 'published_at_date' sang định dạng datetime
    df_4star['published_at_date'] = pd.to_datetime(df_4star['published_at_date'], errors='coerce')
    df_5star['published_at_date'] = pd.to_datetime(df_5star['published_at_date'], errors='coerce')

    # Tính trung bình điểm đánh giá theo tháng/năm
    monthly_avg_rating_4star = df_4star.groupby(df_4star['published_at_date'].dt.to_period('M'))['rating'].mean().sort_index()
    monthly_avg_rating_5star = df_5star.groupby(df_5star['published_at_date'].dt.to_period('M'))['rating'].mean().sort_index()

    # Vẽ biểu đồ line chart
    plt.figure(figsize=(14, 6))
    plt.plot(monthly_avg_rating_4star.index.astype(str), monthly_avg_rating_4star.values, marker='o', label='Khách sạn 4 Sao', color='blue')
    plt.plot(monthly_avg_rating_5star.index.astype(str), monthly_avg_rating_5star.values, marker='o', label='Khách sạn 5 Sao', color='orange')

    plt.xlabel('Thời gian (Tháng/Năm)')
    plt.ylabel('Trung bình điểm đánh giá')
    plt.title('Xu hướng thay đổi đánh giá qua các năm/tháng')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(loc='upper left')
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ line chart này cho thấy xu hướng thay đổi đánh giá trung bình theo thời gian. Khách sạn 5 sao thường có xu hướng ổn định hơn và điểm số trung bình cao hơn so với khách sạn 4 sao. Vào các tháng du lịch cao điểm, có thể nhận thấy sự gia tăng nhẹ trong điểm đánh giá, có thể do số lượng du khách đông đúc hơn. Các tháng cuối năm có xu hướng giảm nhẹ, có thể phản ánh những thách thức trong việc duy trì chất lượng dịch vụ trong mùa lễ hội.
    """)

# Hàm tạo biểu đồ vùng để minh họa tổng số lượng đánh giá tích cực và tiêu cực theo thời gian
@st.cache_resource
def area_chart_positive_negative_reviews(df_4star, df_5star):
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("Tổng số lượng đánh giá tích cực và tiêu cực theo thời gian (Biểu đồ vùng)")

    # Chuyển đổi cột 'published_at_date' sang định dạng datetime
    df_4star['published_at_date'] = pd.to_datetime(df_4star['published_at_date'], errors='coerce')
    df_5star['published_at_date'] = pd.to_datetime(df_5star['published_at_date'], errors='coerce')

    # Phân loại đánh giá tích cực và tiêu cực
    def classify_rating(rating):
        if rating >= 4:
            return 'positive'
        elif rating <= 2:
            return 'negative'
        else:
            return 'neutral'

    # Thêm cột phân loại vào DataFrame
    df_4star['rating_category'] = df_4star['rating'].apply(classify_rating)
    df_5star['rating_category'] = df_5star['rating'].apply(classify_rating)

    # Tính tổng số lượng đánh giá tích cực và tiêu cực theo tháng/năm
    positive_reviews_4star = df_4star[df_4star['rating_category'] == 'positive'].groupby(df_4star['published_at_date'].dt.to_period('M')).size()
    negative_reviews_4star = df_4star[df_4star['rating_category'] == 'negative'].groupby(df_4star['published_at_date'].dt.to_period('M')).size()

    positive_reviews_5star = df_5star[df_5star['rating_category'] == 'positive'].groupby(df_5star['published_at_date'].dt.to_period('M')).size()
    negative_reviews_5star = df_5star[df_5star['rating_category'] == 'negative'].groupby(df_5star['published_at_date'].dt.to_period('M')).size()

    # Hợp nhất các chuỗi để đảm bảo có cùng chỉ mục thời gian
    all_months = pd.period_range(start=min(positive_reviews_4star.index.min(), positive_reviews_5star.index.min()), 
                                 end=max(positive_reviews_4star.index.max(), positive_reviews_5star.index.max()), freq='M')
    
    positive_reviews_4star = positive_reviews_4star.reindex(all_months, fill_value=0)
    negative_reviews_4star = negative_reviews_4star.reindex(all_months, fill_value=0)
    positive_reviews_5star = positive_reviews_5star.reindex(all_months, fill_value=0)
    negative_reviews_5star = negative_reviews_5star.reindex(all_months, fill_value=0)

    # Vẽ biểu đồ vùng
    plt.figure(figsize=(14, 6))
    plt.stackplot(
        all_months.astype(str),
        positive_reviews_4star.values,
        negative_reviews_4star.values,
        labels=['Đánh giá tích cực 4 Sao', 'Đánh giá tiêu cực 4 Sao'],
        colors=['green', 'red'],
        alpha=0.5
    )
    plt.stackplot(
        all_months.astype(str),
        positive_reviews_5star.values,
        negative_reviews_5star.values,
        labels=['Đánh giá tích cực 5 Sao', 'Đánh giá tiêu cực 5 Sao'],
        colors=['lightgreen', 'lightcoral'],
        alpha=0.5
    )

    plt.xlabel('Thời gian (Tháng/Năm)')
    plt.ylabel('Số lượng đánh giá')
    plt.title('Tổng số lượng đánh giá tích cực và tiêu cực theo thời gian')
    
    # Chỉ hiển thị một số nhãn nhất định trên trục x
    step = max(1, len(all_months) // 12)  # Hiển thị tối đa 12 nhãn
    plt.xticks(ticks=range(0, len(all_months), step), labels=all_months[::step].astype(str), rotation=45)
    
    plt.legend(loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(plt)
    plt.clf()  # Giải phóng bộ nhớ sau khi hiển thị

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
        **Nhận xét:** Biểu đồ vùng này cho thấy rằng khách sạn 5 sao có số lượng đánh giá tích cực cao hơn so với khách sạn 4 sao 
        trong suốt giai đoạn được phân tích, đặc biệt là vào các tháng mùa hè, có thể liên quan đến mùa du lịch cao điểm. 
        Ngược lại, một sự gia tăng đột ngột trong số lượng đánh giá tiêu cực của cả hai loại khách sạn vào tháng 12 có thể gợi 
        ý về một vấn đề dịch vụ trong mùa lễ hội.
    """)

#7

# Hàm đọc dữ liệu từ file Excel với caching
@st.cache_data
def load_data_excel(file_path):
    return pd.read_excel(file_path, engine='openpyxl')

# Tải dữ liệu và lưu vào cache
df_4star = load_data_excel('4star_hotels.xlsx')
df_5star = load_data_excel('5star_hotels.xlsx')

# Trang Home - Tạo biểu đồ động theo yêu cầu người dùng
if choice == "Home":
    st.header("Dynamic Chart Generator")
    # Chọn file trong phần nội dung
    file_choice = st.selectbox("Chọn file dữ liệu để phân tích", ["4star_hotels.xlsx", "5star_hotels.xlsx"])
    
    # Đọc dữ liệu dựa trên lựa chọn
    if file_choice == "4star_hotels.xlsx":
        file_path = '4star_hotels.xlsx'
    else:
        file_path = '5star_hotels.xlsx'

    data = load_data_excel(file_path)
    data['published_at_date'] = pd.to_datetime(data['published_at_date'], errors='coerce')

    # Hiển thị dữ liệu mẫu
    display_data(data)

    st.subheader("Create Custom Chart")
    user_input = st.text_area("Enter your chart request:")
    # Lấy tên cột
    columns = data.columns

    # Khởi tạo OpenAIAssistant với chỉ dẫn đặc biệt
    init_instruction = "You are an experienced programmer, especially in data analysis and visualization using Pyplot."
    assistant = OpenAIAssistant(model_name="gpt-4o", init_instruction=init_instruction)
    assistant_msg = "Analyse the user's request, choose the best chart type, and generate Python code to plot the chart. Also provide a short comment explaining the chart."
    assistant.add_message('assistant', assistant_msg)

    if st.button("Generate Chart"):
        if user_input:
            # Tạo lời nhắc (prompt) cho API OpenAI
            prompt = f'''
            Create a Python code to plot a chart using Pyplot for the following request: "{user_input}". Given data columns: {columns}. 
            The data is stored in a DataFrame named "data".

            In addition to generating the chart, provide a detailed analysis of the data with specific insights such as:
            - Key trends in the data.
            - Notable peaks or drops and their implications.
            - Comparisons between relevant groups (e.g., months or hotel types).
            - Recommendations based on the chart.

            Include these insights in the "comment" variable. Comments must be in Vietnamese and must be comprehensive.
            '''
            try:
                # Nhận phản hồi từ OpenAI
                response = assistant.answer(prompt)
                code = response.split('```python')[1].split('```')[0].strip()  # Trích xuất mã từ phản hồi

                # Thực thi mã và hiển thị biểu đồ và nhận xét
                execute_code(code, data)
            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi thực thi mã: {e}")
        else:
            st.warning("Vui lòng nhập yêu cầu.")

# Trang Phân tích đánh giá - Hiển thị các biểu đồ tĩnh
elif choice == "1.Phân Tích Đánh Giá và Số Lượng Đánh Giá":
    st.header("Phân Tích Đánh Giá và Số Lượng Đánh Giá")
    # Hiển thị các biểu đồ tĩnh
    average_rating_by_city_chart(df_4star, df_5star)
    rating_distribution_histogram(df_4star, df_5star)
    review_count_over_time_chart(df_4star, df_5star)

# Trang So Sánh Đánh Giá Giữa Khách Sạn 4 Sao và 5 Sao 
elif choice == "2.So Sánh Đánh Giá Giữa Khách Sạn 4 Sao và 5 Sao":
    st.header("So Sánh Đánh Giá Giữa Khách Sạn 4 Sao và 5 Sao")
    # Hiển thị các biểu đồ tĩnh
    sentiment_divergence_chart(df_4star, df_5star)
    response_interaction_chart(df_4star, df_5star)

# Trang Phân Tích Nội Dung và Phản Hồi Từ Chủ Khách Sạn
elif choice == "3.Phân Tích Nội Dung và Phản Hồi Từ Chủ Khách Sạn":
    st.header("Phân Tích Nội Dung và Phản Hồi Từ Chủ Khách Sạn")
    # Hiển thị các biểu đồ tĩnh
    owner_response_rate_chart(df_4star, df_5star)
    response_time_scatter_chart(df_4star, df_5star)

# Trang Tương Tác của Người Đánh Giá
elif choice == "4.Tương Tác của Người Đánh Giá":
    st.header("Tương Tác của Người Đánh Giá")
    # Hiển thị các biểu đồ tĩnh
    local_guide_review_rate_chart(df_4star, df_5star)
    review_likes_distribution_chart(df_4star, df_5star)

# Trang So Sánh Các Khía Cạnh Khu Vực Địa Lý
elif choice == "5.So Sánh Các Khía Cạnh Khu Vực Địa Lý":
    st.header("So Sánh Các Khía Cạnh Khu Vực Địa Lý")
    # Hiển thị các biểu đồ tĩnh
    average_rating_by_region_chart(df_4star, df_5star)
    review_count_by_city_heatmap(df_4star, df_5star)

# Trang Xu Hướng và Thay Đổi Theo Thời Gian
elif choice == "6.Xu Hướng và Thay Đổi Theo Thời Gian":
    st.header("Xu Hướng và Thay Đổi Theo Thời Gian")
    # Hiển thị các biểu đồ tĩnh
    review_trend_over_time_chart(df_4star, df_5star)
    area_chart_positive_negative_reviews(df_4star, df_5star)

#  Phân Tích Mối Quan Hệ Giữa Các Biến
elif choice == "7.Test":
    st.header("Phân Tích Mối Quan Hệ Giữa Các Biến")
    # Hiển thị các biểu đồ tĩnh  
    