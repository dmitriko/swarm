swarm
=====

This is my attempt to create an application  
for managing a set of workers with one manager  
process via AMQP protocol.  

Now it seems to me that this approach is not so interesting.  
Let me explain. RabbitMQ is a wonderful software but,  
having it in a High Available mode is rather an issue.

So the next thing I would try is a set of workers that  
communicate via Websockets protocol.

I make this repo available mostly for myself.  
A few things like testing AMQP application,  
JSON serialization, linux network management  
seems interesting though I was going to try Golang  
for that purporse. 

But frankly, these days I am far away from all this stuff,  
but rather deep in the microcontrollers. 


--  
your simple python developer