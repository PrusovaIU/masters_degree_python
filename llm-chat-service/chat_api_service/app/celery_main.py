from chat_api_service.app.infra.celery_app import celery_app

if __name__ == '__main__':
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=100',
        '--pool=custom'
    ])
