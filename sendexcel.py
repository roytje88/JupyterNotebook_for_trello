#!/usr/bin/env python
# coding: utf-8

# In[ ]:


exec(open("./cardsperdate.py").read())


# In[ ]:


labelslist = []
for i,j in kaarten.items():
    for k,l in j.items():
        if k=='labels' and l != {}:
            for m,n in l.items():
                labelslist.append((i,n))


# In[ ]:


memberslist = []
for i,j in kaarten.items():
    for k,l in j.items():
        if k=='members' and l !={}:
            for m,n in l.items():
                memberslist.append((i,n))


# In[ ]:


if labelslist != []:
    columnslabels = ['cardid','label']
    columnsmembers = ['cardid','member']
    df1 = pd.DataFrame(data=kaarten).T
    df2 = pd.DataFrame(data=labelslist,columns=columnslabels)
    df3 = pd.merge(df1,df2,on='cardid', how='left')
    df4 = pd.DataFrame(data=memberslist,columns=columnsmembers)
    df5 = pd.merge(df3,df4,on='cardid', how='left')
    df5.to_excel('alldata.xlsx')
else:
    columnsmembers = ['cardid','member']
    df1 = pd.DataFrame(data=kaarten).T
    df2 = pd.DataFrame(data=memberslist,columns=columnsmembers)
    df3 = pd.merge(df1,df2,on='cardid', how='left')
    df3.to_excel('alldata.xlsx')
    


# In[ ]:


df = pd.DataFrame(data=datesdict).T
df.to_excel('dates.xlsx')


# In[ ]:


fromaddr = email
msg = MIMEMultipart() 
msg['From'] = fromaddr 
msg['To'] = toaddr 
msg['Subject'] = subj
body = " "
msg.attach(MIMEText(body, 'plain')) 
filename_alldata = "alldata.xlsx"
attachment_alldata = open("./alldata.xlsx", "rb") 
filename_dates = "dates.xlsx"
attachment_dates = open("./dates.xlsx", "rb") 

p = MIMEBase('application', 'octet-stream') 
p.set_payload((attachment_alldata).read()) 
encoders.encode_base64(p) 
p.add_header('Content-Disposition', "attachment; filename= %s" % filename_alldata)
msg.attach(p) 

q = MIMEBase('application', 'octet-stream') 
q.set_payload((attachment_dates).read()) 
encoders.encode_base64(q) 
q.add_header('Content-Disposition', "attachment; filename= %s" % filename_dates)
msg.attach(q)
s = smtplib.SMTP('smtp.gmail.com', 587) 
s.starttls() 
s.login(fromaddr, password) 
text = msg.as_string() 
s.sendmail(fromaddr, toaddr, text)
s.quit() 

