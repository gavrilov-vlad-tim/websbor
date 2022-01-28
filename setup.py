from setuptools import setup

with open('requirements.txt') as reqs_file:
    reqs = [str(line.strip()) for line in reqs_file.readlines()]

setup(
    name='websbor_client',
    version='0.1',
    description='Клиент для WEB API сервиса федеральной службы государственной статистики',
    packages=['websbor'],
    url='https://github.com/gavrilov-vlad-tim/orgs_legal_info.git',
    install_requires=reqs
)