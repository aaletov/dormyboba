from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class AcademicType(Base):
    __tablename__ = 'academic_type'
    __table_args__ = (
        PrimaryKeyConstraint('type_id', name='academic_type_pkey'),
    )

    type_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_name: Mapped[Optional[str]] = mapped_column(String(50))

    dormyboba_user: Mapped[List['DormybobaUser']] = relationship('DormybobaUser', back_populates='academic_type')
    mailing: Mapped[List['Mailing']] = relationship('Mailing', back_populates='academic_type')


class DormybobaRole(Base):
    __tablename__ = 'dormyboba_role'
    __table_args__ = (
        PrimaryKeyConstraint('role_id', name='dormyboba_role_pkey'),
        UniqueConstraint('role_name', name='dormyboba_role_role_name_key')
    )

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[Optional[str]] = mapped_column(String(50))

    dormyboba_user: Mapped[List['DormybobaUser']] = relationship('DormybobaUser', back_populates='role')


class Institute(Base):
    __tablename__ = 'institute'
    __table_args__ = (
        PrimaryKeyConstraint('institute_id', name='institute_pkey'),
    )

    institute_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    institute_name: Mapped[Optional[str]] = mapped_column(String(50))

    dormyboba_user: Mapped[List['DormybobaUser']] = relationship('DormybobaUser', back_populates='institute')
    mailing: Mapped[List['Mailing']] = relationship('Mailing', back_populates='institute')


class Queue(Base):
    __tablename__ = 'queue'
    __table_args__ = (
        PrimaryKeyConstraint('queue_id', name='queue_pkey'),
    )

    queue_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[Optional[str]] = mapped_column(String(256))
    open: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    close: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    user: Mapped[List['DormybobaUser']] = relationship('DormybobaUser', secondary='queue_to_user', back_populates='queue')


class SentToken(Base):
    __tablename__ = 'sent_token'
    __table_args__ = (
        PrimaryKeyConstraint('sent_token_id', name='sent_token_pkey'),
        UniqueConstraint('token', name='sent_token_token_key'),
        UniqueConstraint('user_id', name='sent_token_user_id_key')
    )

    sent_token_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[Optional[str]] = mapped_column(String(1024))
    user_id: Mapped[Optional[int]] = mapped_column(Integer)


class DormybobaUser(Base):
    __tablename__ = 'dormyboba_user'
    __table_args__ = (
        ForeignKeyConstraint(['academic_type_id'], ['academic_type.type_id'], name='dormyboba_user_academic_type_id_fkey'),
        ForeignKeyConstraint(['institute_id'], ['institute.institute_id'], name='dormyboba_user_institute_id_fkey'),
        ForeignKeyConstraint(['role_id'], ['dormyboba_role.role_id'], name='dormyboba_user_role_id_fkey'),
        PrimaryKeyConstraint('user_id', name='dormyboba_user_pkey'),
        UniqueConstraint('peer_id', name='dormyboba_user_peer_id_key')
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    peer_id: Mapped[Optional[int]] = mapped_column(Integer)
    role_id: Mapped[Optional[int]] = mapped_column(Integer)
    academic_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    institute_id: Mapped[Optional[int]] = mapped_column(Integer)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    group: Mapped[Optional[str]] = mapped_column(String(5))

    queue: Mapped[List['Queue']] = relationship('Queue', secondary='queue_to_user', back_populates='user')
    academic_type: Mapped['AcademicType'] = relationship('AcademicType', back_populates='dormyboba_user')
    institute: Mapped['Institute'] = relationship('Institute', back_populates='dormyboba_user')
    role: Mapped['DormybobaRole'] = relationship('DormybobaRole', back_populates='dormyboba_user')


class Mailing(Base):
    __tablename__ = 'mailing'
    __table_args__ = (
        ForeignKeyConstraint(['academic_type_id'], ['academic_type.type_id'], name='mailing_academic_type_id_fkey'),
        ForeignKeyConstraint(['institute_id'], ['institute.institute_id'], name='mailing_institute_id_fkey'),
        PrimaryKeyConstraint('mailing_id', name='mailing_pkey')
    )

    mailing_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    theme: Mapped[Optional[str]] = mapped_column(String(256))
    mailing_text: Mapped[Optional[str]] = mapped_column(Text)
    at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    academic_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    institute_id: Mapped[Optional[int]] = mapped_column(Integer)
    year: Mapped[Optional[int]] = mapped_column(Integer)

    academic_type: Mapped['AcademicType'] = relationship('AcademicType', back_populates='mailing')
    institute: Mapped['Institute'] = relationship('Institute', back_populates='mailing')


t_queue_to_user = Table(
    'queue_to_user', Base.metadata,
    Column('user_id', Integer, primary_key=True, nullable=False),
    Column('queue_id', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['queue_id'], ['queue.queue_id'], name='queue_to_user_queue_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['dormyboba_user.user_id'], name='queue_to_user_user_id_fkey'),
    PrimaryKeyConstraint('user_id', 'queue_id', name='queue_to_user_pkey')
)
