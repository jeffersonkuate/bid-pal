# Bid Pal

## Introduction

This tool is intended to provide an intuitive and equitable method of distributing an arbitrary amount of assets between
an arbitrary amount of players.

The drafting process is as follows.
1. The first player enters the name of an asset as listed in a user defined list under the `assetSets` attribute of the
`config.json` file. The specific list to be used is determined by the `assetSet` (singular) attribute.
2. The same player enters an amount less than his current balance (initial balance determined by the `startBalance`
attribute) to bid on the asset.
3. The next player in rotation can choose whether or not to pay the previous bid multiplied by the Bid-Multiplier
rounded up (as determined by the `bidMultiplier` attribute), if their balance exceeds that amount.
   - If they choose to do so the bid is increased and the next player in rotation gets the same option.
   - If a player cannot bid or chooses not to, they are removed from the bidding process for the current asset.
4. The bidding process continues for X more rounds with a rotating starting player (X determined by the `initialDrafts`
attribute).
5. The last player left eligible to bid on an asset is awarded the asset and is debited their bid amount from their
current balance.