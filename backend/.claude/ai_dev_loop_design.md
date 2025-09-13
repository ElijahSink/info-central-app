# AI Dev Loop System Design

## Core Loop Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Generate   │───▶│   Execute Code   │───▶│  Analyze Result │
│     Code        │    │   in Sandbox     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                                              │
         │               ┌──────────────────┐           │
         └───────────────│   AI Iterate     │◄──────────┘
                         │   With Context   │
                         └──────────────────┘
```

## Implementation Components

### 1. Enhanced Block Service
```python
class BlockService:
    async def create_block_with_iteration(self, prompt: str, max_iterations: int = 3):
        for attempt in range(max_iterations):
            # Generate code
            code = await ai_service.generate_code(prompt, context=previous_failures)
            
            # Test execution  
            result = await execution_service.execute_and_analyze(code)
            
            if result.success:
                return save_successful_block(code, result)
            else:
                # Add failure to context for next iteration
                previous_failures.append(result)
        
        # Max iterations reached - save with error state
        return save_failed_block(code, previous_failures)
```

### 2. Enhanced Execution Service
```python
class ExecutionService:
    async def execute_and_analyze(self, code: str) -> ExecutionResult:
        # Run code in sandbox
        stdout, stderr, return_code = await self.execute_subprocess(code)
        
        # Analyze the results
        if return_code == 0:
            data = json.loads(stdout)
            if "error" in data:
                return ExecutionResult(
                    success=False,
                    error_type="logical_error", 
                    error_details=data["error"],
                    suggestions=self.analyze_error_patterns(data["error"])
                )
            return ExecutionResult(success=True, data=data)
        else:
            return ExecutionResult(
                success=False,
                error_type="execution_error",
                error_details=stderr,
                suggestions=self.analyze_execution_error(stderr)
            )
```

### 3. Enhanced AI Service
```python
class AIService:
    async def generate_code_with_context(self, prompt: str, failures: List[ExecutionResult]):
        system_prompt = self.build_iterative_prompt(failures)
        
        user_message = f"""
Original request: {prompt}

Previous attempts failed:
{self.format_failure_context(failures)}

Learn from these failures and generate improved code that addresses the specific issues.
"""
        
        # Send to OpenAI with failure context
        return await self.call_openai(system_prompt, user_message)
        
    def build_iterative_prompt(self, failures: List[ExecutionResult]):
        base_prompt = self.get_system_prompt()
        
        if failures:
            failure_analysis = "\n".join([
                f"Previous failure: {f.error_details}"
                f"Suggested fix: {f.suggestions}"
                for f in failures
            ])
            
            base_prompt += f"""
            
CRITICAL: Previous attempts failed with these errors:
{failure_analysis}

You MUST analyze these failures and avoid repeating the same mistakes.
Try alternative approaches, different APIs, or different parsing strategies.
"""
        
        return base_prompt
```

### 4. Error Analysis Intelligence
```python
class ErrorAnalyzer:
    def analyze_error_patterns(self, error: str) -> str:
        patterns = {
            "Video container not found": "Try inspecting the actual HTML structure. Use browser dev tools to find real CSS selectors.",
            "Connection timeout": "The website may block scrapers. Try adding headers or use an API instead.",
            "403 Forbidden": "Website blocks scrapers. Find an official API or RSS feed.",
            "JSON decode error": "Response isn't JSON. Check if you need to parse HTML or handle redirects.",
        }
        
        for pattern, suggestion in patterns.items():
            if pattern.lower() in error.lower():
                return suggestion
        
        return "Analyze the error and try a different approach."
```

## Example Dev Loop Flow

### Iteration 1: Fox 13 Weather
- **AI generates**: BeautifulSoup scraping with `.weather-video-container`
- **Execute**: `{"error": "Video container not found"}`
- **AI sees**: CSS selector didn't work

### Iteration 2: Improved Strategy  
- **AI generates**: Multiple fallback selectors: `video`, `.video-player`, `iframe[src*="video"]`
- **Execute**: Still no luck, but finds iframe with weather widget
- **AI sees**: Website uses embedded weather widgets

### Iteration 3: Alternative Approach
- **AI generates**: Use National Weather Service API for Tampa instead of scraping
- **Execute**: `{"temperature": 78, "forecast": "Partly cloudy"}`
- **Success**: Real weather data!

## Benefits

1. **Self-Improving**: AI learns from each failure
2. **Robust**: Multiple strategies tried automatically  
3. **Adaptive**: Switches approaches when scraping fails
4. **User Experience**: User sees working blocks, not errors
5. **Knowledge Building**: Successful patterns stored for reuse

## Implementation Priority

1. **Phase 1**: Basic execute → analyze → retry loop
2. **Phase 2**: Error pattern recognition  
3. **Phase 3**: Context accumulation across iterations
4. **Phase 4**: Cross-block learning and pattern storage