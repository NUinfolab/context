"use strict";
_kangoLoader.add("kango/lang", function(require, exports, module) {
var NotImplementedException=require("kango/utils").NotImplementedException;function LangBase(){}LangBase.prototype={evalInSandbox:function(e,a){throw new NotImplementedException;},evalScriptsInSandbox:function(e,a){for(var b="",c=0;c<a.length;c++){for(var d=0;d<a[c].requires.length;d++)b+=a[c].requires[d].text+"\n\n";b+=a[c].text+"\n\n"}return this.evalInSandbox(e,b)}};








var object=require("kango/utils").object;function Lang(){}Lang.prototype=object.extend(LangBase,{createHTMLSandbox:function(b,a){return a(window)}});module.exports=new Lang;

});