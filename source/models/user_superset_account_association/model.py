from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import relationship
from source.repository.database import Base

class UserSupersetAccountAssociation(Base):
    __tablename__ = "user_superset_account_association"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False) 
    superset_user_id = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "superset_user_id", name="uq_user_superset_account"),
    )
    
    user = relationship("User", back_populates="user_superset_accounts") 