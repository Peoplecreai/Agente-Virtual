from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class TravelState:
    """Conversation state for a travel request."""

    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    venue: Optional[str] = None
    reason: Optional[str] = None
    flight_pref: Optional[str] = None
    hotel_pref: Optional[str] = None
    frequent_flyer: Optional[str] = None
    seat_pref: Optional[str] = None
    budget: Optional[str] = None
    passport: Optional[bool] = None
    visa: Optional[bool] = None
    share_room: Optional[bool] = None

    def to_dict(self) -> Dict[str, str]:
        return {k: v for k, v in self.__dict__.items() if v}

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        if not data:
            return cls()
        return cls(**data)
