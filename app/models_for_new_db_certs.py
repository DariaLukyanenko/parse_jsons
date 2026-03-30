# -*- coding: utf-8 -*-
from contextvars import ContextVar
import logging
from typing import Any, Optional
from sqlalchemy import (Column, Date, DateTime, ForeignKey, Index, Integer, String,
                        UniqueConstraint, func, Integer, Text, TypeDecorator, 
                        ForeignKeyConstraint, BigInteger, text, types)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.core.db import Base
from app.log import log_function

# Контекстная переменная для хранения информации о текущей записи
current_record_context: ContextVar[Optional[dict]] = ContextVar('current_record_context', default=None)


class RecordContext:
    """Контекстный менеджер для установки информации о текущей записи"""
    
    def __init__(self, record_type: str, record_id: Any = None, extra_info: str = None):
        """
        Args:
            record_type: Тип записи (Certificate, Applicant, Manufacturer и т.д.)
            record_id: ID записи (idCertificate, inn и т.д.)
            extra_info: Дополнительная информация (номер сертификата и т.д.)
        """
        self.context_data = {
            "record_type": record_type,
            "record_id": record_id,
            "extra_info": extra_info
        }
        self.token = None
    
    def __enter__(self):
        self.token = current_record_context.set(self.context_data)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        current_record_context.reset(self.token)
        return False
    
    @staticmethod
    def get_context_string() -> str:
        """Получить строку с информацией о текущем контексте"""
        ctx = current_record_context.get()
        if ctx is None:
            return "Контекст не установлен"
        
        parts = []
        if ctx.get("record_type"):
            parts.append(f"Тип: {ctx['record_type']}")
        if ctx.get("record_id"):
            parts.append(f"ID: {ctx['record_id']}")
        if ctx.get("extra_info"):
            parts.append(f"Доп.инфо: {ctx['extra_info']}")
        
        return " | ".join(parts) if parts else "Контекст пуст"
    
    
class TruncatedStringWithLog(types.TypeDecorator):
    impl = types.String
    cache_ok = True
    
    def __init__(self, length=255, *args, **kwargs):
        super().__init__(length, *args, **kwargs)
        self.length = length
    
    def process_bind_param(self, value, dialect):
        if value is not None and isinstance(value, str) and len(value) > self.length:
            original_length = len(value)
            truncated_value = value[:self.length]
            
            # Получаем контекст текущей записи
            context_info = RecordContext.get_context_string()
            
            logging.warning(
                f"Обрезка строки. [{context_info}] "
                f"Исходная длина: {original_length}, обрезано до: {self.length}. "
                f"Начало строки: '{truncated_value[:50]}...'"
            )
            
            return truncated_value
        return value
    
    
class ContactMixin:
    """Абстрактный набор колонок для контактных таблиц."""
    idContact = Column(Integer, nullable=False)
    idContactType = Column(Integer)
    value = Column(TruncatedStringWithLog(255))

    date_from = Column(DateTime)
    date_to = Column(DateTime)
    created_at = Column(DateTime)
    

class AddressMixin:
    """Абстрактный набор колонок для адресных таблиц."""
    idAddress = Column(Integer, nullable=False)
    idAddrType = Column(Integer)
    idCodeOksm = Column(TruncatedStringWithLog(255))
    oksmShort = Column(Integer)

    idSubject = Column(TruncatedStringWithLog(255))
    idDistrict = Column(TruncatedStringWithLog(255))
    idCity = Column(TruncatedStringWithLog(255))
    idLocality = Column(TruncatedStringWithLog(255))
    idStreet = Column(TruncatedStringWithLog(255))
    idHouse = Column(TruncatedStringWithLog(255))

    flat = Column(TruncatedStringWithLog(255))
    postCode = Column(TruncatedStringWithLog(255))

    fullAddress = Column(TruncatedStringWithLog(255))
    gln = Column(TruncatedStringWithLog(255))

    foreignDistrict = Column(TruncatedStringWithLog(255))
    foreignCity = Column(TruncatedStringWithLog(255))
    foreignLocality = Column(TruncatedStringWithLog(255))
    foreignStreet = Column(TruncatedStringWithLog(255))
    foreignHouse = Column(TruncatedStringWithLog(255))

    uniqueAddress = Column(TruncatedStringWithLog(255))
    otherGln = Column(TruncatedStringWithLog(255))
    glonass = Column(TruncatedStringWithLog(255))

    date_from = Column(DateTime)
    date_to = Column(DateTime)
    created_at = Column(DateTime)


