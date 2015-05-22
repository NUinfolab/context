"use strict";
_kangoLoader.add("kango-ui/notifications", function(require, exports, module) {
var utils=require("kango/utils"),object=utils.object,EventTarget=utils.EventTarget,NotImplementedException=utils.NotImplementedException;function INotifications(){}INotifications.prototype={show:function(a,b,c,d){throw new NotImplementedException;}};function getPublicApi(){return utils.createApiWrapper(module.exports,INotifications.prototype)};








function Notifications(){}Notifications.prototype={show:function(a,b,c,d){window.Notification&&(a=new Notification(a,{body:b,icon:c}),a.onclick=d,a.show())}};module.exports=new Notifications;module.exports.getPublicApi=getPublicApi;

});