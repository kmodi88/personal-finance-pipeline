from datetime import date
from sqlalchemy import String, Float, Date, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # negative = expense
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=True)
    source_file: Mapped[str] = mapped_column(String(255), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
