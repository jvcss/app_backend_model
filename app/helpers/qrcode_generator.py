# app/helpers/qrcode_generator.py
import qrcode
import io
import base64
from typing import Optional

def generate_qr_code_base64(data: str, box_size: int = 10, border: int = 4) -> str:
    """
    Gera um QR Code a partir de uma string e retorna como Base64.
    
    Args:
        data: String a ser codificada no QR Code (ex: otpauth_url)
        box_size: Tamanho de cada "box" do QR Code (padrão: 10)
        border: Tamanho da borda em boxes (padrão: 4)
    
    Returns:
        String Base64 da imagem PNG do QR Code
    
    Example:
        >>> qr_b64 = generate_qr_code_base64("otpauth://totp/...")
        >>> # No frontend: <img src="data:image/png;base64,{qr_b64}" />
    """
    try:
        # Cria o QR Code
        qr = qrcode.QRCode(
            version=1,  # Tamanho automático
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Gera a imagem
        img = qr.make_image(fill_color="black", back_color="white")

        # Converte para Base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        return img_base64

    except Exception as e:
        # Log do erro em produção
        print(f"Erro ao gerar QR Code: {str(e)}")
        raise ValueError("Falha ao gerar QR Code") from e

def generate_qr_code_data_url(data: str, box_size: int = 10, border: int = 4) -> str:
    """
    Gera QR Code e retorna como Data URL pronto para usar em <img src="...">
    
    Returns:
        String no formato: "data:image/png;base64,iVBORw0KGgo..."
    """
    img_base64 = generate_qr_code_base64(data, box_size, border)
    return f"data:image/png;base64,{img_base64}"

def generate_qr_for_terminal_api(data: str) -> Optional[str]:
    """
    Gera um QR Code simples para exibir no terminal (ASCII).
    Útil para testes rápidos em ambientes sem GUI.
    
    Returns:
        String ASCII do QR Code ou None se falhar.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr.print_ascii(invert=True)
    except Exception as e:
        print(f"Erro ao gerar QR Code para terminal: {str(e)}")
        return None
