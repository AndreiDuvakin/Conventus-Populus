import smtplib
from json import loads
from email.message import EmailMessage
from data.roles import Roles
from data.users import User
from data.staff_projects import StaffProjects
from data import db_session
import uuid


def check_password(password=''):
    smb = 'qwertyuiopasdfghjklzxcvbnm'
    if len(password) < 6:
        return 'Пароль должен быть длиннее 6 символов'
    elif False in [True if i.isalpha() and i.lower() in smb or i.isdigit() else False for i in password]:
        return 'Пароль может содержать только буквы латинского алфавита и цифры'
    elif True not in [True if i.isdigit() else False for i in password]:
        return 'Пароль должен содержать буквы разного регистра и цифры'
    elif False not in [True if i.islower() and i.isalpha() else False for i in password]:
        return 'Пароль должен содержать буквы разного регистра и цифры'
    else:
        return 'OK'


def mail(msg, to, topic='Подтверждение почты'):
    with open('incepted.config', 'r', encoding='utf-8').read() as file:
        file = loads(file)
    login, password = file["mail_login"], file["mail_password"]
    email_server = "smtp.yandex.ru"
    sender = "incepted@yandex.ru"
    em = EmailMessage()
    em.set_content(msg)
    em['To'] = to
    em['From'] = sender
    em['Subject'] = topic
    mailServer = smtplib.SMTP(email_server)
    mailServer.set_debuglevel(1)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(login, password)
    mailServer.ehlo()
    mailServer.send_message(em)
    mailServer.quit()


def init_db_default():
    data_session = db_session.create_session()
    roles = [['admin', 2], ['moderator', 1], ['user', 0]]
    for i in roles:
        role = Roles(
            name=i[0],
            rights=i[1]
        )
        data_session.add(role)
    data_session.commit()
    data_session.close()


def get_user_data(user):
    resp = {
        'id': user.id,
        'name': user.name,
        'surname': user.surname,
        'login': user.login,
        'email': user.email,
        'photo': user.photo,
        'role': user.role
    }
    return resp


def get_projects_data(project):
    data_session = db_session.create_session()
    staff = data_session.query(StaffProjects.user).filter(StaffProjects.project == project.id).all()
    resp = {
        'id': project.id,
        'name': project.name,
        'logo': project.photo,
        'description': project.description,
        'staff': list(map(lambda x: get_user_data(x), data_session.query(User).filter(
            User.id.in_(list(map(lambda x: x[0], staff)))).all())) if staff else []
    }
    resp['staff'].insert(0, get_user_data(data_session.query(User).filter(User.id == project.creator).first()))
    return resp


def save_project_logo(photo):
    filename = f'static/app_files/project_logo/{uuid.uuid4()}.png'
    with open(filename, 'wb') as f:
        photo.save(f)
    return filename
