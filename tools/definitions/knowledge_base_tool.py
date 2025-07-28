knowledge_base_tool_definition = {
        "type": "function",
        "function": {
            "name": "search_knowledge_base_themis",
            "description": "Query a knowledge base to retrieve relevant about Themis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user question or search query."
                    },
                    "options": {
                        "type": "object",
                        "properties": {
                            "num_results": {
                                "type": "number",
                                "description": "Number of top results to return."
                            },
                            "domain_filter": {
                                "type": [
                                    "string",
                                    "null"
                                ],
                                "description": "Optional domain to narrow the search (e.g. 'finance', 'medical'). Pass null if not needed."
                            },
                            "sort_by": {
                                "type": [
                                    "string",
                                    "null"
                                ],
                                "enum": [
                                    "relevance",
                                    "date",
                                    "popularity",
                                    "alphabetical"
                                ],
                                "description": "How to sort results. Pass null if not needed."
                            }
                        },
                        "required": [
                            "num_results",
                            "domain_filter",
                            "sort_by"
                        ],
                        "additionalProperties": False
                    }
                },
                "required": [
                    "query",
                    "options"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }