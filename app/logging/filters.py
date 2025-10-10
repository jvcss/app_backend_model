"""
Filtros para controlar quais logs são enviados ao WhatsApp
"""
import logging
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Dict

from app.helpers.getters import isDebugMode


class RateLimitFilter(logging.Filter):
    """
    Filtra logs para evitar spam no WhatsApp
    Limita número de mensagens por hora
    """
    
    def __init__(self, max_per_hour: int = 10, window_minutes: int = 60):
        """
        Args:
            max_per_hour: Número máximo de mensagens por hora
            window_minutes: Janela de tempo em minutos para contagem
        """
        super().__init__()
        self.max_per_hour = max_per_hour
        self.window_minutes = window_minutes
        self.message_times: Dict[str, list] = defaultdict(list)
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Retorna True se a mensagem deve ser enviada
        """
        now = datetime.now(timezone.utc)
        
        # Cria chave baseada no nível do log
        key = getattr(record, 'levelname', 'UNKNOWN')
        
        # Remove timestamps antigos
        cutoff = now - timedelta(minutes=self.window_minutes)
        self.message_times[key] = [
            t for t in self.message_times[key] 
            if t > cutoff
        ]
        
        # Verifica se excedeu o limite
        if len(self.message_times[key]) >= self.max_per_hour:
            # Em caso de erro crítico, sempre envia
            if record.levelno >= logging.ERROR:
                return True
            return False
        
        # Adiciona timestamp atual
        self.message_times[key].append(now)
        return True


class EnvironmentFilter(logging.Filter):
    """
    Filtra logs baseado no ambiente
    Em desenvolvimento, não envia para WhatsApp
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Retorna True se deve enviar (apenas em produção)
        """
        # Em debug mode, nunca envia
        if isDebugMode():
            return False
        
        return True


class LevelFilter(logging.Filter):
    """
    Filtra por nível de severidade
    Permite enviar apenas logs importantes
    """
    
    def __init__(self, min_level: int = logging.WARNING):
        """
        Args:
            min_level: Nível mínimo para envio
        """
        super().__init__()
        self.min_level = min_level
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Retorna True se o nível é suficientemente alto
        """
        return record.levelno >= self.min_level


class KeywordFilter(logging.Filter):
    """
    Filtra mensagens que contêm palavras-chave específicas
    Útil para monitorar eventos específicos
    """
    
    def __init__(self, keywords: list = None, blacklist: list = None):
        """
        Args:
            keywords: Lista de palavras-chave para incluir
            blacklist: Lista de palavras-chave para excluir
        """
        super().__init__()
        self.keywords = [k.lower() for k in (keywords or [])]
        self.blacklist = [k.lower() for k in (blacklist or [])]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Retorna True se a mensagem deve ser enviada
        """
        message = record.getMessage().lower()
        
        # Verifica blacklist primeiro
        if self.blacklist and any(word in message for word in self.blacklist):
            return False
        
        # Se não há keywords definidas, passa tudo
        if not self.keywords:
            return True
        
        # Verifica se contém alguma keyword
        return any(word in message for word in self.keywords)


class DeduplicationFilter(logging.Filter):
    """
    Remove mensagens duplicadas em um curto período
    Evita spam de erros repetitivos
    """
    
    def __init__(self, window_seconds: int = 300):
        """
        Args:
            window_seconds: Janela de tempo para considerar duplicatas
        """
        super().__init__()
        self.window_seconds = window_seconds
        self.seen_messages: Dict[str, datetime] = {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Retorna True se não é duplicata recente
        """
        # Cria hash da mensagem
        message_key = f"{record.levelname}:{record.getMessage()[:100]}"
        
        now = datetime.now(timezone.utc)
        
        # Verifica se já vimos essa mensagem recentemente
        if message_key in self.seen_messages:
            last_seen = self.seen_messages[message_key]
            if (now - last_seen).total_seconds() < self.window_seconds:
                return False
        
        # Atualiza timestamp
        self.seen_messages[message_key] = now
        
        # Limpa mensagens antigas (mantém apenas última hora)
        cutoff = now - timedelta(hours=1)
        self.seen_messages = {
            k: v for k, v in self.seen_messages.items()
            if v > cutoff
        }
        
        return True


class CompositeFilter(logging.Filter):
    """
    Combina múltiplos filtros
    Todos devem retornar True para a mensagem passar
    """
    
    def __init__(self, *filters: logging.Filter):
        super().__init__()
        self.filters = filters
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Retorna True apenas se todos os filtros aprovarem
        """
        return all(f.filter(record) for f in self.filters)