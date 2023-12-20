# blog/sql_queries.py

INSERT_USER = """
INSERT INTO auth_user (username, password, email, first_name, last_name)
VALUES (%s, %s, %s, %s, %s)
"""

INSERT_USER_PROFILE = """
INSERT INTO user_profile_userprofile (user_id, bio, avatar_url)
VALUES (%s, %s, %s)
"""

SELECT_USER_BY_CREDENTIALS = """
SELECT * FROM auth_user WHERE username = %s;

"""

SELECT_ALL_POSTS = """
SELECT * FROM blog_post
"""

SELECT_USER_PROFILE = """
SELECT * FROM user_profile_userprofile WHERE user_id = %s
"""
