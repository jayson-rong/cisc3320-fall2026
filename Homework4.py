from pathlib import Path
import queue
import threading
import time
import multiprocessing

class ThreadBuffer:
    def __init__(self, size):
        self.size = size
        self.queue = queue.Queue(maxsize = size)
        self.lock = threading.Lock()
        self.items_produced = 0
        self.items_consumed = 0
    
    def put_item(self, item, producer):
        isWaiting = False
        
        while True:
            # Only one thread can access the buffer at a time
            with self.lock:
                if not self.queue.full():

                    if isWaiting and item is not None:
                        print(f"[producer {producer}] resumed")

                    self.queue.put(item)

                    # Buffer is not full --> Increase an item count
                    if item is not None:
                        self.items_produced += 1

                    current_size = self.queue.qsize()

                    # Producer can now produce an item into the buffer
                    if item is not None:
                        print(f"[producer {producer}] produced {item} buffer size: {current_size}")

                    break

                # Item in the buffer is full -> producer waits
                if not isWaiting:
                    if item is not None:
                        print(f"[producer {producer}] buffer full - waiting")
                    isWaiting = True

            time.sleep(0.1)

        if item is None:
            return False

        return True

    def get_item(self, consumer):
        
        # Keep checking until an item is removed from buffer
        while True:
            with self.lock:
                if not self.queue.empty():
                    item = self.queue.get()

                    # Item in the buffer --> consume 1
                    if item is not None:
                        self.items_consumed += 1

                    current_size = self.queue.qsize()

                    if item is not None:
                        current_size -= self.queue.queue.count(None)

                    if item is not None:
                        print(f"[consumer {consumer}] consumed {item} buffer size: {current_size}")
                    break

            time.sleep(0.1)

        # Nothing in the buffer
        if item is None:
            print(f"[consumer {consumer}] received stop signal - exiting")
            return None

        return item

    def get_size(self):
        with self.lock:
            return self.queue.qsize()

class Producer(threading.Thread):
    
    def __init__(self, producer, buffer, num_producers):
        threading.Thread.__init__(self)
        self.producer = producer
        self.buffer = buffer
        self.num_producers = num_producers
    
    def producing_Item(self):
        
        try:
            myFile = Path("ReadFile.txt")
            with open(myFile, 'r') as scan:
                index = 0

                for line in scan:
                    
                    item = line.strip()
                    
                    if item == "":
                        index += 1
                        continue
                    
                    if index % self.num_producers == self.producer - 1:
                        self.buffer.put_item(item, self.producer)
                        time.sleep(0.1)

                    index += 1

        except FileNotFoundError:
            print(f"Error: File {myFile} not found.")

    def run(self):
        
        start_time = time.time()
        
        # Same memory address
        # print("Producer Memory Address: ", id(self.buffer))
        
        self.producing_Item()
        end_time = time.time()
        finished_time = end_time - start_time

        print(f"[producer {self.producer}] finished in {finished_time:.2f} units of time.")

class Consumer(threading.Thread):
    
    def __init__(self, consumer, buffer, num_consumers):
        threading.Thread.__init__(self)
        self.consumer = consumer
        self.buffer = buffer
        self.num_consumers = num_consumers

    def consuming_Item(self):
        
        while True:
            
            consumeItem = self.buffer.get_item(self.consumer)
            
            if consumeItem is None:
                break
            time.sleep(0.2)

    def run(self):
        
        start_time = time.time()
        
        # Same Memory Address
        # print("Consumer Memory Address: ", id(self.buffer))
        
        self.consuming_Item()
        end_time = time.time()
        finished_time = end_time - start_time

        print(f"[consumer {self.consumer}] finished in {finished_time:.2f} units of time.")

class MProcessBuffer:

    def __init__(self, size):
        self.size = size
        self.queue = multiprocessing.Queue(maxsize=size)
        self.lock = multiprocessing.Lock()
        
        self.item_produced = multiprocessing.Value('i', 0)
        self.item_consumed = multiprocessing.Value('i', 0)
    
    def Mput_item(self, item, producer):
        
        self.queue.put(item)

        if item is not None:
            with self.item_produced.get_lock():
                self.item_produced.value += 1

            Mcurrent_size = self.queue.qsize()

            print(f"[producer {producer}] produced {item} buffer size: {Mcurrent_size}")

    def Mget_item(self, consumer):

            item = self.queue.get()

            if item is not None:
                with self.item_consumed.get_lock():
                    self.item_consumed.value += 1

                Mcurrent_size = self.queue.qsize()

                print(f"[consumer {consumer}] consumed {item} buffer size: {Mcurrent_size}")

            else:
                print(f"[consumer {consumer}] received stop signal - exiting")

            return item
        
    def Mget_size(self):
        with self.lock:
            return self.queue.qsize()

