"""Intent router for natural language queries using LLM tool calling."""

import sys
import json
from typing import Optional
from services.lms_client import LMSClient
from services.llm_client import LLMClient


# Tool definitions for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks in the system",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution histogram for a lab (4 buckets: 0-25, 26-50, 51-75, 76-100)",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return", "default": 5},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled learners and their groups",
            "parameters": {
                "type": "object",
                "properties": {
                    "enrolled_after": {"type": "string", "description": "Optional ISO date to filter learners enrolled after this date"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger a data sync from the autochecker API to refresh the database",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

SYSTEM_PROMPT = """You are a helpful assistant for a Software Engineering course LMS. 
You have access to tools that let you fetch data about labs, tasks, scores, and learners.

When the user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Use the tool results to formulate a helpful response

Available tools:
- get_items: List all labs and tasks
- get_scores: Score distribution for a lab (buckets: 0-25%, 26-50%, 51-75%, 76-100%)
- get_pass_rates: Per-task pass rates and attempt counts
- get_timeline: Submissions per day
- get_groups: Per-group performance
- get_top_learners: Top N students by score
- get_completion_rate: Completion percentage
- get_learners: List of enrolled students
- trigger_sync: Refresh data from autochecker

For questions like "which lab has the lowest pass rate", you need to:
1. First call get_items to see what labs exist
2. Then call get_pass_rates for each lab
3. Compare and report the lowest

Always be specific and cite the data in your response."""


class IntentRouter:
    """Routes natural language queries to backend tools via LLM."""

    def __init__(self, lms_client: LMSClient, llm_client: LLMClient):
        """Initialize the intent router.

        Args:
            lms_client: Client for LMS API calls.
            llm_client: Client for LLM calls.
        """
        self.lms_client = lms_client
        self.llm_client = llm_client

    async def route(self, message: str) -> str:
        """Route a natural language message to the appropriate tool(s).

        Args:
            message: User's message text.

        Returns:
            Response text.
        """
        messages = [{"role": "user", "content": message}]
        
        # Track tool calls for debugging
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM with tools
            response, tool_calls = await self.llm_client.chat_with_tools(
                messages=messages,
                tools=TOOLS,
                system_prompt=SYSTEM_PROMPT,
            )
            
            # If LLM returned a response without tool calls, we're done
            if not tool_calls:
                return response
            
            # Execute tool calls and build results
            tool_results = []
            for tool_call in tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})
                
                # Debug output
                print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
                
                result = await self._execute_tool(tool_name, tool_args)
                tool_results.append({
                    "name": tool_name,
                    "arguments": tool_args,
                    "result": result,
                })
                
                # Debug output
                result_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                print(f"[tool] Result: {result_preview}", file=sys.stderr)
            
            print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)
            
            # Add tool results to conversation
            for tr in tool_results:
                # Format the assistant message with tool call
                messages.append({
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{
                        "id": f"call_{tr['name']}",
                        "type": "function",
                        "function": {
                            "name": tr["name"],
                            "arguments": json.dumps(tr["arguments"]),
                        },
                    }],
                })
                # Format the tool response
                messages.append({
                    "role": "tool",
                    "tool_call_id": f"call_{tr['name']}",
                    "content": json.dumps(tr["result"], default=str) if not isinstance(tr["result"], str) else tr["result"],
                })

        return "I'm having trouble answering this question. Please try rephrasing."

    async def _execute_tool(self, name: str, arguments: dict) -> any:
        """Execute a tool call.

        Args:
            name: Tool name.
            arguments: Tool arguments.

        Returns:
            Tool result.
        """
        if name == "get_items":
            response = await self.lms_client._client.get("/items/")
            response.raise_for_status()
            return response.json()
        
        elif name == "get_scores":
            lab = arguments.get("lab", "")
            response = await self.lms_client._client.get("/analytics/scores", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        
        elif name == "get_pass_rates":
            lab = arguments.get("lab", "")
            response = await self.lms_client._client.get("/analytics/pass-rates", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        
        elif name == "get_timeline":
            lab = arguments.get("lab", "")
            response = await self.lms_client._client.get("/analytics/timeline", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        
        elif name == "get_groups":
            lab = arguments.get("lab", "")
            response = await self.lms_client._client.get("/analytics/groups", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        
        elif name == "get_top_learners":
            lab = arguments.get("lab", "")
            limit = arguments.get("limit", 5)
            response = await self.lms_client._client.get("/analytics/top-learners", params={"lab": lab, "limit": limit})
            response.raise_for_status()
            return response.json()
        
        elif name == "get_completion_rate":
            lab = arguments.get("lab", "")
            response = await self.lms_client._client.get("/analytics/completion-rate", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        
        elif name == "get_learners":
            enrolled_after = arguments.get("enrolled_after")
            params = {"enrolled_after": enrolled_after} if enrolled_after else {}
            response = await self.lms_client._client.get("/learners/", params=params)
            response.raise_for_status()
            return response.json()
        
        elif name == "trigger_sync":
            response = await self.lms_client._client.post("/pipeline/sync")
            response.raise_for_status()
            return response.json()
        
        else:
            return {"error": f"Unknown tool: {name}"}
