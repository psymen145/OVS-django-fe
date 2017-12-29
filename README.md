# Front end for OVS Data Use unit

An responsive intranet site for OVS Data Use unit. This is used to manage projects/data requests for the data use officer. This is currently in development and awaiting news for production environment.

Currently implemented with a legacy SQL Server 

## Dependencies

## Preview

The front end is broken up into different sections. The dashboard is the homepage, where the data use officer can drag and drop different projects into different phases. This was implemented with jQuery UI. The calender is a work in progress but it will allow the user to filter the projects displayed in the dashboard. Note: this dashboard is different for each user group. Only those that are logged in will see the dashboard.

![Dashboard Screenshot](https://github.com/psymen145/OVS-django-fe/blob/master/dashboard.JPG)

The projects tab will show all projects that ever existed. 

![Project Screenshot](https://github.com/psymen145/OVS-django-fe/blob/master/project.JPG)

There are several filtering options and sorting options. The sorting options are located next to each column. The filter options are in the middle. You change what you want to filter by. The dropdown menu will change based on what you want to filter by.

![Project Screenshot](https://github.com/psymen145/OVS-django-fe/blob/master/filterchange.JPG)

Each row in the project table can be clicked anywhere on the row. This will bring you to a view that displays information specific to that project.

![Individual Project Screenshot](https://github.com/psymen145/OVS-django-fe/blob/master/individualproj.JPG)

If the user is logged on and has the correct privileges, he/she can edit the individual project information in this screen. Notice the pencil icons next to boxes. This will change the html to inputs that allows changes to the form. Ajax calls will be made and subsequently make changes in the backend.

Also, there are tabs that show other information for that individual project

The User tab is similar to the project tab, a table showing all users, which links to specific pages for each user.

## License

The source code is released under the [MIT License](https://github.com/psymen145/OVS-django-fe/blob/master/LICENSE).
