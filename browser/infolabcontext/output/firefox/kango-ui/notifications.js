var utils=require("kango/utils"),object=utils.object,EventTarget=utils.EventTarget,NotImplementedException=utils.NotImplementedException;function INotifications(){}INotifications.prototype={show:function(a,b,c,d){throw new NotImplementedException;}};function getPublicApi(){return utils.createApiWrapper(module.exports,INotifications.prototype)};








var console=require("kango/console");function Notifications(){this._alertService=Cc["@mozilla.org/alerts-service;1"].getService(Ci.nsIAlertsService)}Notifications.prototype={show:function(b,a,c,d){var e={observe:function(b,a,c){"alertclickcallback"===a&&d&&d()}};try{this._alertService.showAlertNotification(c||"",b,a,!0,0,e)}catch(f){console.reportError(f)}}};module.exports=new Notifications;module.exports.getPublicApi=getPublicApi;
