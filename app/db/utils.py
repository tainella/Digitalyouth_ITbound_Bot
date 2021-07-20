from typing import Tuple, Optional, Union

from sqlalchemy.orm.session import Session

from .models import Sphere, Task, User


def get_all_interests(session: Session):
    list_to_return = session.query(Sphere).filter_by(status=True).all()
    list_to_return = [association.name for association in list_to_return]
    return list_to_return


def get_opened_tasks(session: Session, interesting_spheres: Tuple[Sphere, ...]):
    if not interesting_spheres:
        interesting_spheres = get_all_interests(session)
    opened_tasks = session.query(Task).filter_by(status='awaiting_specialist').all()
    tasks = []
    for task in opened_tasks:
        common = [sphere for sphere in interesting_spheres if sphere in task.spheres]

        # Если хотя бы одна сфера общая
        if common is not None:
            tasks.append(task)
    return tasks


def get_tasks_for_user(user: User, task_status: Union[str, Tuple[str, ...]]):
    if user.status == 'specialist':
        tasks = user.specialist.tasks
    elif user.status == 'representative':
        tasks = user.representative.tasks
    else:
        raise Exception(f"Ошибка, юзер {user.telegram_id} не является представителем или специалистом")
    curr = []
    if isinstance(task_status, str):
        for task in tasks:
            if task.status == task_status:
                curr.append(task)
    else:
        for task in tasks:
            if task.status in task_status:
                curr.append(task)
    return curr


def get_specialist_spheres(user: User):
    if user.specialist is None:
        raise Exception(f"Ошибка, юзер {user.telegram_id} не является специалистом")
    associations = user.specialist.spheres
    return [association.sphere.name for association in associations]
