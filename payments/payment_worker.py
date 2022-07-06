# from multiprocessing import Process
#
# from payments.models import Payment
#
from typing import Optional
import json
import threading
import pika.channel
import logging

from .exceptions import InvalidPaymentPointException, InvalidPaymentCertException
from .models import Payment, PaymentStatusEnum
from .services import refresh_payment, start_payment, refresh_payment_from_provider_payment
from .sl_payment_service import start_provider_payment, get_provider_payment
from .types import ProviderPayment

from .rmq import settings
from .rmq.payment_consumer_service import payment_consumer_service


def payment_worker():
    logger = logging.getLogger('app')

    logger.info(f"Thread '{threading.current_thread().name}' started")

    def payment_massage_handler(ch: pika.channel.Channel, method, properties, body):

        def _worker_wait_task():
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

        def _worker_complete_task():
            ch.basic_ack(delivery_tag=method.delivery_tag)

        def _is_payment_new(payment: Payment) -> bool:
            return not bool(payment.operation_id)

        def _is_need_continue_check(provider_payment: ProviderPayment) -> bool:
            return provider_payment.final == '0'

        def _is_active_payment(payment: Payment) -> bool:
            return payment.final != '1'


        def _get_payment_from_message(body) -> Optional[Payment]:
            payment_message = json.loads(body.decode())
            return Payment.objects.get(pk=payment_message["id"])

        def _error_end_payment(payment: Payment, error="Worker internal error"):
            payment.status = PaymentStatusEnum.ERROR
            payment.final = '1'
            if not payment.provide_error_text:
                payment.provide_error_text = error
            payment.save()




        logger.info(f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- Message received << {body.decode()} >>'")
        payment = _get_payment_from_message(body)

        if not payment:
            logger.warning(f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment not found")
            _worker_complete_task()
            return

        if not _is_active_payment(payment):
            logger.warning(
                f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment ID: {payment.id} -- {payment}  payment is final status")
            _worker_complete_task()
            return


        logger.info(
            f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment ID {payment.id} -- Payment exist  ({payment})")

        try:
            # Если операция новая создаем платеж. Если платеж ранее создан получаем информацию
            provider_payment = start_provider_payment(payment) if _is_payment_new(payment) else get_provider_payment(payment)
            logger.info(f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment ID {payment.id}  -- Received provider payment({provider_payment})")

            if not provider_payment:
                logger.warning(
                    f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment ID {payment.id}  -- Provider payment not found")
                _error_end_payment(payment)
                _worker_complete_task()

            else:
                refresh_payment_from_provider_payment(payment, provider_payment)

                # Проверяем был ли получен финальный статуc. и далее либо завершаем обработку операии либо отправляем на повторную проверку
                if _is_need_continue_check(provider_payment):
                    logger.info(f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment ID: {payment.id} need_continue_check - {provider_payment}")
                    _worker_wait_task()
                else:
                    logger.info(
                        f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment ID: {payment.id} received final status - {provider_payment}")
                    _worker_complete_task()
        except InvalidPaymentPointException as e:
            logger.warning(f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment ID {payment.id}  -- InvalidPaymentPointException {e}")
            _error_end_payment(payment, f'InvalidPaymentPointException {e}')
            _worker_complete_task()
        except InvalidPaymentCertException as e:
            logger.warning(f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment ID {payment.id}  -- InvalidPaymentCertException {e}")
            _error_end_payment(payment, f'InvalidPaymentCertException {e}')
            _worker_complete_task()
        except Exception as e:
            logger.error(f"{threading.current_thread().name} -- payment_worker > payment_massage_handler -- payment ID {payment.id}  -- ERROR {e}")
            _worker_complete_task()


    channel = payment_consumer_service.create_consumer()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=payment_massage_handler)
    channel.start_consuming()


def start_thread_pool(worker_pool=10):
    threads = []
    for i in range(worker_pool):
        t = threading.Thread(target=payment_worker, daemon=True)
        t.start()
        threads.append(t)
    return threads




