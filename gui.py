# -*- coding: utf-8 -*-


try: #Python 2 imports
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
    import tkMessageBox as message
    from HTMLParser import HTMLParser
    from Tkinter import Image
    from urllib2 import urlopen, URLError, HTTPError
    
except ImportError: #Python 3 imports
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import messagebox as message
    from html.parser import HTMLParser
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
    
import os
import json
import zipfile
from AutoComplete import AutocompleteCombobox
from distutils.version import LooseVersion
import binascii
import sys
import sqlite3

try:
    import FunKiiU as fnku
except ImportError:
    fnku = None
    
PhotoImage=tk.PhotoImage
DEBUG = False

__VERSION__="2.1.5"
targetversion="FunKiiU v2.2"
current_gui=LooseVersion(__VERSION__)



if os.name == 'nt':
    dir_slash = "\\"
else:
    dir_slash = "/"
try:
    fnku_VERSION_ = str(fnku.__VERSION__)
    current_fnku=LooseVersion(fnku_VERSION_)
except:
    fnku__VERSION__ = "?"
    current_fnku=LooseVersion('0')




class VersionParser(HTMLParser):
    fnku_data_set=[]
    gui_data_set=[]
    
    def handle_starttag(self, tag, attrs):
        fnku_data_set=[]
        gui_data_set=[]
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    if value.startswith("/llakssz") and value.endswith(".zip"):
                        self.fnku_data_set.append(value)
                    elif value.startswith("/DerpyBubblez") and value.endswith(".zip"):
                        self.gui_data_set.append(value)

                
