# Queues
Queues are a very common solution found in streaming and event driven architectures.  They help enable an asynchronous solution to many problems, as well as the ability to be distributed across multiple systems enabling fault tolerance and scalable infrastructure.

ELI5 term is a queue is a system that acts as a buffer for messages.  Producers handle events and put messages into the queue where they wait to be processed.  The messages get picked up by a consumer & the messages are removed from the queue after the consumer has finished processing them.

Couple reasons to use queues instead of relational databases.
- queues enable an async solution where you decouple the processing for events.
- instead of immediately processing something after someone bought or requested something, you put it into a queue for it to be processed by a different entity at a later time so the producer can continue taking requests.
- a separate service then reads off of that queue and consumes the message.

## Why not Relational Database instead of a Queue ?
- relational databases have lots of locking mechanisms which kinda screw up the whole idea behind the async nature of queues which is the whole benefit.
  1. New Messages would get inserted into the database table
  2. Consumers would have to update the record in the table saying that they're in the middle of processing the message.
  3. After the consumer is done, the message would then have to be deleted from the table.
- All of these operations involve transactinos & some of them involve locking the table.  bad news bears.
- Consumers would also have to constantly be polling the database for new messages.  Very inefficient. 
- this database solution also quickly stops scaling very well, as opposed to queuing where distributed computing is typically an option available to you.

## AMQP 
AMQP is a messaging protocol that enables conforming client applications to communicate with brokers who sit in the middle.  
- Brokers receive messages from producers and route them to consumers.
- All 3 of producers, brokers, and consumers are separate entities and can exist on different machines.

## Message Acknowledgement
- Networks are unreliable and applications may fail to process messages, so this is where the idea of message acks comes from.
- When a consumer picks up a message off the queue it nofifies the broker(s), saying "hey i got message xyz".  It's at this point that the broker removes that message from the queue.

## Dead Letter Queues
Dead Letter Queues are the place where messages go if they fail to get routed to a consumer, for whatever reason.

# SQS
Managed Queue service by AWS.  does a lot of the heavy lifting for you.  You can implement things like message routing or fanout etc with accompanying services like SNS & eventbridge.

# RabbitMQ
[Article](https://www.rabbitmq.com/tutorials/amqp-concepts.html)

An open source message broker software that you can host yourself, or find a managed service to do it for you.