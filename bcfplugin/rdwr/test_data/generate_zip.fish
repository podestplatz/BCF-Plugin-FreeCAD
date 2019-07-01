set dirName "Issues_BIMcollab_Example"
cd $dirName 

for issue in $argv
  zip -r ../"$dirName".bcf $issue
end

zip ../"$dirName".bcf project.bcfp bcf.version

cd ../
