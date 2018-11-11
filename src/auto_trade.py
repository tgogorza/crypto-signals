from multiprocessing import Process, Queue
from OrderCreators import ThreeCommasOrderCreator
from SignalReaders import CryptoSignalsReader
 
if __name__ == '__main__':
    signal_queue = Queue()
    signal_reader = CryptoSignalsReader()
    order_creator = ThreeCommasOrderCreator()
    p = Process(target=signal_reader.start_reader, args=('BINANCE', 5, signal_queue,))
    #p.daemon = True
    p.start()

    base_amount = 0.0015

    while True:
        signal = signal_queue.get()
        order_creator.place_order(signal, base_amount)