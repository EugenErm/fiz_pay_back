import pika
import settings as settings


def init_rmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RMQ_HOST))
    channel = connection.channel()

    # создаем service_a_inner_exch
    channel.exchange_declare(exchange=settings.RMQ_INPUT_EXCHANGE)

    # создаем dead_letter_exchange
    channel.exchange_declare(exchange=settings.RMQ_DEAD_EXCHANGE)

    # создаем service_a_input_q
    channel.queue_declare(
        queue=settings.RMQ_INPUT_QUEUE,
        durable=True,
        arguments={
            'x-dead-letter-exchange': settings.RMQ_DEAD_EXCHANGE,
        }
    )

    # создаем очередь для "мертвых" сообщений
    channel.queue_declare(
        queue=settings.RMQ_DEAD_QUEUE,
        durable=True,
        arguments={
            # благодаря этому аргументу сообщения из service_a_input_q
            # при nack-е будут попадать в dead_letter_exchange
            'x-message-ttl': settings.RMQ_DEAD_TTL,
            # также не забываем, что у очереди "мертвых" сообщений
            # должен быть свой dead letter exchange
            'x-dead-letter-exchange': settings.RMQ_INPUT_EXCHANGE,
        }
    )
    # связываем очередь "мертвых" сообщений с dead_letter_exchange
    channel.queue_bind(
        exchange=settings.RMQ_DEAD_EXCHANGE,
        queue=settings.RMQ_DEAD_QUEUE,
    )

    # связываем основную очередь с входным exchange
    channel.queue_bind(settings.RMQ_INPUT_QUEUE, settings.RMQ_INPUT_EXCHANGE)

    return channel