# Internet Protocols

## TCP
Transmission Control Protocol.  Commonly refered to as TCP/IP.  Connection based,  Request-response oriented protocol.

IP refers to the Internet Protocol which defines how we send & share information between computers.  It involves sending packets of data which consist of headers (metadata like IP address) and a payload of the actual message.  This is commonly paired with a protocol such as TCP to offer features such as delivery guarantee, non-duplicated packets, and in-order delivery.

TCP is a protocol that offers a guaranteed way for 2 computers to talk to each other over the internet, it does this by using the concept of message acknowledgements. When you send information over the internet, you expect to get a response back saying "Hey I got this data".  If that acknowledgement isn't received, it means that other computer didn't receive the packet.

A connection must be established between the client and server before data can be sent over.  The server must also be listening for connection requests. 

3 Way Handshake:
    1. SYN - Client wants to establish connection with a server, so it sends a SYN segment to start communication and defines the sequence number to start segments with
    2. SYN + ACK - The server responds to the client, acknowledging the request and responding with the sequence number it will start the segments with.
    3. ACK - Client acknowledges the response from the server and they both establish a reliable connection to be used to start actual data/packet transfer.


## UDP
User Datagram Protocol.  Send & forget nature. Used for time-sensitive transmssions like video streaming, VOIP applications, or multiplayer games.  Much faster than TCP but there's tradeoffs because of that.

The messages get sent 1 way and there are tons of them.  Sometimes information can be delayed or lost in the transmission, but this is fine because there's so many coming in to fill those gaps that ~50ms of latency because of the missing packet is acceptable.

There is no guarantee of delivery, ordering, or duplication protection.