# CÁC THƯ VIỆN CẦN THIẾTTHIẾT
import pyodbc
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from collections import Counter
import math 
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# HÀM KẾT NỐI VỚI SQL DATABASE 
def get_connection():
    try:
        connection = pyodbc.connect(
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=LAPTOP-HFTOHS8V;"
            "Database=Spotify_Group11;"
            "UID=sa;"
            "PWD=130624;"
        )
        return connection
    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server: {e}")
        return None

# HÀM TRÍCH XUẤT DỮ LIỆU TỪ CÁC BẢNG 
def fetch_table(table_name):
    connection = get_connection()
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql(query, connection)
    connection.close()
    return data

# HÀM THỰC HIỆN TRUY VẤN SQL VÀ TRẢ VỀ KẾT QUẢ DƯỚI BẢNG DATAFRAME 
def fetch_query(query):
    connection = get_connection()
    data = pd.read_sql(query, connection)
    connection.close()
    return data

# CÁC BẢNG CẦN TRÍCH XUẤT 
table_names = [
    "[dbo].[Artists]",
    "[dbo].[Playlists]",
    "[dbo].[Tracks]",
    "[dbo].[Audio_features]",
    "[dbo].[ArtistData]"
]

# THỰC HIỆN TRÍCH XUẤT DỮ LIỆU TỪ CÁC BẢNG TRÊN 
dataframes = {}
for table_name in table_names:
    dataframes[table_name] = fetch_table(table_name)
    print(f"Data from {table_name} extracted successfully!")
    
st.set_page_config(page_title="Rubric6_Group11", page_icon="🎶", layout="wide")

# CSS để đổi màu nền
st.markdown(
    """
    <style>
        /* Thay đổi màu nền chính */
        .stApp {
            background-color: #000000; /* Nền đen */
            color: white; /* Chữ trắng */
        }
        
        /* Tùy chỉnh thêm vùng widget hoặc text */
        .css-18e3th9, .css-1d391kg {
            background-color: #1E1E1E; /* Xám đậm cho vùng phụ */
            color: white;
        }

        /* Tiêu đề chính */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #1DB954; /* Màu xanh Spotify */
        }
    </style>
    """,
    unsafe_allow_html=True
)
# TIÊU ĐỀ DASHBOARD
# Hiển thị tiêu đề
st.markdown(
    "<h1 style='color: #00ff00;text-align: center; font-size: 100px;'>SPOTIFY ANALYSIS</h1>",
    unsafe_allow_html=True
)
# Hiển thị ảnh
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://static.feber.se/article_images/39/97/72/399772_1280.jpg" 
             style="width: 100%; height: auto;">
    </div>
    """,
    unsafe_allow_html=True
)

#--------- OVERVIEW ------------
st.markdown(
    "<h1 style=' color: #00FF00;font-size: 60px;'>OVERVIEW</h1>",
    unsafe_allow_html=True
)

# Lấy dữ liệu từ DataFrame
total_songs = len(dataframes["[dbo].[Tracks]"])
total_artists = len(dataframes["[dbo].[Artists]"])
total_playlists = len(dataframes["[dbo].[Playlists]"])
total_albums = len(dataframes["[dbo].[Tracks]"]["album_id"].unique())
average_duration = dataframes["[dbo].[Tracks]"]["duration_minutes"].mean()
average_tracks_per_playlist = math.ceil(dataframes["[dbo].[Playlists]"]["num_tracks"].mean())

# Chia thành 2 hàng với 3 ô mỗi hàng
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div style='; color: white;'>
            <strong style='font-size: 25px;'>🎵 Sum Of Track</strong>
            <h2 style='color: #00FF00;font-size: 48px;'><strong>{total_songs}</strong><h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='; color: white;'>
            <strong style='font-size: 25px;'>👨‍🎤 Sum Of Artist</strong>
            <h2 style='color: #00FF00;font-size: 48px;'><strong>{total_artists}</strong><h2>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style='; color: white;'>
            <strong style='font-size: 25px;'>📜 Sum Of Playlist</strong>
            <h2 style='color: #00FF00;font-size: 48px;'><strong>{total_playlists}</strong><h2>
        </div>
    """, unsafe_allow_html=True)
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(f"""
        <div style='; color: white;'>
            <strong style='font-size: 25px;'>💽 Sum Of Album</strong>
            <h2 style='color: #00FF00;font-size: 48px;'><strong>{total_albums}</strong><h2>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div style=' color: white;'>
            <strong style='font-size: 25px;'>⏱️ Average Duration</strong>
            <h2 style='color: #00FF00;font-size: 48px;'><strong>{average_duration:.2f}</strong><h2>
        </div>
    """, unsafe_allow_html=True)
