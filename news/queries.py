#NOTE: add this file and parameter (list of strings)
"""
topic_queries = {
    "topic1": (
        "query1",
        "query2",
        "query3",
    ),
    "topic2": (
        "query4",
        "query5",
        "query6",
    ),
]
"""
from my_queries import topic_queries

"""
# Option B
from comb_query_generator import get_queries
topic_queries = get_queries()
"""
