from typing import Optional

from pydantic import BaseModel



class CreatePaymentDto(BaseModel):
    pam: str
    name: str
    last_name: str
    middle_name: Optional[str]
    amount: int
