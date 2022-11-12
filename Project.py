import Interface


print("Started executing programme!")


#GUI needs to have it's own thread to run correct. Thus, all of the operations needs to be carried out there.
Interface.MainGUILoop()

print("Finished executing programme!")
