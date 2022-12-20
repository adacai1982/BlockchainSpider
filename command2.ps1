$networks = 'eth', 'avax', 'pol', 'bsc', 'arb', 'opt','ftm'
$urls = 'etherscan', 'snowtrace', 'polygonscan', 'bscscan',  'arbiscan', 'optimisticscan','ftmscan'
$command = 'labels.labelcloud.exchange'
for ($counter=0; $counter -lt $networks.Length; $counter++) {
    $network = $networks[$counter]
    $url = $urls[$counter]
    
    scrapy crawl $command -a site=$url
    $newPath = $command + "." + $network
    $oldFile = "data/" + $newPath
    $generatedFile = "data/" + $command
    Remove-item -PATH $oldFile
    Rename-Item -PATH $generatedFile -NewName $newPath

}
