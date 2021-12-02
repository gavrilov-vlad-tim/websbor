from requests import ConnectionError, Session
from requests.exceptions import Timeout


class WebSborClient:
    """
    Клиент для получения данных:
        об организации по ИНН, ОКПО или ОГРН
        об отчетах орагнизации по ID организации в БД
    """
    base_url = 'https://websbor.gks.ru/webstat/api/gs'
    orgs_url = f'{base_url}/organizations'
    indexes_url = f'{base_url}//organizations/{{}}/forms'
    timeout = 2

    def __init__(self, session=None, base_url=None):
        self.base_url = base_url if base_url else self.base_url
        self.session = session if session else Session()

    def send_request(self, method_name, url, **kwargs):
        method = getattr(self.session, method_name)
        response = None
        try:
            response = method(url, timeout=self.timeout, **kwargs)
        except ConnectionError:
            print('Ошибка подключения')
        except Timeout:
            print('Превышено время ожидания ответа')
        return self.parse_response(response)
    
    def parse_response(self, response):
        is_response_success = False
        if response is not None:
            if response.status_code == 200:
                is_response_success = True 
            try:
                response = response.json()
            except ValueError:
                response = None
        return is_response_success, response
    
    def get_orgs(self, okpo='', inn='', ogrn=''):
        payload = {'okpo': okpo, 'inn': inn, 'ogrn': ogrn}
        return self.send_request('post', self.orgs_url, json=payload)

    def get_org_reports(self, org_id=''):
        org_reports_url = self.indexes_url.format(org_id)
        return self.send_request('get', org_reports_url)



class OrgDataGet:
    """
    Класс получения данных организации их форматирования
    """
    org_db_id_field = 'id'

    def __init__(self, client):
        self.client = client
        self.orgs = []
        self.orgs_reports = []
    
    def get_org_data(self, inn):
        status, orgs_data = self.client.get_org_data(inn=inn)

        if not status:
            print(f'При запросе данных для огранизации с ИНН {inn} возникла ошибка')
            print(f'Ответ сервера: {orgs_data}')
            return

        self.orgs.extend(orgs_data)
        for org in orgs_data:
            org_id = org.get(self.org_db_id_field)
            if org_id:
                self.get_org_reports(org_id)

    def get_org_reports(self, org_id):
        status, org_reports_data = self.client.get_org_reports(org_id)
        
        if not status:
            print(f'При запросе отчетов для огранизации с ID {org_id} возникла ошибка')
            print(f'Ответ сервера: {org_reports_data}')
            return

        for org_report in org_reports_data:
            org_report.update(id=org_id)
        self.orgs_reports.extend(org_reports_data)

    def collect_data(self, inns=None):
        if not inns:
            return

        for inn in inns:
            self.get_org_data(inn)
    


        





