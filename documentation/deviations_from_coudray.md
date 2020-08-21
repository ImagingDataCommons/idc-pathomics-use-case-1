# Deviations from Coudray's code

## Tile preparation
* We did use the complete 2167 slides to generate tiles from in contrast to the ~ 1600 slides that Coudray used
* When assigning tiles to training, test and validation set (done separately per class like in coudray's), we did know the total number of tiles -> first assigned patients to test until at least 15% of tiles are in test, then at least 15% validation, leftovers went to training. In contrast Coudray did not know the total number of tiles and thus considered only the number of tiles already sorted -> this means first patient would go to test, second to validation, then to training as long as the percentages of test and validation went down below 15 % again.
