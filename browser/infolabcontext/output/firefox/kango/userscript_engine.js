var extensionInfo=require("kango/extension_info"),io=require("kango/io");function UserscriptEngine(){this._scripts=[];this.init()}
UserscriptEngine.prototype={init:function(){var a=extensionInfo.content_scripts;if(a)for(var b=0;b<a.length;b++){var d=io.getExtensionFileContents(a[b]);d&&this.addScript(a[b],d,io.getExtensionFileUrl(a[b]))}},addScript:function(a,b,d){for(var c=0;c<this._scripts.length;c++)if(this._scripts[c].id==a)return!1;b=new Userscript(b,d||null);this._loadRequiredFiles(b);this._scripts.push({id:a,script:b});return!0},removeScript:function(a){for(var b=0;b<this._scripts.length;b++)if(this._scripts[b].id==a)return this._scripts.splice(b,
1),!0;return!1},clear:function(){this._scripts=[]},getScripts:function(a,b,d){for(var c={},e=0;e<this._scripts.length;e++){var f=this._scripts[e].script,g=f.headers.namespace||"default",h=f.headers["run-at"]||"document-end",k=f.headers["all-frames"]||!1;(d||k)&&h==b&&this._isIncludedUrl(f,a)&&!this._isExcludedUrl(f,a)&&(c[g]=c[g]||[],c[g].push({text:f.text,path:f.path,requires:f.requires}))}return c},_loadRequiredFiles:function(a){if("undefined"!=typeof a.headers.require)for(var b=a.headers.require,
d=0;d<b.length;d++){var c=b[d],e=io.getExtensionFileContents(c);null!=e&&""!=e&&a.requires.push({text:e,path:io.getExtensionFileUrl(c)})}},_checkPatternArray:function(a,b){if("undefined"!=typeof a){a instanceof Array||(a=Array(a));for(var d=0;d<a.length;d++){var c=a[d].replace(/\*/g,"(.*)");if(RegExp(c).test(b))return!0}}return!1},_isIncludedUrl:function(a,b){return null==a.headers.include?!0:this._checkPatternArray(a.headers.include,b)},_isExcludedUrl:function(a,b){return null==a.headers.exclude?
!1:this._checkPatternArray(a.headers.exclude,b)}};function Userscript(a,b){this.text=a;this.path=b;this.headers={};this.requires=[];this._parseHeaders()}
Userscript.prototype={_parseHeaders:function(){this.headers=this._parseHeadersToHashTable(this.text);"undefined"!=typeof this.headers.match&&("undefined"==typeof this.headers.include?this.headers.include=this.headers.match:this.headers.include.concat(this.headers.match))},_parseHeadersToHashTable:function(a){var b={};a=a.split(/\n/);for(var d=0;d<a.length;d++){var c=a[d];if(0==c.indexOf("// ==/UserScript=="))break;var e=c.match(/\/\/ @(\S+)\s*(.*)/);if(null!=e)switch(c=e[1],e=e[2].replace(/\n|\r/g,
""),c){case "include":case "exclude":case "match":case "require":b[c]=b[c]||[];b[c].push(e);break;case "all-frames":b[c]=/^true/i.test(e);break;default:b[c]=e}}return b}};module.exports=new UserscriptEngine;module.exports.UserscriptEngine=UserscriptEngine;module.exports.Userscript=Userscript;








var core=require("kango/core"),utils=require("kango/utils"),browser=require("kango/browser"),lang=require("kango/lang"),object=utils.object;
core.addEventListener("ready",function(){var d=module.exports,b=function(a,c,b){c=d.getScripts(a.document.URL,c,b);object.forEach(c,function(b,c){lang.evalScriptsInSandbox(a,b,c)})};browser.addEventListener("DocumentLoaded",function(a){a=a.window;b(a,"document-end",a==a.top)});browser.addEventListener("DocumentInserted",function(a){a=a.window;b(a,"document-start",a==a.top)})});
