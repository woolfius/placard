app
  .controller('employeesController', ['employeesService', '$scope', 'employeesList','RootFactory', function (employeesService, $scope, employeesList,RootFactory) {

      $scope.peopleList = employeesList;
//       $scope.spinner=true
// ctrl.spinner=false;

      // RootFactory.getUser()
      // RootFactory.


  }])
;