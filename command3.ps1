
$commands = 'labels.labelcloud.exchange', 'labels.labelcloud.dex', 'labels.labelcloud.null'
$network = 'ftm'
$url = 'ftmscan'
    
for ($counter=0; $counter -lt $commands.Length; $counter++) {
    $command = $commands[$counter]
    
    scrapy crawl $command -a site=$url
    $newPath = $command + "." + $network
    $oldFile = "data/" + $newPath
    $generatedFile = "data/" + $command
    Remove-item -PATH $oldFile
    Rename-Item -PATH $generatedFile -NewName $newPath

}
