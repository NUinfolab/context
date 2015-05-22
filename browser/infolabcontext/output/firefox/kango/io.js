var utils=require("kango/utils"),NotImplementedException=utils.NotImplementedException,IOBase=function(){};
IOBase.prototype={getExtensionFileUrl:function(a){throw new NotImplementedException;},isLocalUrl:function(a){return-1==a.indexOf("http://")&&-1==a.indexOf("https://")&&-1==a.indexOf("ftp://")},getFileUrl:function(a){this.isLocalUrl(a)&&(a=this.getExtensionFileUrl(a));return a},getExtensionFileContents:function(a){var b=new XMLHttpRequest;b.open("GET",this.getExtensionFileUrl(a),!1);"undefined"!=typeof b.overrideMimeType&&b.overrideMimeType("text/plain");try{return b.send(null),b.responseText}catch(c){return null}},
getResourceUrl:function(a){throw new NotImplementedException;}};function getPublicApi(){return utils.createApiWrapper(module.exports,IOBase.prototype)};








var extensionInfo=require("kango/extension_info"),utils=require("kango/utils"),object=utils.object;function IO(){this._rootName=extensionInfo.package_id;this._init()}
IO.prototype=object.extend(IOBase,{_registerResourceProtocol:function(){var a=Services.io.getProtocolHandler("resource").QueryInterface(Ci.nsIResProtocolHandler),b=Services.io.newFileURI(__installPath);__installPath.isDirectory()||(b=Services.io.newURI("jar:"+b.spec+"!/",null,null));a.setSubstitution(this._rootName,b)},_unregisterResourceProtocol:function(){Services.io.getProtocolHandler("resource").QueryInterface(Ci.nsIResProtocolHandler).setSubstitution(this._rootName,null)},_init:function(){this._registerResourceProtocol()},
dispose:function(){this._unregisterResourceProtocol()},getExtensionFileUrl:function(a){return"chrome://"+this._rootName+"/content/"+a},getResourceUrl:function(a){return"resource://"+this._rootName+"/"+a}});module.exports=new IO;module.exports.getPublicApi=getPublicApi;
