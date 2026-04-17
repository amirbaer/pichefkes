'use strict';

var app = angular.module('itemsTable', []);

/*
app.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/view1', {
    templateUrl: 'view1/view1.html',
    controller: 'View1Ctrl'
  });
}])*/

app.directive('itemsTable', function() {
    return {
    
        restrict: 'E',
        templateUrl: 'items_table/items_table.html',
        controller: function() {

        }
    };

});

