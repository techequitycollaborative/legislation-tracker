from db.connect import get_conn
from psycopg2.extras import RealDictCursor

# Advocacy details functions
def get_all_most_recent():
    '''
    Retrieves the most recent document/letter for every bill that has one,
    across all organizations. For use on the Advocacy Hub page.
    '''
    with get_conn() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT DISTINCT ON (openstates_bill_id)
                openstates_bill_id,
                bill_number,
                org_name,
                letter_name,
                letter_url,
                created_by,
                created_on,
                created_at
            FROM app.bill_letter_history
            ORDER BY openstates_bill_id, created_at DESC
        """)

        return cursor.fetchall()

        # letters = []
        # for row in rows:
        #     letters.append({
        #         'openstates_bill_id': row[0],
        #         'bill_number': row[1],
        #         'org_name': row[2],
        #         'letter_name': row[3],
        #         'letter_url': row[4],
        #         'created_by': row[5],
        #         'created_on': row[6],
        #         'created_at': row[7]
        #     })

        # return letters
