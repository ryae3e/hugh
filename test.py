



def generate_reply(conversation: list) -> str:
    """Generate a ChatGPT response with a maximum token limit."""
    
    # Check if the last message from the user is "gord?x9"
    if conversation[-1]['role'] == 'user' and conversation[-1]['content'].strip() == "gord?x9":
        return "well hidy how partner"
    
    # If the last message is not the easter egg, return a placeholder response
    return "Placeholder response for normal conversation"

# Test the function with the easter egg
print(generate_reply([{'role': 'user', 'content': 'gord?x9'}]))

# Test the function with a normal message
print(generate_reply([{'role': 'user', 'content': 'Hello, how are you?'}]))