with col6:
    st.markdown(f"""
        <div style=' color: white;'>
            <strong style='font-size: 25px;'>🎧 Track/Playlist</strong>
            <h2 style='color: #00FF00;font-size: 48px;'><strong>{int(average_tracks_per_playlist)}</strong><h2>
        </div>
    """, unsafe_allow_html=True)
    
#---------- ARTISTS --------------
st.markdown(
    "<h1 style=' color: #00FF00;font-size: 60px;'>ARTIST</h1>",
    unsafe_allow_html=True
)
# Query: Số lượng nghệ sĩ theo mức độ phổ biến
popularity_rank_query = """
SELECT popularity, COUNT(*) AS ArtistCount
FROM [dbo].[Artists]
GROUP BY popularity
ORDER BY popularity DESC;
"""
popularity_rank = fetch_query(popularity_rank_query)
# Query: 10 nghệ sĩ nổi tiếng nhất
top_artists_query = """
    SELECT TOP 10 name, popularity
    FROM [dbo].[Artists]
    ORDER BY popularity DESC
"""
top_artists = fetch_query(top_artists_query)
# Vẽ cặp biểu đồ
# Chia layout thành 2 cột
col1, col2 = st.columns(2)

# Biểu đồ 1: Số Lượng Nghệ Sĩ Theo Mức Độ Phổ Biến
with col1:
    # Biểu đồ núi
    fig_popularity = px.area(
        popularity_rank,
        x="popularity",
        y="ArtistCount",
        title="Số Lượng Nghệ Sĩ Theo Mức Độ Phổ Biến",
        labels={"popularity": "Popularity", "ArtistCount": "Artist_Count"},
    )
    # Cập nhật màu nền và bố cục
    fig_popularity.update_traces(line_color="#00FF00", fillcolor="rgba(0, 255, 0, 0.2)")  # Đường màu xanh lá, nền trong suốt xanh lá
    fig_popularity.update_layout(
        title=dict(x=0.5, xanchor="center", font=dict(size=20 , color='#00FF00')),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="white"),
        xaxis=dict(title="Popularity"),
        yaxis=dict(title="Artist Count")
    )
    # Hiển thị biểu đồ
    st.plotly_chart(fig_popularity)

# Biểu đồ 2: Top 10 Nghệ Sĩ Nổi Tiếng Nhất    
with col2:
    # Biểu đồ núi
    fig_artists = px.area(
        top_artists,
        x="name",
        y="popularity",
        title="Top 10 Nghệ Sĩ Nổi Tiếng Nhất",
        labels={"name": "Artist", "popularity": "Popularity"},
    )
    # Cập nhật màu đường và nền của biểu đồ núi
    fig_artists.update_traces(line_color="#00FF00", fillcolor="rgba(0, 255, 0, 0.2)")  # Đường màu xanh lá, nền trong suốt xanh lá
    fig_artists.update_layout(
        title=dict(x=0.5, xanchor="center", font=dict(size=20, color='#00FF00')),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="white"),
        xaxis=dict(tickangle=-45, title="Artist"),
        yaxis=dict(title="Popularity")
    )
    st.plotly_chart(fig_artists)
