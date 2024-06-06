from tkinter import *
import cv2
import face_recognition
import os
from gtts import gTTS 
from PIL import ImageTk,Image
from playsound import playsound
from tkinter import filedialog
import shutil #coping
import re #lang
images_dir = "Humans/Images/"
voices_dir = "Humans/Voices/"
# make Directories to save the images and Voices inside
def makedirs():
    if 'Humans' not in os.listdir('.'):
        os.mkdir('Humans')
        os.mkdir(images_dir)
        os.mkdir(voices_dir)   
# load images from its directory
def load_images(folder):
    images = []
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        image = cv2.imread(path)
        if image is not None:
            images.append((filename, cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
    return images

                        #### This is the main idea ####
#start recognition
def capture_video_stream():
    known_faces_images = load_images(images_dir)
    known_faces_encodings = [face_recognition.face_encodings(image)[0] for _, image in known_faces_images]
    cap = cv2.VideoCapture("http://192.168.1.111:81/stream")

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    try:
        FrameNoFaceTimes=0 #this variable to stop repeat the sound
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to capture frame.")
                break

            # Convert frame to RGB (face_recognition uses RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Find all face locations and encodings in the current frame
            face_locations = face_recognition.face_locations(frame_rgb)
            face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
            if not face_locations:
                FrameNoFaceTimes+=1
                print(FrameNoFaceTimes)
                
                
            # Compare face encodings with the known face encoding
            for face_encoding in face_encodings:
                if FrameNoFaceTimes<=15:#15 is like a timer to out sound again
                    skip = True
                else:
                    skip = False
                # Compare face encoding with the known face encoding
                matches = face_recognition.compare_faces(known_faces_encodings, face_encoding)
                for idx, match in enumerate(matches):
                    if match:
                        if skip: #skipping
                            break
                        else:
                            FrameNoFaceTimes=0
                            name = str(known_faces_images[idx][0]).split('.')[0]#sound name
                            id = name.split("-")[0] # To select his id number
                            # search on the sound that start with the this id
                            l = os.listdir(voices_dir)
                            l.sort()
                            filename = l[int(id)-1]
                            print(filename)
                            try:
                                playsound(f'{voices_dir}{filename}')
                            finally:
                                break

            # Display the frame (optional)
            cv2.imshow('ESP32-CAM Stream', frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Release the VideoCapture and close all windows
        cap.release()
        cv2.destroyAllWindows()

# It's Just showing The stream
def theStream():
    cap = cv2.VideoCapture("http://192.168.1.111:81/stream")
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return
    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
            cv2.imshow('ESP32-CAM Stream', frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Release the VideoCapture and close all windows
        cap.release()
        cv2.destroyAllWindows()
#Adding a new human for recognition earlier



def newPerson():
    global addWin
    global image_field
    global name_field

    addWin = Toplevel(app)
    addWin.title("Add new person")
    addWin.geometry("550x300")

    image_field = Text(addWin, wrap=WORD, width='40', height='1')
    img_button = Button(master=addWin, width='10', height='1',
                        text="select image", command=select_img)
    
    name_field = Text(addWin, wrap=CHAR, width='20', height='1')
    name_label = Label(addWin,text='Enter his name: ',font=("Arial", 12),
                       borderwidth=1,relief=SOLID)
    
    submit = Button(addWin,width='20',height='2',font=("Arial",12),
                    text='Save',command=savingANewPerson)
    cancel = Button(addWin,width='20',height='2',font=("Arial",12),
                    text='Cancel',command=destroy)
    
    img_button.grid(row=0,column=0,pady=30,padx=10)
    image_field.grid(row=0,column=1,pady=30,padx=10)
    name_label.grid(row=1,column=0,pady=30,ipadx=5,ipady=5,padx=10)
    name_field.grid(row=1,column=1,pady=30)
    submit.grid(row=2,column=0,pady=30,padx=10)
    cancel.grid(row=2,column=1,pady=30,padx=10)
def destroy():
    addWin.destroy()
#Select person's picture  
def select_img():
    global file_path

    file_path = filedialog.askopenfilename(title="Select an image",
                                            filetypes=[("images files", "*.jpg"), 
                                                        ("All files", "*.*")])
    if file_path:
        if ('.jpg' or '.jpeg' or '.png') in file_path:

            newPerson()
            image_field.delete('1.0',END)
            image_field.insert('1.0',file_path)
        else:
            newPerson()
    else:
        newPerson()
# Detecting language 
def detect_language(text):
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    english_pattern = re.compile(r'[a-zA-Z]')
    
    if arabic_pattern.search(text):
        return "ar"
    elif english_pattern.search(text):
        return "en"
    else:
        return "Unknown"
#when clicking on save button in add new persons
def savingANewPerson():
    thePathWillSaveIn = os.getcwd()+f"/{images_dir}"
    l = os.listdir(thePathWillSaveIn) # list all images names
    if l:
        l.sort()
        lastImage=l[-1] 
        id = lastImage.split(".")[0]#last id number of images names
    else:
        id=0
    # get the name and image
    name = name_field.get('1.0',END)
    name = name[:-1] # To remove "\n" char
    image = image_field.get('1.0',END)
    image_path = image[:-1] # To remove "\n" char
    print(image_path)
    ###  Saving the picture  ####
    pic_format = image_path.split(".")[1] # select this => (jpg) or (png) or else..
    thePathWillSaveIn = os.getcwd()+f"/{images_dir}{id+1}.{pic_format}" #the path that will save in
    coping = shutil.copy(image_path,thePathWillSaveIn) # coping

    ### Saving the voice ###
    #detect
    if detect_language(name) == 'ar':
        speech = gTTS(text=name, lang='ar', slow=False)
        voice = True
    elif detect_language(name) == 'en':
        speech = gTTS(text=name, lang='en', slow=False)
        voice = True
    else:
        voice =False
    speech.save(f"{voices_dir}{id+1}-{name}.mp3")
    # A picture and voice are saved successfully
    if coping and voice:
        msg = Label(addWin,text="The person saved successfully.",fg="green",font=("Arial",12))
        msg.place(x=170,y=180)
    else:
        msg = Label(addWin,text="there are something error.",fg="red",font=("Arial",12))
        msg.place(x=170,y=180)

# persons button to show saved persons
def showSavedPersons(rng=0):
    global r
    global personsWin
    global length
    r=rng
    personsWin=Toplevel(app)
    personsWin.title("Saved persons")
    personsWin.geometry("500x600+350+70")
    images = list(os.listdir(images_dir))
    images.sort
    length = len(images)
    lastNumber=0
    for n in range(r,r+6):
        if n >= length:
            break
        #left images
        if n%2==0:
            path = os.path.join(images_dir,images[n]) #image path
            images[n] = Image.open(path)
            images[n].thumbnail((150, 150))  
            images[n] = ImageTk.PhotoImage(images[n])
            imgLabel = Label(personsWin, image=images[n])
            imgLabel.image = images[n]  # Keep a reference to avoid garbage collection
            imgLabel.grid(row=n,column=0,padx=('20','10'), pady=15)

            lastSlash = path.rfind("/")
            name = path[lastSlash+1:path.index(".")]
            nameLabel = Label(personsWin,text=name)
            nameLabel.grid(row=n,column=1,padx=('0','70'))
        #right images
        elif n%2==1:
            path = os.path.join(images_dir,images[n]) #image path
            images[n] = Image.open(path)
            images[n].thumbnail((120, 120))  
            images[n] = ImageTk.PhotoImage(images[n])
            imgLabel = Label(personsWin, image=images[n])
            imgLabel.image = images[n]  # Keep a reference to avoid garbage collection
            imgLabel.grid(row=n-1,column=2,padx=('20','10'), pady=15)

            lastSlash = path.rfind("/")
            name = path[lastSlash+1:path.index(".")]
            nameLabel = Label(personsWin,text=name)
            nameLabel.grid(row=n-1,column=3)
            lastNumber=n
    if lastNumber<r<6:
        nextBTN = Button(personsWin,text='Next',width='20',height=2,command=nextPage)
        nextBTN.place(x=280,y=500)
    elif r>length-6:
        backBTN = Button(personsWin,text='Back',width='20',height=2,command=backPage)
        backBTN.place(x=30,y=500)
    else:
        nextBTN = Button(personsWin,text='Next',width='20',height=2,command=nextPage)
        nextBTN.place(x=280,y=520)
        backBTN = Button(personsWin,text='Back',width='20',height=2,command=backPage)
        backBTN.place(x=30,y=520)
def nextPage():
    surplus = length-r
    if surplus < 6:
        personsWin.destroy()
        showSavedPersons(r+surplus)
    else:
        personsWin.destroy()
        showSavedPersons(r+6)


def backPage():
    personsWin.destroy()
    if r-6<=0:
        showSavedPersons(0)
    else:
        showSavedPersons(r-6)

#About(English)
def About():
    try:
        ar_aboutWin.destroy()
    finally:
        
        global en_aboutWin
        en_article=\
"""
Welcome to my App!

This is An application to help blind people.


How to use:

when clicking on start button,
The App start to scan the camera video stream via camera ip address
and detect faces then recognize on them then start making a sound say person name 
to hear the bilnder that sound and know who are in front of him.
'add new person' button to add new person by entering his own picture and name.
'stream' button to show the camera video

"""
        en_aboutWin = Toplevel(app)
        en_aboutWin.title("About")
        en_aboutWin.geometry("700x400+300+100")
        label = Label(master=en_aboutWin,text =en_article)
        label.pack()
        Button(master=en_aboutWin,width='20',height='2',text="Translate to Arabic",
            command=translate).pack()
        
#About(Arabic)
def translate():
    global ar_aboutWin
    en_aboutWin.destroy()
    ar_article=\
    """
مرحبا بكم فى تطبيقى

هذا التطبيق خاص بمساعدة المكفوفين

كيفيه الاستخدام

عند الضغط على زر البدء, 
يقوم التطبيق بمسح الكاميرا عن طريق الاى بى الخاص بها
واكتشاف الوجوه التى ظهرت فى الصوره والتعرف عليها ثم  اخراج صوت باسم صاحب الصوره  
لكى يسمع المكفوف ذلك الصوت ليعرف من هو امامه

-الزر اضافه شخص جديد لكى نقوم بتخزين شخص جديد للتعرف عليه لاحقا عن طريق ادخال صورته واسمه
- 'stream' هذا الزر لكى يعرض صوره الكاميرا

"""
    ar_aboutWin = Toplevel(app)

    # sets the title of the
    # Toplevel widget
    ar_aboutWin.title("حول")
 
    # sets the geometry of toplevel
    ar_aboutWin.geometry("800x400+300+100")
 
    # A Label widget to show in toplevel
    form=Label(ar_aboutWin,justify='right',text=ar_article)
    form.pack()

    #button to change the lang to ar
    switch_lang = Button(ar_aboutWin,width='20',height='2',text="EN",command=About)
    switch_lang.pack()


if __name__ == "__main__":

    makedirs()
    app=Tk()
    w=600;h=500
    app.geometry(f'{w}x{h}+350+100')
    app.title('WRY')
    app.configure(bg='#4661fa')
    frm1=Frame(master=app,width=w,height=h//2,bg='#c1d5f7') 
    frm2=Frame(master=app,width=w,height=h//2,borderwidth=3,relief=SOLID,)
    frm1.grid(row=0,column=0)
    frm2.place(x=100,y=200)

    btn1=Button(master=frm2,width='20',height='2',text="Start",command=capture_video_stream)
    btn2=Button(master=frm2,width='20',height='2',text="stream",command=theStream)
    btn3=Button(master=frm2,width='20',height='2',text="Add a new person",command=newPerson)
    btn4=Button(master=frm2,width='20',height='2',text="About",command=About)
    btn5=Button(master=frm2,width='20',height='2',text="Persons",command=showSavedPersons)
    btn1.grid(row=0,columnspan=2,padx=4,pady=4)
    btn2.grid(row=1,column=0,padx=4,pady=4)
    btn3.grid(row=1,column=1,padx=4,pady=4)
    btn4.grid(row=2,column=0,padx=4,pady=4)
    btn5.grid(row=2,column=1,padx=4,pady=4)
    app.mainloop()
