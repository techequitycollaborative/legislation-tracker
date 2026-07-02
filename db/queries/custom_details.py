from db.connect import get_conn
from psycopg2.extras import RealDictCursor

# Advocacy details functions
def get_all():
    """
    Fetches all custom bill details for a specific bill from all organizations.
    For use on the advocacy hub page.
    """
    
    with get_conn() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT * FROM app.bill_custom_details
            ORDER BY bill_number ASC
        """, )
        
        return cursor.fetchall()
