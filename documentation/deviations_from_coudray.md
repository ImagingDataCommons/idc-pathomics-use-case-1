# Deviations from Coudray's code

## Tile preparation
* We did use the complete 2167 slides to generate tiles from in contrast to the ~ 1600 slides that Coudray used
* When tiling we directly excluded border tiles that can not match our required size of 512x512px, Coudray ignored them at a later step. 
* When assigning tiles to training, test and validation set (done separately per class like in coudray's), we did know the total number of tiles -> first assigned patients to test until at least 15% of tiles are in test, then at least 15% validation, leftovers went to training. In contrast Coudray did not know the total number of tiles and thus considered only the number of tiles already sorted -> this means first patient would go to test, second to validation, then to training as long as the percentages of test and validation went down below 15 % again.
* Coudray generates border tiles of rectangular (instead of quadratic) shape -> probably he is filtering them out prior to feeding the data to the network. 
* Some of coudray's tiles have sharp lines with background on the other side of the line -> not sure yet whether we have them, too 