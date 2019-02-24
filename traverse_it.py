import re
import bs4 as bs
import urllib.request
import urllib.parse
import sqlite3 as sql
import pandas as pd

pd = pd.DataFrame()
##data formating for sql
def format_data(s):
    s.replace("\"","")
    return s

##sqlite3 code here
def create_db(db_name):
    con = sql.connect(db_name)
    cur = con.cursor()
    return con, cur


def create_table(con, cur):
    try:
        cur.execute("""create table if not exists Quotes(Quote text, Author text, tags text)""")
    except Exception as e:
        print('\t'+str(e))
        pass
    con.commit()

def dynamic_insertion(quote, author, tags, con, cur):
    try:
        cur.execute("""insert into Quotes (Quote, Author, tags) values(?, ?, ?)""", (quote, author, tags))
    except Exception as e:
        print('\t'+str(e))
        pass

def read_table():
    c.execute('select * from table_name')
    for row in c.fetchall():
        print(row)

def dump_to_DB(quotes):
    con, cur = create_db('Quotes.db')
    create_table(con, cur)
    print(quotes)
    for q in quotes:
        for i in range(len(q)):
            q[i] = format_data(q[i])
        dynamic_insertion(q[0], q[1], ', '.join(q[2:]), con , cur)
    return con


#The webscrapping code
#extract the .zip links from indian_movies_page_links
def extract_links(root_link):
    url = root_link
    headers= {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    req = urllib.request.Request(url,headers = headers)
    sauce = urllib.request.urlopen(req).read()
    soup = bs.BeautifulSoup(sauce,'lxml')
    inner_links = soup.find_all('a')#urls with html tags
    root_page_links = []
    for each_inner_link in inner_links:
        each_inner_link = str(re.findall(r'\".*\"',str(each_inner_link)))
        root_page_links.append( each_inner_link[3:len(each_inner_link)-3] )#only url
    del inner_links
    return root_page_links #all urls only




def extract_a_tag_text(root_link):
    url = root_link
    headers= {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    req = urllib.request.Request(url,headers = headers)
    sauce = urllib.request.urlopen(req).read()
    soup = bs.BeautifulSoup(sauce,'lxml')
    a_tags = soup.find_all('a')#the a tags
    a_tags_text = []
    for a_tag in a_tags:
        a_tags_text.append(a_tag.text)
    return a_tags_text

def extract_a_tags(root_link):
    url = root_link
    headers= {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    req = urllib.request.Request(url,headers = headers)
    sauce = urllib.request.urlopen(req).read()
    soup = bs.BeautifulSoup(sauce,'lxml')
    a_tags = soup.find_all('a')
    return a_tags
                           
def check_for_zip_links(each_link, zip_links):
    each_page_links = extract_links(each_link)
    each_page_zip_links = []
    for each_inner_link in each_page_links:    
        if each_inner_link.endswith(".zip"):#found a zip link
            each_page_zip_links.append(each_inner_link)
    for each_inner_link in each_page_zip_links:
        zip_links.append(each_inner_link)
    print('appended ', len(each_page_zip_links))

def get_the_level1_urls_alphabets():#working fine
    url = 'https://www.brainyquote.com/'
    save_file = open('alphabets_url.txt', 'w+')
    a_tags = extract_a_tags(url)
    for a_tag in a_tags:
        if len(a_tag.text) == 1:
            if(ord(a_tag.text) >= 65 and ord(a_tag.text) <= 90 ):
                s = str(re.findall(r'\".*\"',str(a_tag)))
                s = s[4:len(s)-3]
                print(url+s)
                save_file.write(url+s+'\n') 
    save_file.close()

def generate_lv2_urls(url, last_page, alphabet):
    urls = []
    for i in range(1,int(last_page)+1):
        urls.append(url[:-2]+alphabet+str(i)+'\n')
    return urls

def get_the_level2_urls_pages_of_alphabets():#alphabets extended
    read_file = open('alphabets_url.txt', 'r+')
    save_file = open('pages_url.txt', 'w+')
    level2_urls_list = []
    for  i in range(26):
        url = read_file.readline()
        print(url)
        headers= {}
        headers['User-Agent']= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        req = urllib.request.Request(url,headers = headers)
        sauce = urllib.request.urlopen(req).read()
        soup = bs.BeautifulSoup(sauce,'lxml')
        
        uls = soup.find_all('ul', class_ = 'pagination bqNPgn pagination-sm')
    
        if uls:
            lis = uls[0].find_all('li')
            last_page = lis[-2].find_all('a')[0].text
            print(last_page)
            alphabet = chr(i+97)
            level2_urls_list.append(generate_lv2_urls(url,last_page, alphabet))
        else:
            level2_urls_list.append(url+'\n')
    print(level2_urls_list)
    
    for urls in level2_urls_list:
            save_file.writelines(urls)
            
    read_file.close()
    save_file.close()

def get_level3_urls():#Author names
    read_file = open('pages_url.txt', 'r+')
    save_file = open('authors_url.txt', 'w+')
    url = read_file.readline()[:-1]
    authors_list = []
    while(url!=''):
        headers= {}
        headers['User-Agent']= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        req = urllib.request.Request(url,headers = headers)
        sauce = urllib.request.urlopen(req).read()
        soup = bs.BeautifulSoup(sauce,'lxml')
        divs = soup.find_all('div', class_ = 'bq_s')
        
        all_authors_links = divs[1].find_all('a')
        
        for each_author_link in all_authors_links:
            each_author_link = str(re.findall(r'\".*\"',str(each_author_link)))
            authors_list.append( url+each_author_link[3:len(each_author_link)-3] +'\n' )#only url
            print( url+each_author_link[3:len(each_author_link)-3])
        url = read_file.readline()[:-1]

    save_file.writelines(authors_list)

    read_file.close()
    save_file.close()

def store_everything():
    read_file = open('authors_url.txt', 'r+')
    authors_urls = read_file.read().split('\n')
    read_file.close()
    current_file = open('current.txt', 'r')
    url = current_file.read()
    current_file.close()
    current_file = open('current.txt', 'w')
    index = authors_urls.index(url)
    current_index = index
    try:
        for i in range(index, len(authors_urls)):
            current_index = i
            print('working on '+authors_urls[i])
            quotes = get_quotes(authors_urls[i])
            try:
                con = dump_to_DB(quotes)
                con.commit()
            except Exception as e:
                print('\t'+str(e))
                pass
    finally:
        current_file.write(authors_urls[current_index])
        current_file.close()
    

        
def get_info(each_quote):
    a_tags = each_quote.find_all('a')
    quote = list()
    for each_a_tag in a_tags:
        quote.append(each_a_tag.text)
    return quote

def get_quotes(url):
    headers= {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    req = urllib.request.Request(url,headers = headers)
    sauce = urllib.request.urlopen(req).read()
    soup = bs.BeautifulSoup(sauce,'lxml')
    divs = soup.find_all('div', id = 'quotesList')#we are into quotesList
    quotes_list = []
    quotes = divs[0].find_all('div', class_ = 'm-brick grid-item boxy bqQt')#we are into each box in the quotesList
    for each_quote in quotes:
        each_quote = get_info(each_quote)
        quotes_list.append(each_quote)
        
    return quotes_list

#get_the_level1_urls_alphabets()
#get_the_level2_urls_pages_of_alphabets()
#get_level3_urls()

store_everything()
























