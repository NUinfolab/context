"use strict";
_kangoLoader.add("kango/console", function(require, exports, module) {
var utils=require("kango/utils"),NotImplementedException=utils.NotImplementedException;function IConsole(){}IConsole.prototype={log:function(a,b){throw new NotImplementedException;},warn:function(a,b){throw new NotImplementedException;},error:function(a,b){throw new NotImplementedException;}};function getPublicApi(){return utils.createApiWrapper(module.exports,IConsole.prototype)};








var utils=require("kango/utils"),string=utils.string;function Console(){}Console.prototype={log:function(a){1<arguments.length&&(a=string.format.apply(string,arguments));console.log(a)},warn:function(a){1<arguments.length&&(a=string.format.apply(string,arguments));console.warn(a)},error:function(a){1<arguments.length&&(a=string.format.apply(string,arguments));console.error(a)},reportError:function(a,b){this.warn("Error in script "+(b||"(unknown)")+": "+a.message);this.warn(a.stack||"(No stack trace available)")}};
module.exports=new Console;module.exports.getPublicApi=getPublicApi;

});