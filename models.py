from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,
                            backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///database.sqlite3', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


teaching_association = Table('teaching_association', Base.metadata,
    Column('instructor_id', Integer, ForeignKey('instructor.id')),
    Column('course_id', Integer, ForeignKey('course.id'))
)

class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    # Courses
    courses = relationship("Course", back_populates="department") # 1-many

    # TODO Faculty

class Instructor(Base):
    __tablename__ = 'instructor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    website = Column(String) # TODO foreign key to websites with availability

    # Courses
    courses = relationship("Course", secondary=teaching_association, back_populates="instructors") # many-many

prerequisite_association = Table('prerequisite_association', Base.metadata,
    Column('course_id', Integer, ForeignKey('course.id')),
    Column('prereq_id', Integer, ForeignKey('course.id'))
)

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer)
    title = Column(String)
    website = Column(String) # TODO foreign key to websites with availability
    
    # Department
    department_id = Column(Integer, ForeignKey('department.id')) # many-1
    department = relationship("Department", back_populates="courses")

    # Instrucotrs
    instructors = relationship("Instructor", secondary=teaching_association, back_populates="courses") # many-many

    # Prerequisites
    prerequisites = relationship(
      "Course", 
      secondary=prerequisite_association, 
      primaryjoin=id==prerequisite_association.c.course_id,
      secondaryjoin=id==prerequisite_association.c.prereq_id
    ) # many-many

    def __repr__(self):
      return f"{self.title} {self.number} in {self.department.name}"
