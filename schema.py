import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Department as DepartmentModel, Instructor as InstructorModel, Course as CourseModel
import re

class Department(SQLAlchemyObjectType):
    class Meta:
        model = DepartmentModel
        interfaces = (relay.Node, )


class Instructor(SQLAlchemyObjectType):
    class Meta:
        model = InstructorModel
        interfaces = (relay.Node, )

class Course(SQLAlchemyObjectType):
    class Meta:
        model = CourseModel
        interfaces = (relay.Node, )
    instructors = graphene.List(Instructor)
    prerequisites = graphene.List(lambda: Course)


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    course = relay.Node.Field(Course)
    all_courses = SQLAlchemyConnectionField(Course)


    search = graphene.List(Course, q=graphene.String())  # List field for search results
    #TODO make search robust enough for
          # CS 201
          # COMPSCI 201
          # CS201
          # CS201: Problem Solving

    def resolve_search(self, info, **args):
      q = args.get("q")
      course_query = Course.get_query(info)
      courses = course_query.filter(CourseModel.title.contains(q) | CourseModel.number.contains(re.findall(r'\d+', q)[0])) 
      return courses

    all_instructors= SQLAlchemyConnectionField(Instructor)
    all_departments = SQLAlchemyConnectionField(Department)


    
    


schema = graphene.Schema(query=Query)
schema.execute(context_value={'session': db_session})
