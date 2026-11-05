
# from config.qdrant_config import client, COLLECTION_NAME, EMBEDDING_MODEL
# from qdrant_client import models

# client.add(
#     collection_name=COLLECTION_NAME,
#     documents=[
#         "The team discussed RAG architecture, ChromaDB, and MCP integration."
#     ],
#     metadata=[
#         {
#             "note_id": "test-001",
#             "title": "RAG Architecture Discussion",
#             "meeting_date": "2026-11-05"
#         }
#     ],
#     ids=["test-001"],
#     model=EMBEDDING_MODEL
# )

# print("Sample note inserted successfully!")

# results = client.query(
#     collection_name=COLLECTION_NAME,
#     query=models.Document(
#         text="What did the team discuss about RAG?",
#         model=EMBEDDING_MODEL
#     ),
#     limit=3
# )

# for point in results.points:
#     print(point.payload)
