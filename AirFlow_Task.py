from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
#from airflow.contrib.operators.gcs_operator import GoogleCloudStorageHook, GCSToGCSOperator
#from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
import requests
from bs4 import BeautifulSoup
import gspread
import os

default_args = {
    'owner': 'jamshaid',
    'start_date': days_ago(0),
    'email': ['jamshaid.afzal@tmcltd.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    dag_id = 'my_Scraping_Dag',
    default_args = default_args,
    description = 'This is my first Dag',
    schedule_interval=timedelta(days=1),
)
# Define the function to scrape data from the website
def scrape_data():
    url = 'https://www.lushusa.com/bath/bath-bombs/?cgid=bath-bombs&start=0&sz=42'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    data = []
    lists = soup.find_all('div', class_ = 'product-tile-body')
    for list in lists:
        Category = list.find('div', class_='product-tile-category').text.strip()
        Product_title = list.find('h3', class_='product-tile-name').text.strip()
        Price = list.find('span', class_='tile-price').text.strip()
        Weight = list.find('span', class_='tile-size').text.strip().replace('/','')
        data.append([Category,Product_title,Price,Weight])
        
    return data
# Define the function to save data to Google Spreadsheet
def save_to_spreadsheet():
    print(os.getcwd())
    gc = gspread.service_account(filename='creds.json')
    sh = gc.open('BathBomber').sheet1
    data = scrape_data()
    for row in data:
        sh.append_row(row)
        
# Define the function to show the data from Google Spreadsheet
def show_data():
    gc = gspread.service_account(filename='creds.json')
    sh = gc.open('BathBomber').sheet1
    data = sh.get_all_values()
    for row in data:
        print(row)
        

# Define the tasks

scrape_data_task = PythonOperator(
    task_id='scrape_data',
    python_callable=scrape_data,
    dag=dag
)
    
save_to_spreadsheet_task = PythonOperator(
    task_id='save_to_spreadsheet',
    python_callable=save_to_spreadsheet,
    dag=dag
)

show_data_task = PythonOperator(
    task_id='show_data',
    python_callable=show_data,
    dag=dag
)


scrape_data_task >> save_to_spreadsheet_task >> show_data_task