from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper, generic_helper
global inprogress_orders

# Create an instance of FastAPI
app = FastAPI()

inprogress_orders = {}

# Create a decorater to handle HTTP get requests
@app.post("/")

# Asynchorous python function
async def handle_request(request : Request):
    # Wait until a json request arrives and then retrieve it
    payload = await request.json()

    # Extract necessary information from the payload based on the structure of the request
    # The request is a Webhookrequest sent by DialogFlow
    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"]["parameters"]
    output_contexts = payload["queryResult"]["outputContexts"]

    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    # Create a routing table to map each intent to a function
    intent_handler_dict = {
        "order.add - context: ongoing-order" : add_to_order,
        "order.remove - context: ongoing-order" : remove_from_order,
        "order.complete - context: ongoing-order" : complete_order,
        "track.order - context: ongoing-tracking" : track_order
    }

    # Call the appropriate function using the intent
    return intent_handler_dict[intent](parameters, session_id)

def add_to_order(parameters : dict, session_id : str):

    # Extract the food items and quantities from the request
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        # If the number of food items supplied is not equal to the number of quantities supplied
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantity again"
    else:
        # If both food item and quantities are equal
        new_food_dict = dict(zip(food_items, quantities))


        if session_id in inprogress_orders:
            # If session_id already exists append food dictionary to current session id
            inprogress_orders[session_id].update(new_food_dict)
        else:
            # Add session_id and food dictionary as a seperate entry
            inprogress_orders[session_id] = new_food_dict

        print("**************")
        print(session_id, inprogress_orders[session_id])
        # Get the current order of the user from the food dictionary
        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])

        fulfillment_text = f"So far you have {order_str}. Do you want anything else?"

    # Return a JSON response indicating the intent has been recieved.
    return JSONResponse(content={
        "fulfillmentText":fulfillment_text
    })

def remove_from_order(parameters : dict, session_id : str):
    if session_id not in inprogress_orders:
        # If an order with the current session id does not exist
        fulfillment = "I'm having trouble finding your order. Sorry! Can you place a new order please"
    else:
        # Extract the current order of the user and the food items in it.
        current_order = inprogress_orders[session_id]
        food_items = parameters["food-item"]
        removed_items = []
        no_such_items = []

        for item in food_items:
            if item not in current_order:
                # If food items is not in user's order.
                no_such_items.append(item)

            else:
                # Remove the food item from the user's order
                removed_items.append(item)
                del current_order[item]

    fulfillment = ""
    if len(removed_items) > 0:
        # If food items were removed from the user's order
        fulfillment += f"Removed {','.join(removed_items)} from your order. "
    
    if len(no_such_items) > 0:
        fulfillment += f"Your current order does not have {','.join(no_such_items)}. "

    if len(current_order.keys())==0:
        # If order is empty
        fulfillment += "Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment += f"Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText":fulfillment
    })

def complete_order(parameters : dict, session_id : str):

    if session_id not in inprogress_orders:
        # If an order with the current session id does not exist
        fulfillment = " I'm having trouble finding your order. Sorry! Can you place a new order please"
    else:
        # Else extract the order from the current session id of the user
        order = inprogress_orders[session_id]

        # Save the order to the database
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillment = "Sorry I couldn't place your order due to a backend error." \
            " Please place a new order again."
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment = f"Awesome, we have placed your order. Here is your order id # {order_id}." \
            f"Your order total is {order_total} which you can pay at the time of delievery."

        # Delete the order once it has been placed.
        del inprogress_orders[session_id]

    db_helper.insert_order_tracking(order_id, "in progress")

    return JSONResponse(content={
        "fulfillmentText":fulfillment
    })

def save_to_db(order : dict):
    
    next_order_id = db_helper.get_next_order_id()
    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

        if rcode == -1: 
            return rcode
    
    return next_order_id


def track_order(parameters : dict, session_id : str):
    
    # Extract the order id from the request
    order_id = int(parameters["order_id"])

    # Get the status of the order from the database
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        # If an order is found from the database
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        # If no order is found
        fulfillment_text = f"No order found with order id: {order_id}"

    # Return a JSON response indicating the intent has been recieved.
    return JSONResponse(content={
        "fulfillmentText":fulfillment_text
    })

