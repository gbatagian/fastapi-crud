from uuid import UUID

from fastapi import APIRouter

from models.portfolio import PortfolioModel
from repositories.base import managed_session
from repositories.portfolio import PortfolioRepository
from schemas.portfolio import PortfolioCreateModel
from schemas.portfolio import PortfolioUpdateModel

portfolio_api = APIRouter()


@portfolio_api.get("/portfolios/{portfolio_id}")
def get_portfolio(
    portfolio_id: UUID,
) -> PortfolioModel | None:
    return PortfolioRepository.get(portfolio_id)


@portfolio_api.post("/portfolios")
def create_portfolio(
    portfolio_create: PortfolioCreateModel,
) -> PortfolioModel:
    with managed_session() as session:
        portfolio = PortfolioModel(
            type=portfolio_create.type, user_id=portfolio_create.user_id
        )
        session.add(portfolio)
        session.commit()
        session.refresh(portfolio)

    return portfolio


@portfolio_api.delete("/portfolios/{portfolio_id}")
def delete_portfolio(
    portfolio_id: UUID,
) -> PortfolioModel | None:
    portfolio = PortfolioRepository.get(portfolio_id)
    if portfolio is None:
        return None

    with managed_session() as session:
        session.delete(portfolio)
        session.commit()

    return portfolio


@portfolio_api.put("/portfolios/{portfolio_id}")
def update_portfolio(
    portfolio_id: UUID,
    portfolio_update: PortfolioUpdateModel,
) -> PortfolioModel | None:
    portfolio = PortfolioRepository.get(portfolio_id)
    if portfolio is None:
        return None

    portfolio.update(portfolio_update)

    with managed_session() as session:
        session.add(portfolio)
        session.commit()
        session.refresh(portfolio)

    return portfolio