# Hiển thị tiêu đề
st.markdown(
    "<h1 style='color: #00ff00;text-align: center; font-size: 50px;'>TOP 10 NGHỆ SĨ NỔI TIẾNG NHẤT</h1>",
    unsafe_allow_html=True
)
# Chèn ảnh của nghệ sĩ trong TOP 10 
images = [
    "C:/Users/ADMIN/Downloads/Bad_Bunny_2019_by_Glenn_Francis.jpg",
    "C:/Users/ADMIN/Downloads/Ariana Grande.jpg",
    "C:/Users/ADMIN/Downloads/Taylor_Swift.webp",
    "C:/Users/ADMIN/Downloads/Drake.jpg",
    "C:/Users/ADMIN/Downloads/juice wrld.jpg",
    "C:/Users/ADMIN/Downloads/BTS.jpg",
    "C:/Users/ADMIN/Downloads/Justin Bieber.jpg",
    "C:/Users/ADMIN/Downloads/J Balvin.jpg",
    "C:/Users/ADMIN/Downloads/Eminem1.jpg",
    "C:/Users/ADMIN/Downloads/The Weeknd.jpg"
]
# Danh sách tên nghệ sĩ tương ứng với các ảnh
artists = [
    "Bad Bunny",
    "Ariana Grande",
    "Taylor Swift",
    "Drake",
    "Juice Wrld",
    "BTS",
    "Justin Bieber",
    "J Balvin",
    "Eminem",
    "The Weeknd"
]
# Danh sách Spotify Embed links - 
spotify_links = [
    "https://open.spotify.com/embed/track/0fea68AdmYNygeTGI4RC18",  # Bad Bunny 
    "https://open.spotify.com/embed/track/0lizgQ7Qw35od7CYaoMBZb",  # Ariana Grande
    "https://open.spotify.com/embed/track/1P17dC1amhFzptugyAO7Il",  # Taylor Swift
    "https://open.spotify.com/embed/track/1zi7xx7UVEFkmKfv06H8x0",  # Drake 
    "https://open.spotify.com/embed/track/6j5BK1cFX9TjJd5EXHGgAn",  # Juice Wrld 
    "https://open.spotify.com/embed/track/5QDLhrAOJJdNAmCTJ8xMyW",  # BTS 
    "https://open.spotify.com/embed/track/6epn3r7S14KUqlReYr77hA",  # Justin Bieber 
    "https://open.spotify.com/embed/track/3Ga6eKrUFf12ouh9Yw3v2D",  # J Balvin 
    "https://open.spotify.com/embed/track/6X2R9KeWi7sII0YRpgzg0j",  # Eminem
    "https://open.spotify.com/embed/track/4MPTj8lMMvxLwT3EwuXFop"   # The Weeknd 
]
#  Số ảnh mỗi hàng
columns_per_row = 5
          
# Hiển thị từng nghệ sĩ và nhạc
columns_per_row = 5  # Số cột mỗi hàng
rows = [images[i:i + columns_per_row] for i in range(0, len(images), columns_per_row)]
artist_rows = [artists[i:i + columns_per_row] for i in range(0, len(artists), columns_per_row)]
spotify_rows = [spotify_links[i:i + columns_per_row] for i in range(0, len(spotify_links), columns_per_row)]
# Kích thước cố định cho ảnh
image_width = 300
image_height = 300
# Hiển thị trong Streamlit
for img_row, artist_row, spotify_row in zip(rows, artist_rows, spotify_rows):
    cols = st.columns(columns_per_row)
    for col, img, artist, spotify_link in zip(cols, img_row, artist_row, spotify_row):
        with col:
            # Hiển thị ảnh
            st.image(img, width=image_width, use_container_width=True)
            # Nhúng Spotify player
            st.markdown(f"""
                <iframe src="{spotify_link}" 
                        width="100%" 
                        height="80" 
                        frameborder="0" 
                        allowtransparency="true" 
                        allow="encrypted-media">
                </iframe>
            """, unsafe_allow_html=True)
