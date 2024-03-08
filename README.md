# parkrun-results <img src="https://user-images.githubusercontent.com/94953297/218050503-c6260c37-f97f-4a70-bfa2-02c70df28b3c.jpg" width="80" height="80">

## 📖 Contents
* [ℹ️ About](https://github.com/jansen88/parkrun-results/tree/master#about)
* [📷 Examples](https://github.com/jansen88/parkrun-results/tree/master#examples)
* [🏃 Developer's notes](https://github.com/jansen88/parkrun-results/tree/master#developers-notes)
* [🔧 Setup](https://github.com/jansen88/parkrun-results/tree/master#setup)

## ℹ️ About
[Parkrun](https://www.parkrun.com.au/), a worldwide community running event held every Saturday morning, invites participants to run together to cover a 5km courses in community park venues. Embracing individuals of all ages and fitness levels, from competitive runners and families to youths and retirees, Parkrun encourages participants to walk, jog, run, or race at their own pace. Originating in the UK, this global phenomenon hosts hundreds of weekly parkruns across Europe, USA, Africa, Australia, and Asia.

This Dash web application enables users to visualize and deep-dive into parkrun results for specific parkrunners. The interface allows parkrunners to monitor and visualize their performance trends over time, while exploring details about their top parkrun locations and attendance.

## 📷 Examples
See sample screenshots below:

![image](https://github.com/jansen88/parkrunFun/assets/94953297/55732323-c2da-4041-914b-3c4cf5ec71ba)
![image](https://github.com/jansen88/parkrunFun/assets/94953297/ce973aae-0358-4c1c-aa24-896ece39238c)
![image](https://github.com/jansen88/parkrunFun/assets/94953297/aac129ad-3e50-42b6-9c50-4257d2fffe10)

## 🏃 Developer's notes
##### Web-scraping
Unfortunately as parkrun does not provide a public [API](https://www.parkrun.com/api/), it is not possible to retrieve data through an API. Required data for this Dash app is fetched by web-scraping an individual page. Intended usage results in similar traffic to human consumption of the parkrun website.

#### Hosting
Please note that the app is not currently deployed to any hosting sites, as many platforms hosting Python applications now require some form of subscription or payment for hosting services. 

I have tested hosting this on PythonAnywhere - while I was able to deploy the app, I ran into significant issues in being able to web-scrape content from PythonAnywhere.

##### Further development
There is opportunity for additional content to be developed and added to this work - e.g. individual event information and visualisations, cross-event or cross-location information. This may be of future interest but is currently backlogged, and not in active development.

## 🔧 Setup
Install requirements - requirements.txt should be more up to date:

```
pip install -r requirements.txt
```

Poetry is out of date - do not use:
```
poetry install
```

To run app locally:
Application entry point is through `app.py`




