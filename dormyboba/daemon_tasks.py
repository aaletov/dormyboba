from time import sleep
import datetime
from vkbottle import CtxStorage, Keyboard, Text
from sqlalchemy import select, and_, delete, or_, and_, update
from sqlalchemy.orm import Session
from .config import ALCHEMY_SESSION_KEY, api
from .model.generated import Mailing, DormybobaUser, Queue, QueueToUser
from .handlers.random import random_id

async def mailing_task() -> None:
    try:
        session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
        stmt = select(Mailing).where(
            or_(
                Mailing.at == None,
                datetime.datetime.now() > Mailing.at
            )
        )
        mailings = session.execute(stmt).all()
        # Only registered
        stmt = select(DormybobaUser).where(
            and_(
                DormybobaUser.institute_id != None,
                DormybobaUser.academic_type_id != None,
                DormybobaUser.year != None,
            )
        )
        users = session.execute(stmt).all()
        for row in mailings:
            mailing: Mailing = row[0]
            relevant_users = []
            for urow in users:
                user: DormybobaUser = urow[0]
                condition = (
                    ((mailing.academic_type_id is None) or
                        (mailing.academic_type_id == user.academic_type_id)) and
                    ((mailing.institute_id is None) or
                        (mailing.institute_id == user.institute_id)) and
                    ((mailing.year is None) or
                        (mailing.year == user.year))
                )
                if condition:
                    relevant_users.append(user)

            message = ""
            if mailing.theme is None:
                message = mailing.mailing_text
            else:
                message = mailing.theme + "\n\n" + mailing.mailing_text
            await api.messages.send(
                user_ids=list([user.user_id for user in relevant_users]),
                message=message,
                random_id=random_id(),
            )
            stmt = delete(Mailing).where(Mailing.mailing_id == mailing.mailing_id)
            session.execute(stmt)
            session.commit()
    except Exception as exc:
        print(exc)

def build_join_keyboard(queue_id: int) -> str:
    return (
        Keyboard(inline=True)
        .add(Text(
            label="Занять очередь",
            payload={"command": "queue_join", "queue_id": queue_id},
        ))
        .get_json()
    )

async def queue_task() -> None:
    try:
        session: Session = CtxStorage().get(ALCHEMY_SESSION_KEY)
        stmt = select(Queue).where(
            and_(
                datetime.datetime.now() > Queue.open,
                Queue.is_opened == False,
            )
        )
        queues = session.execute(stmt).all()
        
        stmt = select(DormybobaUser)
        users = session.execute(stmt).all()

        for row in queues:
            queue: Queue = row[0]
            message = (
                "Открыта очередь" +
                " " +
                f"\"{queue.title}\""
            )
            if queue.description is not None:
                message += (
                    "\n\n" +
                    queue.description
                )
            await api.messages.send(
                user_ids=list([user[0].user_id for user in users]),
                message=message,
                random_id=random_id(),
                keyboard=build_join_keyboard(queue.queue_id),
            )
            stmt = update(Queue).where(Queue.queue_id == queue.queue_id).values(
                is_opened = True,
            )
            session.execute(stmt)
            session.commit()
    except Exception as exc:
        print(exc)
    