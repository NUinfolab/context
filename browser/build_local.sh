# Define list of extensions, pass script argument to build just one
ext_list=('infolabcontext')

if [ $1 ]; then
    ext_list=($1)
fi

for name in "${ext_list[@]}"
do  
    echo "Building local $name..."
    
    cp $name/src/common/extension_info.json.local $name/src/common/extension_info.json
    python kango/kango.py build $name
done
