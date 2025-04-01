import logging
# import os
# import pandas as pd
# from chromadb import PersistentClient
# from chromadb.config import Settings
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# # Load environment variables
# db_path = os.getenv("DB_PATH", "chromadb/")
# dataset_file = os.getenv("DATASET_FILE", r"D:\data\task\aime\data_collection_pipeline\dataset.xlsx")
# top_k = int(os.getenv("TOP_K", 3))

# # Initialize ChromaDB client
# client = PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))

# # Create or get the collection
# collection = client.get_or_create_collection(
#     name="real_estate_data",
#     metadata={"hnsw:space": "cosine"}
# )

# # def add_row_to_chromadb(row_id, row_data):
# #     """
# #     Add a row of data to ChromaDB.

# #     :param row_id: Unique ID for the row.
# #     :param row_data: Dictionary containing the row data.
# #     """
# #     try:
# #         collection.add(
# #             ids=[row_id],
# #             documents=[str(row_data)],  # Store the row data as a string
# #             metadatas=[row_data]  # Store the row data as metadata for filtering
# #         )
# #         logger.info(f"Successfully added row with ID {row_id}")
# #     except Exception as e:
# #         logger.error(f"Error adding row with ID {row_id}: {e}")

# def add_rows_to_chromadb(dataset):
#     """
#     Add multiple rows of data to ChromaDB with metadata for each column.

#     :param dataset: List of dictionaries containing the dataset rows.
#     """
#     try:
#         # Prepare documents, ids, and metadata
#         documents = [str(row) for row in dataset]  # Convert each row to a string for storage
#         ids = [f"row_{i}" for i in range(len(dataset))]  # Generate unique IDs for each row
#         metadatas = dataset  # Use each row as metadata

#         # Add the data to ChromaDB
#         collection.add(
#             documents=documents,
#             ids=ids,
#             metadatas=metadatas  # Store each row's data as metadata
#         )
#         logger.info(f"Successfully added {len(dataset)} rows to ChromaDB")
#     except Exception as e:
#         logger.error(f"Error adding rows to ChromaDB: {e}")


# def search_rows(query, top_k):
#     """
#     Search for the top K rows in ChromaDB based on the query.

#     :param query: Dictionary containing the query filters.
#     :param top_k: Number of top results to return.
#     :return: List of matching rows.
#     """
#     try:
#         results = collection.query(
#             query_texts=[""],  # Empty query text
#             n_results=int(top_k),  # Ensure top_k is passed as an integer
#             where=query  # Use the query as a filter
#         )
#         logger.info(f"Search results: {results}")
#         return results
#     except Exception as e:
#         logger.error(f"Error searching rows: {e}")
#         return None

# def map_query_keys(query, key_mapping):
#     """
#     Map the keys in the query dictionary to the dataset keys using the key_mapping.

#     :param query: Dictionary containing the query filters with original keys.
#     :param key_mapping: Dictionary mapping original keys to dataset keys.
#     :return: Dictionary with mapped keys.
#     """
#     mapped_query = {}
#     for original_key, mapped_key in key_mapping.items():
#         if original_key in query:
#             mapped_query[mapped_key] = {"$eq": query[original_key]}  # Add $eq operator for exact match
#     mapped_query = {"$and": [{key: value} for key, value in mapped_query.items()]}
#     logger.info(f"Mapped Query: {mapped_query}")
#     return mapped_query

# def clean_dataset(file_path, key_mapping):
#     """
#     Load and clean the dataset by removing rows with null values and retaining only the required columns.

#     :param file_path: Path to the dataset file.
#     :param key_mapping: Dictionary mapping original keys to dataset keys.
#     :return: Cleaned dataset as a list of dictionaries.
#     """
#     try:
#         # Load the dataset with the correct engine
#         df = pd.read_excel(file_path, engine="openpyxl")

#         # Retain only the columns specified in the key_mapping values
#         required_columns = list(key_mapping.values())
#         df = df[required_columns]

#         # Remove rows with null values
#         df = df.dropna()

