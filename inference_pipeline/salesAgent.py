from openai import OpenAI
from inference_pipeline.config import settings
import pandas as pd
import json

# Ensure the API key is loaded correctly
if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please check your environment or config.")

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def OpenAiCall(messages: list[dict]):
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL_ID,
        messages=messages
    )
    return response.choices[0].message.content

class SalesAgent:
    def __init__(self):  # Rename parameter
        self.system_prt = {"role": "system", "content": "You are a helpful assistant."}
        self.chatHistory = []
        self.property_requirements = {
            "project_name": None,
            "state": None,
            "listing_price": None,
            "Bedroom": None,
            "Bathroom": None,
            "car_park": None,
            "aspect": None,
            "level": None,
            "storage": None,
            "int_m2": None,
            "ext_m2": None
        }
        self.requirements_extract_prt = """
            You are an intelligent text analyzer. Your task is to extract the value associated with a specific keyword from a user’s statement.

            User Input: A sentence provided by the user.
            Keyword: A specific word for which you need to find the associated value.
            
            Instructions:
            Identify the keyword in the user's sentence.
            Extract the adjective or value that describes the keyword.
            Format your output as a JSON object with the keyword as the key and the extracted value as the value.
            
            Your response should be only JSON, nothing else.
            Now, please analyze the following input and extract the value for the keyword provided.
           
            User question: {question}
            keyword: {keyword}
        """
    
    def map_query_keys(self, query, key_mapping):
        """
        Map the keys in the query dictionary to the dataset keys using the key_mapping.

        :param query: Dictionary containing the query filters with original keys.
        :param key_mapping: Dictionary mapping original keys to dataset keys.
        :return: Dictionary with mapped keys.
        """
        if not query:  # Check if query is None or empty
            return {}

        mapped_query = {}
        for original_key, mapped_key in key_mapping.items():
            # Check if the key exists in the query and its value is not None
            if original_key in query and query[original_key] is not None:
                mapped_query[mapped_key] = query[original_key]
        return mapped_query

    
    def find_similar_rows(self, dataset_path, query):
        """
        Find rows in the dataset that are most similar to the given query.

        :param dataset_path: Path to the dataset file (CSV or Excel).
        :param query: Dictionary containing the query conditions.
        :return: DataFrame containing the most similar rows with similarity scores normalized between 0 and 1.
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
            "int(m2)": "Int. (m2)",
            "ext(m2)": "Ext. (m2)",
        }

        # Map the query keys to dataset keys
        mapped_query = self.map_query_keys(query=query, key_mapping=key_mapping)

        # Iterate through the query conditions and calculate similarity
        for column, value in mapped_query.items():
            # Increment the similarity score for rows that match the condition
            df["similarity_score"] += (df[column] == value).astype(int)

        # Normalize the similarity score between 0 and 1
        max_possible_score = len(mapped_query)  # Maximum possible similarity score
        df["similarity_score"] = df["similarity_score"] / max_possible_score

        # Sort the rows by similarity score in descending order
        df = df.sort_values(by="similarity_score", ascending=False)

        # Retain only the columns specified in key_mapping's values and the similarity score
        result_columns = list(key_mapping.values()) + ["similarity_score"]
        similar_rows = df[result_columns]

        return similar_rows 


    def execute_query(self, query: dict, top_k: int = 3) -> dict:
        """
        Execute the query and return the top-k results in a structured format.

        :param query: Dictionary containing the query conditions.
        :param top_k: Number of top results to return.
        :return: A dictionary containing the structured results with normalized similarity scores.
        """
        dataset_path = settings.DATASET_FILE
        print(f"Dataset path: {dataset_path}")
        # Use the passed query parameter instead of hardcoded values
        similar_rows = self.find_similar_rows(dataset_path=dataset_path, query=query)
        top_k_rows = similar_rows.head(top_k)

        # Convert the DataFrame to a structured dictionary
        structured_result = top_k_rows.to_dict(orient="records")

        # Return the structured result
        return structured_result