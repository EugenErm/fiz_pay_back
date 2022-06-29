from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderPayment:
    id: str
    state: str
    substate: str
    code: str
    final: str

    trans: Optional[str] = None
    server_time: Optional[str] = None
    process_time: Optional[str] = None
    provider_error_text: Optional[str] = None
