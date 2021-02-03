from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import pickle
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import punkt
from nltk.corpus.reader import wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2 as py
import os 
from pathlib import Path

svc_c = pickle.load(open('svc_model.pickle','rb'))
tfidf = pickle.load(open('tfidf.pickle','rb'))

cat_code = {'business':0, 'entertainment':1, 'politics':2, 'sports':3, 'tech':4}
punctuation_signs = list("?:!.,;")
stop_words = list(stopwords.words('english'))
saved = {}

class functionalities:    
    def file(self):
        global filename
        filename = filedialog.askopenfilename()
        #l2 = Label(master, text = "")
        #l2.grid(column = 0, row = 3, padx = 20, pady = 20)
        #l2.configure(text = filename)
        if filename == "":
            return
        else:
            t1.delete('1.0', END)
            t1.insert(END, filename)
            t.delete('1.0', END)
            with open(filename, 'r') as myfile:
                global text
                text = myfile.read()
            t.insert(END, text)
    
    def filepdf(self):
        global filename
        filename = filedialog.askopenfilename()
        if filename == "":
            return
        else:
            t1.delete('1.0', END)
            t1.insert(END, filename)
            t.delete('1.0', END)
            o = open(filename, 'rb')
            pdfr = py.PdfFileReader(o)
            pdfo = pdfr.getPage(0)
            global text
            text = pdfo.extractText()
            t.insert(END, text)
        
    def feature_creation(text):
        lemmatized_text_list = []
        df = pd.DataFrame(columns=['Content'])
        df.loc[0] = text
        df['Content_Parsed_1'] = df['Content'].str.replace("\r", " ")
        df['Content_Parsed_1'] = df['Content_Parsed_1'].str.replace("\n", " ")
        df['Content_Parsed_1'] = df['Content_Parsed_1'].str.replace("    ", " ")
        df['Content_Parsed_1'] = df['Content_Parsed_1'].str.replace('"', '')
        df['Content_Parsed_2'] = df['Content_Parsed_1'].str.lower()
        df['Content_Parsed_3'] = df['Content_Parsed_2']
        for punct_sign in punctuation_signs:
            df['Content_Parsed_3'] = df['Content_Parsed_3'].str.replace(punct_sign, '')
        df['Content_Parsed_4'] = df['Content_Parsed_3'].str.replace("'s", "")
        wordnet_lemmatizer = WordNetLemmatizer()
        lemmatized_list = []
        text = df.loc[0]['Content_Parsed_4']
        text_words = text.split(" ")
        for word in text_words:
            lemmatized_list.append(wordnet_lemmatizer.lemmatize(word, pos="v"))
        lemmatized_text = " ".join(lemmatized_list)    
        lemmatized_text_list.append(lemmatized_text)
        df['Content_Parsed_5'] = lemmatized_text_list
        df['Content_Parsed_6'] = df['Content_Parsed_5']
        for stop_word in stop_words:
            regex_stopword = r"\b" + stop_word + r"\b"
            df['Content_Parsed_6'] = df['Content_Parsed_6'].str.replace(regex_stopword, '')
        df = df['Content_Parsed_6']
        df = df.rename(columns={'Content_Parsed_6': 'Content_Parsed'})
        features = tfidf.transform(df).toarray()
        return features
    
    def cat_name(cat_id):
        for category, i in cat_code.items():    
            if i == cat_id:
                return category
            
    def prediction(self):
        predict_cat = svc_c.predict(functionalities.feature_creation(text))[0]
        predict_prob = svc_c.predict_proba(functionalities.feature_creation(text))[0]
        category = functionalities.cat_name(predict_cat)
        if (predict_prob.max()*100) > 65:
            #t2.delete('1.0', END)
            t2.insert(0.0,category+"\n")
            saved[filename] = category
        else:
            #t2.delete('1.0', END)
            t2.insert(0.0,"other\n")
            saved[filename] = "other"
    
    def savedf(self):
        savdf = pd.DataFrame(list(saved.items()),columns = ['file','category'])
        #filename1 = filedialog.askdirectory()
        filename1 = filedialog.asksaveasfilename(defaultextension='.csv')
        if filename1 == "":
            root1 = Tk()
            root1.title("message")
            root1.config(bg = "royal blue")
            l11 = Label(root1, text = "No file saved", bg = "royal blue").pack()
            b11 = Button(root1, text = 'Ok', command = root1.destroy, bg = "cornflower blue").pack()
        else:
            '''def get_entry():
                global name
                name = e.get()
                root.destroy()
            root = Tk()
            root.title("Save as...")
            root.config(bg = "royal blue")
            labler = Label(root, text="name of the file", anchor=W, bg="royal blue")
            labler.grid(row = 0, column = 0)
            e = Entry(root)
            e.grid(row = 0, column = 1)
            bFrame = Frame(root, width=40, height = 60, bg="royal blue")
            bFrame.grid(row=1)
            b = Button(bFrame, text = "OK", command = get_entry, bg = "cornflower blue")
            b.grid(row = 0)
            mainloop()
            #filename2 = filename1 + '/'+ name + '.csv' '''
            savdf.to_csv(filename1,index = False, header=True)
            saved.clear()
    
    def batch_t(self):
        t.delete('1.0', END)
        filename2 = filedialog.askdirectory()
        if filename2 == "":
            return
        else:
            for f in Path(filename2).iterdir():
                with open(f, "r") as file:
                    global f_name
                    f_name = f.name
                    global text
                    text = file.read()
                    functionalities.prediction_batch()
    
    def batch_pdf(self):
        t.delete('1.0', END)
        filename3 = filedialog.askdirectory()
        if filename3 == "":
            return
        else:
            for f in Path(filename3).iterdir():
                o = open(f,'rb')
                pdfr = py.PdfFileReader(o)
                pdfo = pdfr.getPage(0)
                global text
                text = pdfo.extractText()
                global f_name
                f_name = f.name
                functionalities.prediction_batch()
                
    def prediction_batch():
        predict_cat = svc_c.predict(functionalities.feature_creation(text))[0]
        predict_prob = svc_c.predict_proba(functionalities.feature_creation(text))[0]
        category = functionalities.cat_name(predict_cat)
        t.insert(0.0, f_name+'\n')
        if (predict_prob.max()*100) > 65:
            #t2.delete('1.0', END)
            t2.insert(0.0,category+"\n")
            saved[f_name] = category
        else:
            #t2.delete('1.0', END)
            t2.insert(0.0,"other\n")
            saved[f_name] = "other"
            
    def about(self):
        root2 = Tk()
        root2.title("About the program")
        root2.config(bg = "royal blue")
        Instructions = 'This program is used for reading a text file or a pdf\
        file and then predicting the category of the given article into one of\
        the five categories that are : Business, entertainment, sports, politics,\
        and tech. After that we can save the results in a csv file.'
        Instruct = Label(root2, width=30, height=10, text=Instructions, takefocus=0, wraplength=170, anchor=W, justify=LEFT, bg="cornflower blue")
        Instruct.grid(row=1, column=0, padx=10, pady=2)
        ba = ttk.Button(root2, text = "Ok", command = root2.destroy)
        ba.grid(row = 2, column = 0)
        mainloop()
        
    def about_b(self):
        root3 = Tk()
        root3.title("Button info")
        root3.config(bg = "cornflower blue")
        buttoninfo = 'Functions of the six buttons are:\n1.Browse a text file\
:Select a text file and it will get displayed in the box on the right\
 and its address will be given in the bar below.\n2. Browse a pdf file:\
Same as "Browse a file" button, but is made for handling PDFs.\n3.\
Batch text: Selects a folder with a batch of text files and predict the\
categories of all the files in the folder.\n4. Batch pdf: Same as "Batch\
 text", but it handles PDF files instead.\n5. predict: If "Browse a \
file" or "Browse a pdf" is used then it will be used to predict the \
category of the file.\n6.Exit: Exit the program.'
        button_ins = Label(root3, width = 30, height=30, text=buttoninfo, takefocus=0, wraplength=170, anchor=W, justify=LEFT, bg="cornflower blue")
        button_ins.grid(row = 0, column = 0, padx = 10, pady = 2)
        bbi = ttk.Button(root3 , text = "ok", command = root3.destroy)
        bbi.grid(row = 1)
        mainloop()