#         # Convert the cleaned DataFrame to a list of dictionaries
#         cleaned_data = df.to_dict(orient="records")
#         logger.info(f"Successfully cleaned dataset. Rows retained: {len(cleaned_data)}")
#         return cleaned_data
#     except Exception as e:
#         logger.error(f"Error cleaning dataset: {e}")
#         return []

# def main():
#     # Key mapping from `options` keys to dataset keys
#     key_mapping = {
#         "project_name": "Project Name",
#         "state": "State",
#         "listing_price": "Listing Price",
#         "Bedroom": "Bed",
#         "Bathroom": "Bath",
#         "car_park": "Car",
#         "aspect": "Aspect",
#         "level": "Level",
#         "storage": "Storage",
#         "int": "Int. (m2)",
#         "ext": "Ext. (m2)"
#     }

#     # Clean the dataset
#     dataset = clean_dataset(r"D:\data\task\aime\data_collection_pipeline\dataset.xlsx", key_mapping)

#     # Add cleaned dataset to ChromaDB
#     for i, row in enumerate(dataset):
#         add_rows_to_chromadb(row_data=row)

#     # Example search query with original keys
#     original_query = {
#         "Bedroom": "3",
#         "Bathroom": "2",
#         "car_park": "3",
#         "aspect": "N",
#         "level": "10"
#     }

#     # Map the query keys to dataset keys
#     mapped_query = map_query_keys(original_query, key_mapping)

#     # Search for the top K matching rows
#     top_k_results = search_rows(query=mapped_query, top_k=top_k)
#     print("Top K Results:", top_k_results)

# if __name__ == "__main__":
#     main()


import pandas as pd

def map_query_keys(query, key_mapping):
    """
    Map the keys in the query dictionary to the dataset keys using the key_mapping.

    :param query: Dictionary containing the query filters with original keys.
    :param key_mapping: Dictionary mapping original keys to dataset keys.
    :return: Dictionary with mapped keys.
    """
    mapped_query = {}
    for original_key, mapped_key in key_mapping.items():
        if original_key in query:
            mapped_query[mapped_key] = {"$eq": query[original_key]}  # Add $eq operator for exact match
    mapped_query = {"$and": [{key: value} for key, value in mapped_query.items()]}
    logger.info(f"Mapped Query: {mapped_query}")
    return mapped_query

def find_similar_rows(dataset_path, query):
    """
    Find rows in the dataset that are most similar to the given query.

    :param dataset_path: Path to the dataset file (CSV or Excel).
    :param query: Dictionary containing the query conditions.
    :return: DataFrame containing the most similar rows.
    """
    # Load the dataset
    df = pd.read_excel(dataset_path, engine="openpyxl")

    # Initialize a similarity score column
    df["similarity_score"] = 0

    key_mapping = {
        "project_name": "Project Name",
        "state": "State",
        "listing_price": "Listing Price",
        "Bedroom": "Bed",
        "Bathroom": "Bath",
        "car_park": "Car",
        "aspect": "Aspect",
        "level": "Level",
        "storage": "Storage",
        "int": "Int. (m2)",
        "ext": "Ext. (m2)"
    }
    # Map the query keys to dataset keys
    mapped_query = map_query_keys(query, key_mapping)

    # Iterate through the query conditions and calculate similarity
    for column, value in mapped_query.items():
        # Increment the similarity score for rows that match the condition
        df["similarity_score"] += (df[column] == value).astype(int)

    # Sort the rows by similarity score in descending order
    df = df.sort_values(by="similarity_score", ascending=False)

    # Filter rows with the highest similarity score
    max_score = df["similarity_score"].max()
    similar_rows = df[df["similarity_score"] == max_score]

    # Drop the similarity score column before returning
    similar_rows = similar_rows.drop(columns=["similarity_score"])

    return similar_rows



if __name__ == "__main__":
    # Path to the dataset file
    dataset_path = r"D:\data\task\aime\data_collection_pipeline\dataset.xlsx"

    # Query conditions
    query = {
        "Bed": 3,
        "Bath": 2,
        "Car": 3,
        "Aspect": "N",
        "Level": 10
    }

    # Find similar rows
    similar_rows = find_similar_rows(dataset_path, query)

    # Print the similar rows
    print("Most Similar Rows:")
    print(similar_rows)