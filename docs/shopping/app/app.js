'use strict';

// Declare app level module which depends on views, and components
var app = angular.module('shuppin', [
  'ngRoute',
  'itemsTable',
  'myApp.version',
  'toggle-switch',
]);

app.config(['$routeProvider', function($routeProvider) {
  //$routeProvider.otherwise({redirectTo: '/view2'});
}]);


app.controller('MainController', function($scope) {

        this.newItem = {};

        this.addNewItem = function(item) {
            this.newItem.status = true;
            this.items.push(this.newItem);
            this.newItem = {};
        }

        this.removeItem = function(item) {
            delete this.items[item];
        }

        this.items = [
            {
                "name"      : "tomatoes",
                "status"    :   true,
            },
            {
                "name"      : "cucumbers",
                "status"    :   false,
            },
        ];

});