if __name__ == "__main__":
    f = functionalities()
    master = Tk()
    master.title("Text classifier")
    master.config(bg = "royal blue")
    leftFrame = Frame(master, width=200, height = 600, bg="cornflower blue", highlightthickness=2, highlightbackground="#111")
    leftFrame.grid(row=0, column=0, padx=10, pady=2, sticky=N+S+E+W)
    '''Inst = Label(leftFrame, text="Instructions:", anchor=W, bg="cornflower blue")
    Inst.grid(row=0, column=0, padx=10, pady=2, sticky=W)
    instructions = "This program is used for reading a given text article and\
    categorizing it under 6 labels that are : Business, sports, entertainment,\
    politics, tech and others. There are two buttons:\
    (1)Browse a file : Select a file from the system\
    (2)Predict : It will predict the category of the article."
    Instruct = Label(leftFrame, width=30, height=10, text=instructions, takefocus=0, wraplength=170, anchor=W, justify=LEFT, bg="cornflower blue")
    Instruct.grid(row=1, column=0, padx=10, pady=2)'''
    rightFrame = Frame(master, width=400, height = 600, bg="cornflower blue", highlightthickness=2, highlightbackground="#111")
    rightFrame.grid(row=0, column=1, padx=10, pady=2, sticky=N+S+E+W)
    btnFrame = Frame(leftFrame, width=400, height = 200, bg="cornflower blue")
    btnFrame.grid(row=0, column=0, padx=10, pady=2, sticky = N+S+E+W)
    b1 = ttk.Button(btnFrame, text = "Browse a txt file", command = f.file)
    b1.grid(row=0, column=0, padx=100, pady=2)
    b2 = ttk.Button(btnFrame, text = "predict", command = f.prediction)
    b2.grid(row=2, column=0, padx=100, pady=2)
    b3 = ttk.Button(btnFrame, text = "Browse a pdf file", command = f.filepdf)
    b3.grid(row=0, column=1, padx=100, pady=2)
    b4 = ttk.Button(btnFrame, text = "batch_text", command = f.batch_t)
    b4.grid(row=1, column=0, padx=100, pady=2)
    b5 = ttk.Button(btnFrame, text = "Exit", command = master.destroy)
    b5.grid(row=2, column=1, padx=100, pady=2)
    b6 = ttk.Button(btnFrame, text = "batch_pdf", command = f.batch_pdf)
    b6.grid(row=1, column=1, padx=100, pady=2)
    global t
    t = Text(rightFrame, width = 70, height = 38, takefocus=0, highlightthickness=1, highlightbackground="#333")
    t.grid(row=0, column=0, padx=10, pady=10)
    global t1
    t1 = Text(rightFrame, width = 70, height = 1, takefocus=0, highlightthickness=1, highlightbackground="#333")
    t1.grid(row = 1, column = 0)
    global t2
    t2 = Text(leftFrame, width = 70, height = 33, takefocus=0, highlightthickness=1, highlightbackground="#333")
    t2.grid(row = 3, column = 0,pady = 20, padx= 20)
    menubar = Menu(master)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Save", command = f.savedf)
    #filemenu.add_separator()
    #filemenu.add_command(label="Exit", command=master.destroy)
    helpmenu = Menu(menubar, tearoff = 0)
    helpmenu.add_command(label = "About", command = f.about)
    helpmenu.add_command(label = "About buttons", command = f.about_b)
    menubar.add_cascade(label="File", menu=filemenu)
    menubar.add_cascade(label="Help", menu=helpmenu)
    master.config(menu=menubar)
    mainloop()
