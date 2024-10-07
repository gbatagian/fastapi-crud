from enum import Enum
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from models.portfolio import PortfolioModel
from models.portfolio import PortfolioORM
from repositories.base import SessionManager
from repositories.base import get_db
from repositories.portfolio import PortfolioRepository
from schemas.portfolio import PortfolioCreate
from schemas.portfolio import PortfolioUpdate

portfolio_api = APIRouter()


@portfolio_api.get("/portfolios/{portfolio_id}")
def get_portfolio(
    portfolio_id: UUID, db: SessionManager = Depends(get_db)
) -> PortfolioModel | None:
    return PortfolioRepository(db=db).get(portfolio_id)


@portfolio_api.post("/portfolios")
def create_portfolio(
    portfolio_create: PortfolioCreate, db: SessionManager = Depends(get_db)
) -> PortfolioModel:
    with db.session as session:
        portfolio_orm = PortfolioORM(
            type=portfolio_create.type, user_id=portfolio_create.user_id
        )
        session.add(portfolio_orm)
        session.commit()
        session.refresh(portfolio_orm)

    return PortfolioModel.model_validate(portfolio_orm)


@portfolio_api.delete("/portfolios/{portfolio_id}")
def delete_portfolio(
    portfolio_id: UUID, db: SessionManager = Depends(get_db)
) -> PortfolioModel | None:
    portfolio = PortfolioRepository(db=db).get(portfolio_id)
    if portfolio is None:
        return None

    with db.session as session:
        session.delete(portfolio.orm_model)
        session.commit()

    return portfolio


@portfolio_api.put("/portfolios/{portfolio_id}")
def update_portfolio(
    portfolio_id: UUID,
    portfolio_update: PortfolioUpdate,
    db: SessionManager = Depends(get_db),
) -> PortfolioModel | None:
    portfolio = PortfolioRepository(db=db).get(portfolio_id)
    if portfolio is None:
        return None

    for field in portfolio_update.model_fields.keys():
        update_value = getattr(portfolio_update, field)
        if not update_value:
            continue
        if isinstance(update_value, Enum):
            update_value = update_value.value

        db_field_value = getattr(portfolio.orm_model, field)
        if update_value != db_field_value:
            setattr(portfolio.orm_model, field, update_value)

    with db.session as session:
        session.add(portfolio.orm_model)
        session.commit()
        session.refresh(portfolio.orm_model)

    return portfolio
