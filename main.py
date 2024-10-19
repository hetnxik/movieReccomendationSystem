import pandas as pd
import streamlit as st
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@st.cache_data
def load_data():
    credits = pd.read_csv('tmdb_5000_credits.csv')
    movies = pd.read_csv('tmdb_5000_movies.csv')
    return credits, movies


credit_data, movies_data = load_data()
credit_data = credit_data.rename(columns={'movie_id': 'id'})
movies_data = pd.merge(movies_data, credit_data, on='id')

selected_features = ['genres', 'keywords', 'tagline', 'cast']

for feature in selected_features:
    movies_data[feature] = movies_data[feature].fillna('')

combined_features = (
        movies_data['genres'] + ' ' +
        movies_data['keywords'] + ' ' +
        movies_data['tagline'] + ' ' +
        movies_data['cast']
)

vectorizer = TfidfVectorizer()
feature_vectors = vectorizer.fit_transform(combined_features)
print("Feature vectors:", feature_vectors)

similarity = cosine_similarity(feature_vectors)

st.title("Movie Recommendation System")
movie_name = st.text_input("Enter the name of a movie you like:")

if st.button("Recommend Movies"):
    if movie_name:
        list_of_all_titles = movies_data['original_title'].tolist()

        find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)
        close_match = find_close_match[0] if find_close_match else None

        if not close_match:
            st.error("No close match found! Please try a different movie.")
        else:
            print(f"Closest match: {close_match}")

            index_of_the_movie = movies_data[movies_data.original_title == close_match]['id'].values[0]

            similarity_score = list(enumerate(similarity[index_of_the_movie]))

            sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

            st.subheader('Movies suggested for you:')
            i = 1
            for movie in sorted_similar_movies:
                index = movie[0]
                title_from_index = movies_data[movies_data.index == index]['original_title'].values[0]
                if i <= 5:
                    st.write(f"{i}. {title_from_index}")
                    i += 1

    else:
        st.warning("Enter a movie name.")
