"use strict";
_kangoLoader.add("kango/io", function(require, exports, module) {
var utils=require("kango/utils"),NotImplementedException=utils.NotImplementedException,IOBase=function(){};
IOBase.prototype={getExtensionFileUrl:function(a){throw new NotImplementedException;},isLocalUrl:function(a){return-1==a.indexOf("http://")&&-1==a.indexOf("https://")&&-1==a.indexOf("ftp://")},getFileUrl:function(a){this.isLocalUrl(a)&&(a=this.getExtensionFileUrl(a));return a},getExtensionFileContents:function(a){var b=new XMLHttpRequest;b.open("GET",this.getExtensionFileUrl(a),!1);"undefined"!=typeof b.overrideMimeType&&b.overrideMimeType("text/plain");try{return b.send(null),b.responseText}catch(c){return null}},
getResourceUrl:function(a){throw new NotImplementedException;}};function getPublicApi(){return utils.createApiWrapper(module.exports,IOBase.prototype)};








var utils=require("kango/utils"),object=utils.object;function IO(){}IO.prototype=object.extend(IOBase,{getExtensionFileUrl:function(a){return safari.extension.baseURI+a},getResourceUrl:function(a){return this.getExtensionFileUrl(a)}});module.exports=new IO;module.exports.getPublicApi=getPublicApi;

});