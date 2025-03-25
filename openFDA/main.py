from flask import Flask, render_template, request
import requests
import json
#from daily_med import DailyMed
#dm = DailyMed()

app = Flask(__name__)

#default route, displays about page
@app.route('/')
def index():
    return render_template('about.html')

#display about page
@app.route('/about')
def about():
    return render_template('about.html')

#displayes index page
@app.route('/home', methods=['GET', 'POST'])
def home():
    #on form submission
    if request.method == 'POST':
        # Process form data
        #store the user input "condition" value to a variable
        data = request.form['condition']
        #store the user input "conduct search on" value to a variable
        resultCount = request.form['results']
        #call process_data function with necessary arguments
        results = process_data(data,resultCount)
        #return the function output to front end and render the appropriate html with the results
        return render_template('index.html', results=results, headers=results[0].keys() if results else [])
    #display index.html page on app start
    return render_template('index.html')


def process_data(data,results = 100):
    # store parameters in a variable
    search_criteria = data
    result_limit = results
    url = "https://api.fda.gov/drug/label.json?"
    params = {"search": search_criteria, "limit": result_limit}
    #process to get information from website (openFDA)
    response = requests.get(url,params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        #Fetch results from json data
        filtered_list = [data["results"]][0]
        #Fetch Purpose from results and store it in data_list_purpose
        data_list_purpose = [{key: item[key] for key in ["purpose"] if key in item} for item in filtered_list]
        #Fecth openfda from results and store it in data_list
        data_list = [{key: item[key] for key in ["openfda"] if key in item} for item in filtered_list]
        i = 0
        results = []
        #while through the end of data_list
        while i < len(data_list):
            new_data_list = data_list[i]
            #data cleaning: remove results that don't have openfd and purpose value and include only those purposes that match user search criteria
            if len(new_data_list.get("openfda")) != 0 and data_list_purpose[i].get("purpose") != None and (search_criteria in data_list_purpose[i].get("purpose")[0].lower()):
                filtered_list = new_data_list['openfda']
                # build the url to send request to DailyMed as and when required
                search = filtered_list["brand_name"][0].replace(" ","+")
                url_to_look_for =  "https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query="+search
                #send the results to front end
                results.append({'Brand Name':filtered_list["brand_name"][0], 'Purpose': data_list_purpose[i]['purpose'][0], 'Daily Med URL':url_to_look_for})
            i += 1
    else:
        print(f"Error: {response.status_code}")
       
    return results

if __name__ == '__main__':
    app.run(debug=True)