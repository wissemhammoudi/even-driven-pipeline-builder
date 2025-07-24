from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from source.repository.database import Base

class UserSupersetAccountAssociation(Base):
    __tablename__ = "user_superset_account_association"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    superset_user_id = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "superset_user_id", name="uq_user_superset_account"),
    ) 