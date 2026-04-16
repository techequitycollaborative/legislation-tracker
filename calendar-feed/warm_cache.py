import requests
import time
import psycopg2
from datetime import datetime
from db.config import config


def get_all_tokens():
    """Fetch ALL user and org feed tokens from database with debug info"""
    params = config("postgres")
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    # Get all users with their dashboard status
    cur.execute("""
        SELECT u.feed_token, u.email, u.ai_working_group
        FROM auth.approved_users u
        LEFT JOIN app.user_bill_dashboard ub ON u.email = ub.user_email
        WHERE u.feed_token IS NOT NULL
        GROUP BY u.email, u.ai_working_group, u.feed_token
    """)
    users = [(row[0], row[1], row[2]) for row in cur.fetchall()]

    # Get all orgs with their dashboard status
    cur.execute("""
        SELECT o.feed_token, o.name
        FROM auth.approved_organizations o
        LEFT JOIN app.org_bill_dashboard ob ON o.id = ob.org_id
        WHERE o.feed_token IS NOT NULL
        GROUP BY o.id, o.name, o.feed_token
    """)
    orgs = [(row[0], row[1]) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return users, orgs


def warm_endpoint(endpoint_type, name, url):
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            print(f"✓ {endpoint_type}: {name[:30]}...")
            return 1
        else:
            print(f"✗ {endpoint_type}: {name[:30]}... ({resp.status_code})")
    except Exception as e:
        print(f"✗ {endpoint_type}: {name[:30]}... ({e})")
    return 0


def warm_cache():
    print("Fetching ALL feed tokens from database...")
    users, orgs = get_all_tokens()

    print(f"Warming cache for {len(users)} users and {len(orgs)} orgs")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")

    start = time.time()
    warmed = 0

    base_url = "http://localhost:5000"
    # Build URLs for EVERY user and org
    urls = []

    for token, email, is_wg in users:
        user_url = f"{base_url}/feed/user/{token}"
        warmed += warm_endpoint("User", email, user_url)
        if is_wg == "yes":
            wg_url = f"{base_url}/feed/working-group/{token}"
            warmed += warm_endpoint("WG", email, wg_url)

    for token, name in orgs:
        url = f"{base_url}/feed/org/{token}"
        warmed += warm_endpoint("Org", name, url)

    elapsed = time.time() - start
    print(f"\nFinished at: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Warmed {warmed} endpoints in {elapsed:.1f}s")


if __name__ == "__main__":
    warm_cache()
