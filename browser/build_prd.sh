# Define list of extensions, pass script argument to build just one
ext_list=('context',)

if [ $1 ]; then
    ext_list=($1)
fi

# Where built extensions get copied to
deployment_dir="../web/flaskapp/static/browser-extensions/"

# Doit
for name in "${ext_list[@]}"
do  
    echo -e "\nProcessing $name..."

    cp $name/src/common/extension_info.json.prd $name/src/common/extension_info.json
    python kango/kango.py build $name
    
    echo -e "\nCopying extensions..."   
        
    pushd $name/output/safari > /dev/null
    for d in *.safariextension
    do
        zip -r $d.zip $d > /dev/null
        mv $d.zip ../web/static/browser-extensions/
        echo "* $name/output/safari/$d.zip"
    done
    popd > /dev/null
    
    file_list=( $(find $name/output -name ${name}_*.crx -or -name ${name}_*.xpi) )   
    for f in "${file_list[@]}"
    do
        echo "* $f"
        cp $f $deployment_dir
    done
done
