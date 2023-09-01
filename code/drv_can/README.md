# Drv Can

Repository that storages classes and functions used create a thread that can send,
and receive can messages. The node class will create a thread with a shared object
that receives the commands both for the can module and also the messages to send through can bus.
The commands that can be send to can are create and remove filter, and also send messages.

The version 0.1.X forward is using posix ipc queues, if there is any problem with posix it will
possibly be due to the max messages in queue and the max message size limited by the system.
For more information check [system-shared-tool github](https://github.com/WattRex/System-Tools/tree/develop/code/sys_shd)
To see which is the max messages and the max message size in system run:
```
cat /proc/sys/fs/mqueue/msg_max
cat /proc/sys/fs/mqueue/msgsize_max
```
In order to change the max message or message size in queues run:
```
sudo sh -c 'echo 200 > /proc/sys/fs/mqueue/msg_max'
sudo sh -c 'echo 200 > /proc/sys/fs/mqueue/msgsize_max'
```
