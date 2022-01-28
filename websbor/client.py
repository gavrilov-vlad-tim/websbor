from requests import Session
from requests import codes
from requests.exceptions import ConnectionError, Timeout


class BaseClient:
    """
    Клиент для получения данных:
        об организации по ИНН, ОКПО или ОГРН
        об отчетах орагнизации по ID организации в БД
    """
    base_url = 'https://websbor.gks.ru/webstat/api/gs'
    orgs_url = f'{base_url}/organizations'
    reports_url = f'{base_url}//organizations/{{}}/forms'
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
            if response.status_code == codes.OK:
                is_response_success = True 
            try:
                response = response.json()
            except ValueError:
                response = response.status_code
        return is_response_success, response
    
    def get_organisations(self, okpo='', inn='', ogrn=''):
        payload = {'okpo': okpo, 'inn': inn, 'ogrn': ogrn}
        return self.send_request('post', self.orgs_url, json=payload)

    def get_organisation_reports(self, org_id=''):
        org_reports_url = self.reports_url.format(org_id)
        return self.send_request('get', org_reports_url)


class WebSborClient(BaseClient):
    """
    Класс-обетка над базовым классом клиента. Реализует логику получения
    объектов и организаций и их отчетов, обеспечивая связывание объектов 
    организаций и объектов отчетов 
    """
    routes_error_messages = {
        'orgs': 'При запросе данных огранизаций с ИНН {} возникла ошибка',
        'reports': 'При запросе отчетов для огранизации с ID {} возникла ошибка' 
    }
    default_error_message = 'Роут с таким именем отсутствуте. ID объекта запроса: {}'

    def check_response_status(self, status, response, object_id, route_name):
        """
        Метод реализует проверку ответа возвращенного сервисом ФСГС. Если 
        status имеет занчие False (запрос завершился неудачно) то, 
        будет выведено сообщении с кодом ответа сервиса.
        """
        if not status:
            message = self.routes_error_messages.get(route_name, 
                                                     self.default_message)
            print(message.format(object_id))
            print(f'Ответ сервера: {response}')
        return status

    def get_organisations_by_inn(self, inn):
        """
        Метод реализует получение объектов организации, принадлежащих юридическому
        лицу с указанным ИНН, а такаже получение отчетов для найденных организаций
        """
        # is_success - статус ответa (True/False)
        is_success, orgs = self.get_organisations(inn=inn)

        if not self.check_response_status(is_success, orgs, inn, 'orgs'):
            return

        for org in orgs:
            org_id = org.get('id')
            reports = self.get_reports(org_id)
            reports = reports if reports else []
            org.update(reports=reports)
        return orgs

    def get_reports(self, org_id):
        """
        Метод реализует получение отчетов для организации по пераданному ID организации
        """
        if org_id is None:
            return

        is_success, reports = self.get_organisation_reports(org_id)
        
        if not self.check_response_status(is_success, reports, org_id, 'reports'):
            return
        return reports

    def get_organisations_by_inns_list(self, inns=None):
        """
        Получение данных организаций по списку ИНН
        """
        total_orgainisations = []

        if inns is None:
           return total_orgainisations

        for inn in inns:
            organisations = self.get_organisations_by_inn(inn)
            if organisations:
                total_orgainisations.extend(organisations)
        return total_orgainisations    
