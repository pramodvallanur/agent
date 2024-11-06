from swarm import Swarm, Agent
from datetime import datetime, timedelta
from dateutil import parser
import re
import panel as pn
from swarm.types import Result
import random
import os
os.environ["OPENAI_API_KEY"] = "" # Replace with your key
client = Swarm()

def get_ingredients(food, quantity):
    """Get the ingredients for a particular food item and it's quantity"""
    print(f"Getting ingredients for {food} with quantity {quantity}")
    return {"salt": 100, "sugar": 100}

def procure_ingredients(ingredient, quantity):
    """Place an order to procure the ingredient with the given quantity"""
    print(f"Procuring ingredients for {ingredient} with quantity {quantity}")
    return True

def get_lead_time_to_procure_ingredient(ingredient, quantity):
    """Gets the lead time to procure the ingredient with the given quantity"""
    print(f"Get Lead time ingredients for {ingredient} with quantity {quantity}")
    return "1 hour"

def get_lead_time_to_prepare_and_deliver_food(food):
    """Gets the lead time to prepare and deliver the food. Assume ingredients are available."""
    print(f"Get Lead time to prepare and deliver {food}")
    return "1 hour"

def check_inventory(ingredient, quantity):
    """Check the inventory for the ingredient and the quantity."""
    print(f"Check inventory for {ingredient} and {quantity}")
    return True
    # if ingredient == "salt" and quantity == str(100):
    #     print("Salt is available")
    #     return True
    # print(f"{ingredient} is not available")
    # return False

def generate_quote(food, quantity, address, datetime):
    """Generate a quote for a particular food and quantity delivered to a particular address by a particular time to send it to customer"""
    print(f"Generating quote for {food} with quantity {quantity} at {address} on {datetime}")
    return f"{quantity} of {food} to be delivered to: {address} by: {datetime} costs: 100 $"

def notify_owner(message):
    """Send notification to owner"""
    print(f"Sending notification to owner: {message}")
    return True

def notify_customer(message):
    """Send notification to customer"""
    print(f"Sending notification to customer: {message}")
    return True

def can_deliver(delivery_time, order_time, lead_time_to_procure_prepare_and_deliver_food):
    """Check if the delivery time is less than order_time + lead_time_to_procure_prepare_and_deliver_food"""
    hours = re.findall(r'\d+', lead_time_to_procure_prepare_and_deliver_food)
    time1 = parser.parse(delivery_time)
    time2 = parser.parse(order_time) + timedelta(hours=int(hours[0]))
    result = time1 > time2
    print(f"Comparing {delivery_time} with {lead_time_to_procure_prepare_and_deliver_food} and returned: {result}")
    return result

def schedule_for_delivery():
    """Return a delivery agent which helps in delivery of the food."""
    return delivery_partner_agent

def find_best_delivery_partner(address, delivery_time):
    """Find the best delivery partner to deliver food to the address by the delivery time"""
    print(f"Selecting best Delivery partner to deliver package to the {address} by the {delivery_time}")
    return "UPS"

def create_label_for_delivery_partner(delivery_partner):
    """Create label for the delivery partner"""
    print(f"Creating shipping label for {delivery_partner}")
    return "Delivery Label created."

context_variables = {
    'customer_name': None,  # Initialize customer name to None
    'last_order_id': None,
}

# # Define the Central Agent
central_agent = Agent(
    name="Bakery Agent",
    instructions="You are assisting the owner of the bakery in processing of the requests. When an request is received, ensure all aspects of the order— from product preparation to delivery—are managed efficiently. Notify only the owner if the request cannot be fulfilled by delivery time. Notify the customer to confirm the request with quote, if it can be fulfilled. Once fulfilled prepare for deliver the food.",
    functions=[get_ingredients, check_inventory, generate_quote, get_lead_time_to_procure_ingredient, procure_ingredients, get_lead_time_to_prepare_and_deliver_food, notify_owner, notify_customer, can_deliver, schedule_for_delivery]
)

delivery_partner_agent = Agent(
    name="Delivery Partner Agent",
    instructions="Finds out the best delivery partner to deliver food and creates label for the delivery partner.",
    functions=[find_best_delivery_partner, create_label_for_delivery_partner],
    model="gpt-4o"
)
pn.extension(design="material")

chat_interface = pn.chat.ChatInterface()
chat_interface.send("Welcome to Cymbal Bakery Please enter your name:", user="System", respond=False)

current_agent = central_agent
messages = []
def process_user_message(contents: str, user: str, instance: pn.chat.ChatInterface):
    global current_agent
    global context_variables
    global messages

    if context_variables['customer_name'] is None:
        context_variables['customer_name'] = contents
        chat_interface.send(f"Hello, {contents}! How can I help you today?", user=current_agent.name, avatar="🤖", respond=False)
    else:
        messages.append({"role": "user", "content": contents})

        response = client.run(
            agent=current_agent,
            messages=messages,
            context_variables=context_variables
        )

        for message in response.messages:
            if message['role'] == 'assistant':
                if message['tool_calls']:
                    for tool_call in message['tool_calls']:
                        tool_name = tool_call['function']['name']
                        chat_interface.send(f"Using tool: {tool_name}", user=message['sender'], avatar="🤖", respond=False)
                elif message['content']:
                    chat_interface.send(message['content'], user=message['sender'], avatar="🤖", respond=False)

        messages = response.messages
        current_agent = response.agent
        context_variables = response.context_variables

        # if "order" in contents.lower():
        #     context_variables['last_order_id'] = f"ORD-{random.randint(1000, 9999)}"

chat_interface.callback = process_user_message

chat_interface.servable()
