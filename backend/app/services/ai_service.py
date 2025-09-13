from typing import Dict, Any, Optional
import openai
from openai import AsyncOpenAI
from ..core.config import settings


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def generate_block_code(
        self, 
        user_prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generate both backend and frontend code for a block."""
        
        system_prompt = self._get_system_prompt()
        user_message = self._format_user_prompt(user_prompt, context)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            return self._parse_generated_code(content)
            
        except Exception as e:
            raise Exception(f"AI code generation failed: {str(e)}")
    
    async def heal_block(
        self, 
        original_prompt: str, 
        error_message: str, 
        failed_code: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Attempt to fix a broken block."""
        
        healing_prompt = self._get_healing_prompt()
        user_message = f"""
Original request: {original_prompt}

Failed code:
```python
{failed_code}
```

Error encountered: {error_message}

Please fix the code and explain what was wrong.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": healing_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            return self._parse_generated_code(content)
            
        except Exception as e:
            raise Exception(f"AI healing failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Python and React developer. Generate FUNCTIONAL, WORKING code for dashboard blocks that fetch REAL data from actual APIs and websites.

CRITICAL REQUIREMENTS:
- NEVER use mock/fake data or placeholder URLs
- ALWAYS implement real API calls or web scraping
- Find actual public APIs, RSS feeds, or scrapable websites for the requested data
- Handle errors gracefully with try/catch blocks
- Return real, live data that users can see

CONSTRAINTS:
- Backend: Python only, using these pre-installed packages: requests, httpx, beautifulsoup4, pandas, numpy, python-dateutil, jmespath
- Frontend: React with TypeScript, using Tailwind CSS and shadcn/ui components only
- No additional package installations allowed
- File system access limited to current directory (read-only)
- Network access allowed for API calls

BACKEND CODE EXAMPLES:
```python
import asyncio
import requests
from typing import Dict, Any
from bs4 import BeautifulSoup

class BlockExecutor:
    async def fetch_data(self) -> Dict[str, Any]:
        # Example: For weather data, use a real API like OpenWeatherMap or scrape a weather site
        # Example: For news, use RSS feeds or news APIs
        # Example: For stocks, use financial APIs or scrape financial sites
        # Example: For social media, use public APIs or RSS feeds
        
        try:
            # Replace this with ACTUAL API calls based on user request
            response = requests.get("https://actual-api-endpoint.com/api/data", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "message": "Failed to fetch data"}
    
    async def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # Clean and format the data for the frontend
        # Extract relevant fields, convert formats, etc.
        return raw_data
```

FRONTEND CODE STRUCTURE:
```typescript
interface BlockProps {
  data: any;
  refreshData: () => void;
  isLoading: boolean;
  error?: string;
}

export function GeneratedBlock({ data, refreshData, isLoading, error }: BlockProps) {
  // Your React component here
  // Use Tailwind CSS for styling
  // Use shadcn/ui components: Button, Card, Table, etc.
  return <div>Your component JSX</div>;
}
```

Respond with:
## Backend Code
```python
[backend code here]
```

## Frontend Code
```typescript
[frontend code here]
```

## Explanation
[Brief explanation of what the block does]
"""
    
    def _get_healing_prompt(self) -> str:
        return """You are debugging a failed dashboard block. Fix the code based on the error message.

Follow the same constraints and structure as the original system prompt.
Provide the corrected code and explain what was wrong.

Respond with:
## Backend Code
```python
[fixed backend code here]
```

## Frontend Code  
```typescript
[fixed frontend code here]
```

## Explanation
[What was wrong and how you fixed it]
"""
    
    def _format_user_prompt(self, user_prompt: str, context: Optional[Dict[str, Any]]) -> str:
        message = f"Create a dashboard block for: {user_prompt}"
        
        if context:
            message += f"\n\nContext: {context}"
        
        return message
    
    def _parse_generated_code(self, content: str) -> Dict[str, str]:
        """Parse the AI response to extract backend code, frontend code, and explanation."""
        result = {
            "backend_code": "",
            "frontend_code": "",
            "explanation": ""
        }
        
        lines = content.split('\n')
        current_section = None
        current_code = []
        
        for line in lines:
            if line.strip() == "## Backend Code":
                current_section = "backend"
                current_code = []
            elif line.strip() == "## Frontend Code":
                current_section = "frontend"
                current_code = []
            elif line.strip() == "## Explanation":
                current_section = "explanation"
                current_code = []
            elif line.strip().startswith("```"):
                if current_code and current_section:
                    code_content = '\n'.join(current_code)
                    if current_section == "backend":
                        result["backend_code"] = code_content
                    elif current_section == "frontend":
                        result["frontend_code"] = code_content
                current_code = []
            elif current_section == "explanation":
                current_code.append(line)
            elif current_section and not line.strip().startswith("```"):
                current_code.append(line)
        
        # Handle explanation if it's the last section
        if current_section == "explanation" and current_code:
            result["explanation"] = '\n'.join(current_code).strip()
            
        return result