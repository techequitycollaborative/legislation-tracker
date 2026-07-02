from db.connect import fetch_all

def get_ai_members():
    '''
    Get list of names of AI Working Group members from the database.
    '''
    sql = """
        SELECT name, email, org_name
        FROM auth.approved_users
        WHERE ai_working_group = 'yes';
    """
    return fetch_all(sql, as_dataframe=True)

