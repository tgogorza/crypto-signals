from multiprocessing import Queue
from OrderCreators import ThreeCommasOrderCreator
from SignalReaders import CryptoSignalsReader
import signal
from threading import Thread
import config

signal_queue = Queue()
signal_reader = CryptoSignalsReader()
signal_thread = Thread(target=signal_reader.start_reader, args=('BINANCE', 5, signal_queue,))
signal_thread.daemon = True
order_creator = ThreeCommasOrderCreator()
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
        signal = signal_queue.get()
        order_creator.place_order(signal, base_amount, target_level=config.CRYPTO_SIGNALS_TARGET_LEVEL)
