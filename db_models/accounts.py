from sqlalchemy import Column, String, Integer

from db_models.base import Base


class AccountTransactionTemplate(Base):

    __tablename__ = "accounts_transaction_template"
    __table_args__ = {"schema": "public"}

    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<AccountTransactionTemplate(user={self.user!r}, balance={self.balance})>"