from celery import Celery
"""
Este módulo configura e inicializa uma instância do Celery para gerenciamento de tarefas assíncronas.

- Importa as configurações de broker e backend do módulo de configuração da aplicação.
- Cria o objeto `celery_app` com as seguintes opções:
    - `broker_url`: URL do broker de mensagens utilizado pelo Celery.
    - `result_backend`: Backend utilizado para armazenar os resultados das tarefas.
    - Serialização das tarefas e resultados em formato JSON.
    - Aceita apenas conteúdo no formato JSON.
    - Inclui o módulo de workers para descoberta automática de tarefas.
    - Define opções de transporte do broker, como número máximo de tentativas de reconexão e tempo de visibilidade das tarefas.

Utilize `celery_app` para registrar e executar tarefas assíncronas na aplicação.
"""
from app.core.config import CELERY_BROKER_URL_CASE, CELERY_BROKER_URL_CASE, CELERY_RESULT_BACKEND_CASE

celery_app = Celery(
    broker_url = CELERY_BROKER_URL_CASE,
    result_backend = CELERY_RESULT_BACKEND_CASE,
    task_serializer = 'json',
    result_serializer = 'json',
    accept_content = ['json'],
    include=["app.mycelery.worker"],
    broker_transport_options={
        'max_retries': 6,
        'visibility_timeout': 365*24*60*60,
    }
)
