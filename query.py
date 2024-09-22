import os
import pandas as pd
from bs4 import BeautifulSoup
import pathway as pw
from pathway.stdlib.ml.index import KNNIndex
from pathway.xpacks.llm.embedders import OpenAIEmbedder
from pathway.xpacks.llm.llms import OpenAIChat, prompt_chat_single_qa
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentInputSchema(pw.Schema):
    title: str
    timestamp: str
    content: str

class QueryInputSchema(pw.Schema):
    query: str

# Function to clean HTML content using BeautifulSoup
def clean_html(content):
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()

def run(
    *,
    data_dir: str = "./internationalnews.csv",  # Updated data directory
    api_key: str = os.environ.get("OPENAI_API_KEY", ""),
    host: str = os.environ.get("HOST", "0.0.0.0"),
    port: int = os.environ.get("PORT", "8080"),
    embedder_locator: str = os.environ.get("EMBEDDER_LOCATOR", "text-embedding-ada-002"),
    embedding_dimension: int = int(os.environ.get("EMBEDDING_DIMENSION", "1536")),
    model_locator: str = os.environ.get("MODEL_LOCATOR", "gpt-3.5-turbo"),
    max_tokens: int = int(os.environ.get("MAX_TOKENS", 200)),
    temperature: float = float(os.environ.get("TEMPERATURE", 0.0)),
    **kwargs,
):
    # Read and process the CSV file
    documents_df = pd.read_csv(data_dir)
    
    # Select relevant columns and clean HTML content
    documents = documents_df[['title', 'timestamp', 'content']].to_dict(orient='records')
    for doc in documents:
        doc['content'] = clean_html(doc['content'])

    # Convert to Pathway's internal data structure
    documents = pw.from_records(documents)

    # Initialize the embedder
    embedder = OpenAIEmbedder(
        api_key=api_key,
        model=embedder_locator,
        retry_strategy=pw.udfs.ExponentialBackoffRetryStrategy(),
        cache_strategy=pw.udfs.DefaultCache(),
    )

    # Generate embeddings for the content
    enriched_documents = documents + documents.select(vector=embedder(pw.this.content))

    # Build the KNN Index for document retrieval
    index = KNNIndex(
        enriched_documents.vector, enriched_documents, n_dimensions=embedding_dimension
    )

    # Setup HTTP connection for query
    query, response_writer = pw.io.http.rest_connector(
        host=host,
        port=port,
        schema=QueryInputSchema,
        autocommit_duration_ms=50,
        delete_completed_queries=True,
    )

    # Embed the query
    query += query.select(vector=embedder(pw.this.query))

    # Get nearest documents based on query
    query_context = query + index.get_nearest_items(
        query.vector, k=3, collapse_rows=True
    ).select(documents_list=pw.this.content)  # Fetch content

    # Function to build a prompt
    @pw.udf
    def build_prompt(documents, query):
        docs_str = "\n".join(documents)
        prompt = f"Given the following documents: \n{docs_str}\nanswer this query: {query}"
        return prompt

    # Create prompt for the LLM
    prompt = query_context.select(
        prompt=build_prompt(pw.this.documents_list, pw.this.query)
    )

    # Initialize the OpenAIChat model
    model = OpenAIChat(
        api_key=api_key,
        model=model_locator,
        temperature=temperature,
        max_tokens=max_tokens,
        retry_strategy=pw.udfs.FixedDelayRetryStrategy(),
        cache_strategy=pw.udfs.DefaultCache(),
    )

    # Get responses based on the prompt
    responses = prompt.select(
        query_id=pw.this.id, result=model(prompt_chat_single_qa(pw.this.prompt))
    )

    # Send responses to the HTTP response writer
    response_writer(responses)

    # Run the Pathway engine
    pw.run()

if __name__ == "__main__":
    run()
