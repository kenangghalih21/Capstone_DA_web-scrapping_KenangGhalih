from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
temp = [] # var penampung

for page_num in range(1, 16):    
    url = f'https://www.kalibrr.id/job-board/te/data/{page_num}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

#find your right key here
    Title = soup.find_all('a', attrs={'class':'k-text-primary-color'})[:15]
    Location = soup.find_all('a', attrs={'class':'k-text-subdued k-block'})[:15]
    #post_on
    Post_on = soup.find_all('span', attrs={'class':'k-block k-mb-1'})[:15]
    #get deadline
    Deadline = soup.find_all('span', attrs={'class':'k-block k-mb-1'})[:15]
    # Mencari 15 elemen span dengan class 'class-span' pada halaman tersebut
    Company = soup.find_all('span', {'class':'k-inline-flex k-items-center k-mb-1'})[:15]


    for a in Title:
        print(a.text.strip())
        
    for a in Location:
        print(a.text.strip())
        
    for span in Post_on:
        print(span.text.strip())
        
    for span in Deadline:
        print(span.text.strip())

    for span in Company:
        print(span.text.strip())


#insert the scrapping process here
    
    temp.append((Title, Location, Post_on, Deadline, Company)) 

temp = temp[::-1]

#change into dataframe
data = []
for page_data in temp:
    
    #1 Mengekstrak list yang telah dibuat dalam looping sebelumnya menjadi informasi text
    title_new = [Title.text.strip() for Title in page_data[0]]
    location_new = [Location.text.strip() for Location in page_data[1]]
    post_on_new = [Post_on.text.strip() for Post_on in page_data[2]]
    deadline_new = [Deadline.text.strip() for Deadline in page_data[3]]
    company_new = [Company.text.strip() for Company in page_data[4]]
    
    #2 Menambahkan list yang baru saja dibentuk dengan operator penambahan list (+=) dan menggabungkannya dengan list(zip())
    data += list(zip(title_new, location_new, post_on_new, deadline_new, company_new))

df = pd.DataFrame(data, columns=['title', 'location', 'post_on', 'deadline', 'company'])
    
#insert data wrangling here
df['location'] = df['location'].str.replace(", Indonesia","")
df['location'] = df['location'].str.replace("Kota Jakarta Barat","Jakarta Barat")
df['location'] = df['location'].str.replace("Central Jakarta City","Jakarta Pusat")
df['location'] = df['location'].str.replace("Central Jakarta","Jakarta Pusat")
df['location'] = df['location'].str.replace("South Jakarta","Jakarta Selatan")
df['location'] = df['location'].str.replace("North Jakarta","Jakarta Utara")
df['location'] = df['location'].str.replace("South Tangerang","Tangerang Selatan")
df['location'] = df['location'].str.replace("West Jakarta","Jakarta Barat")
df['location'] = df['location'].str.replace("East Jakarta","Jakarta Timur")
df['location'] = df['location'].str.replace("Kota Jakarta Selatan","Jakarta Selatan")
df['location'] = df['location'].str.replace("Jakarta Selatan City","Jakarta Selatan")
df['location'] = df['location'].str.replace("Kota Jakarta Pusat","Jakarta Pusat")
df['location'] = df['location'].str.replace("Depok City","Depok")
df['location'] = df['location'].str.replace("Sukabumi City","Sukabumi")
df['location'] = df['location'].str.replace("West Lombok","Lombok Barat")

# cleaning post_on
df['post_on'] = df['post_on'].str.split('•').str[0]
df.post_on = df.post_on.str.replace("Posted","")

# cleaning_deadline
df.deadline = df.deadline.str[32:]

def clean_data(x):
    if isinstance(x, str):
        x = x.replace('e ', '')
        x = x.replace('re ', '')
        x = x.replace('r', '')
        x = x.replace('for ', '')
        x = x.replace('fo', '')
        x = x.replace('Ap', 'Apr')
        x = x.replace('Ma', 'May')
        x = x.replace('Mayy', 'May')
    return x
df['deadline'] = df['deadline'].apply(clean_data)
# remove space in front
df.deadline = df.deadline.str.lstrip()

#end of data wranggling 

@app.route("/")
def index(): 

 
	cat_order = df.groupby('location').agg({
	'title' : 'count'
	}).sort_values('title', ascending=True).reset_index().tail(15)
	X = cat_order['location']
	Y = cat_order['title']
	my_colors = ['r','g','b','k','y','m','c']
	fig = plt.figure(figsize=(17,9))
	fig.add_subplot()
	plt.barh(X,Y, color=my_colors) 	

	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result2 = str(figdata_png)[2:-1]

	card_data = f'{cat_order["title"].mean().round(2)}' #be careful with the " and ' 


  	# generate plot
	plot_result = cat_order.plot(figsize = (17,9), x='location', y='title') 
 
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]
    
	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
		plot_result2=plot_result2
		)


if __name__ == "__main__": 
    app.run(debug=True)