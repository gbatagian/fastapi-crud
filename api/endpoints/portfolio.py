from uuid import UUID

from fastapi import APIRouter

from models.portfolio import PortfolioModel
from repositories.base import managed_session
from repositories.portfolio import PortfolioRepository
from schemas.portfolio import PortfolioCreateModel
from schemas.portfolio import PortfolioUpdateModel

portfolio_api = APIRouter()


@portfolio_api.get("/portfolios/{portfolio_id}")
async def get_portfolio(
    portfolio_id: UUID,
) -> PortfolioModel | None:
    return await PortfolioRepository.get(portfolio_id)


@portfolio_api.post("/portfolios")
async def create_portfolio(
    portfolio_create: PortfolioCreateModel,
) -> PortfolioModel:
    async with managed_session() as session:
        portfolio = PortfolioModel(
            type=portfolio_create.type, user_id=portfolio_create.user_id
        )
        session.add(portfolio)
        await session.commit()
        await session.refresh(portfolio)

    return portfolio


@portfolio_api.delete("/portfolios/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: UUID,
) -> PortfolioModel | None:
    portfolio = await PortfolioRepository.get(portfolio_id)
    if portfolio is None:
        return None

    async with managed_session() as session:
        await session.delete(portfolio)
        await session.commit()

    return portfolio


@portfolio_api.put("/portfolios/{portfolio_id}")
async def update_portfolio(
    portfolio_id: UUID,
    portfolio_update: PortfolioUpdateModel,
) -> PortfolioModel | None:
    portfolio = await PortfolioRepository.get(portfolio_id)
    if portfolio is None:
        return None

    portfolio.update(portfolio_update)

    async with managed_session() as session:
        session.add(portfolio)
        await session.commit()
        await session.refresh(portfolio)

    return portfolio
