#SebMail version 1.0

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#import necessary modules

import smtplib                                                 #Used for sending emails
from email.mime.text import MIMEText                           #Used for formatting emails       
from email.mime.multipart import MIMEMultipart                 #Used for formatting emails
from tkinter import *                                          #Used for Graphics
import imaplib                                                 #Used for connecting to your email server
import email                                                   #Used for parsing your emails
import sys                                                     #Used for a lot of other things
import time                                                    #Used for managing time in the program(ticks)
import datetime                                                #Used for managing real-time time and date

#Define design standards
bg_color = 'lightgrey'
textcolor = 'limegreen'
tft = 'Impact'
sft = 'Helvetica'
bbt = u'\21 ' + 'back'
settingtext = u'\u2699 ' + 'Settings'

#define where the login information is located
accountdir = 'account.txt'

#Define the email server
inboxserver = imaplib.IMAP4_SSL('imap.gmail.com')

#Create an empty list for storing the emails
emaillist = []

#Create a class for managing scrollbars(taken from stack overflow)
class VerticalScrolledFrame(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        #create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        height=600, width=2000, yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=FALSE)
        vscrollbar.config(command=canvas.yview)

        #reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        #create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        #track changes to the canvas and frame width and sync them,
        #also updating the scrollbar
        def _configure_interior(event):
            #update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                #update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                #update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

class SebMail():
    #Initiate the window and graphics program
    def __init__(self, *args, **kwargs): 
        self.master = Tk()                                
        self.master.resizable(width=False, height=False)
        self.master.geometry('800x800')
        self.master.configure(background=bg_color)
        self.master.title('SebMail')

        #Create the logo displayed at the top of the window
        self.headerlogo = Label(self.master, text='SebMail', \
                                bg=bg_color, fg=textcolor, \
                                font=(tft, 70))
        self.headerlogo.place(x=210, y=0)
        
        self.loginchecker()

    #Check if logged in
    def loginchecker(self):                                 
        self.login_checker = open(accountdir)
        self.login_check = self.login_checker.readlines()
        self.login_checker.close()
        
        #If not logged in, redirect to login page
        if not self.login_check:
            self.loginpage()

        if self.login_check[1] == 'username    password':
            self.loginpage()

        #If logged in, redirect to main page
        else:
            self.login_info = self.login_check[1].split()
            inboxserver.login(self.login_info[0], self.login_info[1])
            self.mainpage(username=self.login_info[0], password=self.login_info[1])
            
            

    #log in page to have the user log in    
    def loginpage(self):
        #Get rid of any previous widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        self.headerlogo = Label(self.master, text='SebMail', \
                                bg=bg_color, fg=textcolor, \
                                font=(tft, 70))
        self.headerlogo.place(x=210, y=0)

        #Create all the widgets on the logout page
        stringvar1 = StringVar()
        stringvar2 = StringVar()
        
        enter_email = Entry(self.master, width=29, bd=4, relief='sunken', \
                        textvariable=stringvar1, font=(sft, 15))
        enter_password = Entry(self.master, width=29, bd=4, relief='sunken', show='*', \
                        textvariable=stringvar2, font=(sft, 15))
        login_instruct = Label(self.master, text='Please Login to your Account', \
                        bg=bg_color, fg=textcolor, font=(sft, 20))
        login_button = Button(self.master, text='Login', bg=bg_color, fg=textcolor, width=14, \
                        command= lambda: self.login(enter_email, enter_password, login_instruct, \
                        login_button), activebackground=bg_color, \
                        activeforeground=textcolor, font=(sft, 30))
        self.master.bind('<Return>', lambda event, enter_email=enter_email, enter_password=enter_password,\
                        login_instruct=login_instruct, login_button=login_button: \
                        self.login(enter_email, enter_password, login_instruct, login_button)) 
                            
    
        enter_email.place(x=210, y=200)
        enter_password.place(x=210, y=250)
        login_instruct.place(x=190, y=150)
        login_button.place(x=205, y=300)
    
        stringvar1.set('Email Address')
        stringvar2.set('Password')

    #log the user in
    def login(self, enter_email, enter_password, login_instruct, login_button):
        username = enter_email.get()
        password = enter_password.get()
        #Verify that the email exists
        basiccheck = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', \
                              username)
        if basiccheck != None:
            Login = open('account.txt', 'w')
            Login.write('This file is used to store account information\n')
            Login.write(username + '    ' + password)
            Login.close()
            
            try:
                inboxserver.login(username, password)
            except Exception as E:
                login_instruct.config(text='That is not a valid email or password')
                
            self.mainpage(username, password)
        else:
            login_instruct.config(text='That is not a valid email or password')

    #Main page
    def mainpage(self, username, password):
        global emaillist
        #Get rid of any previous widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        self.headerlogo = Label(self.master, text='SebMail', \
                                bg=bg_color, fg=textcolor, \
                                font=(tft, 70))
        self.headerlogo.place(x=210, y=0)

        #Create a frame to manage the buttons on the left side
        self.mpbuttonframe = Frame(self.master)
        self.mpbuttonframe.place(x=20, y=150)

        #Create compose button
        compose_button = Button(self.mpbuttonframe, bg=bg_color, fg=textcolor, \
                                command= lambda: self.sep(username, password), \
                                width=9,
                                activebackground=bg_color, \
                                activeforeground=textcolor, \
                                text='Compose', font=(sft, 20))
        compose_button.grid(row=0, column=0)

        #Create Settings button
        settings_button = Button(self.mpbuttonframe, bg=bg_color, fg=textcolor, \
                                 width=9,
                                 command= lambda: self.settings(username, password), \
                                 activebackground=bg_color, \
                                 activeforeground=textcolor, \
                                 text=settingtext, font=(sft, 20))

        settings_button.grid(row=2, column=0)

        #Create a logout button
        logout_button = Button(self.mpbuttonframe, bg=bg_color, fg=textcolor, \
                                 width=9,
                                 command= lambda: self.logout(), \
                                 activebackground=bg_color, \
                                 activeforeground=textcolor, \
                                 text='Logout', font=(sft, 20))

        logout_button.grid(row=1, column=0)

        #Get emails
        if not emaillist:
            self.getmail(username=username, password=password)
            
        #Reverse the email list so the last recieved email shows up first
        emaillist_formatted = list(reversed(emaillist))

        #Create a frame to manage the emails
        self.mpinboxframe = VerticalScrolledFrame(self.master)
        self.mpinboxframe.place(x=200, y=150)

        #Display all the emails
        emailobjectlist = []
        for recievedemail in emaillist_formatted:
            emailobjectlist.append(Button(self.mpinboxframe.interior, \
                                         width=60, anchor='w', command=lambda recievedemail=recievedemail: self.display_email(recievedemail, username, password), \
                                         text=recievedemail[0], font=(sft, 13)))
            emailobjectlist[-1].pack()

    #get emails
    def getmail(self, username, password):
       global emaillist
       #Access the main inbox
       status, folderdata = inboxserver.select('inbox')

       #Get the date n days ago(used for parsing. Getting all emails would take too long)
       cutoff_date = datetime.datetime.now() - datetime.timedelta(days=7)

       #Correctly format the date to work with IMAP
       cutoff_date = str(cutoff_date)
       cutoff_date = cutoff_date[0:10]
       cutoff_date = str(datetime.datetime.strptime(cutoff_date, '%Y-%m-%d').strftime('%d-%b-%Y'))

       #Create search criteria from the date
       search_criteria = '(SINCE "' + cutoff_date + '")'
       
       if status == 'OK':
           #Search the inbox using the search criteria for any emails in the last n days
           status, inboxdata = inboxserver.search(None, search_criteria)
                                                  
           
           if status != 'OK':
               #display a message if there was no emails in the last n days
               no_emails = Label(self.master, text='No emails to display', \
                                 bg=bg_color, fg=textcolor, font=(sft, 20))
               no_emails.place(x=200, y=400)
               
           #Get all the emails 
           for num in inboxdata[0].split():
               try:
                    status, emaildata = inboxserver.fetch(num, '(RFC822)')

                    #Create a dictionary for each email
                    msg = email.message_from_bytes(emaildata[0][1])
                    hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
                    sender = str(msg['From'])
                    subject = str(hdr)

                    #Get the body of each email
                    self.get_email_text(msg)
                    
                    #Turn all the information from the email into a list
                    sender = re.sub('<[^>]+>', '', sender)
                    formatted_subject = subject[0:70]
                    if len(formatted_subject) > 68:
                        formatted_subject = formatted_subject + '...'
                    print(subject)
                    packed_email_info = [formatted_subject, subject, sender, msg]
                    getsuccess = True

               except Exception as E:
                    print(E)
                    getsuccess = False
                   
               if getsuccess == True:
                   emaillist.append(packed_email_info)

               if getsuccess == False:
                   emaillist.append(['ERROR GETTING MESSAGE'])
    #Get the main text of an email
    def get_email_text(self, email_msg):
        if email_msg.is_multipart():
            for payload in email_msg.get_payload():
                return payload.get_payload()
        else:
            return email_msg.get_payload()
        
    #Display the email
    def display_email(self, recievedemail, username, password):
        #Get rid of any previous widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        self.headerlogo = Label(self.master, text='SebMail', \
                                bg=bg_color, fg=textcolor, \
                                font=(tft, 70))
        self.headerlogo.place(x=210, y=0)

        #Create a page for emails that contain characters python doesn't recognize
        if recievedemail[0] == 'ERROR GETTING MESSAGE':
            displayfail_main = Label(self.master, bg=bg_color, fg=textcolor, \
                                     text='Uh Oh. It looks like there was a problem with this email. \n This was most likely caused by the email containg something that SebMail can\'t recognize', \
                                     font=(sft, 10))
            displayfail_main.place(x=10, y=300)
            
        #Display the email
        else:
           self.email_dispframe = VerticalScrolledFrame(self.master)
           self.email_dispframe.place(x=10, y=130)
           subject_disp = Label(self.email_dispframe.interior, text=recievedemail[1], \
                                width=45, wraplength=750, font=(sft, 20))
           sender_disp = Label(self.email_dispframe.interior, text='From: ' + recievedemail[2], \
                               width=65, anchor='w', font=(sft, 15))
           disp_spacer = Label(self.email_dispframe.interior, text='\n \n', \
                               width=65, anchor='w', font=(sft, 15))
           text_display = Label(self.email_dispframe.interior, text=self.get_email_text(recievedemail[3]), \
                               width=65, anchor='w', wraplength=700, font=(sft, 15))

           subject_disp.pack()
           sender_disp.pack()
           disp_spacer.pack()
           text_display.pack()
           
        #Create a back button
        back_button = Button(self.master, text=bbt, bg=bg_color, fg=textcolor, \
                             activebackground=bg_color, activeforeground=textcolor, \
                             command= lambda: self.mainpage(email, password), \
                             font=(sft, 20))

        back_button.place(x=20, y=740)
           
    #Get information to send an email
    def sep(self, username, password):
        stringvar3 = StringVar()
        stringvar4 = StringVar()
        #Get rid of any previous widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        self.headerlogo = Label(self.master, text='SebMail', \
                                bg=bg_color, fg=textcolor, \
                                font=(tft, 70))
        self.headerlogo.place(x=210, y=0)

        #Create the send email page
        send_instruct = Label(self.master, bg=bg_color, fg=textcolor, text=\
                          'Fill out the necessary information below to send an email', 
                          font=(sft, 15))
        enter_recipient = Entry(self.master, width=29, bd=4, \
                            textvariable=stringvar3, font=(sft, 15))
        enter_subject = Entry(self.master, width=29, bd=4, \
                            textvariable=stringvar4, font=(sft, 15))
        message_instruct = Label(self.master, bg=bg_color, fg=textcolor, text='Message', \
                             font=(sft, 15))
        enter_message = Text(self.master, width=46, height=20, \
                         wrap=WORD, font=(sft, 10))
        send_button = Button(self.master, text='Send', bg=bg_color, fg=textcolor, \
                         activebackground=bg_color, activeforeground=textcolor, \
                         command= lambda: self.send_email(username, password, enter_recipient, \
                                                     enter_subject, enter_message, message_instruct), \
                         width=28, font=(sft, 15))
        back_button = Button(self.master, text=bbt, bg=bg_color, fg=textcolor, \
                             activebackground=bg_color, activeforeground=textcolor, \
                             command= lambda: self.mainpage(username, password), \
                             font=(sft, 20))
        

        stringvar3.set('Recipient')
        stringvar4.set('Subject')

        enter_recipient.place(x=210, y=200)
        enter_subject.place(x=210, y=250)
        send_instruct.place(x=120, y=150)
        message_instruct.place(x=210, y=290)
        enter_message.place(x=210, y=320)
        send_button.place(x=212, y=655)
        back_button.place(x=20, y=740)

    #send an email
    def send_email(self, username, password, enter_recipient, enter_subject, enter_message, \
                   message_instruct):
        
        username = str(username)

        from_addr = username
        to_addr = enter_recipient.get()
        
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = enter_subject.get()

        message = enter_message.get('1.0', 'end-1c')
        recipient = enter_recipient.get()
    
        msg.attach(MIMEText(message, 'plain'))
        
        #Get rid of any previous widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        self.headerlogo = Label(self.master, text='SebMail', \
                                bg=bg_color, fg=textcolor, \
                                font=(tft, 70))
        self.headerlogo.place(x=210, y=0)
        
        #Create a back button    
        back_button = Button(self.master, text=bbt, bg=bg_color, fg=textcolor, \
                             activebackground=bg_color, activeforeground=textcolor, \
                             command= lambda: self.mainpage(email, password), \
                             font=(sft, 20))

        back_button.place(x=20, y=740)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(username, password)
            messagetext = msg.as_string()
            server.sendmail(username, recipient, messagetext)
            server.quit()

        except Exception as E:
            failsend = Label(self.master, bg=bg_color, fg=textcolor, \
                                text='Your message failed to send', font=(sft, 20))
            failsend.place(x=200, y=400)

        else:
            success_send = Label(self.master, bg=bg_color, fg=textcolor, \
                             text='Your message has been sent', font=(sft, 20))
            success_send.place(x=200, y=400)

    #Create the settings page
    def settings(self, username, password):
        #Get rid of any previous widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        self.headerlogo = Label(self.master, text='SebMail', \
                                bg=bg_color, fg=textcolor, \
                                font=(tft, 70))
        self.headerlogo.place(x=210, y=0)

        #Create a back button
        back_button = Button(self.master, text=bbt, bg=bg_color, fg=textcolor, \
                             activebackground=bg_color, activeforeground=textcolor, \
                             command= lambda: self.mainpage(email, password), \
                             font=(sft, 20))

        back_button.place(x=20, y=740)

    #Create a logout function
    def logout(self):
        open_logout = open(accountdir, 'w')
        open_logout.write('This file is used to store account information\n username   password')
        open_logout.close()
        self.loginchecker()
        
#Run the mainloop
if __name__ == '__main__':
    runner = SebMail()
    runner.master.mainloop()
