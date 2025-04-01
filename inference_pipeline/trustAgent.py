from openai import OpenAI
from config.config import settings
import pandas as pd
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def OpenAiCall(messages: list[dict]):
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL_ID,
        messages=messages
    )
    return response.choices[0].message.content

class TrustAgent:
    def __init__(self):  # Rename parameter
        self.chatHistory = []  # Initialize chat history
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
            "int": None,
            "ext": None
        }
        self.role_prt = """
        ## Role:
        You are an experienced, professional real estate sales qualification agent specializing in off-the-plan properties. Your role is to engage with potential buyers in a friendly, conversational manner to understand their needs and match them with suitable properties.

        Conversation Structure:

        ## 1. Build Trust & Initial Engagement
        Introduce yourself warmly and professionally.

        Begin with light conversation to establish rapport.

        Show genuine interest in the buyer as a person, not just a prospect.

        Use a friendly, approachable tone while maintaining professionalism.

        Briefly explain your role and how you can help them find their ideal property.

        Example opening:
        "Hi there! I'm KoKo from linkinc.com. It's great to connect with you today about our off-the-plan properties. Before we dive into specifics, I'd love to learn a bit about you and what brings you to explore new property options right now. How's your day going so far?"

        ## 2. Qualification Questions (you should ask these questions in a natural, conversational manner)
        Ask questions in a natural, conversational manner to understand the buyer’s situation and needs. Cover:

        # 2.1 Personal Circumstances
        Current living situation (renting, own a home, living with family).

        Location preferences and current neighborhood.

        Relationship status (single, couple, family with children).

        Employment situation (industry, stability, length of employment).

        Timeline for purchase/move.

        # 2.2 Purchase Goals
        Purpose of purchase (own occupancy, downsizing, first home, investment).

        Budget range (be tactful when discussing finances).

        Primary motivation for buying (lifestyle change, family needs, retirement planning, investment).

        Previous property purchase experience.

        Long-term plans for the property.

        Specific Requirements
        Size requirements (bedrooms, bathrooms, living spaces).

        Must-have features or amenities.

        Dealbreakers or absolute requirements.

        Preferred completion timeframe.

        Flexibility on location, size, or features.

        ## 3. Communication Guidelines
        Be authentic and honest at all times.

        Listen more than you speak.

        Ask follow-up questions to clarify understanding.

        Never pressure or rush decisions.

        Use conversational language, avoiding industry jargon.

        Acknowledge concerns and answer questions transparently.

        Position yourself as a helpful guide, not a pushy salesperson.

        Express genuine excitement about helping them find the right property.

        End of Conversation Process
        If all necessary information has been collected(specific requirements), and if you got "I've provided all the necessary information" from the customers, send the message - "Thank you for sharing all these details".


        Example closing:
        "Thank you for sharing all these details! This really helps us match you with the right property. I appreciate your time today, and I’ll be in touch soon with options that fit your needs. Have a great day!"
        """
    
        self.system_prt = {"role": "system", "content": f"{self.role_prt}"}

        self.extract_prt = """
        You are an expert real estate data extraction assistant. Given the chat history between a real estate sales qualification agent and a customer, extract the following property requirements from the conversation and return them in a structured JSON format. Ensure accuracy by interpreting the conversation contextually and filling in only the details explicitly mentioned in the chat history. If a value is not provided, leave it as None.

        Extract the following details:

        {{
            "project_name": None,
            "state": None,
            "listing_price": None,
            "Bedroom": None,
            "Bathroom": None,
            "car_park": None,
            "aspect": None,
            "level": None,
            "storage": None,
            "int(m2)": None,
            "ext(m2)": None
        }}
        Instructions:

        Use only the information present in the chat history.

        Maintain the format and set values to None if not explicitly stated.

        Convert any numerical values into appropriate data types (e.g., integer or float where applicable).

        Ignore any irrelevant conversation details unrelated to the property requirements.

        Example Input (Chat History):
        Agent: "What is your preferred project or development?"
        Customer: "I'm interested in the Skyline Residences in Sydney."
        Agent: "Great! Do you have a budget range in mind?"
        Customer: "Somewhere around $750,000."
        Agent: "How many bedrooms and bathrooms do you need?"
        Customer: "I need a 2-bedroom, 2-bathroom apartment with at least one car park."

        Expected Output:
        {{
            "project_name": "Skyline Residences",
            "state": "Sydney",
            "listing_price": 750000,
            "Bedroom": 2,
            "Bathroom": 2,
            "car_park": 1,
            "aspect": None,
            "level": None,
            "storage": None,
            "int(m2)": None,
            "ext(m2)": None
        }}
        Return only the extracted JSON output without any additional text or explanation and without any code block, so that I can parse it directly:

        ### chat history:
        {chat_history}
        """

        self.profile_building_prt = """
        "You are an expert assistant specializing in real estate buyer profiling. Based on the chat history between a real estate qualification agent and a potential buyer, extract key details to construct a structured customer profile. Use contextual understanding to infer details where applicable, but do not assume information not explicitly provided.

        Extract and return the profile in the following JSON format:
        {{
            "name": null,
            "buyer_purpose": null, 
            "financial_capacity": null, 
            "timeline_urgency": null, 
            "primary_motivations": null, 
            "key_decision_factors": null, 
            "lifestyle_needs": null, 
            "potential_objections": null,
            "preferred_location": null,
            "current_living_situation": null,
            "employment_status": null,
            "family_status": null,
            "previous_property_experience": null
        }}
        
        ## Extraction Guidelines:
        name: Extract the buyer’s name if mentioned.

        buyer_purpose: Classify as owner-occupier, downsizer, first-home buyer, investor, or other relevant category.

        financial_capacity: Indicate the buyer’s budget, financial readiness, and any stated constraints.

        timeline_urgency: Assess whether the buyer needs to purchase immediately, in a few months, or is just exploring options.

        primary_motivations: Capture emotional or practical drivers (e.g., upgrading for space, relocating for work, seeking passive income).

        key_decision_factors: Identify essential criteria influencing their choice (e.g., location, amenities, price, potential growth).

        lifestyle_needs: Highlight preferences related to lifestyle, such as proximity to schools, transport, or a vibrant community.

        potential_objections: Note any concerns raised, such as pricing, financing difficulties, location constraints, or market uncertainty.

        preferred_location: Extract the buyer's desired area or region if specified.

        current_living_situation: Identify if the buyer is renting, owning, or living with family.

        employment_status: Capture the buyer’s job industry and stability.

        family_status: Determine if the buyer is single, in a couple, or has children.

        previous_property_experience: Indicate if the buyer has purchased property before or is a first-time buyer.

        ### Example Input (Chat History):
        Agent: "Are you looking for a property to live in or as an investment?"
        Customer: "I'm looking for an investment property to generate rental income."
        Agent: "Do you have a specific budget in mind?"
        Customer: "Ideally around $800,000, but I can stretch a bit for the right place."
        Agent: "How soon are you looking to buy?"
        Customer: "I'm hoping to finalize something in the next three months."
        Agent: "What are the key factors for your decision?"
        Customer: "Location is crucial. I want something with high rental demand, close to transport and amenities."
        Agent: "Where do you currently live?"
        Customer: "I'm renting in Melbourne, but I’d prefer to buy in Sydney."
        Agent: "What do you do for work?"
        Customer: "I work in finance, stable job for 5 years."
        Agent: "Have you purchased property before?"
        Customer: "Yes, I own an apartment in Melbourne."

        ### Expected Output:
        {{
            "name": null,
            "buyer_purpose": "Investor",
            "financial_capacity": "Budget around $800,000, flexible for the right property",
            "timeline_urgency": "Looking to purchase within three months",
            "primary_motivations": "Generate rental income",
            "key_decision_factors": "High rental demand, close to transport and amenities",
            "lifestyle_needs": null,
            "potential_objections": null,
            "preferred_location": "Sydney",
            "current_living_situation": "Renting in Melbourne",
            "employment_status": "Finance, stable job for 5 years",
            "family_status": null,
            "previous_property_experience": "Owns an apartment in Melbourne"
        }}
        Return only the extracted JSON output without any additional text or explanation.

        ### chat history:
        {chat_history}
    """

        self.property_matching_prt = """
        You are an expert real estate sales assistant. Based on the customer's profile (built from the chat history) and the top-K recommended property list, match the best 2-3 properties that align with their preferences and present them persuasively.

        Task:
        1.Justify the Selection
        - Explain why each property aligns with their specific needs, preferences, and motivations.
        - Highlight key decision factors such as price, location, size, features, or investment potential.
        2.Address Potential Concerns
        - If the customer expressed objections (e.g., price, location, financing), proactively address them for each property.
        3.Emphasize Developer Credibility
        - Provide brief but relevant details about the developer’s track record, build quality, and reputation.

        ### customer profile:
        {customer_profile}

        ### top-K recommended properties:
        {top_k_properties}
    """
    
    def chat(self, question: str) -> str:
        """
        Process the user input, add it to chat history, and generate a response using OpenAI's API.

        :param question: User's question or input.
        :return: Generated response from the assistant.
        """
        # Add the user's question to the chat history
        self.chatHistory.append({"role": "user", "content": question})

        # Prepare the messages for the API call
        messages = [self.system_prt] + self.chatHistory

        # Call OpenAI API and get the response
        response_content = OpenAiCall(messages=messages)

        # Add the assistant's response to the chat history
        self.chatHistory.append({"role": "assistant", "content": response_content})

        return response_content

    def extract_property_requirements(self) -> dict:
        """
        Extract property requirements from the chat history using OpenAI.

        :return: Extracted property requirements as a dictionary.
        """
        # Prepare the extraction prompt
        message = [{"role": "user", "content": self.extract_prt.format(chat_history=self.chatHistory)}]

        extracted_data = OpenAiCall(messages=message)
        print(extracted_data)
        # Parse the extracted data as JSON
        try:
            extracted_json = json.loads(extracted_data)
            # Update the property requirements dictionary with the extracted values
            for key, value in extracted_json.items():
                if key in self.property_requirements:
                    self.property_requirements[key] = value
            print("property_requirements from chat history...", self.property_requirements)
        except json.JSONDecodeError:
            print("Failed to parse OpenAI response as JSON.")

    def profile_building(self) -> dict:
        """
        Extract property requirements from the chat history using OpenAI.

        :return: Extracted property requirements as a dictionary.
        """
        # Prepare the extraction prompt
        message = [{"role": "user", "content": self.profile_building_prt.format(chat_history=self.chatHistory)}]

        extracted_data = OpenAiCall(messages=message)
        print(extracted_data)
        # Parse the extracted data as JSON
        try:
            extracted_json = json.loads(extracted_data)
            # Update the property requirements dictionary with the extracted values
            for key, value in extracted_json.items():
                if key in self.property_requirements:
                    self.property_requirements[key] = value
            print("extracted data for profile building ...", self.property_requirements)
        except json.JSONDecodeError:
            print("Failed to parse OpenAI response as JSON.")

    def property_matching(self, customer_profile: dict, top_k_properties: pd.DataFrame) -> str:
        """
        Match properties based on customer profile and top-K recommended properties.

        :param customer_profile: Customer profile data.
        :param top_k_properties: DataFrame containing top-K recommended properties.     
        :return: Matched properties as a string.
        """
        # Prepare the property matching prompt
        message = [{"role": "user", "content": self.property_matching_prt.format(customer_profile=customer_profile, top_k_properties=top_k_properties)}]

        matched_properties = OpenAiCall(messages=message)
        print("matched_properties...", matched_properties)
        return matched_properties
