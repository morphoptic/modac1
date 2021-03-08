PyCharm File watcher
need to rebuild and install for new versions
https://confluence.jetbrains.com/display/IDEADEV/Compiling+File+Watcher

execute ./make.sh

Copy the compiled fsnotifier-<ARCH> binary into the bin/ directory of your IDE (where <ARCH> is the output of `uname -m` on your system).
   /usr/local/bin/pycharm/bin
   
Start the IDE and invoke Help | Edit Custom Properties action (or Configure | Edit Custom Properties from the welcome screen), add the following line, then restart the IDE:
idea.filewatcher.executable.path = fsnotifier-<ARCH>
