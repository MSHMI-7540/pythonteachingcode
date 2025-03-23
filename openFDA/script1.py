from flask import Flask, render_template, request
import requests
import json
from daily_med import DailyMed
dm = DailyMed()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process form data
        data = request.form['condition']
        resultCount = request.form['results']
        results = process_data(data,resultCount) # Function to process data
        return render_template('index.html', results=results, headers=results[0].keys() if results else [])
    return render_template('index.html')

def process_data(data,results = 100):
    # Example processing
    search_criteria = data
    result_limit = results
    url = "https://api.fda.gov/drug/label.json?"
    params = {"search": search_criteria, "limit": result_limit}

    response = requests.get(url,params=params)

    if response.status_code == 200:
        #data = response.json()
        data = json.loads(response.text)
        #print(data)
        #filtered_list = [{key: item[key] for key in ["results"] if key in item} for item in data]
        filtered_list = [data["results"]][0]
        data_list_purpose = [{key: item[key] for key in ["purpose"] if key in item} for item in filtered_list]
        #data_list_indication = [{key: item[key] for key in ["indications_and_usage"] if key in item} for item in filtered_list]
        data_list = [{key: item[key] for key in ["openfda"] if key in item} for item in filtered_list]
        i = 0
        results = []
        while i < len(data_list):
            new_data_list = data_list[i]
            #print(data_list_purpose[i].get("purpose"))
            if len(new_data_list.get("openfda")) != 0 and data_list_purpose[i].get("purpose") != None and (search_criteria in data_list_purpose[i].get("purpose")[0].lower()):
                filtered_list = new_data_list['openfda']
                #print(filtered_list["brand_name"]+data_list_purpose[i]['purpose'])   
                # url
                search = filtered_list["brand_name"][0].replace(" ","+")
                url_to_look_for =  "https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query="+search
                results.append({'Brand Name':filtered_list["brand_name"][0], 'Purpose': data_list_purpose[i]['purpose'][0], 'Daily Med URL':url_to_look_for})
            i += 1
    else:
        print(f"Error: {response.status_code}")
       
    return results

if __name__ == '__main__':
    app.run(debug=True)