# Automation Indications for PyWinAuto

- You must start the program in its proper program folder to reference it with that path  
eg. C:/Multicharts/Multicharts64.exe must be started from the C:/Multicharts folder

- Usually you can access a main window or dialog refering to its name in the title  
eg. app['Optimization Progress'] will give you access to a dialog of the running optimization

- I haven't found inspection tools particularly useful

- Prefer keyboard controls to select and make actions as it is usually a robust way to do things rather that using mouse coordinates

- If you have to use mouse coordinates, first move the window to top left,  
so that the coordinates are more reliable

