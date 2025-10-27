import re

def extract_session_id(session_str : str):

    # Uses regex to extract the session id from the session string
    match = re.search(r"sessions\/(.*)\/contexts", session_str)

    if match:
        # Extract the first match (session id) found in the string
        extracted_string = match.group(1)
        return extracted_string
    
    return ""

def get_str_from_food_dict(food_dict : dict):
    # Prints each food item and it's quantity seperated by a comma
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])

if __name__ == "__main__":
    print(get_str_from_food_dict({"pizza":1,"biryani":2}))
    # print(extract_session_id("projects/mira-chatbot-hvsf/agent/sessions/02a10597-41e1-1a7e-391e-4a57b924e961/contexts/ongoing-order"))