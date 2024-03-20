# Graduaatsproef

## Table of Contents

- [Graduaatsproef](#graduaatsproef)
  - [Table of Contents](#table-of-contents)
  - [Taken](#taken)
  - [Research](#research)
    - [Welke opties zijn er?](#welke-opties-zijn-er)
      - [Azure](#azure)
      - [Prometheus/grafana:](#prometheusgrafana)
      - [ReportPortal:](#reportportal)
  - [Bronnen](#bronnen)

##  Taken
 - [ ] 3 - 4 Opties verzamelen
 - [ ] POC maken per tool
 - [ ] Screenshots invoegen
 - [ ] Pros & cons beschrijven

## Research

### Welke opties zijn er?

#### Azure
Vendor lockin en weinig tot geen customization. 

#### Prometheus/grafana:
Dient eerder voor logs en constante data op te slaan, de resultaten moeten als XML worden opgeslagen en worden uitgelezen. 
De werking is vrij simpel, het meeste werkt out of the box, er moet enkel een script worden geschreven. 
Dit script gaat na het beeindigen van een testrun de resultaten uploaden naar een cloud opslag. 
Deze opslag wordt dan gebruikt door prometheus om de resultaten in een database te steken die gelezen en doorzocht kan worden door een dashboard.


#### ReportPortal:
Complex en groot, maar doet wel wat we we er van vragen.
Dit is een docker-compose stack die speciaal gemaakt is voor het visualiseren van test resultaten. 
De hele stack bestaat uit een dashboard, een database, authenticatie, rabbitmq en verschillende services voor health en metrics te bekijken.

https://reportportal.io/docs/log-data-in-reportportal/ImportDataToReportPortal#import-via-api


## Bronnen

[Grafana docs](#https://grafana.com/docs/grafana/latest/)

[ReportPortal docs](#https://reportportal.io/docs/)


[Automated Test Results: how to track and visualize them](#https://www.solvd.com/blog/automated-test-results-visualization)