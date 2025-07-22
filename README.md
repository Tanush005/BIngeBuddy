
#BingeBuddy  🎬✨
A smart, conversational movie recommendation system designed to solve the "endless scroll" problem on streaming platforms. Built with Python, Streamlit, and Google's Gemini API.

<p align="center">
<em>(Optional but highly recommended: Add a GIF of your app in action here. It dramatically increases engagement.)</em>
<br>
<img src="link_to_your_app_demo.gif" alt="BingeBuddy Demo" width="700"/>
</p>

🎯 The Problem
We've all been there: it's movie night, but you spend more time scrolling through endless, irrelevant recommendations than actually watching something. BingeBuddy was built to fix this. It replaces passive scrolling with an intelligent, conversational experience, helping users find the perfect movie quickly and enjoyably.

🚀 Key Engineering Features
This project demonstrates a full-stack approach to building an AI-powered application, with a focus on performance, user experience, and robust system design.

Conversational Interface (NLU):

Leverages Google's Gemini API to understand natural language queries, moving beyond simple keyword search.

Allows users to discover movies by describing plots, moods, or making comparisons (e.g., "a thriller like Se7en but with a sci-fi twist").

High-Precision Search Pipeline:

Engineered a two-stage search mechanism to ensure accuracy.

Stage 1 (Fuzzy Matching): Uses thefuzz to rapidly find close text matches from the database, correcting for typos.

Stage 2 (AI Disambiguation): The top candidates are passed to the Gemini API, which uses its contextual understanding to select the single most likely movie the user intended.

Performance-Optimized Recommendation Engine:

The core recommendation logic is powered by a Scikit-learn model using a TF-IDF vectorized similarity matrix.

Backend Optimization: The "AI Vibe" feature was identified as a potential latency bottleneck. I re-architected this process to use a single, batched API call for all recommendations on the screen, reducing the number of network requests from N to 1 and cutting perceived load times by over 80%.

Dynamic & Polished UI/UX:

The frontend was built with Streamlit and heavily customized with CSS to create a modern, professional aesthetic.

Features include a dynamic, animated background of movie posters and a "frosted glass" effect on UI elements to enhance visual appeal and readability.

🏛️ System Architecture
The application follows a modular architecture that separates concerns between the user interface, backend logic, and external API services.

graph TD
    A[User Interface (Streamlit)] --> B{Backend Logic (Python)};

    subgraph "Backend Processing"
        B --> C{1. Query Understanding};
        B --> D{2. Recommendation Generation};
        B --> E{3. Content Enrichment};
    end

    C --> F((Google Gemini API));
    D --> G[[ML Model (Scikit-learn/Pandas)]];
    E --> F;

    G --> B;
    F --> B;

    B --> A;

    style A fill:#2b3137,stroke:#fff,stroke-width:2px,color:#fff
    style F fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style G fill:#bbdefb,stroke:#1976d2,stroke-width:2px

🛠️ Tech Stack
Category

Technologies

Frontend

Streamlit, HTML/CSS

Backend & Data

Python, Pandas

Machine Learning

Scikit-learn (TF-IDF, Cosine Similarity)

Generative AI & NLP

Google Gemini API

Search & Utilities

TheFuzz

Large File Handling

Git LFS

🔮 Future Enhancements
Hybrid Recommendation Model: Integrate collaborative filtering (e.g., user ratings) to create a more powerful hybrid model.

User Authentication: Implement user accounts to store preferences, watch history, and provide even more personalized recommendations.

Scalable Deployment: Containerize the application with Docker and deploy it on a cloud platform like Google Cloud Run for scalability.

CI/CD Pipeline: Set up a GitHub Actions workflow to automate testing and deployment.
