from multiprocessing import Queue
from OrderCreators import ThreeCommasOrderCreator, BinanceOrderCreator
from SignalReaders import CryptoSignalsReader, GmailSignalReader
import signal
from threading import Thread
import config
import logging

logging.basicConfig(filename=config.LOGGING_FILE, level=logging.INFO)

signal_queue = Queue()
# signal_reader = CryptoSignalsReader()
# order_creator = ThreeCommasOrderCreator()
signal_reader = GmailSignalReader()
order_creator = BinanceOrderCreator()
signal_thread = Thread(target=signal_reader.start_reader, args=('BINANCE', 5, signal_queue,))
signal_thread.daemon = True
execute_service = True


def termination_handler(signum, frame):
        print('Exiting Reader... Signal handler called with signal', signum)
        exit()


if __name__ == '__main__':    
    #Definal signal termination
    signal.signal(signal.SIGINT, termination_handler)
    signal_thread.start()

    base_amount = config.BASE_ORDER_BTC

    while execute_service:
        try:
            signal = signal_queue.get()
            order_creator.place_order(signal, base_amount)
        except ValueError as ve:
            logging.error(ve.args)
        except Exception as e:
            logging.error('Failed creating order for {}:\n{}'.format(signal['coin'], e.args))
