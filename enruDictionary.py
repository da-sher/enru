#from tkinter import *
#from tkinter import Text, S, N, E, W, LabelFrame
#from tkinter.ttk import Frame, Entry, Button, Scrollbar

import sqlite3,re

class myDictionary():
    def __init__(self,fn):
        self.conn=sqlite3.connect(fn)
        self.cursor=self.conn.cursor()
        pass
    def f_AppendNewWordButton(w):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS newwords(id INTEGER PRIMARY KEY AUTOINCREMENT,word_en TEXT UNIQUE ON CONFLICT IGNORE)')
        self.cursor.execute('INSERT INTO newwords(word_en) VALUES (?)',(w,))
        return
    def f_NewWordDumpButton(*ev):
        self.cursor.execute('SELECT word_en FROM newwords')
        f=open('NewWordDump.txt','w')
        for (x,) in self.cursor.fetchall():
            f.write(x+'\n')
        f.close()
        return
    def worddata(self,word):
        worddata_data=[]
        word2=word.lower()
        word3=word.upper()
        self.cursor.execute('SELECT word_en,translit_IPA,translit_ru,index1 FROM translit WHERE word_en=? OR word_en=? OR word_en=?',(word,word2,word3))
        zzz=self.cursor.fetchall()
        for word_en,translit_IPA,translit_ru,index1 in zzz:
            translit_IPA=translit_IPA and u'{0}'.format(translit_IPA) or u''
            translit_ru=translit_ru and u'{0}'.format(translit_ru) or u''
            self.cursor.execute('SELECT index2,index3,index4,word_ru FROM dictionary WHERE (word_en=? OR word_en=? OR word_en=?) AND index1=?',(word,word2,word3,index1))
            w=[]
            for i2,i3,i4,word_ru in self.cursor.fetchall():
                i2=i2 or ' '
                i3=i3 or ' '
                i4=i4 or ' '
                t0=u'{0} {1} {2} {3}\n'.format(i2,i3,i4,word_ru).replace('0)','').replace('0.','')
                w.append(t0)
            worddata_data.append(dict(word_en=zzz[0][0],translit_IPA=translit_IPA,translit_ru=translit_ru,index1=index1,w=w))
        return worddata_data


class DictionaryBarFrame():
    def __init__(self,master,mydict,dtf,font,row):
        self.dtf=dtf
        self.mydict=mydict
        dictBarFrame=Frame(master)
        dictBarFrame.grid_columnconfigure(0,weight=1)
        #dictBarFrame=master
        self._entry=Entry(master=dictBarFrame,text='',width=40,font=font)
        self._entry.grid(row=0,column=0,sticky=N+W+E)
        self._entry.bind(sequence="<KeyRelease>", func=self._entry_event)
    
        #dictBarButtonFrame=Frame(dictBarFrame)
        #dictAppendNewWordButton=Button(master=dictBarButtonFrame,text='+',width=3,command=self._f_AppendNewWordButton)
        #dictNewWordDumpButton=Button(master=dictBarButtonFrame,text='D',    width=3,command=self.mydict.f_NewWordDumpButton)
        #dictNewWordLoadButton=Button(master=dictBarButtonFrame,text='L',    width=3,command=pics_in_text_w_show)
        #dictAppendNewWordButton.grid(row=0,column=0,sticky=N+W)
        #dictNewWordDumpButton.grid(row=0,column=1,sticky=N+W)
        #dictNewWordLoadButton.grid(row=0,column=2,sticky=N+W)
        dictBarFrame.grid(row=row,column=0,sticky=W)
        #dictBarButtonFrame.grid(row=0,column=0,columnspan=10,sticky=W)
    def _f_AppendNewWordButton(self,e):
        w=self,_entry.get()
        self.mydict.f_AppendNewWordButton(w)
    def _entry_event(self,event):
        self.dtf.thisword(self._entry.get(),setSearchstring=False)    
    def set(self,word):
        self._entry.delete('0','end')
        self._entry.insert('0',word)



class DictionaryTextFrame():
    def __init__(self,master,mydict,font,text_menu,highlight,row):
        self.mydict=mydict
        infoFrame=Frame(master)
        infoFrame.grid_columnconfigure(0,weight=1)
        infoFrame.grid_rowconfigure(0,weight=1)
        #infoFrame.grid_rowconfigure(1,weight=0)
        #infoFrame=master
        self._text=Text(infoFrame,width=40,height=150,font=font,padx=7,pady=7)
        self._scr=Scrollbar(infoFrame,orient="vertical",command=self._text.yview)
        self._text['yscrollcommand'] = self._scr.set
        self._text.tag_config('translit',foreground='blue')
        self._text.tag_config('green',foreground='#009000')
        self._text.grid(row=0,column=0,sticky=S+E+W)
        self._scr.grid(row=0,column=1,sticky=N+S+E)
        #master.grid_rowconfigure(1,weight=1)
        #master.grid_rowconfigure(2,weight=1)
        #master.grid_rowconfigure(3,weight=1)
        infoFrame.grid(row=row,column=0,sticky=N+S+E+W)
        self._text.tag_bind("green",sequence="<Button-1>", func=self.mv3)
        self.t_cm=text_menu
        self.t_cm.install(self)
        self.highlight=highlight
        self._text.bind("<Button-3>", self.t_cm.activate)
        self.entry=None
    def mv3(self,event):
        if self._text.get('current') not in ' \n':
            word=self._text.get('current wordstart','current wordend')
            self.thisword(word)
    def thisword(self,word,setSearchstring=True):
        worddata=self.mydict.worddata
        wdatas=worddata(word)
        if not wdatas:
            if word[-1:]=='s':
                wdatas=worddata(word[:-1])
            elif word[-2:]=='ed':
                wdatas=worddata(word[:-1]) or worddata(word[:-2])
            elif word[-3:]=='ing':
                wdatas=worddata(word[:-3])
            elif word[-2:]=='ly':
                wdatas=worddata(word[:-2])
        if setSearchstring:
            if self.entry: self.entry.set(word)
            #self.dbf.delete('0','end')
            #self.dbf.insert('0',word)
        self._text.delete('0.0','end')
        for wd in wdatas:
            self._text.insert('end',wd['word_en']+u' '+wd['index1']+u' ','title')
            self._text.insert('end',wd['translit_IPA']+' ','translit')
            self._text.insert('end',wd['translit_ru']+u'\n')
            self._text.insert('end',u'\n')
            for t0 in wd['w']:
                if self.highlight:
                    self.en_ru_format(t0)
                else:
                    self._text.insert('end',t0)
            self._text.insert('end',u'----------------\n')
    def en_ru_format(self,text):
        zzz=re.split(u'([-~(]* *[A-Za-z](?:[-A-Za-z()~.,\'\ ]*[-A-Za-z~)]){0,1})',text)
        self._text.insert('end',u'{0}'.format(zzz[0]))
        first_eng=1
        for j in range(len(zzz[1:])//2):
            self._text.insert('end',u'{0}'.format(zzz[2*j+1]),'green')
            self._text.insert('end',u'{0}'.format(zzz[2*j+2]))
    def lock(self):
        pass
    def unlock(self):
        pass

