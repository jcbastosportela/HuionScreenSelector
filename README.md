# What is this about?

I have a Huion H430P that I want to use on my GNU/Linux machine. Driver from [https://github.com/DIGImend/digimend-kernel-drivers/]releases seems to not provide means to control which is the output display of the device (in case you are using multiple displays as I do). Worst is that by default the tablet is outputing to all the displays you may have connected, so makes drawing very ackward.

After some research online I found out that it can be done usinf `xinput`, but having to everytime run a bunch of commands on the terminal in order to select the desired output is not very nice, so I decided to create a simple system tray application that does that for me.
