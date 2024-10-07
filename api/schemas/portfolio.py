from uuid import UUID

from pydantic import BaseModel

from enums.portfolio_type import PortfolioType


class PortfolioCreate(BaseModel):
    type: PortfolioType
    user_id: UUID


class PortfolioUpdate(BaseModel):
    type: PortfolioType
