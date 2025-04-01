import time
from inference_pipeline.trustAgent import TrustAgent
from inference_pipeline.salesAgent import SalesAgent
from openai import OpenAI
from config.config import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def OpenAiCall(messages: list[dict]):
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL_ID,
        messages=messages
    )
    return response.choices[0].message.content

class testingBot:
    def __init__(self):
        self.bot_prt = """
        You are an AI-powered real estate buyer, engaging in a conversation with a sales qualification agent about purchasing a property. 
        Your role is to answer to trustAgent's questions with all your preferences
        until you provide all your preferences, don't terminate the chat actively.
        Respond naturally and conversationally to their questions, using the following information as your preferences:

        Buyer Preferences:
        Looking for a property
        Needs 3 bedrooms and 2 bathrooms
        Budget: Around $500,000
        Preferred project: High Society
        Parking: Requires 2 car spaces
        Aspect: Prefers a north-facing property
        Preferred floor: 5th floor
        Needs additional storage space
        Internal area: At least 100 square meters
        External area: At least 50 square meters

        Response Guidelines:
        Respond naturally and conversationally rather than listing answers directly.
        Adapt responses based on the agent's questions (e.g., if they ask about budget, mention it casually rather than stating it as a fact).
        If the agent asks a question that isn’t covered by the given preferences, respond in a neutral but engaging way (e.g., "I'm open to options, but I'd like something modern.").
        Keep responses friendly and polite, as a real buyer would.
        Do not provide all the details at once; only reveal relevant information when asked.

        Ending the Conversation:
        If you provided your all preferences, you can end the conversation politely by sending a message"I've provided all the necessary information"
        """
        self.chat_history = []

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using OpenAI's LLM based on the bot's preferences.

        :param prompt: The prompt/question from the TrustAgent.
        :return: Generated response from the LLM.
        """
        messages = [
            {"role": "system", "content": self.bot_prt},
            {"role": "user", "content": prompt}
        ]
        response = OpenAiCall(messages)
        return response

    def interact_with_trust_agent(self, trust_agent: TrustAgent, sales_agent: SalesAgent):
        """
        Simulate a conversation between the testingBot and the TrustAgent.

        :param trust_agent: An instance of the TrustAgent class.
        """
        print("Starting simulated conversation with TrustAgent...\n")

        while True:
            # TrustAgent asks a question
            if trust_agent.chatHistory:
                last_response = trust_agent.chatHistory[-1]["content"]
            else:
                last_response = "Hi, how can I assist you today?"

            # print(f"TrustAgent: {last_response}")

            # Generate a response using the bot's preferences
            user_input = self.generate_response(last_response)
            print(f"############ User: {user_input}")

            # Send the response to TrustAgent
            response = trust_agent.chat(user_input)
            print("*"*20)
            print(f"@@@@@@@@@@@@ TrustAgent: {response}\n")

            # Check if the conversation has ended
            if "Thank you for sharing all these details" in response:
                print("Conversation has ended politely.")
                
                
                extracted_data = trust_agent.extract_property_requirements()

                top_k_properties = sales_agent.execute_query(query=extracted_data)

                print("Top K Properties:", top_k_properties)
                
                # Call the profile building method from TrustAgent
                customer_profile = trust_agent.profile_building()

                property_matching = trust_agent.property_matching(customer_profile=customer_profile, top_k_properties=top_k_properties)
                

                print("Extracted Data:", extracted_data)
                
                break

            # Simulate a delay to mimic real-time interaction
            time.sleep(1)

if __name__ == "__main__":
    # Initialize TrustAgent and SalesAgent
    trust_agent = TrustAgent()
    sales_agent = SalesAgent()

    # Initialize the testing bot
    bot = testingBot()

    # Simulate the conversation
    bot.interact_with_trust_agent(trust_agent, sales_agent)