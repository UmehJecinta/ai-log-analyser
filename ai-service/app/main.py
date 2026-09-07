from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import json
import os
import logging

# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# initialise FastAPI app
app = FastAPI(
    title="AI Log Analyser - AI Service",
    description="Analyses logs using AWS Bedrock Claude and returns root cause analysis",
    version="1.0.0"
)

# initialise Bedrock client
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# model ID — configurable via environment variable
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

# define what the incoming request should look like
class LogAnalysisRequest(BaseModel):
    logs: str
    context: str = ""

# define what the response will look like
class LogAnalysisResponse(BaseModel):
    what_went_wrong: str
    where_it_went_wrong: str
    suggested_fix: str
    severity: str
    raw_analysis: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-service"}

@app.post("/analyse", response_model=LogAnalysisResponse)
async def analyse_logs(request: LogAnalysisRequest):
    logger.info("Received log analysis request")

    if not request.logs.strip():
        raise HTTPException(
            status_code=400,
            detail="Logs cannot be empty"
        )

    try:
        # build the prompt
        prompt = f"""You are an expert DevOps engineer and system administrator.
Analyse the following logs and provide a structured analysis.

Logs to analyse:
{request.logs}

{f'Additional context: {request.context}' if request.context else ''}

Provide your analysis in the following exact format:
WHAT_WENT_WRONG: [Explain what the error or issue is in simple terms]
WHERE_IT_WENT_WRONG: [Identify the specific service, file, line, or component where the issue occurred]
SUGGESTED_FIX: [Provide clear, actionable steps to fix the issue]
SEVERITY: [Rate as: LOW, MEDIUM, HIGH, or CRITICAL]"""

        # call AWS Bedrock Claude
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        # extract the response
        response_body = json.loads(response["body"].read())
        analysis_text = response_body["content"][0]["text"]
        logger.info("Successfully received analysis from Bedrock")

        # parse the structured response
        lines = analysis_text.strip().split('\n')
        parsed = {}
        for line in lines:
            if line.startswith('WHAT_WENT_WRONG:'):
                parsed['what_went_wrong'] = line.replace('WHAT_WENT_WRONG:', '').strip()
            elif line.startswith('WHERE_IT_WENT_WRONG:'):
                parsed['where_it_went_wrong'] = line.replace('WHERE_IT_WENT_WRONG:', '').strip()
            elif line.startswith('SUGGESTED_FIX:'):
                parsed['suggested_fix'] = line.replace('SUGGESTED_FIX:', '').strip()
            elif line.startswith('SEVERITY:'):
                parsed['severity'] = line.replace('SEVERITY:', '').strip()

        return LogAnalysisResponse(
            what_went_wrong=parsed.get('what_went_wrong', 'Unable to parse'),
            where_it_went_wrong=parsed.get('where_it_went_wrong', 'Unable to parse'),
            suggested_fix=parsed.get('suggested_fix', 'Unable to parse'),
            severity=parsed.get('severity', 'UNKNOWN'),
            raw_analysis=analysis_text
        )

    except Exception as e:
        logger.error(f"Error analysing logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyse logs: {str(e)}"
        )