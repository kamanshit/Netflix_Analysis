import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

# load the dataset
df=pd.read_csv("mymoviedb.csv", engine="python")

# Convert the release_data to datetime

df['Release_Date']=pd.to_datetime(df["Release_Date"], errors='coerce')

# Drop rows with missing import data

df.dropna(subset=['Title','Overview','Popularity','Vote_Count','Vote_Average', 'Original_Language', 'Genre'], inplace=True)

# conver the Vote count and averate to numeric

df['Vote_Count']=pd.to_numeric(df['Vote_Count'], errors='coerce')
df['Vote_Average']=pd.to_numeric(df['Vote_Average'], errors='coerce')

# Reset indexing
df.reset_index(drop=True, inplace=True)

# st.write(df.shape)
# st.dataframe(df.head())

st.sidebar.title("🎛️ Filter Options")

min_year = int(df['Release_Date'].dt.year.min())
max_year = int(df['Release_Date'].dt.year.max())
# 
selected_year = st.sidebar.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(2010, 2020))


unique_genres = sorted(df['Genre'].dropna().unique())
# Split comma-separated genres and get unique genres
all_genres = df['Genre'].dropna().str.split(',')  # Split by comma
flat_genres = [genre.strip() for sublist in all_genres for genre in sublist]  # Flatten and strip spaces
unique_genres = sorted(set(flat_genres))  # Get unique genres

selected_genres= st.sidebar.multiselect("Select Genre(s)", unique_genres, default=unique_genres)

unique_langs = sorted(df['Original_Language'].dropna().unique())
# selected_langs= st.sidebar.multiselect("Select Language(s)", unique_langs, default=unique_langs)

filtered_df = df[
    (df['Release_Date'].dt.year >= selected_year[0]) & 
    (df['Release_Date'].dt.year <= selected_year[1]) &

    (df['Genre'].isin(selected_genres))
    # (df['Original_Language'].isin(selected_langs))
]
filtered_df = filtered_df.copy()
filtered_df['Year'] = filtered_df['Release_Date'].dt.year

st.title("🎬 Netflix Movies Dashboard")
st.write("This dashboard lets you explore Netflix movie data with filters and visualizations.")

st.write(f"🔎 Showing {len(filtered_df)} movies based on filters")
st.dataframe(filtered_df[['Title', 'Genre', 'Release_Date', 'Vote_Average', 'Popularity']])

# Adding charts


st.markdown("## 🎭 Top Genres Count")

genre_counts = df['Genre'].value_counts().reset_index()
genre_counts.columns = ['Genre', 'Count']
genre_counts = genre_counts.head(15)  # show only top 15 genres

fig = px.bar(
    genre_counts,
    x='Genre',
    y='Count',
    color='Genre',
    text='Count',
    title='Number of movies per genre',
    height=600,
    width=1000
)

fig.update_layout(
    xaxis_tickangle=-45,
    showlegend=False,
    plot_bgcolor='#0e1117',
    paper_bgcolor='#0e1117',
    font=dict(color='white')
)

st.plotly_chart(fig, use_container_width=True)


st.markdown("## ⭐ Top Rated Movies")

top_rated = filtered_df.sort_values(by="Vote_Average", ascending=False).head(10)

fig2 = px.bar(
    top_rated,
    x='Title',
    y='Vote_Average',
    color='Vote_Average',
    text='Vote_Average',
    title='Top 10 Highest Rated Movies',
    height=600
)

fig2.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor='#0e1117',
    paper_bgcolor='#0e1117',
    font=dict(color='white')
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("## 🔥 Most Popular Movies")

top_popular = filtered_df.sort_values(by="Popularity", ascending=False).head(10)

fig3 = px.bar(
    top_popular,
    x='Title',
    y='Popularity',
    color='Popularity',
    text='Popularity',
    title='Top 10 Most Popular Movies',
    height=600
)

fig3.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor='#0e1117',
    paper_bgcolor='#0e1117',
    font=dict(color='white')
)

st.plotly_chart(fig3, use_container_width=True)


st.markdown("## 🗓️ Average Rating Over the Years")

# Create a new column for year
filtered_df['Year'] = filtered_df['Release_Date'].dt.year

# Group by year and calculate average rating
yearly_avg = filtered_df.groupby('Year')['Vote_Average'].mean().reset_index()

fig5 = px.line(
    yearly_avg,
    x='Year',
    y='Vote_Average',
    markers=True,
    title='Average Movie Rating by Year'
)

fig5.update_traces(line_color='orange')
fig5.update_layout(
    xaxis_title='Year',
    yaxis_title='Average Rating',
    plot_bgcolor='#0e1117',
    paper_bgcolor='#0e1117',
    font=dict(color='white')
)

st.plotly_chart(fig5, use_container_width=True)


# Count genre occurrences in filtered_df
genre_counts = {}

for genres in filtered_df['Genre'].dropna():
    for genre in genres.split(','):
        genre = genre.strip()
        if genre in genre_counts:
            genre_counts[genre] += 1
        else:
            genre_counts[genre] = 1

# Convert to DataFrame
genre_count_df = pd.DataFrame({
    'Genre': list(genre_counts.keys()),
    'Count': list(genre_counts.values())
}).sort_values(by="Count", ascending=False)

st.subheader("🍕 Genre Distribution")
fig = px.pie(genre_count_df, names='Genre', values='Count',
             title='Distribution of Genres in Selected Movies',
             color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(fig, use_container_width=True)


top_movies = filtered_df[['Title', 'Vote_Average', 'Vote_Count']].dropna()
top_movies = top_movies[top_movies['Vote_Count'] > 10]  # Filter out low vote counts

top_movies = top_movies.sort_values(by='Vote_Average', ascending=False).head(10)


st.subheader("🎬 Top 10 Movies by Average Rating")

fig = px.bar(top_movies,
             x='Vote_Average',
             y='Title',
             orientation='h',
             title='Top 10 Highest Rated Movies',
             color='Vote_Average',
             color_continuous_scale='Bluered_r')

fig.update_layout(yaxis=dict(autorange="reversed"))  # Highest rating at top
st.plotly_chart(fig, use_container_width=True)



st.subheader("📊 Distribution of Movie Ratings")

fig = px.histogram(filtered_df,
                   x='Vote_Average',
                   nbins=20,
                   title='Distribution of Ratings',
                   color_discrete_sequence=['#636EFA'])

st.plotly_chart(fig, use_container_width=True)


st.subheader("📅 Movies Released per Year")

movies_per_year = filtered_df['Year'].value_counts().sort_index()

fig = px.line(x=movies_per_year.index, 
              y=movies_per_year.values,
              labels={'x': 'Year', 'y': 'Number of Movies'},
              title='Number of Movies Released Each Year')

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("#### ✅ Dashboard Complete")
st.write("You can now explore Netflix movies by filters, see top-rated movies, rating trends, and more!")