# Query SQL: Top 10 nghệ sĩ có lượng người theo dõi cao nhất
top_followed_artists_query = """
SELECT TOP 10 name, num_followers
FROM [dbo].[Artists]
ORDER BY num_followers DESC;
"""
top_followed_artists = fetch_query(top_followed_artists_query)
# Query SQL: Top 10 nghệ sĩ có lượng người nghe hàng tháng cao nhất
top_monthly_listeners_query = """
 SELECT top 10 ad.ArtistID, ad.ArtistName, a.monthly_listeners
    FROM [dbo].[ArtistData] ad
    JOIN [dbo].[Artists] a ON ad.ArtistID = a.id
    ORDER BY a.monthly_listeners DESC;
"""
top_monthly_listeners = fetch_query(top_monthly_listeners_query)
# Vẽ cặp biểu đồ
# Chia layout thành 2 cột
col1, col2 = st.columns(2)
# Biểu đồ 1: Top 10 nghệ sĩ có lượng người theo dõi cao nhất   
with col1:
    fig_top_followed_artists = px.line(
        top_followed_artists,
        x="name",
        y="num_followers",
        title="Top 10 nghệ sĩ có lượng người theo dõi cao nhất",
        labels={"name": "Artist", "num_followers": "Num_Followers"},
        markers=True  # Hiển thị marker trên các điểm
    )
    fig_top_followed_artists.update_traces(line_color="#00FF00")
    fig_top_followed_artists.update_layout(
        title=dict(x=0.5, xanchor="center", font=dict(size=20, color='#00FF00')),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="white"),
        xaxis=dict(title="Artist"),
        yaxis=dict(title="Number of Followers")
    )
    st.plotly_chart(fig_top_followed_artists)
    
# Biểu đồ 2: Top 10 nghệ sĩ có lượng người nghe hàng tháng cao nhất    
with col2:
    fig_top_monthly_listeners = px.line(
        top_monthly_listeners,
        x="ArtistName",
        y="monthly_listeners",
        title="Top 10 nghệ sĩ có lượng người nghe hàng tháng cao nhất",
        labels={"ArtistName": "Artist", "monthly_listeners": "Monthly_Listeners"},
        markers=True  # Hiển thị marker trên các điểm
    )
    fig_top_monthly_listeners.update_traces(line_color="#00FF00")  
    fig_top_monthly_listeners.update_layout(
        title=dict(x=0.5, xanchor="center", font=dict(size=20, color='#00FF00')),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="white"),
        xaxis=dict( title="Artist"),
        yaxis=dict(title="Monthly Listeners")
    )
    st.plotly_chart(fig_top_monthly_listeners)

#------------- GENRES ----------------
st.markdown(
    "<h1 style=' color: #00FF00;font-size: 60px;'>GENRE</h1>",
    unsafe_allow_html=True
)
# Hiển thị ảnh
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://cdn.statically.io/img/audiocaptain.com/f=auto/wp-content/uploads/2021/10/Most-Popular-Music-Genres.jpg" 
             style="width: 100%; height: auto;">
    </div>
    """,
    unsafe_allow_html=True
)
# TOP 10 THỂ LOẠI CÓ NHIỀU NGHỆ SĨ HÁT NHẤT
# Truy vấn dữ liệu từ bảng Artists
top_genre_query = ("""
    SELECT genres
    FROM Artists
