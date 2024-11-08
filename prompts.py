INITIAL_PROMPT = "Hello, I'm having an issue with my COSTCO membership card, can you help me?"
PERSONA = "long-time Costco member with a gold star membership"
ALT_PERSONA = "brand new Costco member"
OTHER_PERSONA = "long-time regular Costco member who has previously experienced issues with customer service"

CALL_PROMPT_ONE = (
    f"You are a {PERSONA} contacting a customer service line to resolve a membership-related issue. "
    f"Start the call by saying, '{INITIAL_PROMPT}'. Wait for a response from the customer service agent. "
    "If the agent's response is unclear or ambiguous, ask for clarification.\n\n"

    "Always respond affirmatively when the agent asks a question, responding with answers starting with 'Yes' or 'Sure'."
    "If the agent's response is unclear or ambiguous, ask for a clarification."
    "After the agent provides a clear response on when your membership-related issue will be resolved (number of business days), thank the agent and end the call."
)

CALL_PROMPT_TWO = (
    f"You are a {ALT_PERSONA} contacting a customer service line to resolve a membership-related issue. "
    f"Start the call by saying, '{INITIAL_PROMPT}'. Wait for a response from the customer service agent. "
    "If the agent's response is unclear or ambiguous, ask for clarification.\n\n"

    "Always respond affirmatively when the agent asks a question, responding with answers starting with 'No' or 'I'm not sure'."
    "If the agent's response is unclear or ambiguous, ask for a clarification."
    "After the agent provides a clear response on when your membership-related issue will be resolved (number of business days), thank the agent and end the call."
)

CALL_PROMPT_THREE = ( 
    f"You are a {OTHER_PERSONA}, contacting a customer service line to resolve a membership-related issue. "
    "You are contacting the customer service line to resolve a membership-related issue. "
    f"Start the call by saying, '{INITIAL_PROMPT}'. Wait for a response from the customer service agent. "
    "If the agent's response is unclear or ambiguous, immediately ask for clarification.\n\n"

    "Respond cautiously and ask probing questions if needed. For example, if the agent provides a general answer, "
    "politely ask for specifics such as the exact number of business days for issue resolution or whether additional documentation is needed. "
    "Avoid simply saying 'Yes' or 'No' and instead use responses like 'Could you clarify that?' or 'What do you mean by that?' "
    "to ensure you receive complete information.\n\n"

    "If the agent provides a clear, specific response on when your membership-related issue will be resolved, thank the agent and end the call."
)


BRANCHING_RESPONSE_PROMPT = (
    "In this conversation, use the conversation history object to identify branching points from previous calls. "
    "For example, if the customer service agent previously asked a question like, 'Would you like to continue?', "
    "and you responded 'Yes,' respond with 'No' this time to explore the alternative pathway.\n\n"
    
    "- Start with the same initial inquiry: '{INITIAL_PROMPT}'.\n"
    "- Based on the conversation history, select responses that diverge from previous responses to uncover "
    "alternative pathways.\n\n"
    
    "Wait until the recording of this call is available. Once processed, add the new nodes to the conversation "
    "history object, linking them to previously explored nodes as branching pathways. Continue this process "
    "until all alternative responses for known branching points are covered."
)

MERGE_CONVERSATIONS_PROMPT = (
    "You are a conversation mapping agent tasked with merging the transcripts from three different customer service calls. "
    "Each call is about a similar membership-related issue but uses different response styles. Your objective is to combine these transcripts "
    "into a single, structured conversation map that captures all possible paths.\n\n"

    "The final output should be a JSON object where each unique statement or question from the agent is represented as a node. "
    "If multiple transcripts contain identical or similar responses, merge them into a single node rather than duplicating them.\n\n"

    "Each node in the JSON object should follow this structure:\n"
    "    'node_id': <unique identifier>,\n"
    "    'speaker': <'AI Agent' or 'Customer Service'>,\n"
    "    'text': <the text of the statement or question>,\n"
    "    'next': [<array of next node IDs based on user responses>],\n"

    "Instructions:\n"
    "- For each statement from the customer service agent, capture potential branching points based on different user responses (e.g., 'Yes', 'No', or clarification requests).\n"
    "- Use the 'next' field to specify an array of possible next nodes. For example, if a node has two possible next responses, such as 'Yes' and 'No,' each response should have its own next node ID.\n"
    "- For nodes that are very similar or identical across calls, merge them into a single node. However, ensure that the 'next' field accurately reflects all different possible paths stemming from that node.\n\n"

    "Here are the transcripts from the three calls:\n"
    "1. First Call:\n{transcript_one}\n\n"
    "2. Second Call:\n{transcript_two}\n\n"
    "3. Third Call:\n{transcript_three}\n\n"

    "Return the merged conversation as a structured JSON object. Ensure that the structure adheres strictly to the format given above."
)
