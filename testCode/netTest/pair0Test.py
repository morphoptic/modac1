import pynng
import trio

async def send_and_recv(sender, receiver, message):
    await sender.asend(message)
    return await receiver.arecv()

with pynng.Pair0(listen='tcp://127.0.0.1:54321') as s1, \
        pynng.Pair0(dial='tcp://127.0.0.1:54321') as s2:
    received = trio.run(send_and_recv, s1, s2, b'hello there old pal!')
    print("received: ",received)
    assert received == b'hello there old pal!'
    
    