class RootWindow(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self)
        self.versions={'gui_new':'','gui_all':'','gui_url':'https://github.com/DerpyBubblez/FunKii-UI/releases','fnku_new':'','fnku_all':'',
                       'fnku_url':'https://github.com/llakssz/FunKiiU/releases'}
        
        self.download_list=[]
        self.selection_list=[]
        self.title_data=[]
        self.nb = ttk.Notebook(self)
        tab1 = ttk.Frame(self.nb)
        self.tab2 = ttk.Frame(self.nb)
        tab3 = ttk.Frame(self.nb)
        tab4 = ttk.Frame(self.nb)
        self.nb.add(tab1,text="Welcome")
        self.nb.add(self.tab2,text="Download")
        self.nb.add(tab3,text="Options")
        self.nb.add(tab4,text="Updates")
        self.nb.pack(fill="both", expand=True)
        self.output_dir=tk.StringVar()
        self.retry_count=tk.IntVar(value=3)
        self.patch_demo=tk.BooleanVar(value=True)
        self.patch_dlc=tk.BooleanVar(value=True)
        self.tickets_only=tk.BooleanVar(value=False)
        self.simulate_mode=tk.BooleanVar(value=False)
        self.filter_usa=tk.BooleanVar(value=True)
        self.filter_eur=tk.BooleanVar(value=True)
        self.filter_jpn=tk.BooleanVar(value=True)
        self.filter_game=tk.BooleanVar(value=True)
        self.filter_dlc=tk.BooleanVar(value=True)
        self.filter_update=tk.BooleanVar(value=True)
        self.filter_demo=tk.BooleanVar(value=True)
        self.filter_hasticket=tk.BooleanVar(value=False)
        self.show_batch=tk.BooleanVar(value=False)
        self.dl_behavior=tk.IntVar(value=1)
        self.fetch_dlc=tk.BooleanVar(value=True)
        self.fetch_updates=tk.BooleanVar(value=True)
        self.remove_ignored=tk.BooleanVar(value=True)
        self.auto_fetching=tk.StringVar(value='prompt')
        self.fetch_on_batch=tk.BooleanVar(value=False)
        self.batch_op_running=tk.BooleanVar(value=False)
        self.total_dl_size=tk.StringVar()
        self.total_dl_size_warning=tk.StringVar()
        self.dl_warning_msg = "     ! You have one or more items in the list with an unknown size. This probably means\n        the tmd can not be downloaded and the title will be skipped by FunKiiU."
        self.idvar=tk.StringVar()
        self.newest_gui_ver=tk.StringVar()
        self.newest_fnku_ver=tk.StringVar()
        self.idvar.trace('w',self.id_changed)
        self.usa_selections={'game':[],'dlc':[],'update':[],'demo':[]}
        self.eur_selections={'game':[],'dlc':[],'update':[],'demo':[]}
        self.jpn_selections={'game':[],'dlc':[],'update':[],'demo':[]}
        self.title_sizes_raw={}
        self.title_sizes={}
        self.reverse_title_names={}
        self.title_dict={}
        self.has_ticket=[]
        self.errors=0
               
        
        # Tab 1
        t1_frm1=ttk.Frame(tab1)   
        t1_frm2=ttk.Frame(tab1)
        t1_frm3=ttk.Frame(tab1)
        t1_frm4=ttk.Frame(tab1)
        t1_frm5=ttk.Frame(tab1)
        t1_frm6=ttk.Frame(tab1)
        
        self.img = PhotoImage(file='logo.ppm')
        logo=ttk.Label(t1_frm1,image=self.img).pack()
        lbl=ttk.Label(t1_frm2,justify='center',text='This is a simple GUI by dojafoja that was written for FunKiiU.\nCredits to cearp, cerea1killer, and all the Github contributors for writing FunKiiU.').pack()
        lbl=ttk.Label(t1_frm3,justify='center',text='If this is your first time running the program, you will need to provide the name of *that key site*. If you haven\'t already\nprovided the address to the key site, you MUST provide it below before proceeding. You only need to provide this information once!').pack(pady=15)
        self.enterkeysite_lbl=ttk.Label(t1_frm4,text='Enter the name of *that key site*. Something like wiiu.thatkeysite.com')
        self.enterkeysite_lbl.pack(pady=15,side='left')
        self.http_lbl=ttk.Label(t1_frm5,text='http://')
        self.http_lbl.pack(pady=15,side='left')
        self.keysite_box=ttk.Entry(t1_frm5,width=40)
        self.keysite_box.pack(pady=15,side='left')
        self.submitkeysite_btn=ttk.Button(t1_frm6,text='submit',command=self.submit_key_site)
        self.submitkeysite_btn.pack()
        self.updatelabel=ttk.Label(t1_frm6,text='')
        self.updatelabel.pack(pady=15)
        
        t1_frm1.pack()
        t1_frm2.pack()
        t1_frm3.pack()
        t1_frm4.pack()
        t1_frm5.pack()
        t1_frm6.pack()


        ## Check for FunKiiU existence and download targeted version if not.
        global fnku
        if not fnku:
            self.set_icon()
            message.showinfo('Missing FunKiiU','You are missing FunKiiU. We are going to download it for you now.',parent=self)
            self.update_application('fnku',targetversion.split('v')[1])
            import FunKiiU as fnku
            global current_fnku
            current_fnku=LooseVersion(str(fnku.__VERSION__))
            message.showinfo('Done','FunKiiU has been downloded for you. Enjoy!',parent=self)
            
        
        # Tab2
        t2_frm0=ttk.Frame(self.tab2)
        t2_frm1=ttk.Frame(self.tab2)
        t2_frm2=ttk.Frame(self.tab2)   
        t2_frm3=ttk.Frame(self.tab2)
        t2_frm4=ttk.Frame(self.tab2)
        t2_frm5=ttk.Frame(self.tab2)
        t2_frm6=ttk.Frame(self.tab2)
        t2_frm7=ttk.Frame(self.tab2)
        t2_frm8=ttk.Frame(self.tab2)
        t2_frm9=ttk.Frame(self.tab2)
        t2_frm10=ttk.Frame(self.tab2)
        t2_frm11=ttk.Frame(self.tab2)
        t2_frm12=ttk.Frame(self.tab2)
        t2_frm13=ttk.Frame(self.tab2)
        t2_frm14=ttk.Frame(self.tab2)
        
        lbl=ttk.Label(t2_frm0,text='Enter as many Title ID\'s as you would like to the list. Use the selection box to make life easier, it has auto-complete.\nYou can also enter a title id manually if you wish. You can set the program to automatically fetch a games update\nand dlc when adding it to the list, adjust download behavior, and more in the Options tab.').pack(padx=5,pady=16)
        lbl=ttk.Label(t2_frm1,text='Choose regions to display:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        filter_box_usa=ttk.Checkbutton(t2_frm1,text='USA',variable=self.filter_usa,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box_eur=ttk.Checkbutton(t2_frm1,text='EUR',variable=self.filter_eur,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box_jpn=ttk.Checkbutton(t2_frm1,text='JPN',variable=self.filter_jpn,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t2_frm2,text='Choose content to display:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        filter_box=ttk.Checkbutton(t2_frm2,text='Game',variable=self.filter_game,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box=ttk.Checkbutton(t2_frm2,text='Update',variable=self.filter_update,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box=ttk.Checkbutton(t2_frm2,text='DLC',variable=self.filter_dlc,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box=ttk.Checkbutton(t2_frm2,text='Demo',variable=self.filter_demo,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box_ticket=ttk.Checkbutton(t2_frm2,text='Only show items with a legit ticket',variable=self.filter_hasticket,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t2_frm3,text='Selection:',font='Helvetica 10 bold').pack(padx=15,pady=7,side='left')
        self.selection_box=AutocompleteCombobox(t2_frm3,values=(self.selection_list),width=73)
        self.selection_box.bind('<<ComboboxSelected>>', self.selection_box_changed)
        self.selection_box.bind('<Return>', self.selection_box_changed)

        ## Change the selection box behavior slightly to clear title id and key boxes on any
        ## non-hits while auto completing. Not sure which is more preferred. 
        #self.selection_box.bind('<<NoHits>>', self.clear_id_key_boxes)
        
        self.selection_box.pack(padx=5,pady=7,side='left')
        lbl=ttk.Label(t2_frm4,text='Title ID:',font='Helvetica 10 bold').pack(padx=15,pady=7,side='left')
        self.id_box=ttk.Entry(t2_frm4,width=30,textvariable=self.idvar)
        self.id_box.pack(padx=5,pady=5,side='left')
        btn=ttk.Button(t2_frm4,text='Add to list',command=lambda:self.add_to_list([self.id_box.get(),])).pack(padx=5,pady=5,side='left')
        self.dl_size_lbl=ttk.Label(t2_frm4,text='Size:,',font='Helvetica 10 bold')
        self.dl_size_lbl.pack(side='left')
        lbl=ttk.Label(t2_frm4,text='Online ticket:',font='Helvetica 10 bold').pack(side='left',padx=5)
        self.has_ticket_lbl=ttk.Label(t2_frm4,text='',font='Helvetica 10 bold')
        self.has_ticket_lbl.pack(side='left')
        lbl=ttk.Label(t2_frm5,text='Key:',font='Helvetica 10 bold').pack(padx=15,pady=7,side='left')
        self.key_box=ttk.Entry(t2_frm5,width=34)
        self.key_box.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t2_frm6,text='Download list:',font='Helvetica 10 bold').pack()
        dl_scroller=ttk.Scrollbar(t2_frm6,orient='vertical')
        dl_scroller.pack(side='right',fill='y')
        self.dl_listbox=tk.Listbox(t2_frm6,width=78,height=12)
        self.dl_listbox.pack(fill='y',pady=3)
        self.dl_listbox.config(yscrollcommand=dl_scroller.set)
        dl_scroller.config(command=self.dl_listbox.yview)
        btn=ttk.Button(t2_frm7,text='Remove selected',command=self.remove_from_list).pack(padx=3,pady=2,side='left',anchor='w')
        btn=ttk.Button(t2_frm7,text='Clear list',command=self.clear_list).pack(padx=3,pady=2,side='left')
        lbl=ttk.Label(t2_frm8,text='',textvariable=self.total_dl_size,font='Helvetica 10 bold').pack(side='left')
        lbl=ttk.Label(t2_frm10,text='',textvariable=self.total_dl_size_warning,foreground='red').pack(side='left')
        lbl1=ttk.Label(t2_frm9,text='Batch options:',font='Helvetica 10 bold').pack(pady=10,padx=15,side='left')
        show=ttk.Radiobutton(t2_frm9,text='Show',variable=self.show_batch,value=True,command=self.toggle_widgets).pack(pady=10,side='left')
        hide=ttk.Radiobutton(t2_frm9,text='Hide',variable=self.show_batch,value=False,command=self.toggle_widgets).pack(pady=10,padx=7,side='left')

        lbl2=ttk.Label(t2_frm11,text='Add all your filtered selections to the list:').pack(padx=10,side='left')
        btn1=ttk.Button(t2_frm11,text='Add all',command=self.add_filtered_to_list).pack(side='left')
        lbl3=ttk.Label(t2_frm12,text='Import batch job:').pack(padx=10,side='left')
        btn2=ttk.Button(t2_frm12,text='Import',command=self.batch_import).pack(side='left')
        lbl4=ttk.Label(t2_frm13,text='Export current list:').pack(padx=10,side='left')
        btn3=ttk.Button(t2_frm13,text='Export',command=self.export_to_batch).pack(side='left')
        btn=ttk.Button(t2_frm14,text='DOWNLOAD',width=30,command=self.download_clicked).pack(padx=5,pady=10,side='left')

              
        t2_frm0.grid(row=0,column=1,columnspan=4,sticky='w')
        t2_frm1.grid(row=1,column=1,columnspan=2,sticky='w')
        t2_frm2.grid(row=2,column=1,columnspan=4,sticky='w')
        t2_frm3.grid(row=3,column=1,columnspan=4,sticky='w')
        t2_frm4.grid(row=4,column=1,columnspan=4,sticky='w')
        t2_frm5.grid(row=5,column=1,columnspan=2,sticky='w')
        t2_frm6.grid(row=6,column=3,rowspan=7,columnspan=3,sticky='e')
        t2_frm7.grid(row=13,column=5,sticky='e')
        t2_frm8.grid(row=13,column=3,padx=20,sticky='w')
        t2_frm9.grid(row=8,column=1,columnspan=2,sticky='w')
        t2_frm10.grid(row=14,column=3,padx=5,columnspan=3,sticky='nw')
        t2_frm11.grid(row=9,column=1,columnspan=2,sticky='w')
        t2_frm12.grid(row=10,column=1,columnspan=2,sticky='w')
        t2_frm13.grid(row=11,column=1,columnspan=2,sticky='w')
        t2_frm14.grid(row=15,column=3,columnspan=3)

        self.batch_frames=(t2_frm11,t2_frm12,t2_frm13)

              
        # Tab3
        t3_frm1=ttk.Frame(tab3)
        t3_frm2=ttk.Frame(tab3)
        t3_frm3=ttk.Frame(tab3)
        t3_frm4=ttk.Frame(tab3)
        t3_frm5=ttk.Frame(tab3)
        t3_frm6=ttk.Frame(tab3)
        t3_frm7=ttk.Frame(tab3)
        t3_frm8=ttk.Frame(tab3)
        t3_frm9=ttk.Frame(tab3)
        self.t3_frm10=ttk.Frame(tab3)
        t3_frm11=ttk.Frame(tab3)
        t3_frm12=ttk.Frame(tab3)
        t3_frm13=ttk.Frame(tab3)
        t3_frm14=ttk.Frame(tab3)
        t3_frm15=ttk.Frame(tab3)
        self.t3_frm16=ttk.Frame(tab3)
        t3_frm17=ttk.Frame(tab3)
        
        lbl=ttk.Label(t3_frm1,text='Output directory:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        self.out_dir_box=ttk.Entry(t3_frm1,width=35,textvariable=self.output_dir)
        self.out_dir_box.pack(padx=5,pady=5,side='left')
        btn=ttk.Button(t3_frm1,text='Browse',command=self.get_output_directory).pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm2,text='Retry count:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        self.retry_count_box=ttk.Combobox(t3_frm2,state='readonly',width=5,values=range(10),textvariable=self.retry_count)
        self.retry_count_box.set(3)
        self.retry_count_box.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm3,text='Patch demo play limit:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        self.patch_demo_true=ttk.Radiobutton(t3_frm3,text='Yes',variable=self.patch_demo,value=True)
        self.patch_demo_false=ttk.Radiobutton(t3_frm3,text='No',variable=self.patch_demo,value=False)
        self.patch_demo_true.pack(padx=5,pady=5,side='left')
        self.patch_demo_false.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm4,text='Patch DLC:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        self.patch_dlc_true=ttk.Radiobutton(t3_frm4,text='Yes',variable=self.patch_dlc,value=True)
        self.patch_dlc_false=ttk.Radiobutton(t3_frm4,text='No',variable=self.patch_dlc,value=False)
        self.patch_dlc_true.pack(padx=5,pady=5,side='left')
        self.patch_dlc_false.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm5,text='Tickets only mode:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        self.tickets_only_true=ttk.Radiobutton(t3_frm5,text='On',variable=self.tickets_only,value=True)
        self.tickets_only_false=ttk.Radiobutton(t3_frm5,text='Off',variable=self.tickets_only,value=False)
        self.tickets_only_true.pack(padx=5,pady=5,side='left')
        self.tickets_only_false.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm6,text='Simulation mode:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        self.simulate_mode_true=ttk.Radiobutton(t3_frm6,text='On',variable=self.simulate_mode,value=True)
        self.simulate_mode_false=ttk.Radiobutton(t3_frm6,text='Off',variable=self.simulate_mode,value=False)
        self.simulate_mode_true.pack(padx=5,pady=5,side='left')
        self.simulate_mode_false.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm7,text='Choose your preferred download behavior:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        bhvr_type=ttk.Radiobutton(t3_frm8,text='Download legit tickets for titles when available and generate fake tickets for titles that do not have legit tickets',variable=self.dl_behavior,value=1,command=self.toggle_widgets).pack(padx=5,pady=5,side='left')
        bhvr_type=ttk.Radiobutton(t3_frm9,text='Only download titles with legit tickets and ignore all others:',variable=self.dl_behavior,value=2,command=self.toggle_widgets).pack(padx=5,pady=5,side='left')
        rem_ignored_bhvr=ttk.Checkbutton(self.t3_frm10,text='Remove ignored items from download list when done.',variable=self.remove_ignored).pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm11,text='Auto-fetch game updates and dlc:',font='Helvetica 10 bold').pack(padx=15,pady=5,side='left')
        lbl=ttk.Label(t3_frm12,text='When adding games to the download list, you can automatically fetch it\'s related update and dlc.').pack(padx=5,side='left')
        bhvr=ttk.Radiobutton(t3_frm13,text='Disabled',variable=self.auto_fetching,value='disabled',command=self.toggle_widgets).pack(padx=5,pady=5,side='left')
        bhvr=ttk.Radiobutton(t3_frm14,text='Prompt for content to fetch',variable=self.auto_fetching,value='prompt',command=self.toggle_widgets).pack(padx=5,pady=5,side='left')
        bhvr=ttk.Radiobutton(t3_frm15,text='Automatically fetch content:',variable=self.auto_fetching,value='auto',command=self.toggle_widgets).pack(padx=5,pady=5,side='left')
        fetch_up_bhvr=ttk.Checkbutton(self.t3_frm16,text='Fetch game updates',variable=self.fetch_updates).pack(padx=15,pady=5,side='left')
        fetch_dlc_bhvr=ttk.Checkbutton(self.t3_frm16,text='Fetch game dlc',variable=self.fetch_dlc).pack(padx=5,pady=5,side='left')
        allow_fetch_bhvr=ttk.Checkbutton(self.t3_frm16,text='Allow auto-fetching when\ndoing batch imports',variable=self.fetch_on_batch).pack(padx=5,pady=5,side='left')
        btn=ttk.Button(t3_frm17,text='Save as my settings',width=20,command=self.save_settings).pack(padx=10,pady=10,anchor='n')
        btn=ttk.Button(t3_frm17,text='Reset settings',width=20,command=lambda:self.load_settings(reset=True)).pack(padx=10,pady=10,anchor='s')
        
        t3_frm1.grid(row=1,column=1,sticky='w')
        t3_frm2.grid(row=2,column=1,sticky='w')
        t3_frm3.grid(row=3,column=1,sticky='w')
        t3_frm4.grid(row=4,column=1,sticky='w')
        t3_frm5.grid(row=5,column=1,sticky='w')
        t3_frm6.grid(row=6,column=1,sticky='w')
        t3_frm7.grid(row=7,column=1,sticky='w')
        t3_frm8.grid(row=8,column=1,padx=40,sticky='w')
        t3_frm9.grid(row=9,column=1,padx=40,sticky='w')
        self.t3_frm10.grid(row=10,column=1,padx=80,sticky='w')
        t3_frm11.grid(row=11,column=1,sticky='w')
        t3_frm12.grid(row=12,column=1,padx=40,sticky='w')
        t3_frm13.grid(row=13,column=1,padx=40,sticky='w')
        t3_frm14.grid(row=14,column=1,padx=40,sticky='w')
        t3_frm15.grid(row=15,column=1,padx=40,sticky='w')
        self.t3_frm16.grid(row=16,column=1,padx=80,sticky='w')
        t3_frm17.grid(row=17,column=2,sticky='e')
        
        
        # Tab 4
        t4_frm0=ttk.Frame(tab4)
        t4_frm1=ttk.Frame(tab4)
        t4_frm2=ttk.Frame(tab4)
        t4_frm3=ttk.Frame(tab4)
        t4_frm4=ttk.Frame(tab4)
        t4_frm5=ttk.Frame(tab4)
        t4_frm6=ttk.Frame(tab4)
        t4_frm7=ttk.Frame(tab4)
        t4_frm8=ttk.Frame(tab4)
        t4_frm9=ttk.Frame(tab4)
        t4_frm10=ttk.Frame(tab4)
        t4_frm11=ttk.Frame(tab4)

        lbl=ttk.Label(t4_frm0,text='Version Information:\n\nSince the FunKii-UI GUI and FunKiiU are two seperate applications developed by different authors,\nswitching versions can break compatibility and shouldn\'t be done if you don\'t know what you are\ndoing. I will try to implement a compatibility list in a future release').pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm1,text='GUI application:',font="Helvetica 13 bold").pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t4_frm2,text='Running version:\nTargeted for:').pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm2,text=__VERSION__+'\n'+targetversion).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm3,text='Latest release:').pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t4_frm3,textvariable=self.newest_gui_ver).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm4,text='Update to latest release:').pack(padx=5,pady=1,side='left')
        btn=ttk.Button(t4_frm4,text='Update',command=lambda:self.update_application('gui',self.versions['gui_new'])).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm5,text='Switch to different version:').pack(padx=5,pady=1,side='left')
        self.gui_switchv_box=ttk.Combobox(t4_frm5,width=7,values=[x for x in self.versions['gui_all']],state='readonly')
        self.gui_switchv_box.pack(padx=5,pady=1,side='left')
        btn=ttk.Button(t4_frm5,text='Switch',command=lambda:self.update_application('gui',self.gui_switchv_box.get())).pack(padx=5,pady=1,side='left')        
        lbl=ttk.Label(t4_frm6,text='').pack(pady=15,side='left')
        lbl=ttk.Label(t4_frm7,text='FunKiiU core application:',font="Helvetica 13 bold").pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t4_frm8,text='running version:').pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm8,text=fnku.__VERSION__).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm9,text='latest release:').pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm9,textvariable=self.newest_fnku_ver).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm10,text='Update to latest release:').pack(padx=5,pady=1,side='left')
        btn=ttk.Button(t4_frm10,text='Update',command=lambda:self.update_application('fnku',self.versions['fnku_new'])).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm11,text='Switch to different version:').pack(padx=5,pady=1,side='left')
        self.fnku_switchv_box=ttk.Combobox(t4_frm11,width=7,values=[x for x in self.versions['fnku_all']],state='readonly')
        self.fnku_switchv_box.pack(padx=5,pady=1,side='left')
        btn=ttk.Button(t4_frm11,text='Switch',command=lambda:self.update_application('fnku',self.fnku_switchv_box.get())).pack(padx=5,pady=1,side='left')
        
        t4_frm0.grid(row=0,column=1,padx=5,pady=5,sticky='w')
        t4_frm1.grid(row=1,column=1,padx=5,sticky='w')
        t4_frm2.grid(row=2,column=1,padx=25,sticky='w')
        t4_frm3.grid(row=3,column=1,padx=25,sticky='w')
        t4_frm4.grid(row=4,column=1,padx=25,sticky='w')
        t4_frm5.grid(row=5,column=1,padx=25,sticky='w')
        t4_frm6.grid(row=6,column=1,padx=5,sticky='w')
        t4_frm7.grid(row=7,column=1,padx=5,sticky='w')
        t4_frm8.grid(row=8,column=1,padx=25,sticky='w')
        t4_frm9.grid(row=9,column=1,padx=25,sticky='w')
        t4_frm10.grid(row=10,column=1,padx=25,sticky='w')
        t4_frm11.grid(row=11,column=1,padx=25,sticky='w')

        self.load_program_revisions()   
        self.check_config_keysite()
        self.total_dl_size.set('Total Size:')
        self.load_settings()
        self.toggle_widgets()
        self.load_title_data()
        self.load_title_sizes()
        self.build_database()
        
        if os.path.isfile('config.json'):
            self.populate_selection_box()
            
        ## Build an sqlite database of all the data in the titlekeys json as well as size information
        ## for the title. Raw size in bytes as well as human readable size is recorded.
        ## The database that ships with the releases are minimal, containing ONLY size information.
        ## A full db build is mostly for redundancy and can be built by deleting the old data.db file,
        ## setting sizeonly=False, uncomment self.build_database() below and run the program.
        ## Be sure to re-comment out self.build_database() before running the program again.
        ## This will take a short while to fetch all the download size information.
        

        #self.build_database()
    
    def build_database(self,sizeonly=True):
        if len(self.title_sizes) >= len(self.title_data):
            return
        print('\nUpdating size information database now.....\n')
        dataset=[]
        compare_ids=[]
        TK = fnku.TK
        try:
            update_count= len(self.title_data) - len(self.title_sizes)
        except:
            update_count = len(self.title_data)
        message.showinfo('Update database', 'Your size info database needs to be updated. We will update '+str(update_count) +' entries now and continue when it\'s done',parent=self)
        if not os.path.isfile('data.db'):
            db=sqlite3.connect('data.db')
            cursor=db.cursor()
            cursor.execute(""" CREATE TABLE titles(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, title_id TEXT, title_key TEXT, name TEXT, region TEXT, content_type TEXT, size TEXT, ticket INT, raw_size INT) """)
        else:
            db=sqlite3.connect('data.db')
            cursor=db.cursor()
        cursor.execute("""SELECT title_id FROM titles""")
        
        for i in cursor:
            compare_ids.append(str(i[0]))
                                                 
        loopcounter=1
        for i in self.title_data:
            if not str(i[2]) in compare_ids:
                print('Fetching database info, title {} of {}'.format(loopcounter,update_count))                                                                        
                name=i[0]
                region=i[1]
                tid=i[2]
                tkey=i[3]
                cont=i[4]
                if tid in self.has_ticket:
                    tick=1
                else:
                    tick=0
                
                sz=0
                total_size=0
                    
                baseurl = 'http://ccs.cdn.c.shop.nintendowifi.net/ccs/download/{}'.format(tid)

                if not fnku.download_file(baseurl + '/tmd', 'title.tmd', 1):
                    print('ERROR: Could not download TMD...')
                else:
                    with open('title.tmd', 'rb') as f:
                        tmd = f.read()
                    content_count = int(binascii.hexlify(tmd[TK + 0x9E:TK + 0xA0]), 16)
    
                    total_size = 0
                    for i in range(content_count):
                        c_offs = 0xB04 + (0x30 * i)
                        c_id = binascii.hexlify(tmd[c_offs:c_offs + 0x04]).decode()
                        total_size += int(binascii.hexlify(tmd[c_offs + 0x08:c_offs + 0x10]), 16)
                    sz = fnku.bytes2human(total_size)
                    os.remove('title.tmd')
                
                dataset.append((tid,tkey,name,region,cont,sz,total_size,tick))
                loopcounter += 1
                
        if len(dataset) > 0:   
            for i in dataset:
                tid=i[0]
                tkey=i[1]
                name=i[2]
                region=i[3]
                cont=i[4]
                sz=i[5]
                raw=i[6]
                tick=i[7]
                if sizeonly:
                    cursor.execute("""INSERT INTO titles (title_id, size, raw_size) VALUES (?, ?, ?)""", (tid,sz,raw))
                else:
                    cursor.execute("""INSERT INTO titles (title_id, title_key, name, region, content_type, size, ticket, raw_size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (tid,tkey,name,region,cont,sz,tick,raw))
        db.commit()
        db.close()
        print('done writing to database.')
        message.showinfo('Done','Done updatating database',parent=self)
        
    def load_title_sizes(self):
        if os.path.isfile('data.db'):
            db = sqlite3.connect('data.db')
            cursor = db.cursor()
            cursor.execute("""SELECT title_id, size, raw_size FROM titles""")
            for i in cursor:
                    self.title_sizes[str(i[0])] = str(i[1])
                    self.title_sizes_raw[str(i[0])] = str(i[2])
            db.close()
        else:
            print('No data.db file found.')
            self.title_sizes={}
            self.title_sizes_raw={}

    def id_changed(self,*args):
        self.key_box.delete('0',tk.END)
        t_id=self.id_box.get()
        if len(t_id) == 16:
            try:
                self.selection_box.set(self.title_dict[t_id].get('longname',''))                
                if t_id in self.has_ticket:
                    self.has_ticket_lbl.configure(text='YES',foreground='green')
                else:
                    self.has_ticket_lbl.configure(text='NO',foreground='red')                
                if self.title_dict[t_id].get('key',None):
                    self.key_box.insert('end',self.title_dict[t_id]['key'])
                if self.title_sizes.get(t_id,None):
                    self.dl_size_lbl.configure(text='Size: '+self.title_sizes[t_id]+',')
                else:
                    self.dl_size_lbl.configure(text='Size: ?,')
                    
            except Exception as e:
                #print(e)
                self.selection_box.set('')
                self.dl_size_lbl.configure(text='Size: ?,')
        
        else:
            if self.dl_size_lbl.cget('text') != 'Size:,':
                self.dl_size_lbl.configure(text='Size:,')
            if self.has_ticket_lbl.cget('text') != '':
                self.has_ticket_lbl.configure(text='')


    def update_keysite_widgets(self):
        txt='Correct keysite is already loaded'
        self.enterkeysite_lbl.configure(text=txt,background='black',foreground='green',font="Helvetica 13 bold")
        self.http_lbl.pack_forget()
        self.keysite_box.pack_forget()
        self.submitkeysite_btn.pack_forget()
        
    def check_config_keysite(self):
        try:
            with open('config.json','r') as cfg:
                config=json.load(cfg)                
                site=config['keysite']
                if fnku.hashlib.md5(site.encode('utf-8')).hexdigest() == fnku.KEYSITE_MD5:
                    self.update_keysite_widgets()
                    
        except IOError:
            pass
        
    def notify_of_update(self,update=True):
        txt='Updates are available in the updates tab'
        fg='red'
        if not update:
            txt='No updates are currently available'
            fg='green'
        self.updatelabel.configure(text=txt,background='black',foreground=fg,font="Helvetica 13 bold")
        
    def update_application(self,app,zip_file):
        if app == 'fnku':
            self.download_zip(self.versions['fnku_url'].split('releases')[0]+'archive'+'/v'+zip_file+'.zip')
        else:
            self.download_zip(self.versions['gui_url'].split('releases')[0]+'archive'+'/v'+zip_file+'.zip')
            
        if self.unpack_zip('update.zip'):
            print('Update completed succesfully! Restart application\nfor changes to take effect.')
            os.remove('update.zip')
            
    def unpack_zip(self,zip_name):
        try:
            print('unzipping update')
            cwd=os.getcwd()
            dest=cwd+dir_slash+zip_name
            zfile=zipfile.ZipFile(dest,'r')
            for i in zfile.namelist():
                if i[-3:] in ('.py','ppm','.db','son'):
                    data=zfile.read(i,None)
                    x=i.split("/")[1]
                    if x!='':
                        with open(x,'wb') as p_file:
                            p_file.write(data)                      
            zfile.close()           
            return True
        
        except Exception as e:
            print('Error:',e)
            return False
        
    def download_zip(self,url):
        try:
            z = urlopen(url)
            print('Downloading ', url)      
            with open('update.zip', "wb") as f:
                f.write(z.read())
            
        except HTTPError as e:
            print("Error:", e.code, url)
        except URLError as e:
            print ("Error:", e.reason, url)
                   
    def populate_selection_box(self,download_data=True):
        if download_data:
            keysite = fnku.get_keysite()
            print(u'Downloading/updating data from {0}'.format(keysite))

            if not fnku.download_file('https://{0}/json'.format(keysite), 'titlekeys.json', 3):
                print('ERROR: Could not download data file...\n')
            else:
                print('DONE....Downloaded titlekeys.json succesfully')
        try:
            self.clear_id_key_boxes()
            self.selection_list=[]    
            self.load_title_data()
            
            if self.filter_usa.get():
                if self.filter_game.get():
                    for i in self.usa_selections['game']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_dlc.get():
                    for i in self.usa_selections['dlc']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)   
                if self.filter_update.get():
                    for i in self.usa_selections['update']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_demo.get():
                    for i in self.usa_selections['demo']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                    
            if self.filter_eur.get():
                if self.filter_game.get():
                    for i in self.eur_selections['game']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_dlc.get():
                    for i in self.eur_selections['dlc']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)       
                if self.filter_update.get():
                    for i in self.eur_selections['update']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_demo.get():
                    for i in self.eur_selections['demo']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                        
            if self.filter_jpn.get():
                if self.filter_game.get():
                    for i in self.jpn_selections['game']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_dlc.get():
                    for i in self.jpn_selections['dlc']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_update.get():
                    for i in self.jpn_selections['update']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_demo.get():
                    for i in self.jpn_selections['demo']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                            
            self.selection_list.sort()
            self.selection_box.set('')
            self.selection_box.configure(values=(self.selection_list))
            self.selection_box.set_completion_list(self.selection_list)
            print('Succesfully populated the selection box..')
        except Exception as e:
            print('Something happened while trying to populate the selection box...')
            print('ERROR:' ,e)

    def clear_id_key_boxes(self,*args):
        self.id_box.delete('0',tk.END)
        self.key_box.delete('0',tk.END)
        
    def selection_box_changed(self,*args):
        user_selected_raw=self.selection_box.get()
        self.clear_id_key_boxes()
        titleid = self.reverse_title_names[user_selected_raw]
        self.id_box.insert('end',titleid)

    def toggle_widgets(self):
        if self.show_batch.get():
            for i in self.batch_frames:
                i.grid()
        else:
            for i in self.batch_frames:
                i.grid_remove()

        if self.dl_behavior.get() == 2:
            self.t3_frm10.grid()
        else:
            self.t3_frm10.grid_remove()
        
        if self.auto_fetching.get() == 'auto':
            self.t3_frm16.grid()
        else:
            self.t3_frm16.grid_remove()

    def export_to_batch(self):
        outf = filedialog.asksaveasfilename(defaultextension='.txt')
        if outf:
            with open(outf,'w') as f:
                for i in self.download_list:
                    f.write(i[1].strip()+'\n')
            message.showinfo('Complete','Done exporting batch job to file')

    def batch_import(self):
        titles=[]
        inf = filedialog.askopenfilename()
        if inf:
            with open(inf,'r') as f:
                lines=f.readlines()
                for line in lines:
                    line=line.strip().strip('\n')
                    line=line.replace('-','')
                    if len(line) == 16:
                        titles.append(line)
            if len(titles) > 0:
                self.add_to_list(titles,batch=True)
    
    def load_title_data(self):       
        self.title_data=[]
        try:
            if not os.path.isfile('titlekeys.json'):
                return
            with open('titlekeys.json') as td:
                title_data=json.load(td)
            self.errors=0
            print('Now parsing titlekeys.json')
            for i in title_data:
                try:
                    if i['name']:
                        titleid=i['titleID']
                        name=i['name']
                        name=name.lower().capitalize().strip()
                        titlekey=i['titleKey']
                        region=i['region']
                        tick=i['ticket']
                        if titleid[4:8] == '0000':
                            content_type='GAME'
                        elif titleid[4:8] == '000c':
                            content_type='DLC'
                        elif titleid[4:8] == '000e':
                            content_type='UPDATE'
                        elif titleid[4:8] == '0002':
                            content_type='DEMO'
                            
                        if tick == '1':
                            self.has_ticket.append(titleid)
                        
                        longname=name+'  --'+region+'  -'+content_type
                        entry=(name,region,titleid,titlekey,content_type,longname)
                        entry2=(longname)
                        self.reverse_title_names[longname]=titleid 
                        self.title_dict[titleid]={'name':name, 'region':region, 'key':titlekey, 'type':content_type, 'longname':longname, 'ticket':tick}
                        
                        if not entry in self.title_data:
                            self.title_data.append(entry)
                            if region == 'USA':
                                if content_type == 'GAME':
                                    if not entry2 in self.usa_selections['game']:
                                        self.usa_selections['game'].append(entry2)
                                elif content_type == 'DLC':
                                    if not entry2 in self.usa_selections['dlc']:
                                        self.usa_selections['dlc'].append(entry2)
                                elif content_type == 'UPDATE':
                                    if not entry2 in self.usa_selections['update']:
                                        self.usa_selections['update'].append(entry2)
                                elif content_type == 'DEMO':
                                    if not entry2 in self.usa_selections['demo']:
                                        self.usa_selections['demo'].append(entry2)
                            elif region == 'EUR':
                                if content_type == 'GAME':
                                    if not entry2 in self.eur_selections['game']:
                                        self.eur_selections['game'].append(entry2)
                                elif content_type == 'DLC':
                                    if not entry2 in self.eur_selections['dlc']:
                                        self.eur_selections['dlc'].append(entry2)
                                elif content_type == 'UPDATE':
                                    if not entry2 in self.eur_selections['update']:
                                        self.eur_selections['update'].append(entry2)
                                elif content_type == 'DEMO':
                                    if not entry2 in self.eur_selections['demo']:
                                        self.eur_selections['demo'].append(entry2)
                            elif region == 'JPN':
                                if content_type == 'GAME':
                                    if not entry2 in self.jpn_selections['game']:
                                        self.jpn_selections['game'].append(entry2)
                                elif content_type == 'DLC':
                                    if not entry2 in self.jpn_selections['dlc']:
                                        self.jpn_selections['dlc'].append(entry2)
                                elif content_type == 'UPDATE':
                                    if not entry2 in self.jpn_selections['update']:
                                        self.jpn_selections['update'].append(entry2)
                                elif content_type == 'DEMO':
                                    if not entry2 in self.jpn_selections['demo']:
                                        self.jpn_selections['demo'].append(entry2)
                except Exception as e:
                    if DEBUG:
                        print('Error on title: ' + titleid)
                        print('ERROR LOADING ',e)
                        self.errors+=1
        except IOError:
            print('No titlekeys.json file was found. The selection box will be empty')
        if DEBUG: print(str(self.errors)+' Titles did not load correctly.')
         
    def sanity_check_input(self,val,chktype):
        try:
            if chktype == 'title':
                if len(val) == 16:
                    val=int(val,16)
                    return True
            elif chktype =='key':
                if len(val) == 32:
                    val=int(val,16)
                    return True
            else:
                return False
        except ValueError:
            return False

    def fetch_related_content(self,tid):
            if not self.fetch_dlc.get and not self.fetch_updates.get():
                return
            update=None
            dlc=None
            up_id='e'
            dlc_id='c'
            tryupid=tid[:7]+up_id+tid[8:]
            trydlcid=tid[:7]+dlc_id+tid[8:]
            if self.title_dict.get(tryupid,None):
                update=tryupid
            if self.title_dict.get(trydlcid,None):
                dlc=trydlcid
            titles={}
            titles['update']=update
            titles['dlc']=dlc
            return titles

    def save_settings(self):
        x=(self.output_dir.get(),self.retry_count.get(),self.patch_demo.get(),self.patch_dlc.get(),self.tickets_only.get(),self.simulate_mode.get(),self.fetch_dlc.get(),self.fetch_updates.get(),
                        self.remove_ignored.get(),self.auto_fetching.get(),self.fetch_on_batch.get(),self.dl_behavior.get())
        settings = {'output_dir':x[0],'retry_count':x[1],'patch_demo':x[2],'patch_dlc':x[3],'tickets_only':x[4],'simulate_mode':x[5],'fetch_dlc':x[6],'fetch_updates':x[7],
                    'remove_ignored':x[8],'auto_fetching':x[9],'fetch_on_batch':x[10],'dl_behavior':x[11]}
        with open('guisettings.json','w') as f:
            json.dump(settings,f)

    def load_settings(self,reset=False):
        if reset:
            self.output_dir.set('')
            self.retry_count.set(3)
            self.patch_demo.set(True)
            self.patch_dlc.set(True)
            self.tickets_only.set(False)
            self.simulate_mode.set(False)
            self.fetch_dlc.set(True)
            self.fetch_updates.set(True)
            self.remove_ignored.set(True)
            self.auto_fetching.set('prompt')
            self.fetch_on_batch.set(False)
            self.dl_behavior.set(1)
            self.save_settings()
            return
            
        with open('guisettings.json', 'r') as f:
            x=json.load(f)
        self.output_dir.set(x['output_dir'])
        self.retry_count.set(x['retry_count'])
        self.patch_demo.set(x['patch_demo'])
        self.patch_dlc.set(x['patch_dlc'])
        self.tickets_only.set(x['tickets_only'])
        self.simulate_mode.set(x['simulate_mode'])
        self.fetch_dlc.set(x['fetch_dlc'])
        self.fetch_updates.set(x['fetch_updates'])
        self.remove_ignored.set(x['remove_ignored'])
        self.auto_fetching.set(x['auto_fetching'])
        self.fetch_on_batch.set(x['fetch_on_batch'])
        self.dl_behavior.set(x['dl_behavior'])
        
            
        
    def add_to_list(self,titles,batch=False):
        do_add_update=False
        do_add_dlc=False
        fetch_bhvr=self.auto_fetching.get()
        fetch_on_batch=self.fetch_on_batch.get()
        fetch_updates=self.fetch_updates.get()
        fetch_dlc=self.fetch_dlc.get()
        if not batch:
            if not len(titles[0]) == 16:
                message.showerror('No title id','You did not provide a 16 digit title id')
                return
            if fetch_bhvr != 'disabled':               
                if titles[0][7] == '0':
                    fetched=self.fetch_related_content(titles[0])
                    try:
                        if fetched:
                            if fetch_updates:
                                if fetched['update']:
                                    if fetch_bhvr == 'prompt':
                                        if message.askyesno('Game update is available','There is an update available for this game, would you like to add it to\nthe list as well?'):
                                            titles.append(fetched['update'])
            
                                    elif fetch_bhvr == 'auto':
                                            titles.append(fetched['update'])
                            if fetch_dlc:
                                if fetched['dlc']:
                                    if fetch_bhvr == 'prompt':
                                        if message.askyesno('Game dlc is available','There is dlc available for this game, would you like to add it to\nthe list as well?'):
                                            titles.append(fetched['dlc'])
                                    elif fetch_bhvr == 'auto':
                                            titles.append(fetched['dlc'])
                    except:
                        pass
                    
        else:
            if fetch_bhvr == 'auto' and fetch_on_batch:
                for title in titles[:]:
                    if title[7] == '0':
                        fetched=self.fetch_related_content(title)
                    try:
                        if fetched:
                            if fetched['update'] and fetch_updates:
                                titles.append(fetched['update'])
                            if fetched['dlc'] and fetch_dlc:
                                titles.append(fetched['dlc'])
                    except Exception as e:
                        print(e)
                                                
                                                                         
        for titleid in titles:
            if len(titleid) == 16:
                td = self.title_dict.get(titleid,{})
                key=None       
                name = td.get('longname',titleid)
                name='  '+name
                if self.sanity_check_input(titleid,'title'):
                    pass
                else:
                    print('Bad Title ID. Must be a 16 digit hexadecimal.')
                    print('Title: '+titleid)
                    continue

                key=td.get('key',self.key_box.get().strip())
                if key == '':
                    key=None
                if not key or self.sanity_check_input(key,'key'):
                    pass
                else:
                    print('Bad Key. Must be a 32 digit hexadecimal.')
                    print('Title: '+titleid)
                    continue
 
                size=int(self.title_sizes_raw.get(titleid,0))
                if size == 0:
                    name =' !'+name
                entry=(name,titleid,key,size)
                if not entry in self.download_list:
                    self.download_list.append(entry)
        
        self.populate_dl_listbox()

    def add_filtered_to_list(self):
        bulk=[]
        for i in self.selection_list:
            if self.reverse_title_names.get(i,None):
                bulk.append(self.reverse_title_names[i])
        self.add_to_list(bulk,batch=True)

    def remove_from_list(self):
        try:
            index=self.dl_listbox.curselection()
            item=self.dl_listbox.get('anchor')
            for i in self.download_list:
                if i[0] == item:
                    self.download_list.remove(i)
            self.populate_dl_listbox()
        except IndexError as e:
            print('Download list is already empty')
            print(e)

    def clear_list(self):
        self.download_list=[]
        self.populate_dl_listbox()
        
    def populate_dl_listbox(self):
        total_size=[]
        trigger_warning=False
        self.dl_listbox.delete('0',tk.END)
        for i in self.download_list:
            name=i[0]
            if i[3] == 0:
                if not trigger_warning:
                    trigger_warning=True
            self.dl_listbox.insert('end',name)
            total_size.append(int(i[3]))
        total_size=sum(total_size)
        total_size=fnku.bytes2human(total_size)
        self.total_dl_size.set('Total size: '+total_size)
        if trigger_warning:
            self.total_dl_size_warning.set(self.dl_warning_msg)
        else:
            self.total_dl_size_warning.set('')
        return

    def submit_key_site(self):
        site=self.keysite_box.get().strip()
        if fnku.hashlib.md5(site.encode('utf-8')).hexdigest() == fnku.KEYSITE_MD5:
            print('Correct key site, now saving...')
            config=fnku.load_config()
            config['keysite'] = site
            fnku.save_config(config)
            print('done saving, you are good to go!')
            self.update_keysite_widgets()
            self.populate_selection_box()
            self.build_database()
            self.load_title_sizes()
            self.nb.select(self.tab2)
        else:
            print('Wrong key site provided. Try again')

    def get_output_directory(self):
        out_dir=filedialog.askdirectory()
        self.out_dir_box.delete('0',tk.END)
        self.out_dir_box.insert('end',out_dir)

    def load_program_revisions(self):
        print('Checking for program updates, this might take a few seconds.......\n')
        url1=self.versions['fnku_url']
        url2=self.versions['gui_url']    
        response = urlopen(url1)
        rslts=response.read()
        rslts=str(rslts)
        x=''
        for i in rslts:
            x=x+i
        parser = VersionParser()
        parser.feed(x)
        response = urlopen(url2)
        rslts=response.read()
        rslts=str(rslts)
        x=''
        for i in rslts:
            x=x+i
        parser = VersionParser()
        parser.feed(x)

        fnku_data_set = parser.fnku_data_set
        gui_data_set = parser.gui_data_set
        
        fnku_all=[]
        fnku_newest=''
        gui_all=[]
        gui_newest=''
        
        for i in fnku_data_set:
            ver=LooseVersion(i.split('/')[4][1:-4])
            fnku_all.append(str(ver))
        fnku_newest=max(fnku_all)
        
        for i in gui_data_set:
            if(i.split('/')[4] == 'download'):
                ver=LooseVersion(i.split('/')[5][1:-4])
            else:
                ver=LooseVersion(i.split('/')[4][1:-4])  #archived url
            if ver > LooseVersion('2.0.5'):
                gui_all.append(ver)
                
        gui_newest=max(gui_all)
        if gui_newest > current_gui or fnku_newest > current_fnku:
            self.notify_of_update()
        else:
            self.notify_of_update(update=False)
            

        self.versions['fnku_all']=fnku_all
        self.versions['fnku_new']=fnku_newest
        self.newest_fnku_ver.set(fnku_newest)
        self.versions['gui_all']=[str(i) for i in gui_all]
        self.versions['gui_new']=str(gui_newest)
        self.newest_gui_ver.set(gui_newest)
        self.gui_switchv_box.configure(values=[x for x in self.versions['gui_all']])
        self.fnku_switchv_box.configure(values=[x for x in self.versions['fnku_all']])
        
    def download_clicked(self):
        title_list=[]
        key_list=[]
        rtry_count=self.retry_count.get()
        ptch_demo=self.patch_demo.get()
        ptch_dlc=self.patch_dlc.get()
        tick_only=self.tickets_only.get()
        sim=self.simulate_mode.get()
        for i in self.download_list:
            title_list.append(i[1])
            key_list.append(i[2])
            
        ignored=[]
        behavior=self.dl_behavior.get()
        for i in self.download_list[:]:
            out_dir=self.output_dir.get().strip()
            t=i[1]
            k=i[2]
            td=self.title_dict.get(t,{})
            n=td.get('name','').strip()
            if td.get('type','').strip() == 'DEMO':
                n=n+'_Demo'
            r=td.get('region','').strip()
                
            if t in self.has_ticket or td.get('type','') == 'UPDATE':
                fnku.process_title_id(t, None, name=n, region=r, output_dir=out_dir, retry_count=rtry_count, onlinetickets=True, patch_demo=ptch_demo,
                                      patch_dlc=ptch_demo, simulate=sim, tickets_only=tick_only)
                self.download_list.remove(i)
                
            else:
                if behavior == 2:
                    if self.remove_ignored.get():
                        self.download_list.remove(i)
                        self.populate_dl_listbox()
                        root.update()
                    ignored.append(i[1])
                    continue
                
                fnku.process_title_id(t, k, name=n, region=r, output_dir=out_dir, retry_count=rtry_count, patch_demo=ptch_demo,
                                      patch_dlc=ptch_demo, simulate=sim, tickets_only=tick_only)
                self.download_list.remove(i)

            
            self.populate_dl_listbox()
            root.update()           
        print(str(len(ignored))+' titles were ignored and not downloaded')

    def set_icon(self):
        icon = PhotoImage(file='icon.ppm')
        self.tk.call('wm', 'iconphoto', self._w, icon)
        
        
if __name__ == '__main__':
    root=RootWindow()
    root.title('FunKii-UI')
    root.resizable(width=False,height=False)
    root.set_icon()
    root.mainloop()
    
