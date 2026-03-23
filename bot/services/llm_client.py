"""LLM client for natural language intent routing with tool calling."""

import json
import re
import httpx
from typing import Optional


class LLMClient:
    """Client for interacting with LLM services for intent detection and tool calling."""

    def __init__(self, api_key: str, base_url: str = "http://localhost:42005/v1", model: str = "qwen3-coder-flash"):
        """Initialize the LLM client."""
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(60.0, connect=10.0, read=60.0, write=10.0),
        )

    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: Optional[str] = None,
    ) -> tuple[str, list[dict]]:
        """Chat with the LLM using tool calling."""
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        response = await self._call_llm(all_messages, tools)
        tool_calls = self._extract_tool_calls(response)

        if tool_calls:
            return "", tool_calls

        return self._extract_content(response), []

    async def _call_llm(self, messages: list[dict], tools: list[dict]) -> dict:
        """Make a raw LLM call with tool support."""
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
        }

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]

    def _extract_tool_calls(self, response: dict) -> list[dict]:
            """Extract tool calls from LLM response."""
            # Check for native tool calls first
            tool_calls = response.get("tool_calls", [])
            if tool_calls:
                result = []
                for tc in tool_calls:
                    func = tc.get("function", {})
                    try:
                        args = json.loads(func.get("arguments", "{}"))
                    except json.JSONDecodeError:
                        args = {}
                    result.append({"name": func.get("name"), "arguments": args})
                return result

            # Check for function_call format
            if "function_call" in response:
                fc = response["function_call"]
                return [{"name": fc.get("name"), "arguments": json.loads(fc.get("arguments", "{}"))}]

            # Parse XML-like function calls from content
            content = response.get("content", "")
            return self._parse_xml_tool_calls(content)

    def _parse_xml_tool_calls(self, content: str) -> list[dict]:
        """Parse XML-style tool calls from content."""
        tool_calls = []

        # Pattern 1: Match <function_name>{"arg": "value"}</function_name>
        pattern = r'<(\w+)>(\{[^}]*\})</\1>'
        matches = re.findall(pattern, content)
        for name, args_str in matches:
            try:
                args = json.loads(args_str)
                tool_calls.append({"name": name, "arguments": args})
            except json.JSONDecodeError:
                pass

        # Pattern 2: Match <function=name>...</function> with <parameter=key>value</parameter>
        func_pattern = r'<function=(\w+)>(.*?)</function>'
        func_matches = re.findall(func_pattern, content, re.DOTALL)
        for name, func_body in func_matches:
            args = {}
            # Extract all <parameter=key>value</parameter>
            param_pattern = r'<parameter=(\w+)>(.*?)</parameter>'
            param_matches = re.findall(param_pattern, func_body, re.DOTALL)
            for param_name, param_value in param_matches:
                param_value = param_value.strip()
                # Try to parse as JSON (for numbers, arrays, objects)
                try:
                    args[param_name] = json.loads(param_value)
                except json.JSONDecodeError:
                    args[param_name] = param_value
            if args:
                tool_calls.append({"name": name, "arguments": args})

        return tool_calls

    def _extract_content(self, response: dict) -> str:
        """Extract text content from LLM response."""
        return response.get("content", "")

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
