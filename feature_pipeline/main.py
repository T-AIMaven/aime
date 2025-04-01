import logging
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            mapped_query[mapped_key] = query[original_key]  # Map to dataset column names
    logger.info(f"Mapped Query: {mapped_query}")
    return mapped_query

def find_similar_rows(dataset_path, query):
    """
    Find rows in the dataset that are most similar to the given query.

    :param dataset_path: Path to the dataset file (CSV or Excel).
    :param query: Dictionary containing the query conditions.
    :return: DataFrame containing the most similar rows with only key_mapping's value fields.
    """
    # Load the dataset
    df = pd.read_excel(dataset_path, engine="openpyxl")

    # Initialize a similarity score column
    df["similarity_score"] = 0

    # Key mapping from query keys to dataset column names
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
        "ext": "Ext. (m2)",
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

    # Drop the similarity score column
    similar_rows = similar_rows.drop(columns=["similarity_score"])

    # Retain only the columns specified in key_mapping's values
    result_columns = list(key_mapping.values())
    similar_rows = similar_rows[result_columns]

    return similar_rows


if __name__ == "__main__":
    # Path to the dataset file
    dataset_path = r"D:\data\task\aime\data_collection_pipeline\dataset.xlsx"

    # Query conditions
    query = {
        "Bedroom": 3,
        "Bathroom": 2,
        "car_park": 3,
        "aspect": "N",
        "level": 9,
        "listing_price": 581900
    }

    # Find similar rows
    similar_rows = find_similar_rows(dataset_path, query)

    # Print the similar rows
    print("Most Similar Rows:")
    print(similar_rows)