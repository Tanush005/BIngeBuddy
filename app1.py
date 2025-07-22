

import streamlit as st
import pickle
import pandas as pd
import google.generativeai as genai
from thefuzz import process
import json

st.set_page_config(
    page_title="BingeBuddy",
    page_icon="🎬",
    layout="centered"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

        /* --- General Body --- */
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
        }

        /* --- Animated Background Container --- */
        .background-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            overflow: hidden;
        }

        .background-collage {
            display: flex;
            flex-wrap: wrap;
            opacity: 0.5; /* MORE VISIBLE: Increased opacity */
            filter: grayscale(0.2) brightness(0.8); /* MORE VISIBLE: Less grayscale, more brightness */
            animation: scrollCollage 120s linear infinite;
        }

        .background-collage img {
            width: 25%; /* 4 images per row */
            height: auto;
            object-fit: cover;
        }

        @keyframes scrollCollage {
            from { transform: translateY(0); }
            to { transform: translateY(-50%); }
        }

        /* --- Main App Container --- */
        [data-testid="stAppViewContainer"] {
            background-color: rgba(0, 0, 0, 0.4); /* MORE VISIBLE: Lighter dark overlay */
            backdrop-filter: blur(5px);
        }

        /* --- Main Content Area Styling --- */
        .main-container {
            padding: 2rem 1.5rem;
        }

        /* --- Header & Subheader --- */
        .header {
            font-size: 3.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5rem;
            background: -webkit-linear-gradient(45deg, #A855F7, #F472B6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding-bottom: 0.5rem;
        }
        .subheader {
            text-align: center;
            color: #A1A1AA;
            margin-bottom: 3rem;
            font-weight: 400;
        }

        /* --- Chat Interface Styling --- */
        .stChatMessage {
            background-color: rgba(15, 15, 25, 0.7);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            padding: 1rem 1.25rem;
            margin: 0.75rem 0;
            animation: fadeIn 0.5s ease-in-out;
        }

        /* --- Recommendation Card Styling --- */
        .movie-card {
            background: rgba(25, 25, 40, 0.8);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: slideInUp 0.6s ease-out;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .movie-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        }
        .movie-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
        }
        .movie-vibe {
            font-style: italic;
            color: #F472B6;
            margin-bottom: 1rem;
        }
        .movie-overview {
            font-weight: 400;
            color: #A1A1AA;
            line-height: 1.6;
        }

        /* --- Animations --- */
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideInUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

# --- HTML for the background collage ---
# This is injected into the app to create the animated background.
background_html = """
<div class="background-container">
    <div class="background-collage">
        <img src="https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"> <!-- The Dark Knight -->
        <img src="https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg"> <!-- Pulp Fiction -->
        <img src="https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlPgr4aRG.jpg"> <!-- Blade Runner 2049 -->
        <img src="https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdU4SSTNFb8.jpg"> <!-- The Matrix -->
        <img src="https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg"> <!-- Forrest Gump -->
        <img src="https://image.tmdb.org/t/p/w500/kDQdFsGc63B7y8hG3s3UaVbV2K2.jpg"> <!-- The Shawshank Redemption -->
        <img src="https://image.tmdb.org/t/p/w500/90ez6ArZppIn2z1z86Eu5XgBwB.jpg"> <!-- Inception -->
        <img src="https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg"> <!-- Fight Club -->
        <img src="https://image.tmdb.org/t/p/w500/interstellarmovie.jpg"> <!-- Interstellar -->
        <img src="https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg"> <!-- Joker -->
        <img src="https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"> <!-- Parasite -->
        <img src="https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"> <!-- The Godfather -->
    </div>
</div>
"""
st.markdown(background_html, unsafe_allow_html=True)


# --- 3. Secure API & Data Loading (Unchanged) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except (KeyError, AttributeError):
    st.error("🚨 Gemini API Key not found! Please add it to your Streamlit secrets.", icon="🛑")
    st.info("Create a file at `.streamlit/secrets.toml` and add the line: `GEMINI_API_KEY = 'YOUR_KEY'`")
    st.stop()


