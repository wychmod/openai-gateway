import sys
from typing import Optional, List, Union, Dict

from pydantic import BaseModel


class ChatCompletionReq(BaseModel):
    model: str
    messages: List
    temperature: Optional[float]
    top_p: Optional[float]
    n: Optional[int]
    stream: Optional[bool]
    stop: Union[str, List, None]
    max_tokens: Optional[int]
    presence_penalty: Optional[float]
    frequency_penalty: Optional[float]
    logit_bias: Optional[Dict]
    user: Optional[str]
