"use strict";
_kangoLoader.add("kango/timer", function(require, exports, module) {
var utils=require("kango/utils"),NotImplementedException=utils.NotImplementedException;function ITimer(){}ITimer.prototype={setInterval:function(a,b){return new NotImplementedException},clearInterval:function(a){return new NotImplementedException},setTimeout:function(a,b){return new NotImplementedException},clearTimeout:function(a){return new NotImplementedException}};function getPublicApi(){return utils.createApiWrapper(module.exports,ITimer.prototype)};








function Timer(){}Timer.prototype={setInterval:function(a,b){return window.setInterval(a,b)},clearInterval:function(a){return window.clearInterval(a)},setTimeout:function(a,b){return window.setTimeout(a,b)},clearTimeout:function(a){return window.clearTimeout(a)}};module.exports=new Timer;module.exports.getPublicApi=getPublicApi;

});