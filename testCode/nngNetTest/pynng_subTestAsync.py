# PyNNG example of Pub/Sub with both normal and async versions
import time
from pynng import Pub0, Sub0, Timeout
import trio


address = 'tcp://127.0.0.1:31313'
sub0 = Sub0(dial=address, recv_timeout=1000)
sub1 = Sub0(dial=address, recv_timeout=1000)
sub2 = Sub0(dial=address, recv_timeout=1000)
sub3 = Sub0(dial=address, recv_timeout=1000)

def syncLoop():
    while True:
        print("sub0 rcv:",sub0.recv())  # prints b'wolf...' since that is the matching message
        print("sub1 rcv:",sub1.recv())  # prints b'puppy...' since that is the matching message

    # sub2 will receive all messages (since empty string matches everything)
        print("sub2 rcv:",sub2.recv())  # prints b'puppy...' since it was sent first
        print("sub2 rcv:",sub2.recv())  # prints b'wolf...' since it was sent second

        try:
            sub3.recv()
            assert False, 'never gets here since sub3 is not subscribed'
        except Timeout:
            print('got a Timeout since sub3 had no subscriptions')
        time.sleep(1)

async def asyncSubLoop( ):
    print("Begin Async Sub Loop")
    while True:
        s = await sub0.arecv()
        print("sub0 rcv:",s)  # prints b'wolf...' since that is the matching message
        s = await sub1.arecv()
        print("sub1 rcv:",s)  # prints b'puppy...' since that is the matching message

        # sub2 will receive all messages (since empty string matches everything)
        #s = await asyncReadSubscriber(sub2)
        print("sub2 rcv:",await sub2.arecv())  # prints b'puppy...' since it was sent first
        print("sub2 rcv:",await sub2.arecv())  # prints b'wolf...' since it was sent second

        try:
            sub3.recv()
            assert False, 'never gets here since sub3 is not subscribed'
        except Timeout:
            print('got a Timeout since sub3 had no subscriptions')

        await trio.sleep(1)
    print ("End forever async subscriber loop")
    pass

if __name__ == "__main__":
    sub0.subscribe(b'wolf')
    sub1.subscribe(b'puppy')
    # The empty string matches everything!
    sub2.subscribe(b'')
    # we're going to send two messages before receiving anything, and this is
    # the only socket that needs to receive both messages.
    sub2.recv_buffer_size = 2
    # sub3 is not subscribed to anything
    # make sure everyone is connected
    print("all set, wait a moment then Publish")
    time.sleep(1)

    #syncLoop()
    trio.run(asyncSubLoop)
    sub0.close()
    sub1.close()
    sub2.close()
    sub3.close()