""")
top_genre = fetch_query(top_genre_query)

# Tách chuỗi thể loại nhạc và loại bỏ giá trị NULL hoặc trống
all_genres = []
for genres in top_genre['genres']:
    if genres:  # Kiểm tra nếu genres không phải NULL hoặc trống
        genre_list = genres.split(',')
        all_genres.extend([genre.strip() for genre in genre_list])
        
# Đếm số lượng nghệ sĩ cho mỗi thể loại nhạc
genre_counts = Counter(all_genres)
# Lấy 10 thể loại nhạc phổ biến nhất
top_10_genres = genre_counts.most_common(10)
# Chuyển dữ liệu thành DataFrame
top_10_genres_df = pd.DataFrame(top_10_genres, columns=['Genre', 'Num_Artists'])
# Sắp xếp dữ liệu theo số lượng nghệ sĩ giảm dần
top_10_genres_df = top_10_genres_df.sort_values(by='Num_Artists', ascending=False)

# Tạo biểu đồ núi (area chart)
fig = px.area(top_10_genres_df, x='Genre', y='Num_Artists', title='Top 10 Genres with the Most Artists')
# Cập nhật màu sắc và layout
fig.update_traces(line_color='#00FF00', fillcolor='rgba(0, 255, 0, 0.5)')
fig.update_layout(
    plot_bgcolor='#000000',
    paper_bgcolor='#000000',
    height=800,
    font=dict(color='#00FF00'),
    title=dict(x=0.5, xanchor='center', font=dict(size=20, color='#00FF00')),
    xaxis=dict(title='Genre', tickmode='array', tickangle=45),
    yaxis=dict(title='Number of Artists'),
    showlegend=False
)
# Hiển thị biểu đồ trong Streamlit
st.plotly_chart(fig)

#-------------- PLAYLIST ---------------
st.markdown(
    "<h1 style=' color: #00FF00;font-size: 60px;'>PLAYLIST</h1>",
    unsafe_allow_html=True
)
# Hiển thị ảnh
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://www.thakzhan.de/content/images/2022/05/Titelbild_Spotify_Genres.png" 
             style="width: 100%; height: auto;">
    </div>
    """,
    unsafe_allow_html=True
)
#Biểu đồ: Top 50 playlist có số lượng người theo dõi cao nhất
# Query SQL
top_playlists_query = """
SELECT TOP 50 playlist_name, num_followers
FROM [dbo].[Playlists]
ORDER BY num_followers DESC;
"""
top_playlists = fetch_query(top_playlists_query)
# Vẽ biểu đồ 
fig_top_playlists = px.area(
    top_playlists,
    x="playlist_name",
    y="num_followers",
    title="Top 50 playlist có số lượng người theo dõi cao nhất",
    labels={"playlist_name": "Playlist", "num_followers": "Num_Followers"},
)

fig_top_playlists.update_traces(line_color="#00FF00", fillcolor="rgba(0, 255, 0, 0.2)")  # Đường màu xanh lá, nền trong suốt xanh lá

fig_top_playlists.update_layout(
    title=dict(x=0.5, xanchor="center", font=dict(size=20, color='#00FF00')),
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    height=800, 
    font=dict(color="white"),
    xaxis=dict(tickangle=-45)
)
# Hiển thị biểu đồ 
st.plotly_chart(fig_top_playlists)


# ----------------- AUDIO_FEATURE ---------------- 
st.markdown(
    "<h1 style=' color: #00FF00;font-size: 60px;'>AUDIO_FEATURE </h1>",
    unsafe_allow_html=True
)
# TOP 10 BÀI HÁT PHỔ BIẾN NHẤT THEO AUDIO_FEATURES
# Lấy dữ liệu mức độ phổ biến
track_popularity_query = ("""
   SELECT TOP 10 T.track_name, A.popularity
FROM [dbo].[Tracks] as T
JOIN Audio_features as A ON T.track_id = A.id
ORDER BY A.popularity DESC
""")
track_popularity = fetch_query(track_popularity_query)
# Vẽ biểu đồ biến động
fig = px.line(
    track_popularity,
    x="track_name",
    y="popularity",
    title="Top 10 Bài Hát Theo Mức Độ Phổ Biến",
    labels={"track_name": "Track Name", "popularity": "Popularity"}
)

