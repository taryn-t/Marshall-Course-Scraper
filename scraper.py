from selenium import webdriver 
from selenium.webdriver.common.by import By
import json


def ScrapeByLink():
    #empty dictionary we will use to write to json file
    json_object = {
        "data":[]
    }

    #empty list for appending subject data to
    data =[]

    # create webdriver object 
    driver = webdriver.Firefox() 

    #get the course page from the schedule of courses
    driver.get("https://mubert.marshall.edu/scheduleofcourses.php?term=202502") 

    #grabs all elements with the class 'subjects'
    parentElements = driver.find_elements(By.CLASS_NAME, "subjects")

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
        
        current_url = driver.current_url
        dept_urls.append(current_url)
        
        driver.back()
        
        #refresh the original list
        parentElements = driver.find_elements(By.CLASS_NAME, "subjects")
        parentElement = parentElements[1]
        linkElements = parentElement.find_elements(By.TAG_NAME, "a")
    

    #find each department/subject
    for url in dept_urls:
    
        
        department = {
            "name": "",
            "courses": []
        }
        driver.get(url)
        
        name_header = driver.find_element(By.TAG_NAME, "h3").text
        
        department["name"] = name_header[:4]
        
        courses=[]
        

        
        
        course_headers = driver.find_elements(By.TAG_NAME, "h4")
        
        
        #find each course in dept/subject
        for header in course_headers:
            
            sections = []
            course = {
                "name": "",
                "sections":[]
            }
            
            course["name"] = header.text.replace("-","")
            
            main_parent = header.find_element(By.XPATH, '..')
            
            course_table = driver.execute_script(
            "return arguments[0].nextElementSibling;", main_parent)

            table_body = course_table.find_element(By.XPATH, "./tbody")
            
            table_rows = table_body.find_elements(By.XPATH, "./tr")
            
            #find each section in specific course
            for row in table_rows:
                table_data = row.find_elements(By.XPATH, "./td")
                if len(table_data) == 8:
                    section = table_data[1].text
                    sections.append(section)
            
                    course["sections"] = sections
                    
            #add course to total courses        
            courses.append(course)
        
        #set course data for the department
        department["courses"] = courses
        
        #add department to the data list
        data.append(department)

    #when loop is complete it 
    json_object["data"] = data
        

    with open("results.json", "w") as outfile: 
        json.dump(json_object, outfile)
        
ScrapeByLink()
        
        
        
        


