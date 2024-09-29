from pydantic import BaseModel, Field

"""
This file declares all the schemas for OpenAPI specification.

In order to export this configuration, run the application and go to the following link:
http://localhost:<api_port>/openapi.json

"""

class Prompt(BaseModel):
    message: str = Field(examples=["What are all the switches available?"])