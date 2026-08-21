from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_banned: Mapped[bool] = mapped_column(
        default=False,
    )

    amount_of_messages: Mapped[int] = mapped_column(
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    spam_messages: Mapped[list["SpamMessages"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    bot_tagged_messages: Mapped[list["BotTaggedMessages"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Messages_Base(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_message_id: Mapped[int] = mapped_column(
        BigInteger,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    text: Mapped[str] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class SpamMessages(Messages_Base):
    __tablename__ = "spam_messages"

    spam_keyword: Mapped[str] = mapped_column(
        String(255),
    )

    user: Mapped["User"] = relationship(
        back_populates="spam_messages",
    )



class BotTaggedMessages(Messages_Base):
    __tablename__ = "bot_tagged_messages"

    tagged_bot_username: Mapped[str] = mapped_column(
        String(255),
    )

    user: Mapped["User"] = relationship(
        back_populates="bot_tagged_messages",
    )

