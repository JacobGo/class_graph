# Academic Graph

This is supposed to be a GraphQL interface to the UMass academic calendar.

## References
https://docs.graphene-python.org/projects/sqlalchemy/en/latest/

`pip install SQLAlchemy graphene_sqlalchemy Flask Flask-GraphQL BeautifulSoup4 PyQuery`

`rm -f database.sqlite3 && python seed.py && python server.py`