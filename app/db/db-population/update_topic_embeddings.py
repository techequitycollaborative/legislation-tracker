from sentence_transformers import SentenceTransformer
from yaml import safe_load
from datetime import datetime, timezone
import sys
sys.path.insert(0, '..')
from config import db_config as config
import psycopg2

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_topics_from_yaml(yaml_path: str = "../../utils/topic_keywords.yaml"):
    """Load and validate YAML data"""
    with open(yaml_path) as f:
        topic_config = safe_load(f)
    
    if not isinstance(topic_config, dict):
        raise ValueError("YAML must contain a dictionary of topics...")
    
    return [
        {"phrase": topic, "keywords": contents["keywords"]}
        for topic, contents in topic_config.items()]

def generate_embeddings(topics: list[dict]) -> list[tuple]:
    """Convert topics to DB-ready tuples (phrase, embedding, keywords, timestamp)"""
    embeddings = []
    for topic in topics:
        text = f"{topic['phrase']} {' '.join(topic['keywords'])}"
        embedding = model.encode(text)

        embeddings.append([
            topic["phrase"],
            embedding.tolist(),
            topic["keywords"],
            datetime.now(timezone.utc)
        ])
    return embeddings

def upsert_topic_embeddings(embeddings: list[tuple]):
    """Batch upsert topic embeddings to DB with error handling"""
    conn = None
    try:
        # Load the database configuration
        db_config = config('postgres', '../credentials.ini')
        
        # Establish connection to the PostgreSQL server
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                contents = ','.join(
                    cur.mogrify("(%s,%s,%s,%s)", x).decode("utf-8")
                    for x in embeddings
                )

                cur.execute(f"""
                    INSERT INTO snapshot.topic_embedding
                            (topic_phrase, embedding, keywords, embedding_updated_at)
                            VALUES {contents}
                            ON CONFLICT (topic_phrase) DO UPDATE SET
                                embedding = EXCLUDED.embedding,
                                keywords = EXCLUDED.keywords,
                                embedding_updated_at = EXCLUDED.embedding_updated_at
                            """)
                print(cur.statusmessage)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to update records", error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")

    return

def main():
    try:
        print("Loading topics from YAML...")
        topics = load_topics_from_yaml()

        print("Generating embeddings...")
        embeddings = generate_embeddings(topics)

        print(f"Upserting {len(embeddings)} topics to snapshot schema...")
        upsert_topic_embeddings(embeddings)

        print("Successfully updated topic embeddings")
    except Exception as e:
        print(f"Error: {str(e)}")
    return

if __name__ == "__main__":
    main()

