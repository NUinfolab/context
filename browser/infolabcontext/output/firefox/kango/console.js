var utils=require("kango/utils"),NotImplementedException=utils.NotImplementedException;function IConsole(){}IConsole.prototype={log:function(a,b){throw new NotImplementedException;},warn:function(a,b){throw new NotImplementedException;},error:function(a,b){throw new NotImplementedException;}};function getPublicApi(){return utils.createApiWrapper(module.exports,IConsole.prototype)};








var utils=require("kango/utils"),string=utils.string;function Console(){}
Console.prototype={_logMessage:function(a,c){var b=1<a.length?string.format.apply(string,a):a[0],d=Cc["@mozilla.org/scripterror;1"].createInstance(Ci.nsIScriptError);d.init(b,null,null,null,null,c,null);Services.console.logMessage(d)},log:function(a){1<arguments.length&&(a=string.format.apply(string,arguments));Services.console.logStringMessage(a)},warn:function(a){this._logMessage(arguments,1)},error:function(a){this._logMessage(arguments,0)},reportError:function(a,c){var b=Cc["@mozilla.org/scripterror;1"].createInstance(Ci.nsIScriptError);
b.init(a.message,c||a.fileName,null,a.lineNumber,a.columnNumber,0,null);Services.console.logMessage(b)}};module.exports=new Console;module.exports.getPublicApi=getPublicApi;
