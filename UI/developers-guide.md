QA4SM Angular UI
================

## Development environment - build tools
Necessary software packages to run and build the UI
- Node.js -> at least v22 (might need to `nvm install 22` first)
- npm
- angular-cli
For the current angular version please check package.json, this will imply which node.js version is needed. 


### Node.js installation
https://nodejs.org/en/download/package-manager

If you already have node.js on your machine, you can verify version typing:

```
nvm ls
```

To switch between versions use:
```
nvm use vv.v.v
```

### npm
npm comes with Node.js, no extra step is needed.

### Angular CLI installation
Install angular cli
```
npm install -g @angular/cli
```
[General dev. env. setup guide from angular](https://angular.dev/tools/cli/setup-local)

## Building the project
The project root directory is `qa4sm/UI`
Enter the root directory and execute:
```
npm install
```
In this step npm will install all necessary dependencies for the project. These dependencies are 
defined in
`package.json` and `package-lock.json`.

## Starting the project
After installing the project dependencies the angular application can be started by 
executing `ng serve` from the `UI` directory.

Note that you can also execute `ng serve --configuration development` from the `UI` directory
to view more detailed error information in the browser console if you encounter JavaScript 
or Angular errors.

Since django runs in the root context, the UI application needs another one. (We don't want to 
mix django, django rest and angular urls). The angular application has the /ui/ context path, 
all relative urls defined in the application are relative to this path.

During the startup the server also compiles the project. Once it's done the application is reachable 
at http://localhost:4200/ui

### Development reverse proxy
The system (django+UI) uses http cookies for authentication, session management and CSRF 
protection.  
Browsers are very strict when it comes to cookies and cross origin resource sharing which would 
mean a lot of trouble if the django api and the UI would be available on different hosts. 
(like `http://localhost:8000/api` and `http://localhost:4200/ui`)  

Luckily the angular dev. server has built-in reverse proxy functionality that can be used to resolve
such issues in the development environment. `src/proxy.conf.json` contains the necessary 
configuration.  
Using this reverse proxy the django api will also be available at `http://localhost:4200/api` 
which will make the browsers happy. 

The reverse proxy starts automatically with `npm run start-with-path`, no extra command is needed.  
However, it expects the django api at `http://localhost:8000/api`. If you have the django application
running somewhere else (different ip or different port) you need to adjust `src/proxy.conf.json`

# Project structure
For those who are new to Angular I can highly recommend watching [this introductory course](https://www.youtube.com/watch?v=9RG3MiEBEIw&list=PLqq-6Pq4lTTb7JGBTogaJ8bm7f8VCvFkj)
or at least the [2nd video of the series](https://www.youtube.com/watch?v=u8QF9QIiGHI&list=PLqq-6Pq4lTTb7JGBTogaJ8bm7f8VCvFkj&index=2) in 
order to get a basic understanding of the framework and how it is different from
traditional web development.  
You can of course visit the official   [Angular website](https://angular.io/guide/architecture) too for details.


The project makes use of all angular building blocks (module, component, service)
These blocks are structured into the following tree:
```bash
-app
 |-modules
 | |-module-x
 | | |-component-x-1
 | | |-component-x-2
 | | |-service-x-1
 | | |-service-x-2
 | |-module-y
 | | |-component-y-1
 | | |-component-y-2
 | | |-service-y-1
 | | |-service-y-2
 |-pages
 | |-page-x
 | |-page-y
```

## Pages
Pages are angular components that implement the [main section](#page-layout) 
of each *page* that is reachable via a URL. Pages are the top level components that integrate other, 
smaller components in order to offer a specific, complex feature.

Example: Home page, Validate page, User profile page, etc

## Modules
A module is a high level building block that has one or more components.

Example module: a password change dialog, dataset and version selector panel, a specific dataset filter

## Components
Components build up modules. Number of components in a module depends on the complexity of the module.
Components responsible for **presenting and collecting data** to and from the user. 
Further processing this data or sending it to the backend is a job for the services.

## Services
Services implement the "business logic" of the UI.
Tasks that belong to the services are:
- handling http communication with the backend
- managing application state (e.g.: user login status)


## Page layout
The application has two sections at the moment:
- header: navigation bar on top of the page
- main section: the rest of the page under the header

