# from multiprocessing import Process
#
# from payments.models import Payment
#

# class PaymentWorker(Process):
#     def __init__(self, queue):
#         super(PaymentWorker, self).__init__()
#         self.queue = queue
#
#     def run(self):
#         for data in iter(self.queue.get, None):
#
#             pass
#             # payment = Payment.objects.get(pk=473)