@st.cache_data
def load_data():
    try:
        list_df = pd.read_pickle('movies.pkl')
        details_df = pd.read_pickle('movie1.pkl')
        similarity_matrix = pickle.load(open('similarity.pkl', 'rb'))
        if 'overview' not in details_df.columns:
            st.error("❌ Your 'movie1.pkl' file is missing the 'overview' column.")
            st.stop()
        return list_df, details_df, similarity_matrix
    except FileNotFoundError as e:
        st.error(f"❌ Data file not found: {e}. Please ensure 'movies.pkl', 'movie1.pkl', and 'similarity.pkl' are present.")
        st.stop()


movies_list_df, movies_details_df, similarity = load_data()


# --- 4. OPTIMIZED Core Functions for Speed (Unchanged) ---

@st.cache_data
def find_movie_from_query(query: str, titles: tuple) -> str:
    top_candidates = process.extract(query, titles, limit=3)
    candidate_titles = [title for title, score in top_candidates if score > 50]
    if not candidate_titles: return "No match found"
    if len(candidate_titles) == 1: return candidate_titles[0]

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    A user searched for a movie with the query: "{query}".
    From these candidates: {', '.join(candidate_titles)}, which is the most likely intended movie?
    Return only the single, best-matching movie title.
    """
    try:
        response = model.generate_content(prompt)
        best_match = response.text.strip()
        return best_match if best_match in candidate_titles else candidate_titles[0]
    except Exception:
        return candidate_titles[0]


@st.cache_data
def get_ai_vibes_for_movies(titles: list) -> dict:
    movie_list_str = "\n".join([f"- {title}" for title in titles])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    For each movie in the following list, generate a single, catchy, and intriguing sentence that describes its 'vibe'.

    Movie List:
    {movie_list_str}

    Return your response as a valid JSON object where the keys are the exact movie titles and the values are the vibe sentences. Example:
    {{
      "Inception": "A mind-bending thriller where dreams are the new heist.",
      "The Matrix": "A cyberpunk reality check that will make you question everything."
    }}
    """
    try:
        response = model.generate_content(prompt)
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        vibes_dict = json.loads(json_response)
        return vibes_dict
    except Exception:
        return {title: "A cinematic experience." for title in titles}


def get_recommendations(movie_title: str):
    try:
        idx = movies_list_df[movies_list_df['title'] == movie_title].index[0]
        sim_scores = sorted(list(enumerate(similarity[idx])), key=lambda x: x[1], reverse=True)[1:6]
        movie_indices = [i[0] for i in sim_scores]
        return movies_details_df.iloc[movie_indices]
    except IndexError:
        return pd.DataFrame()


# --- 5. Main App UI (Unchanged) ---
st.markdown("<div class='main-container'>", unsafe_allow_html=True)

st.markdown("<h1 class='header'>BingeBuddy</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Your AI-powered guide to the world of cinema.</p>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "What movie is on your mind today?"}]
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Suggest movies like 'The Dark Knight'..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("✨ The AI is casting its spell..."):
            all_titles = tuple(movies_list_df['title'].tolist())
            seed_movie = find_movie_from_query(prompt, all_titles)

            if seed_movie == "No match found":
                response_content = "I couldn't find that exact movie in my database. Could you try another title?"
                st.error(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})
            else:
                recommendations = get_recommendations(seed_movie)
                recommended_titles = recommendations['title'].tolist()

                ai_vibes = get_ai_vibes_for_movies(recommended_titles)

                response_header = f"Excellent choice! Since you liked **{seed_movie}**, you might also enjoy these:"
                st.markdown(response_header)

                recommendations_html = ""
                for index, movie in recommendations.iterrows():
                    title = movie['title']
                    overview_text = movie.get('overview', 'Overview not available.')
                    ai_vibe = ai_vibes.get(title, "A cinematic experience.")

                    recommendations_html += f"""
                        <div class="movie-card">
                            <p class="movie-title">{title}</p>
                            <p class="movie-vibe">✨ Vibe: {ai_vibe}</p>
                            <p class="movie-overview">{overview_text}</p>
                        </div>
                    """

                st.markdown(recommendations_html, unsafe_allow_html=True)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_header + recommendations_html})

st.markdown("</div>", unsafe_allow_html=True)
