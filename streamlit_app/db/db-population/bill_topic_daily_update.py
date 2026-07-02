from sentence_transformers import SentenceTransformer
import numpy as np
from yaml import safe_load
import sys
sys.path.insert(0, '..')
from config import db_config as config
from update_topic_embeddings import main as topic_update
import psycopg2
from nltk.corpus import stopwords
import re
from collections import defaultdict
from tqdm.auto import tqdm

# Global variables
SESSION = "20252026"

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define a function to remove stopwords from text
stop_words = set(stopwords.words('english'))
legislation_words = [
    "law",
    "provisions",
    "existing",
    "establishes",
    "requires",
    "establish",
    "require",
    "laws",
    "prohibit",
    "prohibits"
]
stop_words.update(legislation_words)

def preprocess(text):
    # stop_words = set(stopwords.words('english'))
    words = re.findall(r'\b\w+\b', text.lower())  # Tokenize
    return ' '.join([w for w in words if w not in stop_words])

def embed(text):
    return model.encode(preprocess(text))

def keyword_regex(yaml_path: str = "../../utils/topic_keywords.yaml"):
    with open(yaml_path) as f:
        topic_config = safe_load(f)

    # Initialize dictionary mapping
    keyword_to_topics = defaultdict(list) # keyword, List[topic1, topic2]
    all_keywords = set() # A global set of keywords for optimized DF updates

    # Fill mapping and update global set
    for topic, data in topic_config.items():
        # Select keywords if available
        keywords = data["keywords"]

        # if a topic does not have keywords, treat it like its own keyword
        if not keywords:
            keywords = [topic] 
        
        # Now update the keyword -> topic mapping
        for keyword in keywords:
            # normalize to lowercase
            keyword_to_topics[keyword.lower()].append(topic)
        
        # Finally update the global set
        all_keywords.update(keywords) 

    # Create global regex pattern
    pattern = '|'.join(rf'\b{re.escape(word)}\b' for word in all_keywords)
    global_keyword_regex = re.compile(rf"\b{pattern}\b", flags=re.IGNORECASE)
    return global_keyword_regex

def topic_refresh(cur) -> bool:
    """Check if topic embeddings are stale (>30 days old)"""
    print("Checking if topic embeddings are stale...")
    cur.execute("""
        SELECT EXISTS (
                SELECT 1 FROM snapshot.topic_embedding
                WHERE embedding_updated_at < NOW() - INTERVAL '30 days'
                LIMIT 1
            );
    """)
    print(cur.statusmessage)
    return cur.fetchone()[0]

def fetch_bills_for_topic_assignment(cur):
    """Return bills that need topic assignment:
    1. Embedding is missing, OR
    2. Bill was updated since the last embedding computation, OR
    3. Topics have been refreshed since the bill was last assigned topics
    
    Returns a list of openstates_bill_ids"""
    print("Selecting stale and unassigned bills...")
    cur.execute("""
        SELECT b.openstates_bill_id, b.title, b.abstract
        FROM snapshot.bill b
        LEFT JOIN snapshot.bill_embedding e ON b.openstates_bill_id = e.openstates_bill_id
        LEFT JOIN (
                SELECT openstates_bill_id, MAX(assigned_at) AS last_assigned
                FROM snapshot.bill_topics
                GROUP BY openstates_bill_id
                ) t ON b.openstates_bill_id = t.openstates_bill_id
        WHERE
            -- Bill is in active session
            b.session = %s
            AND ( -- No embedding exists
                e.openstates_bill_id IS NULL
                -- bill has changed since last embedding was computed
                OR (CAST(b.updated_at AS TIMESTAMP) > e.computed_at)
                -- topics have been refreshed since the last assignment
                OR (t.last_assigned < (
                    SELECT MAX(embedding_updated_at)
                    FROM snapshot.topic_embedding
                    )
                )
            );
    """, (SESSION,))
    print(cur.statusmessage)
    return cur.fetchall()

def update_bill_embedding(cur, bill_id, bill_title, bill_abstract, title_weight=0.9):
    """Store/update embedding of a single bill"""
    title_embed = embed(bill_title)
    abstract_embed = embed(bill_abstract)
    embedding = (title_weight * title_embed) + ((1 - title_weight) * abstract_embed)
    cur.execute("""
        INSERT INTO snapshot.bill_embedding
        (openstates_bill_id, weighted_embedding, computed_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (openstates_bill_id) DO UPDATE SET
                weighted_embedding = EXCLUDED.weighted_embedding,
                computed_at = NOW();
    """, (bill_id, embedding.tolist()))
    return

def assign_bill_topics(cur, pattern, bill_id, bill_title, bill_abstract, threshold=0.384):
    """Assign bill topics first by keyword match, then by cosine similarity above threshold (default 0.4)"""
    # Delete old assignments
    cur.execute("""
        DELETE FROM snapshot.bill_topics WHERE openstates_bill_id = %s;
    """, (bill_id,))

    # -- Insert rows with keyword match
    keywords = pattern.findall(bill_title)
    if keywords:
        keywords_array = "{" + ",".join(keywords) + "}" 
        cur.execute("""
            INSERT INTO snapshot.bill_topics
            (openstates_bill_id, topic_phrase, match_method, similarity)
            SELECT %s, topic_phrase, 'keyword', NULL
            FROM snapshot.topic_embedding
            WHERE keywords && %s::text[]; -- Overlap operator
        """, (bill_id, keywords_array))

    # -- Insert rows with cosine similarity
    cur.execute("""
        SELECT weighted_embedding FROM snapshot.bill_embedding WHERE openstates_bill_id = %s;
    """, (bill_id,))

    bill_embedding = np.array(cur.fetchone()[0])

    cur.execute("""
        INSERT INTO snapshot.bill_topics
        (openstates_bill_id, topic_phrase, match_method, similarity)
        SELECT %s, topic_phrase, 'similarity', 1 - (embedding <=> %s)
        FROM snapshot.topic_embedding
        WHERE 1 - (embedding <=> %s) >= %s;
    """, (bill_id, bill_embedding.tolist(), bill_embedding.tolist(), threshold))

    return

def main():
    conn = None
    pattern = keyword_regex()

    try:
        # Load the database configuration
        db_config = config('postgres', '../credentials.ini')
        
        # Establish connection to the PostgreSQL server
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                # check if topics need refreshing
                if topic_refresh(cur):
                    topic_update()

                # Fetch bill IDs and text contents if they need topic assignment
                bill_contents = fetch_bills_for_topic_assignment(cur)

                # For each bill, update its stored embedding and assign topics
                for bill in tqdm(bill_contents):
                    update_bill_embedding(cur, *bill)
                    # Assign topics
                    assign_bill_topics(cur, pattern, *bill)
                pass
    except (Exception, psycopg2.DatabaseError) as error:
        print("Failed to update records", error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed")
    return

if __name__ == "__main__":
    main()