var object=require("kango/utils").object;function Lang(){}Lang.prototype=object.extend(LangBase,{createHTMLSandbox:function(b,a){return a(window)}});module.exports=new Lang;
