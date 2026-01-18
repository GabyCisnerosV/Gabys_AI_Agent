AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Checks availability and books a meeting. Use this when a user provides their name, email, time, and reason.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time_iso": {"type": "string", "description": "The ISO 8601 formatted start time (e.g., 2026-01-20T14:00:00Z)"},
                    "duration_minutes": {"type": "integer", "description": "Meeting length, default to 30."},
                    "visitor_name": {"type": "string", "description": "Name of the visitor."},
                    "visitor_email": {"type": "string", "description": "Email of the visitor (REQUIRED)."},
                    "description": {"type": "string", "description": "Topic of the meeting."}
                },
                "required": ["start_time_iso", "duration_minutes", "visitor_name", "visitor_email", "description"]
            }
        }
    }
]