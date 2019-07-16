from models import engine, db_session, Base, Department, Course, Instructor
Base.metadata.create_all(bind=engine)

compsci = Department(name="Computer Science", short="COMPSCI")
math = Department(name="Math", short="MATH")
db_session.add(compsci)
db_session.add(math)

john = Instructor(name="John")
paul = Instructor(name="Paul")
db_session.add(john)
db_session.add(paul)

intro_cs = Course(title="Intro to CS", number=101, department=compsci, instructors=[john])
db_session.add(intro_cs)
medium_cs = Course(title="Intermediate CS", number=201, prerequisites=[intro_cs], department=compsci, instructors=[john])
db_session.add(medium_cs)
db_session.commit()

intro_math = Course(title="Intro to Math", number=101, department=math, instructors=[paul])
db_session.add(intro_math)
medium_math = Course(title="Intermediate Math", number=201, prerequisites=[intro_math], department=math, instructors=[paul])
db_session.add(medium_math)
db_session.commit()

advanced_cs = Course(title="Advanced CS", number=301, prerequisites=[medium_cs, medium_math], department=compsci, instructors=[john, paul])
db_session.add(advanced_cs)

db_session.commit()

print(advanced_cs.prerequisites)