# Tùy chỉnh biểu đồ
fig.update_traces(line_color="#00FF00", marker=dict(color='green'))  
fig.update_layout(
    title=dict(x=0.5, xanchor="center", font=dict(size=20, color='#00FF00')),
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    font=dict(color="white"),
    xaxis=dict(title="Track Name", tickangle=-45),
    yaxis=dict(title="Popularity"),
    height=800,  # Đặt chiều cao 
    width=1600 
)

# Hiển thị biểu đồ trong ứng dụng Streamlit
st.plotly_chart(fig)

#GIÁ TRỊ TRUNG BÌNH CỦA AUDIO_FEATURE
# Truy vấn dữ liệu từ bảng audio_feature
Average_Feature_query = ("""
SELECT 
    danceability, 
    energy, 
    speechiness, 
    acousticness, 
    instrumentalness, 
    liveness, 
    valence
FROM Audio_Features
""")
Average_Feature = fetch_query(Average_Feature_query)
# Tính trung bình giá trị của mỗi đặc trưng (column)
audio_means = Average_Feature.mean()
# Chuyển đổi trung bình thành DataFrame để vẽ biểu đồ radar
audio_means_df = pd.DataFrame(audio_means).reset_index()
audio_means_df.columns = ['Feature', 'Average Value']
# Vẽ biểu đồ radar
fig = px.line_polar(
    audio_means_df, 
    r='Average Value', 
    theta='Feature', 
    line_close=True,  # Đóng vòng tròn
    title="Average Audio Feature", 
    labels={'Average Value': 'Average Value', 'Feature': 'Feature'}
)
# Cập nhật màu sắc
fig.update_traces(
    line_color="#00FF00",  # Màu xanh lá
    fillcolor="rgba(0, 255, 0, 0.3)"  # Màu nền trong suốt màu xanh lá
)
# Cập nhật layout
fig.update_layout(
    polar=dict(
        bgcolor="#000000",  # Đặt nền cho phần biểu đồ radar
        radialaxis=dict(
            visible=True,
            range=[0, 1],  # Phạm vi từ 0 đến 1 cho các giá trị từ 0% đến 100%
            tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1],  # Các giá trị đánh dấu trục
            ticktext=["0%", "20%", "40%", "60%", "80%", "100%"],  # Hiển thị các giá trị phần trăm
            showticklabels=True,  # Hiển thị nhãn trên trục
            tickfont=dict(color="#00FF00"),  # Màu chữ xanh lá cho các nhãn
            gridcolor="lightgray",  # Màu xám sáng cho các đường kẻ
            linecolor="lightgray"  # Màu xám sáng cho các đường trục
        ),
        angularaxis=dict(
            tickfont=dict(color="#00FF00"),  # Màu chữ xanh lá cho các nhãn góc
            gridcolor="lightgray",  # Màu xám sáng cho các đường kẻ
            linecolor="lightgray"  # Màu xám sáng cho các đường trục
        ) 
    ),       
    title=dict(x=0.5, xanchor="center", font=dict(size=20, color='#00FF00')),
    paper_bgcolor="#000000",  # Màu nền biểu đồ là đen
    plot_bgcolor="#000000",   # Màu nền của phần vẽ biểu đồ là đen
    font=dict(color="#00FF00"), # Màu chữ xanh 
    width=1400,  # Đặt chiều rộng của biểu đồ
    height=800  # Đặt chiều cao của biểu đồ
)
# Hiển thị biểu đồ trong Streamlit
st.plotly_chart(fig)

# Hiển thị Lời cảm ơn 
st.markdown(
    "<h1 style='color: #00ff00;text-align: center; font-size: 40px;'>Thank you for visiting our website. Have a nice day!🎤</h1>",
    unsafe_allow_html=True
)
## Câu lệnh xem streamlit: streamlit run Group11_St.py 





