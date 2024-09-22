International News 
Summarize and access information about international news happening around the world.

It enables AI-powered summarization of multiple news articles in real-time, providing users with the latest updates on global events using advanced natural language processing techniques.

1. Run with Docker (Preferred)
Create a .env file and an InternationalNews folder in the root directory of the project. Copy and paste the following configuration, replacing <Your Token> with your actual OpenAI API key:

HOST=0.0.0.0
PORT=8080
EMBEDDING_DIMENSION=768
EMBEDDER_LOCATOR=togethercomputer/m2-bert-80M-2k-retrieval
MODEL_LOCATOR=togethercomputer/m2-bert-80M-2k-retrieval
MAX_TOKENS=200
TEMPERATURE=0.0
TOGETHER_API_KEY=<Your Token>
PATHWAY_PERSISTENT_STORAGE=/tmp/cache

2. From the project root folder, open your terminal and rundocker-compose -f docker-config.yml up
3. Navigate to localhost:8501 on your browser when docker installion is successful.
   
General route:
Clone the repository
This is done with the git clone command followed by the URL of the repository.
Set environment variables
Start the application by running main.py.
Run Streamlit UI.

python main.py
