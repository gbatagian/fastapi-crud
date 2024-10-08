from uuid import UUID

from pydantic import BaseModel

from enums.portfolio_type import PortfolioType


class PortfolioCreateModel(BaseModel):
    type: PortfolioType
    user_id: UUID


class PortfolioUpdateModel(BaseModel):
    type: PortfolioType | None = None
