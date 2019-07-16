from models import engine, db_session, Base, Department, Course, Instructor, Website
Base.metadata.create_all(bind=engine)
import urllib
from bs4 import BeautifulSoup
import re

pattern = r"([^\s]+)\s*?([0-9]{3,})\s*?"
# re.findall(pattern, string.split("Prereq")[-1])

def check_available(url):
  return url != "" # TODO actually check website

def parse_number(course):
  if course.find('a'):
    return course.find('a')['name'].strip()

def parse_title(course):
  if course.find('a'):
    return course.find('a').text.split(':')[-1].strip()

def parse_website(course):
  if course.find('a'):
    url = course.find('a')['href']
    available = check_available(url) 
    return url, available
  return None,None

def parse_instructors(instructors):
  return [i.strip() for i in instructors.text[15:].split(',')]

def parse_prerequisites(prereqs):
  return re.findall(pattern, prereqs.text.split("Prereq")[-1])

def get_or_create(session, model, **kwargs):
  instance = session.query(model).filter_by(**kwargs).first()
  if instance:
      return instance
  else:
      instance = model(**kwargs)
      session.add(instance)
      session.commit()
      return instance

def add_course(number, title, website, instructors, prereqs):
  compsci = get_or_create(db_session, Department, short="COMPSCI", name="Computer Science")
  course = get_or_create(db_session, Course, number=number, department=compsci)
  course.title = title
  course.website = website
  for name in instructors:
    instructor = get_or_create(db_session, Instructor, name=name)
    
    if course.instructors:
      course.instructors.append(instructor) 
    else:
      course.instructors = [instructor]

  last_department = None
  last_department_code = ""

  for department_code, number in prereqs:
    department_codes = db_session.query(Department).filter(Department.short.contains(last_department_code))
    if department_code.lower() not in [code.short.lower() for code in department_codes] and last_department:
      department = last_department
    else:
      department = get_or_create(db_session, Department, short=department_code)
    last_department = department
    prereq = get_or_create(db_session, Course, number=number, department=department)
    if course.prerequisites:
      course.prerequisites.append(prereq) 
    else:
      course.prerequisites = [prereq]
  

soup = BeautifulSoup(open('list.html').read(), "lxml").find('div', {"class": "field-item"})
for dom_course in soup.findAll('h2'):
  title = parse_title(dom_course)
  number = parse_number(dom_course)
  if not title:
    continue

  dom_instructors = dom_course.find_next_sibling("h3")
  instructors = parse_instructors(dom_instructors)

  dom_prereqs = dom_instructors.find_next_sibling("p")
  prereqs = parse_prerequisites(dom_prereqs)

  url, available = parse_website(dom_course)
  website = get_or_create(db_session, Website, url=url, available=available)


  add_course(number, title, website, instructors, prereqs)

