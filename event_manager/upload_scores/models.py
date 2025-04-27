from pydantic import BaseModel, Field

class PlayerEntry(BaseModel):
    playerName: str = Field(..., description="Username of the player")
    playerId: int = Field(..., description="Unique Discord or system ID of the player")
    totalEntries: int = Field(..., ge=0, description="Total number of entries, must be zero or positive")

    @classmethod
    def player_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('playerName must not be empty.')
        return v