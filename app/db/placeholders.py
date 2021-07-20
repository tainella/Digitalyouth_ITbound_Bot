from sqlalchemy import orm

from .models import User, Sphere, Specialist, Representative, Moderator, Task, SphereToSpecialist, SphereToTask


def placeholders(session: orm.session.Session):
    # Users
    users = [User(418878871, "teadove", "Петер", "Ибрагимов Петер Ильгизович", "+79778725196"),
             User(346235776, "tainella", "Amelia Zagadka", "Полей-Добронравова Амелия Вадимовна", "+79262895840"),
             User(1409549287, "teameekey", "Петер 2.0", "Иванов Иван Иванович"),
             User(1624330498, 'elfen_clan', 'Каэде', "Антон Семёнов")]
    session.add_all(users)

    # Spheres
    spheres = [Sphere("Дизайн"), Sphere('SMM'), Sphere("Разработка ПО под Windows"), Sphere("Мобильная разработка"),
               Sphere("Консультирование"), Sphere("CRM"), Sphere("Разработка телеграм ботов"), Sphere("Фронтенд")]
    session.add_all(spheres)

    # Specialist
    specialist = Specialist(users[0])
    session.add(specialist)

    # Spheres to specialist
    spheres_to_specialist = [SphereToSpecialist(spheres[0], specialist), SphereToSpecialist(spheres[2], specialist),
                             SphereToSpecialist(spheres[4], specialist), SphereToSpecialist(spheres[3], specialist),
                             SphereToSpecialist(spheres[-1], specialist)]

    session.add_all(spheres_to_specialist)

    # Representative
    representatives = [Representative(users[1], "ООО название компании"),
                       Representative(users[3], "ООО моя оборона")]

    session.add_all(representatives)

    # Moderator
    moderator = Moderator(users[2], is_admin=True)
    session.add(moderator)

    # Task
    tasks = [Task("Разработать телеграм бота", representatives[0], "Разработать ТГ бота для ведения учёта посещений "
                                                                   "собраний, полное ТЗ при контакте"),
             Task("Разработать дизайн для сайта", representatives[0],
                  "Разработать дизайн для сайта НКО для сборов пожертвований для бездомных", specialist=specialist,
                  status='in_work'),
             Task("Разработать сайт для НКО", representatives[0], status="awaiting_specialist")]
    session.add_all(tasks)

    # SphereToTask
    sphere_to_tasks = [SphereToTask(spheres[-2], tasks[0]), SphereToTask(spheres[-1], tasks[1]),
                       SphereToTask(spheres[0], tasks[1])]
    session.add_all(sphere_to_tasks)

    session.commit()
