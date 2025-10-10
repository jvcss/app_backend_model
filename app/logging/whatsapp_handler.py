"""
Handler de logging para envio de mensagens via WhatsApp
Utiliza Evolution API para envio
"""
import logging
import asyncio
from typing import Optional

from app.services.whatsapp import WhatsAppService


class WhatsAppHandler(logging.Handler):
    """
    Handler customizado para enviar logs via WhatsApp

    Usa Evolution API para envio de mensagens
    """

    def __init__(
        self,
        phone_number: str,
        api_url: str,
        token: str,
        instance: str,
        level: int = logging.WARNING
    ):
        """
        Args:
            phone_number: Número de destino no formato 5562999999999
            api_url: URL da Evolution API
            token: Token de autenticação da Evolution API
            instance: Nome da instância do WhatsApp
            level: Nível mínimo de log para envio
        """
        super().__init__(level)

        self.phone_number = phone_number

        # Inicializa cliente WhatsApp
        try:
            self.client = WhatsAppService(
                api_url=api_url,
                token=token,
                instance=instance
            )
            self.enabled = True
        except Exception as e:
            print(f"Erro ao inicializar WhatsApp client: {e}")
            self.enabled = False

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emite o log record enviando mensagem via WhatsApp
        """
        if not self.enabled:
            return

        try:
            # Formata a mensagem
            message = self.format(record)

            # Limita tamanho da mensagem (WhatsApp tem limite de 1600 caracteres)
            if len(message) > 1500:
                message = message[:1497] + "..."

            # Envia via WhatsApp (método assíncrono)
            asyncio.run(self.client.send_message(self.phone_number, message))

        except Exception as e:
            # Qualquer outro erro
            print(f"Erro inesperado ao enviar WhatsApp: {e}")
            self.handleError(record)


class WhatsAppHandlerAsync(WhatsAppHandler):
    """
    Versão assíncrona do handler (usa Celery task)
    Para evitar bloquear a thread principal
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Envia de forma assíncrona via Celery task
        """
        if not self.enabled:
            return

        try:
            from app.mycelery.worker import send_whatsapp_log

            message = self.format(record)

            # Limita tamanho
            if len(message) > 1500:
                message = message[:1497] + "..."

            # Envia para fila Celery com os parâmetros corretos
            send_whatsapp_log.delay(
                api_url=self.client.api_url,
                token=self.client.token,
                instance=self.client.instance,
                phone_number=self.phone_number,
                message=message
            )

        except Exception as e:
            print(f"Erro ao agendar envio de WhatsApp: {e}")
            # Fallback para envio síncrono
            super().emit(record)
