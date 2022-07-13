# from multiprocessing import Process
#
# from payments.models import Payment
#
import json
import threading
import pika.channel
import logging


from payments.models import Payment
from payments.services.payment_provider_sl_adapter import payment_provider_adapter
from payments.services.payment_service import payment_service as ps
from payments.services.rmq import settings
from payments.services.rmq.payment_consumer_service import payment_consumer_service





def payment_worker():
    payment_provider = payment_provider_adapter
    payment_service = ps
    logger = logging.getLogger('app')

    logger.debug(f"Thread '{threading.current_thread().name}' started")

    def start_provider_payment(payment: Payment):
        logger.debug(f"Thread '{threading.current_thread().name}' -- Start provider payment ID: {payment.id}")
        return payment_provider.create_payout(payment)

    def get_provider_payment(payment: Payment):
        logger.debug(f"'{threading.current_thread().name} -- Get provider payment by ID: {payment.id}")
        return payment_provider.get_payout_by_id(payment.id)

    def get_payment_by_id(id: int):
        return payment_service.get_payment_by_id(id)

    def update_payment_info(provider_payment, payment: Payment):
        logger.debug(f"'{threading.current_thread().name} -- Update payment info Payment ID: {payment.id}; provider_payment: {provider_payment}")
        payment_service.refresh_payment_status_from_provider_payment(payment.id, provider_payment)

    def payment_is_new(payment: Payment) -> bool:
        return not bool(payment.operation_id)

    def is_need_continue_check(payment_info) -> bool:
        return payment_info['final'] == '0'

    def payment_massage_handler(ch: pika.channel.Channel, method, properties, body):
        logger.debug(f"Message << {body.decode()} >> received on thread '{threading.current_thread().name}'")
        payment_message = json.loads(body.decode())

        payment = get_payment_by_id(payment_message["id"])

        if not payment:
            # Если операции несуществует, выводим ошибку
            logger.error(f"{threading.current_thread().name} -- Payment ID: {payment_message['id']} not found")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        logger.debug(
            f"{threading.current_thread().name} -- Payment exist  ({payment}) ")

        # Если операция новая создаем платеж и получаем информацию о нем. Если платеж ранее создан получаем информацию о нем
        provider_payment = start_provider_payment(payment) if payment_is_new(payment) else get_provider_payment(payment)

        logger.debug(
            f"{threading.current_thread().name} -- Received provider_payment ({provider_payment})")

        # Обновляем информацю о платеже в БД
        update_payment_info(provider_payment, payment)

        # Проверяем был ли получен финальный статуc. и далее либо завершаем обработку операии либо отправляем на повторную проверку
        if is_need_continue_check(provider_payment):
            logger.debug(f"{threading.current_thread().name} -- Payment ID: {payment_message['id']} need_continue_check - {provider_payment}")
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        else:
            logger.debug(
                f"{threading.current_thread().name} -- Payment ID: {payment_message['id']} received final status - {provider_payment}")
            ch.basic_ack(delivery_tag=method.delivery_tag)



    channel = payment_consumer_service.create_consumer()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=payment_massage_handler)
    channel.start_consuming()

def start_thread_pool(worker_pool=1):
    threads = []
    for i in range(worker_pool):
        t = threading.Thread(target=payment_worker, daemon=True)
        t.start()
        threads.append(t)
    return threads


