$networks = 'eth', 'avax', 'pol', 'bsc', 'arb', 'opt'
$urls = 'etherscan', 'snowtrace', 'polygonscan', 'bscscan',  'arbiscan', 'optimisticscan'
$commands = 'labels.labelcloud.exchange', 'labels.labelcloud.dex', 'labels.labelcloud.null'
for ($counter=0; $counter -lt $networks.Length; $counter++) {
    $network = $networks[$counter]
    $url = $urls[$counter]
    
    for($counter2=0; $counter2 -lt $commands.Length; $counter2++) {
        $command = $commands[$counter2]
        scrapy crawl $command -a site=$url
        $newPath = $command + "." + $network
        $oldFile = "data/" + $newPath
        $generatedFile = "data/" + $command
        Remove-item -PATH $oldFile
        Rename-Item -PATH $generatedFile -NewName $newPath
    }

}
