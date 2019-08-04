#Bid Pal

##Introduction

This tool is intended to provide an intuitive and equitable method of distributing an arbitrary amount of assets between
an arbitrary amount of players.

The drafting process is as follows. The first player enters the name of an asset as listed in a user defined list under
the `assetSets` attribute of the `config.json` file. The specific list to be used is determined by the `assetSet`
(singular) attribute. The same player then get's to enter an amount less than his current balance (initial balance
determined by the `startBalance` attribute) to bid on the asset. The next player can choose whether or not to pay
the previous bid multiplied by the Bid-Multiplier rounded down (as determined by the `bidMultiplier` attribute), if
their balance exceeds that amount. If they choose to do so the bid is increased and the next player in line gets the
same option. If a player cannot bid or choose not to, they are removed from the bidding process for the current asset.
The last player left eligible to bid on an asset is awarded the asset and is debited their bid amount from their current
balance. The bidding process then continues for X more rounds with a rotating starting player (X determined by the
`initialDrafts` attribute).