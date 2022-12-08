# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| ------------ | ------------ | ------------ |
| Azure Postgres Database | Basic tier with 1 vCPU Core and 5GB of storage |   2616.67 INR|
| Azure Service Bus | Basic tier with Max message size of 256KB with shared capacity  | 4.11 INR |
| Azure App Service Plan | B1 with 100 total ACU and 1.75GB of memory (free for first 1 month)| 946.67 INR |  
| Azure Cache For Redis | C0 Basic Tier with 250MB Cache | 1,179.24 INR |
| Azure Function App |  Consumption (Serverless ) |  0.001307 INR for each execution |

## Architecture Explanation
This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.

- The Tech Conference Web App is deployed to Azure Web App rather than to an Azure Virtual Machine using lift and shift method because currently the app requirements fit well with in the App Service Limits.
- The App needs less than 4 vCPU Cores and less than 14 GB of memory and if the load increases in the future then there is always an option to horizontally scale the app by increasing or decreasing the number of web app instances or vertically scale the app by increasing or decreasing the web app resources such as compute,memory and storage.
- It is also very easy to deploy the web app to Azure App Service and also Python is one of the few supported programming languages.
- Azure function is cost effective in this architecture because it only runs the logic when a message is enqueued into the queue and you only have to pay for each function execution.
- It makes perfect sense to decouple the logic for notifying the attendees from the web app to azure function with a service bus queue trigger.
- Decoupling the logic for notifying the attendees from the web app leads to app being more responsive, improves the user experience and also reduction in HTTP timeout exceptions.
- Azure functions are also scalable to meet the incoming traffic.
