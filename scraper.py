from selenium import webdriver 
from selenium.webdriver.common.by import By
import json

json_object = {
    "data":[]
}

data =[]
# create webdriver object 
driver = webdriver.Firefox() 

# get google.co.in 
driver.get("https://mubert.marshall.edu/scheduleofcourses.php?term=202502") 

parentElements = driver.find_elements(By.CLASS_NAME, "subjects")

parentElement = parentElements[1]
linkElements = parentElement.find_elements(By.TAG_NAME, "a")

dept_urls =[]

    
# dept_urls= [elem.get_attribute('href')  for elem in linkElements]
link_list_length = len(linkElements)

for i in range(link_list_length):
    linkElements[i].click()
    
    current_url = driver.current_url
    dept_urls.append(current_url)
    
    driver.back()
    
    parentElements = driver.find_elements(By.CLASS_NAME, "subjects")
    parentElement = parentElements[1]
    linkElements = parentElement.find_elements(By.TAG_NAME, "a")
  


print(dept_urls)

#each department
for url in dept_urls:
    print(url)
    department = {
        "name": "",
        "courses": []
    }
    name_header = driver.find_element(By.TAG_NAME, "h3").text
    
    department["name"] = name_header[:3]
    
    courses=[]
    

    driver.get(url)
    
    course_headers = driver.find_elements(By.TAG_NAME, "h4")
    
    #each course
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
        # course_table = main_parent.find_element(By.XPATH, "following-sibling::*[1]")
        table_body = course_table.find_element(By.XPATH, "./tbody")
        
        table_rows = table_body.find_elements(By.XPATH, "./tr")
        
        
        for row in table_rows:
            table_data = row.find_elements(By.XPATH, "./td")
            if len(table_data) == 8:
                section = table_data[1].text
                sections.append(section)
        
                course["sections"] = sections
                
        courses.append(course)
    
    department["courses"] = courses
    data.append(department)

json_object["data"] = data
    

with open("results.json", "w") as outfile: 
    json.dump(json_object, outfile)
        
        
        
        


