exports.object.freeze=function(a){return 0<=Services.vc.compare(Services.appinfo.platformVersion,"24.0")?Object.freeze(a):a};
