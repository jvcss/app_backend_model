"""
Script para testar o sistema de logging customizado
Execute: python test_logging.py
"""
import asyncio
import time
from app.logging import get_logger

# Cria logger para testes
logger = get_logger("test_module")


def test_warning():
    """Testa log de warning"""
    print("\n=== TESTANDO WARNING ===")
    logger.warning(
        "Taxa de uso de memória alta",
        memory_percent=85,
        threshold=80,
        server="web-01"
    )


def test_info():
    """Testa log de info"""
    print("\n=== TESTANDO INFO ===")
    logger.info(
        "Novo usuário cadastrado",
        user_id=12345,
        email="teste@exemplo.com",
        plan="premium"
    )


def test_request():
    """Testa log de request"""
    print("\n=== TESTANDO REQUEST ===")
    logger.request(
        "API request processada",
        method="POST",
        path="/api/auth/login",
        status_code=200,
        duration=0.152,
        user_id=123
    )


def test_error():
    """Testa log de error"""
    print("\n=== TESTANDO ERROR ===")
    try:
        # Simula um erro
        result = 1 / 0
    except ZeroDivisionError:
        logger.error(
            "Erro ao processar pagamento",
            exc_info=True,
            payment_id=9876,
            amount=150.50
        )


def test_slow():
    """Testa log de operação lenta"""
    print("\n=== TESTANDO SLOW ===")
    
    # Simula operação lenta
    start = time.time()
    time.sleep(2.5)
    duration = time.time() - start
    
    logger.slow(
        "Query do banco de dados muito lenta",
        duration=duration,
        threshold=1.0,
        query="SELECT * FROM users WHERE active = TRUE",
        rows_returned=15000
    )


def test_great():
    """Testa log de sucesso"""
    print("\n=== TESTANDO GREAT ===")
    logger.great(
        "Deploy em produção finalizado!",
        version="2.1.0",
        environment="production",
        duration=120,
        services_updated=5
    )


def test_complex_scenario():
    """Testa cenário complexo"""
    print("\n=== TESTANDO CENÁRIO COMPLEXO ===")
    
    # Simula processo com múltiplos logs
    logger.info("Iniciando processo de migração de dados")
    
    try:
        # Primeira fase
        logger.info("Fase 1: Validando dados", records_to_migrate=10000)
        time.sleep(0.5)
        
        # Segunda fase (com warning)
        logger.warning(
            "Fase 2: Dados inconsistentes encontrados",
            inconsistent_records=50
        )
        time.sleep(0.5)
        
        # Terceira fase (simulando lentidão)
        start = time.time()
        time.sleep(2.2)
        duration = time.time() - start
        logger.slow(
            "Fase 3: Migração de registros grande",
            duration=duration,
            threshold=2.0,
            records_processed=10000
        )
        
        # Finalização
        logger.great(
            "Migração concluída com sucesso!",
            total_records=10000,
            successful=9950,
            failed=50,
            duration=3.5
        )
        
    except Exception as e:
        logger.error(
            "Falha crítica na migração",
            exc_info=True
        )


def test_all():
    """Executa todos os testes"""
    print("=" * 60)
    print("INICIANDO TESTES DO SISTEMA DE LOGGING")
    print("=" * 60)
    
    test_warning()
    time.sleep(0.5)
    
    test_info()
    time.sleep(0.5)
    
    test_request()
    time.sleep(0.5)
    
    test_error()
    time.sleep(0.5)
    
    test_slow()
    time.sleep(0.5)
    
    test_great()
    time.sleep(0.5)
    
    test_complex_scenario()
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)
    print("\nVerifique:")
    print("1. Console para ver os logs")
    print("2. WhatsApp (se configurado) para notificações")
    print("\nNOTA: Em modo desenvolvimento, WhatsApp está desabilitado")


if __name__ == "__main__":
    test_all()
