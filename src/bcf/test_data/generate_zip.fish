set dirName "Example1"
cd $dirName 

for issue in $argv
  zip -r ../"$dirName".bcf $issue
end

zip ../"$dirName".bcf project.bcfp bcf.version

cd ../
