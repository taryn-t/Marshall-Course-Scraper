from selenium import webdriver 
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import json
import pandas as pd 
import re

class web_scraper:
    
    def __init__(self):
        
        self.driver = webdriver.Firefox() 

        
        self.json_object = {
            "data":[]
        }
        
        self.subjects_df = pd.DataFrame()
        self.courses_df = pd.DataFrame()
        self.sections_df = pd.DataFrame()
        
        self.create_subjects_df()
        self.create_courses_df()
        self.create_sections_df()
        
    
   
    def create_dfs_from_object(self):
        data = self.json_object["data"]
        
        for subject in data:
            subject_id = subject["name"]
            subject_obj = {"id": subject_id, "name": subject_id }
            subject_df = pd.DataFrame(subject_obj,index=[0])
            
            self.subjects_df = pd.concat([self.subjects_df, subject_df])
            
            for course in subject["courses"]:
                sub_arr = re.split("\s", course["name"], 2)
                course_id = sub_arr[0]+sub_arr[1]
                course_obj = {"id": course_id, "name":sub_arr[2], "subject_id": subject_id }
                course_df = pd.DataFrame(course_obj,index=[0])
                self.courses_df = pd.concat([self.courses_df, course_df])
                
                for section in course["sections"]:
                    
                    section_obj = {"id": section["id"], 'textbook_link': section["textbook_link"], "course_id": course_id }
                    section_df = pd.DataFrame(section_obj,index=[0])
                    self.sections_df = pd.concat([self.sections_df, section_df])
            
    
    def create_subjects_df(self):
        col_names =  ['id', 'name'] 
        self.subjects_df  = pd.DataFrame(columns = col_names,index=[0]) 
        
            
    def create_courses_df(self):
        col_names =  ['id', 'name','subject_id'] 
        self.courses_df  = pd.DataFrame(columns = col_names,index=[0]) 
       
    
    def create_sections_df(self):
        col_names =  ['id', 'textbook_link', "course_id"] 
        self.sections_df  = pd.DataFrame(columns = col_names,index=[0]) 
       
        
                
    def scrape_by_link(self):

        #empty list for appending subject data to
        data =[]
        

        #get the course page from the schedule of courses
        self.driver.get("https://mubert.marshall.edu/scheduleofcourses.php?term=202502") 

        #grabs all elements with the class 'subjects'
        parentElements = self.driver.find_elements(By.CLASS_NAME, "subjects")

        #gets the second element in the subjects list which contains all the links to undergraduate courses
        parentElement = parentElements[1]

        #gets all the link elements in the section
        linkElements = parentElement.find_elements(By.TAG_NAME, "a")

        #empty list for adding the true urls
        dept_urls = []

        #get length of links    
        link_list_length = len(linkElements)

        #collects the true url with search params
        for i in range(link_list_length):
            linkElements[i].click()
            
            current_url = self.driver.current_url
            dept_urls.append(current_url)
            
            self.driver.back()
            
            #refresh the original list
            parentElements = self.driver.find_elements(By.CLASS_NAME, "subjects")
            parentElement = parentElements[1]
            linkElements = parentElement.find_elements(By.TAG_NAME, "a")
        

        #find each department/subject
        for url in dept_urls:
        
            
            department = {
                "name": "",
                "courses": []
            }
            self.driver.get(url)
            
            name_header = self.driver.find_element(By.TAG_NAME, "h3").text
            
            sub_str = name_header[:4]
            
            sub_arr = re.split("\s", sub_str, 1)
            
            subject_name = sub_arr[0]
            
            department["name"] = subject_name
            
            print("Scraping subject " + subject_name )
            
            courses=[]

            course_headers = self.driver.find_elements(By.TAG_NAME, "h4")
            
            
            #find each course in dept/subject
            for header in course_headers:                
                course = {
                    "name": "",
                    "sections":[],
                    
                }
                sections = []
                
                course["name"] = header.text.replace("-","")
                
                main_parent = header.find_element(By.XPATH, '..')
                
                course_table = self.driver.execute_script(
                "return arguments[0].nextElementSibling;", main_parent)

                table_body = course_table.find_element(By.XPATH, "./tbody")
                
                table_rows = table_body.find_elements(By.XPATH, "./tr")
                
                #find each section in specific course
                for row in table_rows:
                    table_data = row.find_elements(By.XPATH, "./td")
                    if len(table_data) == 8:
                        
                        section = {
                            "id": "",
                            "textbook_link": ""
                        }
                        
                        section["id"] = table_data[1].text
                        try:
                            textbook_td = table_data[-1]
                            textbook_a = textbook_td.find_element(By.TAG_NAME, "a")
                            textbook_link = textbook_a.get_attribute("href")
                            section["textbook_link"] = textbook_link
                        except:
                            section["textbook_link"] = "N/A"
                        
                            
                        sections.append(section)
                
                course["sections"] = sections    
                        
                        
                #add course to total courses        
                courses.append(course)
            
            #set course data for the department
            department["courses"] = courses
            
            #add department to the data list
            data.append(department)

        #when loop is complete it 
        self.json_object["data"] = data
            

    def write_to_json(self):
        with open("results.json", "w") as outfile: 
            json.dump(self.json_object, outfile)  
            
            
    def create_csv_files(self):
        
        self.write_subjects_to_csv()
        self.write_courses_to_csv()
        self.write_sections_to_csv()
    
    def write_subjects_to_csv(self):
         self.subjects_df.to_csv('subjects.csv')
    
    def write_courses_to_csv(self):
         self.courses_df.to_csv('courses.csv')
         
    def write_sections_to_csv(self):
         self.sections_df.to_csv('sections.csv')
         
    def read_json_data(self):
        f = open('results.json') 
        self.json_object = json.load(f)
        f.close()
            
         
    
            
            


# scraper = web_scraper()  

# scraper.scrape_by_link()
# scraper.write_to_json()
# scraper.read_json_data()
# scraper.create_dfs_from_object()
# scraper.create_csv_files()