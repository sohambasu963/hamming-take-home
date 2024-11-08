conversation_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "conversation_response",
        "schema": {
            "type": "object",
            "properties": {
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "node_id": {
                                "type": "string",
                                "description": "Unique identifier for the conversation node"
                            },
                            "speaker": {
                                "type": "string",
                                "description": "The speaker of this node, e.g., 'AI Agent' or 'Customer Service'"
                            },
                            "text": {
                                "type": "string",
                                "description": "The text content of the conversation at this node"
                            },
                            "next": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "List of IDs for possible next nodes based on user responses"
                                },
                                "description": "Array of node IDs representing possible next nodes"
                            }
                        },
                        "required": ["node_id", "speaker", "text", "next"],
                        "additionalProperties": False
                    },
                    "description": "Array of conversation nodes, each representing a single point in the conversation flow"
                }
            },
            "required": ["nodes"],
            "additionalProperties": False
        },
        "strict": True
    }
}
