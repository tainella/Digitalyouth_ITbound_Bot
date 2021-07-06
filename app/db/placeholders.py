from sqlalchemy import orm

from .models import User, Sphere, Specialist, SphereToSpecialist


def placeholders(session: orm.session.Session):
    # Users
    users = [User(418878871, "teadove", "Петер", "Ибрагимов Петер Ильгизович", "+79778725196"),
             User(346235776, "tainella", "Amelia Zagadka", "Полей-Добронравова Амелия Вадимовна", "+79262895840"),
             User(1409549287, "teameekey", "Петер 2.0", "Иванов Иван Иванович")]
    session.add_all(users)
    # Spheres
    spheres = [Sphere("Дизайн"), Sphere('SMM'), Sphere("Разработка ПО под Windows"), Sphere("Мобильная разработка"),
               Sphere("Консультирование"), Sphere("CRM")]
    session.add_all(spheres)
    # Specialist
    specialist = Specialist(users[0])
    session.add(specialist)
    # Spheres to specialist
    spheres_to_specialist = [SphereToSpecialist(spheres[0], specialist), SphereToSpecialist(spheres[2], specialist),
                             SphereToSpecialist(spheres[4], specialist), SphereToSpecialist(spheres[3], specialist)]

    session.add_all(spheres_to_specialist)

    session.commit()
