from tkinter import *
from tkinter import messagebox
from tkinter.messagebox import *

class EAN13 (object):
    def __init__ (self):
        window = Tk()
        window.title('EAN-13 Barcode Generator')
        window.resizable(False,False)

        # create variable to store the inputs
        self.fileVar = StringVar()
        self.codeVar = StringVar()

        # create variable to initiate coordinate x,y
        self.x, self.y = 65, 150

        # Text for output file entry
        fileText = Label(window, text='Save barcode to PS file [eg: EAN13.eps]:')
        fileText.pack()

        # Make output file name entry
        fileInput = Entry(window, textvariable=self.fileVar, width=40)
        fileInput.pack()

        # Text for code entry
        codeText = Label(window, text='Enter code (first 12 decimal digits):')
        codeText.pack()

        # Make code entry
        codeInput = Entry(window, textvariable=self.codeVar ,width=40)
        codeInput.pack()

        # Bind enter to validate the input and make the barcode
        window.focus_set()
        window.bind('<Return>', self.validateInput)

        # Make canvas to draw the barcode
        self.canvas = Canvas(window, width=400, height=450, relief='ridge', bg='#F1F1F0', bd = 5)
        self.canvas.pack(padx=30, pady=(10,20))

        window.mainloop() 

    # Function to validate the input and make the barcode
    def validateInput(self):
        self.fileName = self.fileVar.get()
        self.codeDigit = self.codeVar.get()
        self.canvas.delete('all')
        # create variable to initiate coordinate x,y
        self.x, self.y = 65, 150
        if len(self.codeDigit) != 12 or not self.codeDigit.isdigit():
            messagebox.showerror('Wrong input!', 'Please enter correct input code.')
        elif self.fileName[-4:] != '.eps':
            messagebox.showerror('Wrong input!', 'Please enter correect output file name.')
        else:
            digit = self.encodeDigit() # encode the input code to binary
            self.drawRectangle(digit) # draw the barcode
            self.canvas.postscript(file=self.fileName, colormode='color') # save the barcode to .eps file

    # Function to draw the barcode separator in start and end of the barcode
    def start(self):
        for i in '101':
            if i == '1':
                self.canvas.create_rectangle(self.x,self.y,self.x+3,self.y+200, outline='', fill='#5E83BA')
                self.x += 3
            else:
                self.canvas.create_rectangle(self.x,self.y,self.x+3,self.y+200, outline='', fill='#F1F1F0')
                self.x += 3

    # Function to draw the content one barcode group
    def content(self,digit):
        for i in digit:
            if i == '1':
                self.canvas.create_rectangle(self.x,self.y,self.x+3,self.y+180, outline='', fill='#091D36')
                self.x += 3
            else:
                self.canvas.create_rectangle(self.x,self.y,self.x+3,self.y+180, outline='', fill='#F1F1F0')
                self.x += 3

    # Function to draw the barcode separator in the middle of the barcode
    def middle(self):
        for i in '01010':
            if i == '1':
                self.canvas.create_rectangle(self.x,self.y,self.x+3,self.y+200, outline='', fill='#5E83BA')
                self.x += 3
            else:
                self.canvas.create_rectangle(self.x,self.y,self.x+3,self.y+200, outline='', fill='#F1F1F0')
                self.x += 3

    # Function to draw the entire barcode and text
    def drawRectangle(self, digit):
        self.start()
        self.content(digit[:42]) # the binary consist of 84 digit, take only first half for 1st group
        self.middle()
        self.content(digit[42:]) # take 2nd half, for 2nd group
        self.start()

        # Text for title, barcode digit, and check digit.
        self.canvas.create_text(200,100, text='EAN-13 Barcode:', font=('Arial', 24), fill='#678B8B')
        self.canvas.create_text(55,343, text=self.codeDigit[0], font=('Courier New', 18))
        self.canvas.create_text(138,343, text=self.codeDigit[1:7], font=('Courier New', 18))
        self.canvas.create_text(275,343, text=self.codeDigit[7:], font=('Courier New', 18))
        self.canvas.create_text(200,400, text=f'Check Digit: {self.codeDigit[-1]}', font=('Arial', 24), fill='#E4AAA6')
    
    # Function to encode the input digit
    def encodeDigit (self):
        code = self.codeDigit

        # database for encoding
        structure = ['LLLLLL', 'LLGLGG', 'LLGGLG', 'LLGGGL', 'LGLLGG ', 'LGGLLG', 'LGGGLL', 'LGLGLG', 'LGLGGL', 'LGGLGL']
        encodingL = ['0001101', '0011001', '0010011', '0111101', '0100011', '0110001', '0101111', '0111011', '0110111', '0001011']
        encodingR = ['1110010', '1100110', '1101100', '1000010', '1011100', '1001110', '1010000', '1000100', '1001000', '1110100']
        encodingG = [i[::-1] for i in encodingR]

        # Function to compute the checksum
        def checksum(code):
            res = 0
            # multiply each digit with corresponding position, and add them
            for i in range(12):
                if i%2 == 0:
                    res += int(code[i])
                else:
                    res += int(code[i])*3
            checkdigit = res%10
            return '0' if checkdigit == 0 else str(10-checkdigit)

        code = code + checksum(code)
        self.codeDigit = code # so it can be used outside the function

        operation = structure[int(code[0])] # choose appropriate encoding pattern according 1st digit

        self.encodedFirst = ''

        # Encode for first group
        for i in range(6):
            if operation[i] == 'L':
                self.encodedFirst = self.encodedFirst + encodingL[int(code[i+1])]
            elif operation[i] == 'G':
                self.encodedFirst = self.encodedFirst + encodingG[int(code[i+1])]
            elif operation[i] == 'R':
                self.encodedFirst = self.encodedFirst + encodingR[int(code[i+1])]

        self.encodedLast = ''

        # Encode 2nd group
        for i in range(7, 13):
            self.encodedLast = self.encodedLast + encodingR[int(code[i])]

        return self.encodedFirst+self.encodedLast

if __name__ == '__main__':
    EAN13()
