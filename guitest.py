from Tkinter import *



#main window
root = Tk()

mainFraim = Frame(root, bg = '#FFFFFF')


#Fraim for combine Labels
fraimExtra = Frame(mainFraim, bg = '#ECDBBB')

#text-area to enter btrfs-device name
deviceText = Label(fraimExtra, text = "Enter device name. Example: /dev/sda9", font = "Verdana 12", bg = '#ECDBBB')
deviceText.place(relx = 0.001, rely = 0)
enterDevice = Entry(fraimExtra, width = 30)
enterDevice.place(relx = 0.002, rely = 0.1)

#text-area to enter path of output files
pathText = Label(fraimExtra, text = "Enter path for output files. Custom: current directory.", font = "Verdana 12", bg = '#ECDBBB')
pathText.place(relx = 0.001, rely = 0.3)
enterPath = Entry(fraimExtra, width = 30)
enterPath.place(relx = 0.002, rely = 0.4)

#text-area to enter output file(s) name(s)
filenameText = Label(fraimExtra, text = "Enter name of output file(s). Custom: [$device_name]-btrfs-graph.", font = "Verdana 12", bg = '#ECDBBB')
filenameText.place(relx = 0.001, rely = 0.6)
enterFilename = Entry(fraimExtra, width = 30)
enterFilename.place(relx = 0.002, rely = 0.7)


fraimExtra.place(relx = 0, rely = 0, relwidth = 0.8, relheight = 0.93)




#checkbutton for choosing type(s) of output file(s)
fraimCheck  = Frame(mainFraim, bg = '#8C794C')


checkinformText = Label(fraimCheck, text = "Chose type(s) of\noutput files", font = "Arial 12", bg = '#8C794C')
checkinformText.pack()

checkList = {}
checkList['pdfCheck'] = BooleanVar()
checkList['svgCheck'] = BooleanVar()
checkList['pngCheck'] = BooleanVar()
checkList['dotCheck'] = BooleanVar()
checkList['gd2Check'] = BooleanVar()

check_1 = Checkbutton(fraimCheck, text = "pdf", variable = checkList['pdfCheck'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)
check_2 = Checkbutton(fraimCheck, text = "svg", variable = checkList['svgCheck'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)
check_3 = Checkbutton(fraimCheck, text = "png", variable = checkList['pngCheck'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)
check_4 = Checkbutton(fraimCheck, text = "dot", variable = checkList['dotCheck'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)
check_5 = Checkbutton(fraimCheck, text = "gd2", variable = checkList['gd2Check'], onvalue = True, offvalue = False, font = "Arial 14", bg = '#8C794C', highlightthickness = 0)

check_2.select()

check_1.pack()
check_2.pack()
check_3.pack()
check_4.pack()
check_5.pack()

fraimCheck.place(relx = 0.8, rely = 0, relwidth = 0.2, relheight = 0.93)



#button to start building graph
butStart = Button(mainFraim, font = "Arial 20", bg = '#B5A16A')
butStart["text"] = "Generate Graph"
butStart.place(relx = 0, rely = 0.87, relwidth = 1, relheight = 0.13)



mainFraim.pack(fill = BOTH, expand = 1)


root.minsize(670, 220)
root.maxsize(670, 220)
root.title("BTRFS Graph")
root.mainloop()