class MProducer(multiprocessing.Process):
    
    def __init__(self, producer, buffer, number_producer):
        
        multiprocessing.Process.__init__(self)
        self.producer = producer
        self.buffer = buffer
        self.number_producer = number_producer

    def Mproducing_Item(self):

        try:
            myFile = Path("ReadFile.txt")
            with open(myFile, 'r') as scan:
                
                mIndex = 0

                for line in scan:
                    item = line.strip()
                    
                    if item == "":
                        mIndex += 1
                        continue
                    
                    if mIndex % self.number_producer == self.producer - 1:
                        self.buffer.Mput_item(item, self.producer)
                        time.sleep(0.1)
                
                    mIndex += 1
                
        except FileNotFoundError:
            print(f"Error: File {myFile} not found.")
        
    def run(self):
        
        Mstart_time = time.time()

        # Different Memory Address 
        # print("Producer Memory Address: ", id(self.buffer))
        
        self.Mproducing_Item()
        Mend_time = time.time()

        mFinished_time = Mend_time - Mstart_time

        print(f"[producer {self.producer}] finished in {mFinished_time:.2f} units of time.")
    
class MConsumer(multiprocessing.Process):
    
    def __init__(self, consumer, buffer, number_consumer):
        
        multiprocessing.Process.__init__(self)
        self.consumer = consumer
        self.buffer = buffer
        self.number_consumer = number_consumer

    def Mconsuming_Item(self):

        while True:
            
            consumeItem = self.buffer.Mget_item(self.consumer)

            if consumeItem is None:
                break
            time.sleep(0.2)

    def run(self):
        
        Mstart_time = time.time()
        
        # Same Memory address
        # print("Consumer Memory Address: ", id(self.buffer))
        
        self.Mconsuming_Item()
        Mend_time = time.time()
        Mfinished_time = Mend_time - Mstart_time

        print(f"[consumer {self.consumer}] finished in {Mfinished_time:.2f} units of time.")
    
def start_multiprocess():
    
    global shared_Pbuffer
    buffer_Msize = 2
    shared_Pbuffer = MProcessBuffer(buffer_Msize)

    number_producer = 2
    number_consumer = 2

    p_producers = []
    c_consumers = []

    # Start consumers
    for i in range(1, number_consumer + 1):
        c = MConsumer(consumer = i, buffer = shared_Pbuffer, number_consumer = number_consumer)
        c_consumers.append(c)
        c.start()

    # Start producers
    for i in range(1, number_producer + 1):
        p = MProducer(producer = i, buffer = shared_Pbuffer, number_producer = number_producer)
        p_producers.append(p)
        p.start()

    for p in p_producers:
        p.join()

    # Send stop signals
    for i in range(number_consumer):
        shared_Pbuffer.Mput_item(None, "poisonpill")

    for c in c_consumers:
        c.join()

    print(f"\nItems produced: {shared_Pbuffer.item_produced.value}")
    print(f"Items consumed: {shared_Pbuffer.item_consumed.value}")

def start_thread():

    # All threads share a single buffer
    global shared_buffer
    buffer_size = 2
    shared_buffer = ThreadBuffer(buffer_size)
    
    num_producer = 2
    num_consumer = 2
    producers = []
    consumers = []

    # Producer and Consumer begin executing a thread
    for i in range(1, num_consumer + 1):
        c = Consumer(consumer = i, buffer = shared_buffer, num_consumers = num_consumer)
        consumers.append(c)
        c.start()

    for i in range(1, num_producer + 1):
        p = Producer(producer = i, buffer = shared_buffer, num_producers = num_producer)
        producers.append(p)
        p.start()

    # Wait for one thread to finish before moving on to other threads
    for p in producers:
        p.join()

    for i in range(num_consumer):
        shared_buffer.put_item(None, "poisonpill")

    for c in consumers:
        c.join()

    print(f"\nall producers finished, all consumers finished, " f"{shared_buffer.get_size()} items left")

    print(f"\nItems produced: {shared_buffer.items_produced}")
    print(f"Items consumed: {shared_buffer.items_consumed}")

    if shared_buffer.items_produced == shared_buffer.items_consumed:
        print("Items produced == Items consumed")
    else:
        print("Items produced != Items consumed")

if __name__ == "__main__":
    start_thread()
    start_multiprocess()

    # Written: In multithreading, I noticed that producer and consumer shared the same memory space within a process.
    #          In multiprocessing, I noticed that producer and consumer shared the same buffer, but they have separate memory spaces.
